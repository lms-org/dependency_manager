#!/usr/bin/env python3

from distutils.core import setup

setup(name='LMS-Dependency-Manager',
    version='1.0',
    description='Handle C/C++ Projects',
    author='Philipp Schmette',
    author_email='philipp.schmette@gmx.de',
    url='https://github.com/lms-org/dependency_manager',
    packages=['lms_dm'],
    package_data={'lms_dm': ['data/lms_packagelist.json','data/tum_phoenix_packagelist.json']},
    scripts=['lpm', 'lms-register-dependency.py']
)
