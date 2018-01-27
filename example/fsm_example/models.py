from django.db import models
from django.utils import timezone
from django_fsm import FSMField, transition

from .utils import ModelEnum


class State(ModelEnum):
    """Constants to represent the `state`s of the PublishableModel"""
    DRAFT = 'DRAFT'            # Early stages of content editing
    APPROVED = 'APPROVED'      # Ready to be published
    PUBLISHED = 'PUBLISHED'    # Visible on the website
    EXPIRED = 'EXPIRED'        # Period for which the model is set to display has passed
    DELETED = 'DELETED'        # Soft delete state

    @classmethod
    def get_states__accessible_by_employee(cls):
        """An employee can access the only if the post.state is not State.DELETED"""
        return [state.value for index, state in enumerate(cls.get_all_members())
                if state.name not in [State.DELETED]]

    @classmethod
    def get_states__previously_published(cls):
        """Post would be published at some point of time only if post.state is one of these:
            State.PUBLISHED
            State.EXPIRED
            State.DELETED
        """
        relevant_states = [State.PUBLISHED,
                           State.EXPIRED,
                           State.DELETED]

        return [state.value for index, state in enumerate(relevant_states)]


class PublishableModel(models.Model):

    name = models.CharField(max_length=42, blank=False)

    # One state to rule them all
    state = FSMField(
        default=State.DRAFT.value,
        verbose_name='Publication State',
        choices=State.paired_details(),
        protected=True,
    )

    # For scheduled publishing
    display_from = models.DateTimeField(blank=True, null=True)
    display_until = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = 'Post'
        verbose_name_plural = 'Posts'

    def __unicode__(self):
        return self.name

    ########################################################
    # Transition Conditions
    # These must be defined prior to the actual transitions
    # to be referenced.

    def has_display_dates(self):
        return self.display_from and self.display_until
    has_display_dates.hint = 'Display dates are required to expire a page.'

    def can_display(self):
        '''
        The display dates must be valid for the current date
        '''
        return self.check_displayable(timezone.now())
    can_display.hint = 'The display dates may need to be adjusted.'

    def is_expired(self):
        return self.state == State.EXPIRED.value

    def check_displayable(self, date):
        """
        Check that the current date falls within this object's display dates,
        if set, otherwise default to being displayable.
        """
        if not self.has_display_dates():
            return True

        displayable = self.display_from < date < self.display_until
        # Expired Pages should transition to the expired state
        if not displayable and not self.is_expired:
            self.expire()  # Calling the expire transition
            self.save()
        return displayable

    ########################################################
    # Workflow (state) Transitions

    @transition(field=state, source=[State.APPROVED.value, State.EXPIRED.value],
                target=State.PUBLISHED.value,
                conditions=[can_display])
    def publish(self):
        """
        Publish the object.
        """

    @transition(field=state, source=State.PUBLISHED.value, target=State.EXPIRED.value,
                conditions=[has_display_dates])
    def expire(self):
        """
        Automatically called when a object is detected as being not
        displayable. See `check_displayable`
        """
        self.display_until = timezone.now()

    @transition(field=state, source=State.PUBLISHED.value, target=State.APPROVED.value)
    def unpublish(self):
        """
        Revert to the approved state
        """

    @transition(field=state, source=State.DRAFT.value, target=State.APPROVED.value)
    def approve(self):
        """
        After reviewed by stakeholders, the Page is approved.
        """

    @transition(field=state, source=State.EXPIRED.value, target=State.DRAFT.value)
    def reactivate(self):
        """
        Even after expiring, the page can be re-posted.
        """

