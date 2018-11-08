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

from __future__ import absolute_import, division, print_function

from inspire_utils.record import get_value, get_values_for_schema


def test_get_value_returns_all_values():
    record = {
        'titles': [
            {'title': 'first title'},
            {'title': 'second title'},
        ],
    }

    expected = [
        'first title',
        'second title',
    ]
    result = get_value(record, 'titles.title')

    assert expected == result


def test_get_value_allows_indexes_in_paths():
    record = {
        'titles': [
            {'title': 'first title'},
            {'title': 'second title'},
        ],
    }

    expected = 'second title'
    result = get_value(record, 'titles.title[1]')

    assert expected == result


def test_get_value_allows_slices_in_paths():
    record = {
        'titles': [
            {'title': 'first title'},
            {'title': 'second title'},
        ],
    }

    expected = [
        'first title',
        'second title',
    ]
    result = get_value(record, 'titles.title[:]')

    assert expected == result


def test_get_value_returns_none_if_inner_key_does_not_exist_on_string():
    record = {
        'foo': 'bar'
    }

    result = get_value(record, 'foo.value')

    assert result is None


def test_get_values_for_schema():
    elements = [
        {'schema': 'good', 'value': 'first'},
        {'schema': 'bad', 'value': 'second'},
        {'schema': 'good', 'value': 'third'},
    ]
    assert get_values_for_schema(elements, 'good') == ['first', 'third']
