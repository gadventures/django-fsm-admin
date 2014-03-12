
# django-fsm-admin

Simple mixin and template tag to integrate django-fsm state
transitions into the django admin.


## Try the example

    mkvirtualenv fsm_admin
    python setup.py develop
    cd example
    pip install -r requirements.txt
    ./manage.py syncdb
    ./manage.py runserver
