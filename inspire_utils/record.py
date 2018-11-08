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

from six import string_types

import re


SPLIT_KEY_PATTERN = re.compile(r'\.|\[')


def get_value(record, key, default=None):
    """Return item as `dict.__getitem__` but using 'smart queries'.

    .. note::

        Accessing one value in a normal way, meaning d['a'], is almost as
        fast as accessing a regular dictionary. But using the special
        name convention is a bit slower than using the regular access:
        .. code-block:: python
            >>> %timeit x = dd['a[0].b']
            100000 loops, best of 3: 3.94 us per loop
            >>> %timeit x = dd['a'][0]['b']
            1000000 loops, best of 3: 598 ns per loop
    """
    def getitem(k, v, default):
        if isinstance(v, string_types):
            raise KeyError
        elif isinstance(v, dict):
            return v[k]
        elif ']' in k:
            k = k[:-1].replace('n', '-1')
            # Work around for list indexes and slices
            try:
                return v[int(k)]
            except IndexError:
                return default
            except ValueError:
                return v[slice(*map(
                    lambda x: int(x.strip()) if x.strip() else None,
                    k.split(':')
                ))]
        else:
            tmp = []
            for inner_v in v:
                try:
                    tmp.append(getitem(k, inner_v, default))
                except KeyError:
                    continue
            return tmp

    # Check if we are using python regular keys
    try:
        return record[key]
    except KeyError:
        pass

    keys = SPLIT_KEY_PATTERN.split(key)
    value = record
    for k in keys:
        try:
            value = getitem(k, value, default)
        except KeyError:
            return default
    return value


def get_values_for_schema(elements, schema):
    """Return all values from elements having a given schema.

    Args:
        elements(Iterable[dict]): an iterable of elements, which are all dicts
            having at least the ``schema`` and ``value`` keys.
        schema(str): the schema that the values need to follow.

    Returns:
        list: all values conforming to the given schema.

    Example:
        >>> elements = [
        ...     {'schema': 'TWITTER', 'value': 's_w_hawking'},
        ...     {'schema': 'WIKIPEDIA', 'value': 'Stephen_Hawking'}
        ... ]
        >>> get_values_for_schema(elements, 'TWITTER')
        ['s_w_hawking']
    """
    return [element['value'] for element in elements if element['schema'] == schema]
