from __future__ import unicode_literals

from collections import defaultdict

from django.conf import settings
from django.contrib import messages
from django.utils.translation import ugettext as _
from django.utils.encoding import force_text
from django.contrib.admin.templatetags.admin_urls import add_preserved_filters
from django.http import HttpResponseRedirect


class FSMTransitionMixin(object):
    """
    Mixin to use with `admin.ModelAdmin` to support transitioning
    a model from one state to another (workflow style).

    * The change_form.html must be overriden to use the custom submit
      row template (on a model or global level).

          {% load fsm_admin %}
          {% block submit_buttons_bottom %}{% fsm_submit_row %}{% endblock %}

    * To optionally display hints to the user about what's needed
      to transition to other states that aren't available due to unmet
      pre-conditions, add this to the change_form as well:

          {% block after_field_sets %}
              {{ block.super }}
              {% fsm_transition_hints %}
          {% endblock %}

    * There must be one and only one FSMField on the model.
    * There must be a corresponding model function to run the transition,
      generally decorated with the transition decorator. This is what
      determines the available transitions. Without a function, the action
      in the submit row will not be available.
    * In the absence of specific transition permissions, the user must
      have change permission for the model.
    """
    # Each transition input is named with the state field and transition.
    # e.g. _fsmtransition-publish_state-publish
    #      _fsmtransition-revision_state-delete
    fsm_input_prefix = '_fsmtransition'
    # The name of one or more FSMFields on the model to transition
    fsm_field = ['state']
    change_form_template = 'fsm_admin/change_form.html'
    default_disallow_transition = not getattr(settings, 'FSM_ADMIN_FORCE_PERMIT', False)

    def _fsm_get_transitions(self, obj, request, perms=None):
        """
        Gets a list of transitions available to the user.

        Available state transitions are provided by django-fsm
        following the pattern get_available_FIELD_transitions
        """
        user = request.user
        fsm_fields = self._get_fsm_field_list()

        transitions = {}
        for field in fsm_fields:
            transitions_func = 'get_available_user_{0}_transitions'.format(field)
            transitions_generator = getattr(obj, transitions_func)(user) if obj else []
            transitions[field] = self._filter_admin_transitions(transitions_generator)
        return transitions

    def get_redirect_url(self, request, obj):
        """
        Hook to adjust the redirect post-save.
        """
        return request.path

    def fsm_field_instance(self, fsm_field_name):
        """
        Returns the actual state field instance, as opposed to
        fsm_field attribute representing just the field name.
        """
        return self.model._meta.get_field(fsm_field_name)

    def display_fsm_field(self, obj, fsm_field_name):
        """
        Makes sure get_FOO_display() is used for choices-based FSM fields.
        """
        field_instance = self.fsm_field_instance(fsm_field_name)
        if field_instance and field_instance.choices:
            return getattr(obj, 'get_%s_display' % fsm_field_name)()
        else:
            return getattr(obj, fsm_field_name)

    def response_change(self, request, obj):
        """
        Override of `ModelAdmin.response_change` to detect the FSM button
        that was clicked in the submit row and perform the state transtion.
        """
        if not getattr(obj, '_fsmtransition_results', None):
            return super(FSMTransitionMixin, self).response_change(request, obj)

        if obj._fsmtransition_results['status'] == messages.SUCCESS:
            msg = _('%(obj)s successfully set to %(new_state)s') % obj._fsmtransition_results
        else:
            msg = _('Error! %(obj)s failed to %(transition)s') % obj._fsmtransition_results

        self.message_user(request, msg, obj._fsmtransition_results['status'])

        opts = self.model._meta
        redirect_url = self.get_redirect_url(request=request, obj=obj)

        preserved_filters = self.get_preserved_filters(request)
        redirect_url = add_preserved_filters({'preserved_filters': preserved_filters, 'opts': opts}, redirect_url)
        return HttpResponseRedirect(redirect_url)

    def _is_transition_available(self, obj, transition, request):
        """
        Checks if the requested transition is available
        """
        transitions = []
        for field, field_transitions in iter(self._fsm_get_transitions(obj, request).items()):
            transitions += [t.name for t in field_transitions]
        return transition in transitions

    def _filter_admin_transitions(self, transitions_generator):
        """
        Filter the given list of transitions, if their transition methods are declared as admin
        transitions. To allow a transition inside fsm_admin, add the parameter
        `admin=True` to the transition decorator, for example:
        ```
        @transition(field='state', source=['startstate'], target='finalstate', custom=dict(admin=True))
        def do_something(self):
            ...
        ```

        If the configuration setting `FSM_ADMIN_FORCE_PERMIT = True` then only transitions with
        `custom=dict(admin=True)` are allowed. Otherwise, if `FSM_ADMIN_FORCE_PERMIT = False` or
        unset only those with `custom=dict(admin=False)`
        """
        for transition in transitions_generator:
            if transition.custom.get('admin', self.default_disallow_transition):
                yield transition

    def _get_requested_transition(self, request):
        """
        Extracts the name of the transition requested by user
        """
        for key in request.POST.keys():
            if key.startswith(self.fsm_input_prefix):
                fsm_input = key.split('-')
                return (fsm_input[1], fsm_input[2])
        return None, None

    def _do_transition(self, transition, request, obj, form, fsm_field_name):
        original_state = self.display_fsm_field(obj, fsm_field_name)
        msg_dict = {
            'obj': force_text(obj),
            'transition': transition,
            'original_state': original_state,
        }
        # Ensure the requested transition is available
        available = self._is_transition_available(obj, transition, request)
        trans_func = getattr(obj, transition, None)
        if available and trans_func:
            # Run the transition
            try:
                # Attempt to pass in the request and by argument if using django-fsm-log
                trans_func(request=request, by=request.user)
            except TypeError:
                try:
                    # Attempt to pass in the by argument if using django-fsm-log
                    trans_func(by=request.user)
                except TypeError:
                    # If the function does not have a by attribute, just call with no arguments
                    trans_func()
            new_state = self.display_fsm_field(obj, fsm_field_name)

            # Mark the fsm_field as changed in the form so it will be
            # picked up when the change message is constructed
            form.changed_data.append(fsm_field_name)

            msg_dict.update({'new_state': new_state, 'status': messages.SUCCESS})
        else:
            msg_dict.update({'status': messages.ERROR})

        # Attach the results of our transition attempt
        setattr(obj, '_fsmtransition_results', msg_dict)

    def save_model(self, request, obj, form, change):
        fsm_field, transition = self._get_requested_transition(request)
        if transition:
            self._do_transition(transition, request, obj, form, fsm_field)
        super(FSMTransitionMixin, self).save_model(request, obj, form, change)

    def get_transition_hints(self, obj):
        """
        See `fsm_transition_hints` templatetag.
        """
        hints = defaultdict(list)
        transitions = self._get_possible_transitions(obj)

        # Step through the conditions needed to accomplish the legal state
        # transitions, and alert the user of any missing condition.
        # TODO?: find a cleaner way to enumerate conditions methods?
        for transition in transitions:
            for condition in transition.conditions:

                # If the condition is valid, then we don't need the hint
                if condition(obj):
                    continue

                # if the transition is hidden, we don't need the hint
                if transition.custom.get('admin', self.default_disallow_transition):
                    continue

                hint = getattr(condition, 'hint', '')
                if hint:
                    if hasattr(transition, 'custom') and transition.custom.get(
                            'button_name'):
                        hints[transition.custom['button_name']].append(hint)
                    else:
                        hints[transition.name.title()].append(hint)

        return dict(hints)

    def _get_possible_transitions(self, obj):
        """
        Get valid state transitions from the current state of `obj`
        """
        fsm_fields = self._get_fsm_field_list()
        for field in fsm_fields:
            fsmfield = obj._meta.get_field(field)
            transitions = fsmfield.get_all_transitions(self.model)
            for transition in transitions:
                if transition.source in [getattr(obj, field), '*']:
                    yield transition

    def _get_fsm_field_list(self):
        """
        Ensure backward compatibility by converting a single fsm field to
        a list.  While we are guaranteeing compatibility we should use
        this method to retrieve the fsm field rather than directly
        accessing the property.
        """
        if not isinstance(self.fsm_field, (list, tuple,)):
            return [self.fsm_field]

        return self.fsm_field
