#!/usr/bin/env python3

from distutils.core import setup

setup(name='LMS-Dependency-Manager',
    version='1.0',
    description='Handle C/C++ Projects',
    author='Philipp Schmette',
    author_email='philipp.schmette@gmx.de',
    url='https://github.com/lms-org/dependency_manager',
    packages=['lms'],
    package_data={'lms': ['data/lms_packagelist.json']},
    scripts=['lms-install-dependency.py', 'lms-register-dependency.py']
)
