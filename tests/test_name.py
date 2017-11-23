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
from mock import patch

from inspire_utils.name import normalize_name, generate_name_variations, ParsedName


def test_normalize_name_full():
    expected = 'Smith, John Peter'

    assert expected == normalize_name('Smith, John Peter')


def test_normalize_name_handles_names_with_first_initial():
    expected = 'Smith, J. Peter'

    assert expected == normalize_name('Smith, J Peter')
    assert expected == normalize_name('Smith, J. Peter')
    assert expected == normalize_name('Smith, J. Peter ')


def test_normalize_name_handles_names_with_middle_initial():
    expected = 'Smith, John P.'

    assert expected == normalize_name('Smith, John P.')
    assert expected == normalize_name('Smith, John P. ')
    assert expected == normalize_name('Smith, John P ')


def test_normalize_name_handles_names_with_dots_initials():
    expected = 'Smith, J.P.'

    assert expected == normalize_name('Smith, J. P.')
    assert expected == normalize_name('Smith, J.P.')
    assert expected == normalize_name('Smith, J.P. ')
    assert expected == normalize_name('Smith, J. P. ')


def test_normalize_name_handles_names_with_spaces():
    expected = 'Smith, J.P.'

    assert expected == normalize_name('Smith, J P ')
    assert expected == normalize_name('Smith, J P')


def test_normalize_name_handles_names_with_several_last_names():
    expected = 'Smith Davis, J.P.'

    assert expected == normalize_name('Smith Davis, J.P.')


def test_normalize_name_handles_jimmy():  # http://jimmy.pink
    expected = 'Jimmy'

    assert expected == normalize_name('Jimmy')


def test_normalize_name_handles_unicode():
    expected = u'蕾拉'

    assert expected == normalize_name(u'蕾拉')


def test_normalize_name_converts_unicode_apostrophe_to_normal_apostrophe():
    expected = u'M\'Gregor, Jimmy'

    assert expected == normalize_name(u'M’Gregor, Jimmy')


@pytest.mark.parametrize("input_author_name,expected", [
    ('Smith, John Jr', 'Smith, John, Jr.'),
    ('Smith, John Jr.', 'Smith, John, Jr.'),
    ('Smith, John III', 'Smith, John, III'),
    ('Smith, John iii', 'Smith, John, III'),
    ('Smith, John VIII', 'Smith, John, VIII'),
    ('Smith, John viii', 'Smith, John, VIII'),
    ('Smith, John IV', 'Smith, John, IV'),
    ('Smith, John iv', 'Smith, John, IV'),
])
def test_normalize_name_handles_suffixes(input_author_name, expected):
    assert normalize_name(input_author_name) == expected


@pytest.mark.parametrize("input_author_name,expected", [
    ('Sir John Smith', 'Smith, John'),
    ('Bao, Hon', 'Bao, Hon'),
])
def test_normalize_name_handles_titles(input_author_name, expected):
    assert normalize_name(input_author_name) == expected


def test_generate_name_variations_with_two_non_lastnames():
    name = 'Ellis, John Richard'
    expected_name_variations = {
        'Ellis',
        'Ellis J',
        'Ellis J R',
        'Ellis J Richard',
        'Ellis John',
        'Ellis John R',
        'Ellis John Richard',
        'Ellis R',
        'Ellis Richard',
        'Ellis, J',
        'Ellis, J R',
        'Ellis, J Richard',
        'Ellis, John',
        'Ellis, John R',
        'Ellis, John Richard',
        'Ellis, R',
        'Ellis, Richard',
        'J Ellis',
        'J R Ellis',
        'J Richard Ellis',
        'John Ellis',
        'John R Ellis',
        'John Richard Ellis',
        'R Ellis',
        'Richard Ellis',
        'J, Ellis',
        'J R, Ellis',
        'J Richard, Ellis',
        'John, Ellis',
        'John R, Ellis',
        'John Richard, Ellis',
        'R, Ellis',
        'Richard, Ellis',
    }

    result = generate_name_variations(name)

    assert set(result) == expected_name_variations


def test_generate_name_variations_with_more_than_two_non_lastnames_does_not_add_extra_spaces():
    name = 'Ellis, John Richard Philip'

    result = generate_name_variations(name)

    assert 'Ellis, John  Philip' not in set(result)


def test_generate_name_variations_with_two_lastnames():
    name = u'Caro Estevez, David'
    expected = {
        # Lastnames only
        'Caro',
        'Caro Estevez',
        # Lastnames first and then non lastnames
        u'Caro Estevez D',
        u'Caro Estevez David',
        u'Caro Estevez, D',
        u'Caro Estevez, David',
        u'Caro D',
        u'Caro, D',
        u'Caro David',
        u'Caro, David',
        # Non lastnames first and then lastnames
        u'D Caro',
        u'D, Caro',
        u'D Caro Estevez',
        u'D, Caro Estevez',
        u'David Caro',
        u'David, Caro',
        u'David Caro Estevez',
        u'David, Caro Estevez',
    }

    result = generate_name_variations(name)

    assert set(result) == expected


def test_generate_name_variations_with_three_lastnames_dashed_ignores_the_dash():
    name = u'Caro-Estévez Martínez, David'
    expected = {
        # Lastnames only
        'Caro',
        'Caro Estevez Martinez',
        # Lastnames first and then non lastnames
        u'Caro Estevez Martinez D',
        u'Caro Estevez Martinez David',
        u'Caro Estevez Martinez, D',
        u'Caro Estevez Martinez, David',
        u'Caro D',
        u'Caro, D',
        u'Caro David',
        u'Caro, David',
        # Non lastnames first and then lastnames
        u'D Caro',
        u'D, Caro',
        u'D Caro Estevez Martinez',
        u'D, Caro Estevez Martinez',
        u'David Caro',
        u'David, Caro',
        u'David Caro Estevez Martinez',
        u'David, Caro Estevez Martinez',
    }

    result = generate_name_variations(name)

    assert set(result) == expected


def test_generate_name_variations_with_firstname_as_initial():
    name = 'Smith, J'
    expected = {
        # Lastname only
        'Smith',
        # Lastnames first and then non lastnames
        'Smith J',
        'Smith, J',
        # Non lastnames first and then lastnames
        'J Smith',
        'J, Smith',
    }

    result = generate_name_variations(name)

    assert set(result) == expected


def test_generate_name_variations_with_only_one_name():
    name = 'Jimmy'
    expected = {
        'Jimmy',
    }

    result = generate_name_variations(name)

    assert set(result) == expected


def test_generate_name_variations_with_one_name_does_capitalization():
    name = 'jimmy'
    expected = {
        'Jimmy',
    }

    result = generate_name_variations(name)

    assert set(result) == expected


def test_generate_name_variations_with_many_names_defers_generating_variations():
    import logging
    logger = logging.getLogger('inspire_utils.name')
    with patch.object(logger, 'error') as mock_error:
        many_names_as_one_author = 'Tseng, Farrukh Azfar Todd Huffman Thilo Pauly'

        result = generate_name_variations(many_names_as_one_author)

        assert result == [many_names_as_one_author]

        args, _ = mock_error.call_args
        assert args[0].startswith('Skipping name variations generation - too many names')


def test_generate_name_variations_capitalizes_first_letters():
    name = 'mele, salvatore'
    expected = {
        # Lastname only
        'Mele',
        # Lastnames first and then non lastnames
        'Mele S',
        'Mele, S',
        'Mele Salvatore',
        'Mele, Salvatore',
        # Non lastnames first and then lastnames
        'Salvatore Mele',
        'Salvatore, Mele',
        'S Mele',
        'S, Mele',
    }

    result = generate_name_variations(name)

    assert set(result) == expected


def test_generate_name_variations_works_with_two_consecutive_commas():
    name = 'Perelstein,, Maxim'
    expected = {
        # Lastname only
        'Perelstein',
        # Lastnames first and then non lastnames
        'Perelstein M',
        'Perelstein, M',
        'Perelstein Maxim',
        'Perelstein, Maxim',
        # Non lastnames first and then lastnames
        'Maxim Perelstein',
        'Maxim, Perelstein',
        'M Perelstein',
        'M, Perelstein',
    }

    result = generate_name_variations(name)

    assert set(result) == expected


def test_parsed_name_creates_lastname_with_only_on_name_part():
    name = u'ellis'
    parsed_name = ParsedName(name)

    assert not all([parsed_name.first, parsed_name.middle, parsed_name.suffix])
    assert parsed_name.last == name
