
# django-fsm-admin

Mixin and template tags to integrate django-fsm state transitions into 
the django admin.

## Usage

In your admin.py file:

    from fsm_admin.mixins import FSMTransitionMixin

    class YourModelAdmin(FSMTransitionMixin, admin.ModelAdmin):
        pass

    admin.site.register(PublishableModel, PublishableModelAdmin)

Override the admin change_form.html for your model
(your_app/templates/admin/your_app/your_model/change_form.html)

    {% extends 'admin/change_form.html' %}
    {% load fsm_admin %} 

    {% block submit_buttons_bottom %}{% fsm_submit_row %}{% endblock %}

    {% block after_field_sets %}
        {{ block.super }}
        {% block transition_hints %}{% fsm_transition_hints %}{% endblock %}
    {% endblock %}  

## Try the example

    mkvirtualenv fsm_admin
    python setup.py develop
    cd example
    pip install -r requirements.txt
    ./manage.py syncdb
    ./manage.py runserver
