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

2. Ensure that you have "django.core.context_processors.request" in your TEMPLATE_CONTEXT_PROCESSORS in Django settings. If TEMPLATE_CONTEXT_PROCESSORS is not yet defined, add
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

