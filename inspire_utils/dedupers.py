# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014-2024 CERN.
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

import six


def dedupe_list(list_with_duplicates):
    """Remove duplicates from a list preserving the order.

    We might be tempted to use the list(set(l)) idiom, but it doesn't
    preserve the order, which hinders testability.
    """
    result = []

    for el in list_with_duplicates:
        if el not in result:
            result.append(el)

    return result


def dedupe_list_of_dicts(ld):
    """Remove duplicates from a list of dictionaries preserving the order.

    We can't use the generic list helper because a dictionary isn't
    hashable. Adapted from
    http://stackoverflow.com/a/9427216/374865.
    """

    def _freeze(o):
        """Recursively freezes a dict into an hashable object.

        Adapted from http://stackoverflow.com/a/21614155/374865.
        """
        if isinstance(o, dict):
            return frozenset((k, _freeze(v)) for k, v in six.iteritems(o))
        elif isinstance(o, (list, tuple)):
            return tuple(_freeze(v) for v in o)
        else:
            return o

    result = []
    seen = set()

    for d in ld:
        f = _freeze(d)
        if f not in seen:
            result.append(d)
            seen.add(f)

    return result


def dedupe_all_lists(obj, exclude_keys=(), dedupe_top_level=True):
    """Recursively remove duplicates from all lists.

    Args:
        obj: collection to deduplicate
        exclude_keys (Container[str]): key names to ignore for deduplication
        dedupe_top_level (bool): whether the top-level list should be deduplicated too
    """
    squared_dedupe_len = 10
    if isinstance(obj, dict):
        new_obj = {}
        for key, value in obj.items():
            dedupe_top_level = key not in exclude_keys
            new_obj[key] = dedupe_all_lists(value, exclude_keys, dedupe_top_level)
        return new_obj
    elif isinstance(obj, (list, tuple, set)):
        new_obj = [dedupe_all_lists(v, exclude_keys) for v in obj]
        if dedupe_top_level:
            if len(new_obj) < squared_dedupe_len:
                new_obj = dedupe_list(new_obj)
            else:
                new_obj = dedupe_list_of_dicts(new_obj)
        return type(obj)(new_obj)
    else:
        return obj
