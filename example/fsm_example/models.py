from django.db import models
from django.utils import timezone

from django_fsm.db.fields import FSMField, transition


class State(object):
    '''
    Constants to represent the `state`s of the PublishableModel
    '''
    DRAFT = 'draft'            # Early stages of content editing
    APPROVED = 'approved'      # Ready to be published
    PUBLISHED = 'published'    # Visible on the website
    EXPIRED = 'expired'        # Period for which the model is set to display has passed
    DELETED = 'deleted'        # Soft delete state

    CHOICES = (
        (DRAFT, DRAFT),
        (APPROVED, APPROVED),
        (PUBLISHED, PUBLISHED),
        (EXPIRED, EXPIRED),
        (DELETED, DELETED),
    )


class PublishableModel(models.Model):

    name = models.CharField(max_length=42, blank=False)

    # One state to rule them all
    state = FSMField(
        default=State.DRAFT,
        verbose_name='Publication State',
        choices=State.CHOICES,
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
    # to be refrenced.

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
        return self.state == State.EXPIRED

    def check_displayable(self, date):
        '''
        Check that the current date falls within this object's display dates,
        if set, otherwise default to being displayable.
        '''
        if not self.has_display_dates():
            return True

        displayable = self.display_from < date and self.display_until > date
        # Expired Pages should transition to the expired state
        if not displayable and not self.is_expired:
            self.expire()  # Calling the expire transition
            self.save()
        return displayable

    ########################################################
    # Workflow (state) Transitions

    @transition(field=state, source=[State.APPROVED, State.EXPIRED],
        target=State.PUBLISHED,
        conditions=[can_display])
    def publish(self):
        '''
        Publish the object.
        '''

    @transition(field=state, source=State.PUBLISHED, target=State.EXPIRED,
        conditions=[has_display_dates])
    def expire(self):
        '''
        Automatically called when a object is detected as being not
        displayable. See `check_displayable`
        '''
        self.display_until = timezone.now()

    @transition(field=state, source=State.PUBLISHED, target=State.APPROVED)
    def unpublish(self):
        '''
        Revert to the approved state
        '''

    @transition(field=state, source=State.DRAFT, target=State.APPROVED)
    def approve(self):
        '''
        After reviewed by stakeholders, the Page is approved.
        '''
