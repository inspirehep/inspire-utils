# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014-2017 CERN.
#
# INSPIRE is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE. If not, see <http://www.gnu.org/licenses/>.
#
# In applying this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

"""INSPIRE-specific utils."""

from __future__ import absolute_import, division, print_function

from setuptools import find_packages, setup


URL = 'https://github.com/inspirehep/inspire-utils'

readme = open('README.rst').read()

setup_requires = [
    'autosemver~=0.0,>=0.5.2',
]

install_requires = [
    'Unidecode~=1.0,>=1.0.22',
    'babel~=2.0,>=2.5.1',
    'lxml~=4.0,>=4.4.0',
    'nameparser~=0.0,>=0.5.3',
    'python-dateutil~=2.0,>=2.6.1',
    'six~=1.0,>=1.10.0',
    'elasticsearch==7.1.0',
    'elasticsearch-dsl~=7.1',
    'inspire-schemas==61.4.12',
    'parsel>=1.5'
]

docs_require = []

tests_require = [
    'flake8-future-import~=0.0,>=0.4.3',
    'mock~=2.0,>=2.0.0',
    'pytest-cov~=2.0,>=2.5.1',
    'pytest~=4.0,>=4.6.0',
]

extras_require = {
    'docs': docs_require,
    'tests': tests_require,
    'tests:python_version=="2.7"': [
        'unicode-string-literal~=1.0,>=1.1',
    ],
}

extras_require['all'] = []
for name, reqs in extras_require.items():
    extras_require['all'].extend(reqs)

packages = find_packages(exclude=['docs'])

setup(
    name='inspire-utils',
    autosemver={
        'bugtracker_url': URL + '/issues',
    },
    url=URL,
    license='GPLv3',
    author='CERN',
    author_email='admin@inspirehep.net',
    packages=packages,
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    description=__doc__,
    long_description=readme,
    setup_requires=setup_requires,
    install_requires=install_requires,
    tests_require=tests_require,
    extras_require=extras_require,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
