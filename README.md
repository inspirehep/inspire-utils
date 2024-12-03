
<!--
    This file is part of INSPIRE.
    Copyright (C) 2014-2024 CERN.

    INSPIRE is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    INSPIRE is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with INSPIRE. If not, see <http://www.gnu.org/licenses/>.

    In applying this license, CERN does not waive the privileges and immunities
    granted to it by virtue of its status as an Intergovernmental Organization
    or submit itself to any jurisdiction.
-->

 # INSPIRE-Utils

### About
INSPIRE-specific utils.


### Development

Tests should be run both for python 2 and python 3.
For python 2 its recommended to run them through docker:
```bash
docker build -f Dockerfile.py2   -t inspire-utils:py2 .
docker run inspire-utils:py2 pytest tests
```

For python 3 you can run them locally:
```bash
pip install .[tests]
pytest tests
```

