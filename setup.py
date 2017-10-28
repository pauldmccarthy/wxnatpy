#!/usr/bin/env python
#
# setup.py - setuptools configuration for wxnatpy
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#


from __future__ import print_function

import os.path as op

from setuptools import setup


basedir = op.dirname(__file__)

# Dependencies are listed in requirements.txt
install_requires = open(op.join(basedir, 'requirements.txt'), 'rt').readlines()
setup_requires   = ['pytest-runner'],
tests_require    = ['coverage', 'pytest-cov', 'pytest-runner', 'pytest'],

# Extract the version number from wxnat/__init__.py
version = {}
with open(op.join(basedir, "wxnat", "__init__.py"), 'rt') as f:
    for line in f:
        if line.startswith('__version__'):
            exec(line, version)
            break

version = version.get('__version__')

# long description from readme
with open(op.join(basedir, 'README.md'), 'rt') as f:
    readme = f.read()

setup(

    name='wxnatpy',
    version=version,
    description='wxPython XNAT repository browser',
    long_description=readme,
    url='https://github.com/pauldmccarthy/wxnatpy',
    author='Paul McCarthy',
    author_email='pauldmccarthy@gmail.com',
    license='Apache License Version 2.0',

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Topic :: Software Development :: Libraries :: Python Modules'],

    packages=['wxnat'],
    include_package_data=True,
    install_requires=install_requires,
    setup_requires=setup_requires,
    tests_require=tests_require,
    test_suite='wxnat/tests',
)
