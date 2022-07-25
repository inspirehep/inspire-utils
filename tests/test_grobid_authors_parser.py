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
import os
import pkg_resources
from inspire_utils.grobid_authors_parser import GrobidAuthors


def test_process_grobid_authors():

    grobid_response = pkg_resources.resource_string(
        __name__,
        os.path.join(
            'fixtures',
            'grobid_full_doc.xml'
        )
    )
    expected_authors = [
        {
            "parsed_affiliations": [
                {
                    "department": [u"S. N"],
                    "name": u"Bose National Centre for Basic Sciences, JD Block",
                    "address": {
                        "country": u"India",
                        "cities": [u"Kolkata-700106"],
                        "postal_address": u"Sector III, Salt Lake, Kolkata-700106, India",
                    },
                }
            ],
            "author": {
                "raw_affiliations": [
                    {
                        "value": u"S. N. Bose National Centre for Basic Sciences, JD Block, Sector III, Salt Lake, Kolkata-700106, India."
                    }
                ],
                "emails": [u"parthanandi@bose.res.in"],
                "full_name": u"Nandi, Partha",
            },
        },
        {
            "parsed_affiliations": [
                {
                    "department": [
                        u"Indian Institute of Engineering Science and Technology"
                    ],
                    "address": {
                        "country": u"India",
                        "cities": [u"Shibpur, Howrah"],
                        "postal_address": u"Shibpur, Howrah, India",
                    },
                }
            ],
            "author": {
                "raw_affiliations": [
                    {
                        "value": u"Indian Institute of Engineering Science and Technology, Shibpur, Howrah, West Bengal-711103, India."
                    }
                ],
                "emails": [u"sankarshan.sahu2000@gmail.com"],
                "full_name": u"Sahu, Sankarshan",
            },
        },
        {
            "parsed_affiliations": [
                {
                    "department": [u"S. N"],
                    "name": u"Bose National Centre for Basic Sciences, JD Block",
                    "address": {
                        "country": u"India",
                        "cities": [u"Kolkata-700106"],
                        "postal_address": u"Sector III, Salt Lake, Kolkata-700106, India",
                    },
                }
            ],
            "author": {
                "raw_affiliations": [
                    {
                        "value": u"S. N. Bose National Centre for Basic Sciences, JD Block, Sector III, Salt Lake, Kolkata-700106, India."
                    }
                ],
                "emails": [u"sayankpal@bose.res.in"],
                "full_name": u"Pal, Sayan Kumar",
            },
        },
    ]

    expected_authors_count = len(expected_authors)

    authors = GrobidAuthors(grobid_response)
    assert len(authors) == expected_authors_count
    assert authors.parse_all() == expected_authors


def test_grobid_incomplete_authors():

    grobid_response = pkg_resources.resource_string(
        __name__,
        os.path.join(
            'fixtures',
            'grobid_incomplete_doc.xml'
        )
    )

    expected_authors = [
        {"parsed_affiliations": None, "author": {"full_name": u"Nandi"}},
        {
            "parsed_affiliations": [
                {
                    "address": {
                        "cities": [u"Shibpur, Howrah"],
                        "postal_address": u"Shibpur, Howrah",
                    }
                }
            ],
            "author": {
                "raw_affiliations": [
                    {
                        "value": u"Indian Institute of Engineering Science and Technology, Shibpur, Howrah, West Bengal-711103, India."
                    }
                ],
                "full_name": u"Sahu, Sankarshan",
            },
        },
        {
            "parsed_affiliations": [
                {
                    "department": [u"S. N"],
                    "name": u"Bose National Centre for Basic Sciences, JD Block",
                }
            ],
            "author": {
                "raw_affiliations": [
                    {
                        "value": u"S. N. Bose National Centre for Basic Sciences, JD Block, Sector III, Salt Lake, Kolkata-700106, India."
                    }
                ],
                "emails": [u"sayankpal@bose.res.in"],
                "full_name": u"Pal, Sayan Kumar",
            },
        },
    ]

    expected_authors_count = len(expected_authors)
    authors = GrobidAuthors(grobid_response)
    assert len(authors) == expected_authors_count
    assert authors.parse_all() == expected_authors


def test_grobid_no_authors():

    grobid_response = pkg_resources.resource_string(
        __name__,
        os.path.join(
            'fixtures',
            'grobid_no_authors_doc.xml'
        )
    )

    expected_authors = []
    expected_authors_count = 0
    authors = GrobidAuthors(grobid_response)
    assert len(authors) == expected_authors_count
    assert authors.parse_all() == expected_authors


def test_grobid_empty_author():

    grobid_response = pkg_resources.resource_string(
        __name__,
        os.path.join(
            'fixtures',
            'grobid_empty_author_doc.xml'
        )
    )

    expected_authors = [{'parsed_affiliations': None, 'author': {'full_name': u'Abc, Xyz'}}, {'parsed_affiliations': None, 'author': {'emails': [u'some@email.cern'], 'full_name': u'Yzc'}}]
    expected_authors_count = 2
    authors = GrobidAuthors(grobid_response)
    assert len(authors) == expected_authors_count
    assert authors.parse_all() == expected_authors
