from __future__ import unicode_literals

from collections import defaultdict

from django.contrib.contenttypes.models import ContentType
from django.contrib import messages
from django.utils.translation import ugettext as _
from django.contrib.admin.models import LogEntry, CHANGE
from django.utils.encoding import force_text, force_unicode
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

    # name of the FSMField on the model to transition
    fsm_field = 'state'
    change_form_template = 'fsm_admin/change_form.html'

    def _fsm_get_transitions(self, obj, perms=None):
        """
        Gets a list of transitions available to the user.

        Available state transitions are provided by django-fsm
        following the pattern get_available_FIELD_transitions
        """
        transitions_func = 'get_available_{}_transitions'.format(self.fsm_field)
        transitions = getattr(obj, transitions_func)() if obj else []
        return transitions

    def get_redirect_url(self, request, obj):
        """
        Hook to adjust the redirect post-save.
        """
        return request.path

    @property
    def fsm_field_instance(self):
        """
        Returns the actual state field instance, as opposed to
        fsm_field attribute representing just the field name.
        """
        return self.model._meta.get_field_by_name(self.fsm_field)[0]

    def display_fsm_field(self, obj):
        """
        Makes sure get_FOO_display() is used for choices-based FSM fields.
        """
        if self.fsm_field_instance.choices:
            return getattr(obj, 'get_%s_display' % self.fsm_field)()
        else:
            return getattr(obj, self.fsm_field)

    def response_change(self, request, obj):
        """
        Override of `ModelAdmin.response_change` to detect the FSM button
        that was clicked in the submit row and perform the state transtion.
        """
        # Each transition button is named with the transition.
        # e.g. _fsmtransition-publish
        #      _fsmtransition-delete
        transition_key = [k for k in request.POST.keys() if k.startswith("_fsmtransition")]
        if not transition_key:
            return super(FSMTransitionMixin, self).response_change(request, obj)

        # Extract the function name from the transition key
        transition = transition_key[0].split('-')[1]
        original_state = self.display_fsm_field(obj)
        msg_dict = {
            'obj': force_text(obj),
            'transition': transition,
        }

        # Ensure the requested transition is availble
        transitions = self._fsm_get_transitions(obj)
        available = any([t.name == transition for t in transitions])
        trans_func = getattr(obj, transition, None)

        if available and trans_func:
            # Run the transition
            try:
                #Attempt to pass in the by argument if using django-fsm-log
                trans_func(by=request.user)
            except TypeError:
                #If the function does not have a by attribute, just call with no arguments
                trans_func()

            # The transition may not be marked to automatically save, so
            # we assume that it should always be saved.
            obj.save()
            new_state = self.display_fsm_field(obj)

            # Done! Log the change and message user
            self.log_state_change(obj, request.user.id, original_state, new_state)
            msg_dict.update({'new_state': new_state})
            msg = _('%(obj)s successfully set to %(new_state)s') % msg_dict
            self.message_user(request, msg, messages.SUCCESS)
        else:
            msg = _('Error! %(obj)s failed to %(transition)s') % msg_dict
            self.message_user(request, msg, messages.ERROR)

        opts = self.model._meta
        redirect_url = self.get_redirect_url(request=request, obj=obj)

        preserved_filters = self.get_preserved_filters(request)
        redirect_url = add_preserved_filters({'preserved_filters': preserved_filters, 'opts': opts}, redirect_url)
        return HttpResponseRedirect(redirect_url)

    def log_state_change(self, obj, user_id, original_state, new_state):
        """
        Log the transition of the object to the history.
        """
        LogEntry.objects.log_action(
            user_id=user_id,
            content_type_id=ContentType.objects.get_for_model(obj.__class__).pk,
            object_id=obj.pk,
            object_repr=force_unicode(obj),
            action_flag=CHANGE,
            change_message='Changed {} from {} to {}'.format(self.fsm_field_instance.verbose_name, original_state, new_state),
        )

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

                hint = getattr(condition, 'hint', '')
                if hint:
                    hints[transition.name].append(hint)

        return dict(hints)

    def _get_possible_transitions(self, obj):
        """
        Get valid state transitions from the current state of `obj`
        """
        fsmfield = obj._meta.get_field_by_name(self.fsm_field)[0]
        transitions = fsmfield.get_all_transitions(self.model)
        for transition in transitions:
            if transition.source in [getattr(obj, self.fsm_field), '*']:
                yield transition
