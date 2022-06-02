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
from inspire_utils.name import (ParsedName, format_name,
                                generate_name_variations, normalize_name)
from inspire_utils.query import ordered
from mock import patch


def test_normalize_name_full():
    expected = "Smith, John Peter"

    assert expected == normalize_name("Smith, John Peter")


def test_normalize_name_handles_names_with_first_initial():
    expected = "Smith, J. Peter"

    assert expected == normalize_name("Smith, J Peter")
    assert expected == normalize_name("Smith, J. Peter")
    assert expected == normalize_name("Smith, J. Peter ")


def test_normalize_name_handles_names_with_middle_initial():
    expected = "Smith, John P."

    assert expected == normalize_name("Smith, John P.")
    assert expected == normalize_name("Smith, John P. ")
    assert expected == normalize_name("Smith, John P ")


def test_normalize_name_handles_names_with_dots_initials():
    expected = "Smith, J.P."

    assert expected == normalize_name("Smith, J. P.")
    assert expected == normalize_name("Smith, J.P.")
    assert expected == normalize_name("Smith, J.P. ")
    assert expected == normalize_name("Smith, J. P. ")


def test_normalize_name_handles_names_with_spaces():
    expected = "Smith, J.P."

    assert expected == normalize_name("Smith, J P ")
    assert expected == normalize_name("Smith, J P")


def test_normalize_name_handles_names_with_several_last_names():
    expected = "Smith Davis, J.P."

    assert expected == normalize_name("Smith Davis, J.P.")


def test_normalize_name_handles_jimmy():  # http://jimmy.pink
    expected = "Jimmy"

    assert expected == normalize_name("Jimmy")


def test_regression_name_with_comma():
    expected = "Jessica"
    assert expected == normalize_name("Jessica, ")


def test_normalize_name_handles_unicode():
    expected = u"蕾拉"

    assert expected == normalize_name(u"蕾拉")


def test_normalize_name_converts_unicode_apostrophe_to_normal_apostrophe():
    expected = u"M'Gregor, Jimmy"

    assert expected == normalize_name(u"M’Gregor, Jimmy")


@pytest.mark.parametrize(
    "input_author_name,expected",
    [
        ("Smith, John Jr", "Smith, John, Jr."),
        ("Smith, John Jr.", "Smith, John, Jr."),
        ("Smith, John III", "Smith, John, III"),
        ("Smith, John iii", "Smith, John, III"),
        ("Smith, John VIII", "Smith, John, VIII"),
        ("Smith, John viii", "Smith, John, VIII"),
        ("Smith, John IV", "Smith, John, IV"),
        ("Smith, John iv", "Smith, John, IV"),
    ],
)
def test_normalize_name_handles_suffixes(input_author_name, expected):
    assert normalize_name(input_author_name) == expected


@pytest.mark.parametrize(
    "input_author_name,expected",
    [("Sir John Smith", "Smith, John"),
     ("Bao, Hon", "Bao, Hon"), ("ed witten", "Witten, Ed")],
)
def test_normalize_name_handles_titles(input_author_name, expected):
    assert normalize_name(input_author_name) == expected


def test_generate_name_variations_with_two_non_lastnames():
    name = "Ellis, John Richard"
    expected_name_variations = {
        "ellis",
        "ellis j",
        "ellis j r",
        "ellis j richard",
        "ellis john",
        "ellis john r",
        "ellis john richard",
        "ellis r",
        "ellis richard",
        "ellis, j",
        "ellis, j r",
        "ellis, j richard",
        "ellis, john",
        "ellis, john r",
        "ellis, john richard",
        "ellis, r",
        "ellis, richard",
        "j ellis",
        "j r ellis",
        "j richard ellis",
        "john ellis",
        "john r ellis",
        "john richard ellis",
        "r ellis",
        "richard ellis",
        "j, ellis",
        "j r, ellis",
        "j richard, ellis",
        "john, ellis",
        "john r, ellis",
        "john richard, ellis",
        "r, ellis",
        "richard, ellis",
    }

    result = generate_name_variations(name)

    assert set(result) == expected_name_variations


def test_generate_name_variations_with_more_than_two_non_lastnames_does_not_add_extra_spaces():
    name = "Ellis, John Richard Philip"

    result = generate_name_variations(name)

    assert "ellis, john  philip" not in set(result)


def test_generate_name_variations_with_two_lastnames():
    name = u"Caro Estevez, David"
    expected = {
        # Lastnames only
        u"caro",
        u"estevez",
        u"caro estevez",
        # Lastnames first and then non lastnames
        u"caro estevez d",
        u"caro estevez david",
        u"caro estevez, d",
        u"caro estevez, david",
        u"caro d",
        u"caro, d",
        u"caro david",
        u"caro, david",
        u"estevez d",
        u"estevez david",
        u"estevez, d",
        u"estevez, david",
        # Non lastnames first and then lastnames
        u"d caro",
        u"d, caro",
        u"d estevez",
        u"d, estevez",
        u"d caro estevez",
        u"d, caro estevez",
        u"david caro",
        u"david, caro",
        u"david estevez",
        u"david, estevez",
        u"david caro estevez",
        u"david, caro estevez",
    }

    result = generate_name_variations(name)

    assert set(result) == expected


def test_generate_name_variations_with_three_lastnames_dashed_ignores_the_dash():
    name = u"Caro-Estévez Martínez, David"
    expected = {
        # Lastnames only
        u"caro",
        u"estevez",
        u"martinez",
        u"caro estevez martinez",
        # Lastnames first and then non lastnames
        u"caro estevez martinez d",
        u"caro estevez martinez david",
        u"caro estevez martinez, d",
        u"caro estevez martinez, david",
        u"caro d",
        u"caro, d",
        u"caro david",
        u"caro, david",
        u"estevez d",
        u"estevez, d",
        u"estevez david",
        u"estevez, david",
        u"martinez d",
        u"martinez, d",
        u"martinez david",
        u"martinez, david",
        # Non lastnames first and then lastnames
        u"d caro",
        u"d, caro",
        u"d estevez",
        u"d, estevez",
        u"d martinez",
        u"d, martinez",
        u"d caro estevez martinez",
        u"d, caro estevez martinez",
        u"david caro",
        u"david, caro",
        u"david estevez",
        u"david, estevez",
        u"david martinez",
        u"david, martinez",
        u"david caro estevez martinez",
        u"david, caro estevez martinez",
    }

    result = generate_name_variations(name)

    assert set(result) == expected


def test_generate_name_variations_with_firstname_as_initial():
    name = "Smith, J"
    expected = {
        # Lastname only
        u"smith",
        # Lastnames first and then non lastnames
        u"smith j",
        u"smith, j",
        # Non lastnames first and then lastnames
        u"j smith",
        u"j, smith",
    }

    result = generate_name_variations(name)

    assert set(result) == expected


def test_generate_name_variations_with_only_one_name():
    name = "Jimmy"
    expected = {
        u"jimmy",
    }

    result = generate_name_variations(name)

    assert set(result) == expected


def test_generate_name_variations_with_many_names_defers_generating_variations():
    import logging

    logger = logging.getLogger("inspire_utils.name")
    with patch.object(logger, "warning") as mock_warning:
        many_names_as_one_author = "Tseng, Farrukh Azfar Todd Huffman Thilo Pauly"

        result = generate_name_variations(many_names_as_one_author)

        assert result == [many_names_as_one_author]

        args, _ = mock_warning.call_args
        assert args[0].startswith(
            "Skipping name variations generation - too many names"
        )


def test_generate_name_variations_capitalizes_first_letters():
    name = "mele, salvatore"
    expected = {
        # Lastname only
        u"mele",
        # Lastnames first and then non lastnames
        u"mele s",
        u"mele, s",
        u"mele salvatore",
        u"mele, salvatore",
        # Non lastnames first and then lastnames
        u"salvatore mele",
        u"salvatore, mele",
        u"s mele",
        u"s, mele",
    }

    result = generate_name_variations(name)

    assert set(result) == expected


def test_generate_name_variations_works_with_two_consecutive_commas():
    name = "Perelstein,, Maxim"
    expected = {
        # Lastname only
        u"perelstein",
        # Lastnames first and then non lastnames
        u"perelstein m",
        u"perelstein, m",
        u"perelstein maxim",
        u"perelstein, maxim",
        # Non lastnames first and then lastnames
        u"maxim perelstein",
        u"maxim, perelstein",
        u"m perelstein",
        u"m, perelstein",
    }

    result = generate_name_variations(name)

    assert set(result) == expected


def test_generate_name_variations_with_short_lastname_and_initial():
    # Should not output something like `o y` or any similar variation.
    name = "Oz, Y"
    expected = {
        # Lastname only
        u"oz",
        # Lastnames first and then non lastnames
        u"oz y",
        u"oz, y",
        # Non lastnames first and then lastnames
        u"y oz",
        u"y, oz",
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
    expected = "Almeida, C.A.S."

    assert expected == normalize_name("Almeida, C. A. S.")
    assert expected == normalize_name("Almeida, C. A.S.")
    assert expected == normalize_name("Almeida, C.A. S.")
    assert expected == normalize_name("Almeida, C.A.S.")


def test_normalize_name_handles_multiple_middle_names_with_and_without_initials():
    expected = "Smith, J.A. Peter J."

    assert expected == normalize_name("Smith, J. A. Peter J.")
    assert expected == normalize_name("Smith, J.A. Peter J.")


def test_format_author_name():
    expected = "Stanley Martin Lieber"

    assert expected == format_name("Lieber, Stanley Martin")

    expected = "Robert Downey, Jr."

    assert expected == format_name("Downey, Robert Jr.")


def test_format_author_name_with_initials():
    expected = "S. M. Lieber"

    assert expected == format_name(
        "Lieber, Stanley Martin", initials_only=True)


def test_format_author_name_with_initials_with_all_caps_name():
    expected = "T. S. Holland"

    assert expected == format_name("HOLLAND, TOM STANLEY", initials_only=True)


def test_parsed_name_initials():
    parsed_name = ParsedName("Holland, Tom Stanley")
    expected = "T. S."

    assert expected == parsed_name.first_initials

    expected = ["T.", "S."]

    assert expected == parsed_name.first_initials_list


@pytest.mark.parametrize(
    "input_author_name,expected",
    [("Lieber, Ed", "E. Lieber"),
     ('Lieber, Ed Viktor', "E. V. Lieber"),
     ('Lieber, Ed Jr.', "E. Lieber, Jr."),
     ('Lieber, Ed Victor Jr.', "E. V. Lieber, Jr."),
     ],
)
def test_format_author_name_with_initials_when_first_name_is_similar_to_title(input_author_name, expected):

    assert expected == format_name(
        input_author_name, initials_only=True)


def test_parsed_wrong_names_and_not_fail():
    names = [
        (u"Proffesor.M.", u"Proffesor.M."),
        (u"ˇ Sirˇ", u"Sirˇ, ˇ."),
    ]

    for name, expected in names:
        assert ParsedName(name).dumps() == expected


def test_unicode_characters_in_format_name():
    assert format_name("Cañas, Ramón") == u"Ramón Cañas"
    assert format_name("Süß, Jörg") == u"Jörg Süß"
    assert format_name("Møller, Kyösti") == u"Kyösti Møller"
    assert format_name("Varejão, François") == u"François Varejão"


def test_first_names_are_never_printed_with_initials_only_if_no_last_name():
    expected = u"Jimmy"

    assert expected == format_name("Jimmy", initials_only=True)


def test_first_name_with_dash_is_initialized_correctly():
    assert u"Z. Y. Yin" == format_name("Zhao-Yu Yin", initials_only=True)


def test_first_name_with_dash_is_printed_with_dash_and_initialized_correctly():
    expected = "Huang-Wei Pan"
    parsed_name = ParsedName.loads(expected)
    result = " ".join(parsed_name.first_list + parsed_name.last_list)
    assert expected == result


def test_first_name_initials_without_whitespace_is_initialized_correctly():
    assert u"M. A. M. G. Garcia" == format_name(
        "Miguel A-M.G. Garcia", initials_only=True
    )


def test_last_name_recognized_correctly_regression_test():
    assert u"De Sousa Vieira" == ParsedName.loads("De Sousa Vieira, M.C.").last


def test_generate_es_query_lastname_firstname_with_commas_and_initials():
    name = "ellis, john k."

    expected_query = {
        "nested": {
            "path": "authors",
            "query": {
                "bool": {
                    "must": [
                        {
                            "match": {
                                "authors.last_name": {
                                    "operator": "AND",
                                    "query": "Ellis",
                                }
                            }
                        },
                        {
                            "bool": {
                                "must": [
                                    {
                                        "bool": {
                                            "should": [
                                                {
                                                    "match_phrase_prefix": {
                                                        "authors.first_name": {
                                                            "analyzer": "names_analyzer",
                                                            "query": "John",
                                                        }
                                                    }
                                                },
                                                {
                                                    "match": {
                                                        "authors.first_name": {
                                                            "analyzer": "names_initials_analyzer",
                                                            "operator": "AND",
                                                            "query": "John",
                                                        }
                                                    }
                                                },
                                            ]
                                        }
                                    },
                                    {
                                        "match": {
                                            "authors.first_name.initials": {
                                                "analyzer": "names_initials_analyzer",
                                                "operator": "AND",
                                                "query": "K",
                                            }
                                        }
                                    },
                                ]
                            }
                        },
                    ]
                }
            },
        }
    }
    parsed_name = ParsedName(name)
    generated_es_query = parsed_name.generate_es_query()
    assert ordered(generated_es_query) == ordered(expected_query)


def test_generate_es_query_first_author_lastname_firstname_with_commas_and_initials():
    name = "ellis, john k."

    expected_query = {
        "nested": {
            "path": "first_author",
            "query": {
                "bool": {
                    "must": [
                        {
                            "match": {
                                "first_author.last_name": {
                                    "operator": "AND",
                                    "query": "Ellis",
                                }
                            }
                        },
                        {
                            "bool": {
                                "must": [
                                    {
                                        "bool": {
                                            "should": [
                                                {
                                                    "match_phrase_prefix": {
                                                        "first_author.first_name": {
                                                            "analyzer": "names_analyzer",
                                                            "query": "John",
                                                        }
                                                    }
                                                },
                                                {
                                                    "match": {
                                                        "first_author.first_name": {
                                                            "analyzer": "names_initials_analyzer",
                                                            "operator": "AND",
                                                            "query": "John",
                                                        }
                                                    }
                                                },
                                            ]
                                        }
                                    },
                                    {
                                        "match": {
                                            "first_author.first_name.initials": {
                                                "analyzer": "names_initials_analyzer",
                                                "operator": "AND",
                                                "query": "K",
                                            }
                                        }
                                    },
                                ]
                            }
                        },
                    ]
                }
            },
        }
    }
    parsed_name = ParsedName(name)
    generated_es_query = parsed_name.generate_es_query("first_author")
    assert ordered(generated_es_query) == ordered(expected_query)


def test_generate_es_query_query_author_with_composite_last_name():
    name = "de Rham"
    expected_query = {
        "nested": {
            "path": "authors",
            "query": {
                "bool": {
                    "must": [
                        {
                            "match": {
                                "authors.last_name": {
                                    "query": "Rham",
                                    "operator": "AND",
                                }
                            }
                        },
                        {
                            "bool": {
                                "should": [
                                    {
                                        "match_phrase_prefix": {
                                            "authors.first_name": {
                                                "query": "de",
                                                "analyzer": "names_analyzer",
                                            }
                                        }
                                    },
                                    {
                                        "match": {
                                            "authors.first_name": {
                                                "query": "de",
                                                "operator": "AND",
                                                "analyzer": "names_initials_analyzer",
                                            }
                                        }
                                    },
                                    {
                                        "match": {
                                            "authors.full_name": {
                                                "query": "de Rham",
                                                "operator": "AND",
                                            }
                                        }
                                    },
                                ]
                            }
                        },
                    ]
                }
            },
        }
    }

    parsed_name = ParsedName(name)
    generated_es_query = parsed_name.generate_es_query()
    assert ordered(generated_es_query) == ordered(expected_query)


def test_generate_es_query_split_fa_initial_and_firstname_without_a_space():
    name = "D.John Smith"
    expected_query = {
        "nested": {
            "path": "first_author",
            "query": {
                "bool": {
                    "must": [
                        {
                            "match": {
                                "first_author.last_name": {
                                    "operator": "AND",
                                    "query": "Smith",
                                }
                            }
                        },
                        {
                            "bool": {
                                "must": [
                                    {
                                        "match": {
                                            "first_author.first_name.initials": {
                                                "analyzer": "names_initials_analyzer",
                                                "operator": "AND",
                                                "query": "D",
                                            }
                                        }
                                    },
                                    {
                                        "bool": {
                                            "should": [
                                                {
                                                    "match_phrase_prefix": {
                                                        "first_author.first_name": {
                                                            "analyzer": "names_analyzer",
                                                            "query": "John",
                                                        }
                                                    }
                                                },
                                                {
                                                    "match": {
                                                        "first_author.first_name": {
                                                            "analyzer": "names_initials_analyzer",
                                                            "operator": "AND",
                                                            "query": "John",
                                                        }
                                                    }
                                                },
                                            ]
                                        }
                                    },
                                ]
                            }
                        },
                    ]
                }
            },
        }
    }

    parsed_name = ParsedName(name)
    generated_es_query = parsed_name.generate_es_query("first_author")
    assert ordered(generated_es_query) == ordered(expected_query)


def test_generate_es_query_hack_to_split_two_initials_without_a_space():
    name = "D.K. Smith"
    expected_query = {
        "nested": {
            "path": "authors",
            "query": {
                "bool": {
                    "must": [
                        {
                            "match": {
                                "authors.last_name": {
                                    "operator": "AND",
                                    "query": "Smith",
                                }
                            }
                        },
                        {
                            "bool": {
                                "must": [
                                    {
                                        "match": {
                                            "authors.first_name.initials": {
                                                "analyzer": "names_initials_analyzer",
                                                "operator": "AND",
                                                "query": "D",
                                            }
                                        }
                                    },
                                    {
                                        "match": {
                                            "authors.first_name.initials": {
                                                "analyzer": "names_initials_analyzer",
                                                "operator": "AND",
                                                "query": "K",
                                            }
                                        }
                                    },
                                ]
                            }
                        },
                    ]
                }
            },
        }
    }

    parsed_name = ParsedName(name)
    generated_es_query = parsed_name.generate_es_query("authors")
    assert ordered(generated_es_query) == ordered(expected_query)


def test_generate_es_query_split_fa_two_initials_without_a_space():
    name = "D.K. Smith"
    expected_query = {
        "nested": {
            "path": "first_author",
            "query": {
                "bool": {
                    "must": [
                        {
                            "match": {
                                "first_author.last_name": {
                                    "operator": "AND",
                                    "query": "Smith",
                                }
                            }
                        },
                        {
                            "bool": {
                                "must": [
                                    {
                                        "match": {
                                            "first_author.first_name.initials": {
                                                "analyzer": "names_initials_analyzer",
                                                "operator": "AND",
                                                "query": "D",
                                            }
                                        }
                                    },
                                    {
                                        "match": {
                                            "first_author.first_name.initials": {
                                                "analyzer": "names_initials_analyzer",
                                                "operator": "AND",
                                                "query": "K",
                                            }
                                        }
                                    },
                                ]
                            }
                        },
                    ]
                }
            },
        }
    }

    parsed_name = ParsedName(name)
    generated_es_query = parsed_name.generate_es_query("first_author")
    assert ordered(generated_es_query) == ordered(expected_query)


def test_generate_es_query_lastname_initial():
    name = "ellis, j"
    expected_query = {
        "nested": {
            "path": "authors",
            "query": {
                "bool": {
                    "must": [
                        {
                            "match": {
                                "authors.last_name": {
                                    "operator": "AND",
                                    "query": "Ellis",
                                }
                            }
                        },
                        {
                            "match": {
                                "authors.first_name.initials": {
                                    "analyzer": "names_initials_analyzer",
                                    "operator": "AND",
                                    "query": "J",
                                }
                            }
                        },
                    ]
                }
            },
        }
    }

    parsed_name = ParsedName(name)
    generated_es_query = parsed_name.generate_es_query()
    assert ordered(generated_es_query) == ordered(expected_query)


def test_generate_es_query_first_author_lastname_initial():
    name = "ellis, j"
    expected_query = {
        "nested": {
            "path": "first_author",
            "query": {
                "bool": {
                    "must": [
                        {
                            "match": {
                                "first_author.last_name": {
                                    "operator": "AND",
                                    "query": "Ellis",
                                }
                            }
                        },
                        {
                            "match": {
                                "first_author.first_name.initials": {
                                    "analyzer": "names_initials_analyzer",
                                    "operator": "AND",
                                    "query": "J",
                                }
                            }
                        },
                    ]
                }
            },
        }
    }

    parsed_name = ParsedName(name)
    generated_es_query = parsed_name.generate_es_query("first_author")
    assert ordered(generated_es_query) == ordered(expected_query)


def test_generate_es_query_lastname_firstname():
    name = "ellis, john"

    expected_query = {
        "nested": {
            "path": "authors",
            "query": {
                "bool": {
                    "must": [
                        {
                            "match": {
                                "authors.last_name": {
                                    "operator": "AND",
                                    "query": "Ellis",
                                }
                            }
                        },
                        {
                            "bool": {
                                "should": [
                                    {
                                        "match_phrase_prefix": {
                                            "authors.first_name": {
                                                "analyzer": "names_analyzer",
                                                "query": "John",
                                            }
                                        }
                                    },
                                    {
                                        "match": {
                                            "authors.first_name": {
                                                "analyzer": "names_initials_analyzer",
                                                "operator": "AND",
                                                "query": "John",
                                            }
                                        }
                                    },
                                ]
                            }
                        },
                    ]
                }
            },
        }
    }
    parsed_name = ParsedName(name)
    generated_es_query = parsed_name.generate_es_query()
    assert ordered(generated_es_query) == ordered(expected_query)


def test_generate_es_query_first_author_lastname_firstname():
    name = "ellis, john"

    expected_query = {
        "nested": {
            "path": "first_author",
            "query": {
                "bool": {
                    "must": [
                        {
                            "match": {
                                "first_author.last_name": {
                                    "operator": "AND",
                                    "query": "Ellis",
                                }
                            }
                        },
                        {
                            "bool": {
                                "should": [
                                    {
                                        "match_phrase_prefix": {
                                            "first_author.first_name": {
                                                "analyzer": "names_analyzer",
                                                "query": "John",
                                            }
                                        }
                                    },
                                    {
                                        "match": {
                                            "first_author.first_name": {
                                                "analyzer": "names_initials_analyzer",
                                                "operator": "AND",
                                                "query": "John",
                                            }
                                        }
                                    },
                                ]
                            }
                        },
                    ]
                }
            },
        }
    }
    parsed_name = ParsedName(name)
    generated_es_query = parsed_name.generate_es_query("first_author")
    assert ordered(generated_es_query) == ordered(expected_query)


def test_generate_es_query_lastname_firstname_without_comma():
    name = "john ellis"

    expected_query = {
        "nested": {
            "path": "authors",
            "query": {
                "bool": {
                    "must": [
                        {
                            "match": {
                                "authors.last_name": {
                                    "query": "Ellis",
                                    "operator": "AND",
                                }
                            }
                        },
                        {
                            "bool": {
                                "should": [
                                    {
                                        "match_phrase_prefix": {
                                            "authors.first_name": {
                                                "query": "John",
                                                "analyzer": "names_analyzer",
                                            }
                                        }
                                    },
                                    {
                                        "match": {
                                            "authors.first_name": {
                                                "query": "John",
                                                "operator": "AND",
                                                "analyzer": "names_initials_analyzer",
                                            }
                                        }
                                    },
                                    {
                                        "match": {
                                            "authors.full_name": {
                                                "query": "John Ellis",
                                                "operator": "AND",
                                            }
                                        }
                                    },
                                ]
                            }
                        },
                    ]
                }
            },
        }
    }
    parsed_name = ParsedName(name)
    generated_es_query = parsed_name.generate_es_query()
    assert ordered(generated_es_query) == ordered(expected_query)


def test_generate_es_query_first_author_lastname_firstname_without_comma():
    name = "john ellis"

    expected_query = {
        "nested": {
            "path": "first_author",
            "query": {
                "bool": {
                    "must": [
                        {
                            "match": {
                                "first_author.last_name": {
                                    "query": "Ellis",
                                    "operator": "AND",
                                }
                            }
                        },
                        {
                            "bool": {
                                "should": [
                                    {
                                        "match_phrase_prefix": {
                                            "first_author.first_name": {
                                                "query": "John",
                                                "analyzer": "names_analyzer",
                                            }
                                        }
                                    },
                                    {
                                        "match": {
                                            "first_author.first_name": {
                                                "query": "John",
                                                "operator": "AND",
                                                "analyzer": "names_initials_analyzer",
                                            }
                                        }
                                    },
                                    {
                                        "match": {
                                            "first_author.full_name": {
                                                "query": "John Ellis",
                                                "operator": "AND",
                                            }
                                        }
                                    },
                                ]
                            }
                        },
                    ]
                }
            },
        }
    }

    parsed_name = ParsedName(name)
    generated_es_query = parsed_name.generate_es_query("first_author")
    assert ordered(generated_es_query) == ordered(expected_query)


def test_generate_es_query_lastname_firstname_without_commas_and_initials():
    name = "john k. ellis"

    expected_query = {
        "nested": {
            "path": "authors",
            "query": {
                "bool": {
                    "must": [
                        {
                            "match": {
                                "authors.last_name": {
                                    "operator": "AND",
                                    "query": "Ellis",
                                }
                            }
                        },
                        {
                            "bool": {
                                "must": [
                                    {
                                        "bool": {
                                            "should": [
                                                {
                                                    "match_phrase_prefix": {
                                                        "authors.first_name": {
                                                            "analyzer": "names_analyzer",
                                                            "query": "John",
                                                        }
                                                    }
                                                },
                                                {
                                                    "match": {
                                                        "authors.first_name": {
                                                            "analyzer": "names_initials_analyzer",
                                                            "operator": "AND",
                                                            "query": "John",
                                                        }
                                                    }
                                                },
                                            ]
                                        }
                                    },
                                    {
                                        "match": {
                                            "authors.first_name.initials": {
                                                "analyzer": "names_initials_analyzer",
                                                "operator": "AND",
                                                "query": "K",
                                            }
                                        }
                                    },
                                ]
                            }
                        },
                    ]
                }
            },
        }
    }

    parsed_name = ParsedName(name)
    generated_es_query = parsed_name.generate_es_query()
    assert ordered(generated_es_query) == ordered(expected_query)


def test_generate_es_query_first_author_lastname_firstname_without_commas_and_initials():
    name = "john k. ellis"

    expected_query = {
        "nested": {
            "path": "first_author",
            "query": {
                "bool": {
                    "must": [
                        {
                            "match": {
                                "first_author.last_name": {
                                    "operator": "AND",
                                    "query": "Ellis",
                                }
                            }
                        },
                        {
                            "bool": {
                                "must": [
                                    {
                                        "bool": {
                                            "should": [
                                                {
                                                    "match_phrase_prefix": {
                                                        "first_author.first_name": {
                                                            "analyzer": "names_analyzer",
                                                            "query": "John",
                                                        }
                                                    }
                                                },
                                                {
                                                    "match": {
                                                        "first_author.first_name": {
                                                            "analyzer": "names_initials_analyzer",
                                                            "operator": "AND",
                                                            "query": "John",
                                                        }
                                                    }
                                                },
                                            ]
                                        }
                                    },
                                    {
                                        "match": {
                                            "first_author.first_name.initials": {
                                                "analyzer": "names_initials_analyzer",
                                                "operator": "AND",
                                                "query": "K",
                                            }
                                        }
                                    },
                                ]
                            }
                        },
                    ]
                }
            },
        }
    }

    parsed_name = ParsedName(name)
    generated_es_query = parsed_name.generate_es_query("first_author")
    assert ordered(generated_es_query) == ordered(expected_query)


def test_generate_es_query_works_for_unambigous_names():
    name = "J. David Ellis"

    expected_query = {
        "nested": {
            "path": "authors",
            "query": {
                "bool": {
                    "must": [
                        {
                            "match": {
                                "authors.last_name": {
                                    "query": "Ellis",
                                    "operator": "AND",
                                }
                            }
                        },
                        {
                            "bool": {
                                "must": [
                                    {
                                        "match": {
                                            "authors.first_name.initials": {
                                                "query": "J",
                                                "operator": "AND",
                                                "analyzer": "names_initials_analyzer",
                                            }
                                        }
                                    },
                                    {
                                        "bool": {
                                            "should": [
                                                {
                                                    "match_phrase_prefix": {
                                                        "authors.first_name": {
                                                            "query": "David",
                                                            "analyzer": "names_analyzer",
                                                        }
                                                    }
                                                },
                                                {
                                                    "match": {
                                                        "authors.first_name": {
                                                            "query": "David",
                                                            "operator": "AND",
                                                            "analyzer": "names_initials_analyzer",
                                                        }
                                                    }
                                                },
                                                {
                                                    "match": {
                                                        "authors.full_name": {
                                                            "query": "J. David Ellis",
                                                            "operator": "AND",
                                                        }
                                                    }
                                                },
                                            ]
                                        }
                                    },
                                ]
                            }
                        },
                    ]
                }
            },
        }
    }

    parsed_name = ParsedName(name)
    generated_es_query = parsed_name.generate_es_query()
    assert ordered(generated_es_query) == ordered(expected_query)


def test_generate_es_query_title_name():
    name = "ed witten"
    expected_query = {
        'nested': {
            'path': 'authors', 'query': {
                'bool': {
                    'must': [
                        {
                            'match': {
                                u'authors.last_name': {
                                    'operator': 'AND',
                                    'query': u'Witten'
                                }
                            }
                        }, {
                            'bool': {
                                'should': [
                                    {
                                        'match_phrase_prefix': {
                                            u'authors.first_name': {
                                                'query': u'Ed',
                                                'analyzer': 'names_analyzer'
                                            }
                                        }
                                    }, {
                                        'match': {
                                            u'authors.first_name': {
                                                'operator': 'AND',
                                                'query': u'Ed',
                                                'analyzer': 'names_initials_analyzer'
                                            }
                                        }
                                    }, {
                                        'match': {
                                            u'authors.full_name': {
                                                'operator': 'AND',
                                                'query': 'Ed Witten'
                                            }
                                        }
                                    }
                                ]
                            }
                        }
                    ]
                }
            }
        }
    }
    parsed_name = ParsedName(name)
    generated_es_query = parsed_name.generate_es_query()
    assert ordered(generated_es_query) == ordered(expected_query)


def test_parsed_name_doesnt_produce_error_when_first_and_last_name_empty():
    empty_parsed_name = ParsedName("")
    parsed_name_with_title_only = ParsedName("Editor")
    assert empty_parsed_name is not None
    assert parsed_name_with_title_only is not None
