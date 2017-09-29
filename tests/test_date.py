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

import pytest

from inspire_utils.date import (
    PartialDate,
    earliest_date,
    format_date,
    normalize_date,
)


def test_partial_date_accepts_valid_dates():
    PartialDate(1686, 6, 30)


def test_partial_date_raises_on_invalid_dates():
    with pytest.raises(ValueError):
        PartialDate(1686, 1, 42)


def test_partial_date_raises_on_day_with_no_month():
    with pytest.raises(TypeError):
        PartialDate(1686, None, 30)


def test_partial_date_raises_on_wrong_types():
    with pytest.raises(TypeError):
        PartialDate('1686', '6', '30')


def test_partial_date_equality():
    assert PartialDate(1686, 6) == PartialDate(1686, 6)


def test_partial_dates_sorts_incomplete_dates_after_complete_dates():
    complete = PartialDate(1686, 6, 30)
    incomplete = PartialDate(1686)

    assert complete < incomplete


def test_partial_date_loads():
    expected = PartialDate(1686, 6)

    assert expected == PartialDate.loads('1686-06')


def test_partial_date_from_parts():
    expected = PartialDate(1686, 6)

    assert expected == PartialDate.from_parts(1686, 'June')


def test_partial_date_pprints_when_cast_to_str():
    expected = 'Jun, 1686'

    assert expected == str(PartialDate(1686, 6))


def test_format_date():
    expected = u'Jun 30, 1686'
    result = format_date('1686-06-30')

    assert expected == result


def test_format_date_incomplete():
    expected = u'Jun, 1686'
    result = format_date('1686-06')

    assert expected == result


def test_normalize_date_handles_ISO():
    expected = '1686-06-30'
    result = normalize_date('1686-06-30')

    assert expected == result


def test_normalize_date_handles_year_only():
    expected = '1686'
    result = normalize_date('1686')

    assert expected == result


def test_normalize_date_handles_year_month():
    expected = '1686-06'
    result = normalize_date('1686-06')

    assert expected == result


@pytest.mark.xfail(reason='Output is wrong as year has less than 4 digits')
def test_normalize_date_handles_default_dates():
    default_date1 = '0001-01-01'
    default_date2 = '0002-02-02'

    assert default_date1 == normalize_date('0001-01-01')
    assert default_date2 == normalize_date('0002-02-02')


def test_normalize_date_handles_human_friendly_dates():
    expected = '1686-06-30'
    result = normalize_date('Fri June 30 1686')

    assert expected == result


def test_normalize_date_raises_on_dates_without_year():
    with pytest.raises(ValueError):
        normalize_date('Fri June 30')


def test_normalize_date_raises_on_unparseable_dates():
    with pytest.raises(ValueError):
        normalize_date('Foo')


def test_earliest_date():
    expected = '1686-06-30'
    result = earliest_date(['1686-06', '1686-06-30'])

    assert expected == result
