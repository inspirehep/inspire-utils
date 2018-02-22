# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2018 CERN.
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

"""Description"""

from __future__ import absolute_import, division, print_function

import pytest

from inspire_utils.urls import ensure_scheme, record_url_by_pattern


@pytest.mark.parametrize(
    'url,scheme,expected',
    [
        ('http://inspirehep.net', None, 'http://inspirehep.net'),
        ('http://inspirehep.net', 'https', 'http://inspirehep.net'),
        ('inspirehep.net', None, 'http://inspirehep.net'),
        ('inspirehep.net', 'custom+http', 'custom+http://inspirehep.net'),
        (u'ïnśpirę.nẽt', 'https', u'https://ïnśpirę.nẽt'),
    ],
    ids=[
        'scheme already present',
        'scheme present, ignores default',
        'add default scheme',
        'add custom scheme',
        'unicode',
    ]
)
def test_ensure_scheme(url, scheme, expected):
    if scheme:
        assert ensure_scheme(url, default_schema=scheme) == expected
    else:
        assert ensure_scheme(url) == expected


@pytest.mark.parametrize(
    'pattern,recid,expected',
    [
        (
            'http://inspirehep.net/record/{recid}',
            123,
            'http://inspirehep.net/record/123',
        ),
        (
            'inspirehep.net/record/{recid}',
            '4567',
            'http://inspirehep.net/record/4567',
        ),
        (
            u'http://ïnśpirę.nẽt/record/{recid}',
            123,
            u'http://ïnśpirę.nẽt/record/123',
        ),
    ],
    ids=[
        'integer recid, scheme already present',
        'string recid, no scheme',
        'unicode url',
    ]
)
def test_record_url_by_pattern(pattern, recid, expected):
    assert record_url_by_pattern(pattern, recid) == expected
