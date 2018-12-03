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

from inspire_utils.name import (
    normalize_name,
    format_name,
    generate_name_variations,
    ParsedName,
)


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
        'ellis',
        'ellis j',
        'ellis j r',
        'ellis j richard',
        'ellis john',
        'ellis john r',
        'ellis john richard',
        'ellis r',
        'ellis richard',
        'ellis, j',
        'ellis, j r',
        'ellis, j richard',
        'ellis, john',
        'ellis, john r',
        'ellis, john richard',
        'ellis, r',
        'ellis, richard',
        'j ellis',
        'j r ellis',
        'j richard ellis',
        'john ellis',
        'john r ellis',
        'john richard ellis',
        'r ellis',
        'richard ellis',
        'j, ellis',
        'j r, ellis',
        'j richard, ellis',
        'john, ellis',
        'john r, ellis',
        'john richard, ellis',
        'r, ellis',
        'richard, ellis',
    }

    result = generate_name_variations(name)

    assert set(result) == expected_name_variations


def test_generate_name_variations_with_more_than_two_non_lastnames_does_not_add_extra_spaces():
    name = 'Ellis, John Richard Philip'

    result = generate_name_variations(name)

    assert 'ellis, john  philip' not in set(result)


def test_generate_name_variations_with_two_lastnames():
    name = u'Caro Estevez, David'
    expected = {
        # Lastnames only
        u'caro',
        u'estevez',
        u'caro estevez',
        # Lastnames first and then non lastnames
        u'caro estevez d',
        u'caro estevez david',
        u'caro estevez, d',
        u'caro estevez, david',
        u'caro d',
        u'caro, d',
        u'caro david',
        u'caro, david',
        u'estevez d',
        u'estevez david',
        u'estevez, d',
        u'estevez, david',
        # Non lastnames first and then lastnames
        u'd caro',
        u'd, caro',
        u'd estevez',
        u'd, estevez',
        u'd caro estevez',
        u'd, caro estevez',
        u'david caro',
        u'david, caro',
        u'david estevez',
        u'david, estevez',
        u'david caro estevez',
        u'david, caro estevez',
    }

    result = generate_name_variations(name)

    assert set(result) == expected


def test_generate_name_variations_with_three_lastnames_dashed_ignores_the_dash():
    name = u'Caro-Estévez Martínez, David'
    expected = {
        # Lastnames only
        u'caro',
        u'estevez',
        u'martinez',
        u'caro estevez martinez',
        # Lastnames first and then non lastnames
        u'caro estevez martinez d',
        u'caro estevez martinez david',
        u'caro estevez martinez, d',
        u'caro estevez martinez, david',
        u'caro d',
        u'caro, d',
        u'caro david',
        u'caro, david',
        u'estevez d',
        u'estevez, d',
        u'estevez david',
        u'estevez, david',
        u'martinez d',
        u'martinez, d',
        u'martinez david',
        u'martinez, david',
        # Non lastnames first and then lastnames
        u'd caro',
        u'd, caro',
        u'd estevez',
        u'd, estevez',
        u'd martinez',
        u'd, martinez',
        u'd caro estevez martinez',
        u'd, caro estevez martinez',
        u'david caro',
        u'david, caro',
        u'david estevez',
        u'david, estevez',
        u'david martinez',
        u'david, martinez',
        u'david caro estevez martinez',
        u'david, caro estevez martinez'
    }

    result = generate_name_variations(name)

    assert set(result) == expected


def test_generate_name_variations_with_firstname_as_initial():
    name = 'Smith, J'
    expected = {
        # Lastname only
        u'smith',
        # Lastnames first and then non lastnames
        u'smith j',
        u'smith, j',
        # Non lastnames first and then lastnames
        u'j smith',
        u'j, smith',
    }

    result = generate_name_variations(name)

    assert set(result) == expected


def test_generate_name_variations_with_only_one_name():
    name = 'Jimmy'
    expected = {
        u'jimmy',
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
        u'mele',
        # Lastnames first and then non lastnames
        u'mele s',
        u'mele, s',
        u'mele salvatore',
        u'mele, salvatore',
        # Non lastnames first and then lastnames
        u'salvatore mele',
        u'salvatore, mele',
        u's mele',
        u's, mele',
    }

    result = generate_name_variations(name)

    assert set(result) == expected


def test_generate_name_variations_works_with_two_consecutive_commas():
    name = 'Perelstein,, Maxim'
    expected = {
        # Lastname only
        u'perelstein',
        # Lastnames first and then non lastnames
        u'perelstein m',
        u'perelstein, m',
        u'perelstein maxim',
        u'perelstein, maxim',
        # Non lastnames first and then lastnames
        u'maxim perelstein',
        u'maxim, perelstein',
        u'm perelstein',
        u'm, perelstein',
    }

    result = generate_name_variations(name)

    assert set(result) == expected


def test_generate_name_variations_with_short_lastname_and_initial():
    # Should not output something like `o y` or any similar variation.
    name = 'Oz, Y'
    expected = {
        # Lastname only
        u'oz',
        # Lastnames first and then non lastnames
        u'oz y',
        u'oz, y',
        # Non lastnames first and then lastnames
        u'y oz',
        u'y, oz',
    }

    result = generate_name_variations(name)

    assert len(result) == len(expected)

    assert set(result) == expected


def test_parsed_name_from_parts():
    parsed_name = ParsedName.from_parts("John", "Smith", "Peter", "Jr", "Sir")

    expected = "Smith, John Peter, Jr."
    result = parsed_name.dumps()

    assert result == expected


def test_normalize_name_handles_multiple_middle_names():
    expected = 'Almeida, C.A.S.'

    assert expected == normalize_name('Almeida, C. A. S.')
    assert expected == normalize_name('Almeida, C. A.S.')
    assert expected == normalize_name('Almeida, C.A. S.')
    assert expected == normalize_name('Almeida, C.A.S.')


def test_normalize_name_handles_multiple_middle_names_with_and_without_initials():
    expected = 'Smith, J.A. Peter J.'

    assert expected == normalize_name('Smith, J. A. Peter J.')
    assert expected == normalize_name('Smith, J.A. Peter J.')


def test_format_author_name():
    expected = 'Stanley Martin Lieber'

    assert expected == format_name('Lieber, Stanley Martin')

    expected = 'Robert Downey Jr.'

    assert expected == format_name('Downey, Robert Jr.')


def test_format_author_name_with_initials():
    expected = 'S. M. Lieber'

    assert expected == format_name('Lieber, Stanley Martin', initials_only=True)


def test_parsed_name_initials():
    parsed_name = ParsedName("Holland, Tom Stanley")
    expected = "T. S."

    assert expected == parsed_name.first_initials

    expected = [
        "T.",
        "S."
    ]

    assert expected == parsed_name.first_initials_list


def test_unicode_characters_in_format_name():
    assert format_name('Cañas, Ramón') == u'Ramón Cañas'
    assert format_name('Süß, Jörg') == u'Jörg Süß'
    assert format_name('Møller, Kyösti') == u'Kyösti Møller'
    assert format_name('Varejão, François') == u'François Varejão'
