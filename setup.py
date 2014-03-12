from setuptools import setup

setup(name='django-fsm-admin',
    version='0.0.1',
    author='G Adventures',
    author_email='software@gadventures.com',
    url='https://github.com/gadventures/django-fsm-admin',
    packages=[
        'fsm_admin',
    ],
    install_requires=[
        'Django>=1.6',
        'django-fsm>=1.5.1',
    ]
)
