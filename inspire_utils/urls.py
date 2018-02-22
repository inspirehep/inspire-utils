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

"""URL-related utils."""

from __future__ import absolute_import, division, print_function

from six import text_type
from six.moves.urllib.parse import urlsplit, urlunsplit, SplitResult


def ensure_scheme(url, default_scheme='http'):
    """Adds a scheme to a url if not present.

    Args:
        url (string): a url, assumed to start with netloc
        default_scheme (string): a scheme to be added

    Returns:
        string: URL with a scheme
    """
    parsed = urlsplit(url, scheme=default_scheme)
    if not parsed.netloc:
        parsed = SplitResult(
            scheme=parsed.scheme,
            netloc=parsed.path,
            path='',
            query=parsed.query,
            fragment=parsed.fragment
        )

    return urlunsplit(parsed)


def record_url_by_pattern(pattern, recid):
    """Get a URL to a record constructing it from a pattern.

    Args:
        pattern (string): a URL pattern as a format-friendly string with a
            `recid` field
        recid (Union[string, int]): record ID

    Returns:
        string: built record URL
    """
    return text_type(ensure_scheme(pattern)).format(recid=recid)
