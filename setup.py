#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
from setuptools import setup, find_packages

import fsm_admin

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

with open('README.rst') as f:
    readme = f.read()

setup(
    name='django-fsm-admin',
    version=fsm_admin.__version__,
    author=fsm_admin.__author__,
    description='Integrate django-fsm state transitions into the django admin',
    long_description=readme,
    author_email='software@gadventures.com',
    url='https://github.com/gadventures/django-fsm-admin',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Django>=1.6',
        'django-fsm>=2.0.0',
    ],
    keywords='django',
    license='MIT License',
    platforms=['any'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ]
)
