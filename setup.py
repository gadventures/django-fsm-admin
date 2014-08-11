from setuptools import setup, find_packages

setup(name='django-fsm-admin',
    version='1.0.4',
    author='G Adventures',
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
