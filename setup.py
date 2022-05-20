#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
from setuptools import setup, find_packages

import fsm_admin

readme = open("README.rst").read()

setup(
    name="django-fsm-admin",
    version=fsm_admin.__version__,
    author=fsm_admin.__author__,
    description="Integrate django-fsm state transitions into the django admin",
    long_description=readme,
    long_description_content_type="text/x-rst",
    author_email="software@gadventures.com",
    url="https://github.com/gadventures/django-fsm-admin",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "Django>=1.6",
        "django-fsm>=2.1.0",
    ],
    keywords="django fsm admin",
    license="MIT",
    platforms=["any"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
    ]
)
