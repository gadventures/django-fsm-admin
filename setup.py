from setuptools import setup, find_packages

setup(name='django-fsm-admin',
    version='0.0.3',
    author='G Adventures',
    author_email='software@gadventures.com',
    url='https://github.com/gadventures/django-fsm-admin',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Django>=1.6',
        'django-fsm>=1.5.1',
    ],
)
