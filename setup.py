#
# This file is part of INSPIRE.
# Copyright (C) 2014-2024 CERN.
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

from setuptools import find_packages, setup

URL = "https://github.com/inspirehep/inspire-utils"

with open("README.md") as f:
    readme = f.read()

install_requires = [
    'Unidecode~=1.0,>=1.2.0',
    'babel~=2.9,>=2.9.1',
    'lxml~=5.0',
    'nameparser~=1.1,>=1.1.3',
    'python-dateutil~=2.9,>=2.9.0',
    'six~=1.0,>=1.10.0'
]

docs_require = []

tests_require = [
    'flake8-future-import~=0.0,>=0.4.3',
    'mock~=2.0,>=2.0.0',
]

dev_require = [
    "pre-commit==3.5.0",
]

extras_require = {
    "docs": docs_require,
    "tests": tests_require,
    "dev": dev_require,
    'tests:python_version=="2.7"': [
        "unicode-string-literal~=1.0,>=1.1",
        "pytest~=4.0,>=4.6.0",
    ],
    'tests:python_version>="3"': [
        "pytest~=8.0,>=8.2.2",
    ],
}

extras_require["all"] = []
for _name, reqs in extras_require.items():
    extras_require["all"].extend(reqs)

packages = find_packages(exclude=["docs"])

setup(
    name="inspire-utils",
    url=URL,
    license="GPLv3",
    author="CERN",
    author_email="admin@inspirehep.net",
    packages=packages,
    include_package_data=True,
    zip_safe=False,
    platforms="any",
    description=__doc__,
    long_description=readme,
    install_requires=install_requires,
    tests_require=tests_require,
    extras_require=extras_require,
    version="3.0.62",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
