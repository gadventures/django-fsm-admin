.. _QuickCast: http://quick.as/aq8fogo
.. _django-fsm: https://github.com/kmmbvnr/django-fsm

===============================
django-fsm-admin
===============================

Mixin and template tags to integrate django-fsm_
state transitions into the django admin.

Installation
------------
::

    $ pip install django-fsm-admin

Or from github:

::

    $ pip install -e git://github.com/gadventures/django-fsm-admin.git#egg=django-fsm-admin

Usage
-----
1. Add ``fsm_admin`` to your INSTALLED_APPS

2. Ensure that you have "django.core.context_processors.request" in your TEMPLATE_CONTEXT_PROCESSORS
in Django settings. If TEMPLATE_CONTEXT_PROCESSORS is not yet defined, add
::
    from django.conf import global_settings

    TEMPLATE_CONTEXT_PROCESSORS = global_settings.TEMPLATE_CONTEXT_PROCESSORS + (
        'django.core.context_processors.request',
    )


3. In your ``admin.py`` file, use `FSMTransitionMixin` to add behaviour to your ModelAdmin.
FSMTransitionMixin should be before `ModelAdmin`, the order is important.

It assumes that your workflow state field is named `state` but you can override it
or add additional workflow state fields with the attribute `fsm_field`

::

    from fsm_admin.mixins import FSMTransitionMixin

    class YourModelAdmin(FSMTransitionMixin, admin.ModelAdmin):
        # The name of one or more FSMFields on the model to transition
        fsm_field = ['wf_state',]

        admin.site.register(YourModel, YourModelAdmin)

4. By adding ``custom=dict(admin=False)`` to the transition decorator, one can disallow a transition
to show up in the admin interface. This specially is useful, if the transition method accepts
parameters without default values, since in **django-fsm-admin** no arguments can be passed into the
transition method.

::

        @transition(field='state', source=['startstate'], target='finalstate', custom=dict(admin=False))
        def do_something(self, some_param):
            # will not add a button "Do Something" to your admin model interface

By adding ``FSM_ADMIN_FORCE_PERMIT = True`` to your configuration settings, the above restriction
becomes the default. Then one must explicitly allow that a transition method shows up in the
admin interface.

::

        @transition(field='state', source=['startstate'], target='finalstate', custom=dict(admin=True))
        def proceed(self):
            # will add a button "Proceed" to your admin model interface


This is useful, if most of your state transitions are handled by other means, such as external
events communicating with the API of your application.


Try the example
---------------

::

    $ git clone git@github.com:gadventures/django-fsm-admin.git
    $ cd django-fsm-admin
    $ mkvirtualenv fsm_admin
    $ pip install -r requirements.txt
    $ python fsm_admin/setup.py develop
    $ cd example
    $ ./manage.py syncdb
    $ ./manage.py runserver

Demo
----
Watch a QuickCast_ of the django-fsm-admin example

.. image:: http://i.imgur.com/IJuE9Sr.png
    :width: 728px
    :height: 346px
    :target: QuickCast_

