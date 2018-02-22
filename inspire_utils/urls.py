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

import re

from six import text_type


def ensure_scheme(url, default_schema='http'):
    """Adds a scheme to a url if not present.

    Scheme is defined in section 3.1 of http://www.ietf.org/rfc/rfc2396.txt

    Args:
        url (string): a url
        default_schema (string): a scheme to be added

    Returns:
        string: URL with a scheme
    """
    if not re.match(r'^[a-zA-Z][a-zA-Z+\-.0-9]*://', url):
        url = '%s://%s' % (default_schema, url)

    return url


def record_url_by_pattern(pattern, recid):
    """Get a URL to a record constructing it from a pattern.

    Args:
        pattern (string): a URL pattern as a format-friendly string with a
            `recid` field
        recid (Union[string, int]): record ID

    Returns:
        string: built record URL
    """
    recid = text_type(recid)
    return text_type(ensure_scheme(pattern)).format(recid=recid)
