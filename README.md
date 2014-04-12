
# django-fsm-admin

Mixin and template tags to integrate [django-fsm](https://github.com/kmmbvnr/django-fsm)
state transitions into the django admin.

## Installation

    $ pip install django-fsm-admin

Or from github:

    $ pip install -e git://github.com/gadventures/django-fsm-admin.git#egg=django-fsm-admin

## Usage

1. Add `fsm_admin` to your INSTALLED_APPS

2. In your admin.py file, use `FSMTransitionMixin` to add behaviour to your ModelAdmin.

        from fsm_admin.mixins import FSMTransitionMixin

        class YourModelAdmin(FSMTransitionMixin, admin.ModelAdmin):
            pass

        admin.site.register(PublishableModel, PublishableModelAdmin)

3. Override the admin change_form.html for your model

        {% extends 'admin/change_form.html' %}
        {% load fsm_admin %}

        {% block submit_buttons_bottom %}{% fsm_submit_row %}{% endblock %}

        {% block after_field_sets %}
            {{ block.super }}
            {% fsm_transition_hints %}
        {% endblock %}  

(e.g. `your_app/templates/admin/your_app/your_model/change_form.html`)

## Try the example

    git clone git@github.com:gadventures/django-fsm-admin.git
    cd django-fsm-admin
    mkvirtualenv fsm_admin
    pip install -r requirements.txt
    python fsm_admin/setup.py develop
    cd example
    ./manage.py syncdb
    ./manage.py runserver

## Demo

[![Watch a QuickCast of the django-fsm-admin example](http://i.imgur.com/IJuE9Sr.png)](http://quick.as/aq8fogo)
