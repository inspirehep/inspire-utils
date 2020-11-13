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


def wrap_queries_in_bool_clauses_if_more_than_one(
    queries, use_must_clause, preserve_bool_semantics_if_one_clause=False
):
    """Helper for wrapping a list of queries into a bool.{must, should} clause.
    Args:
        queries (list): List of queries to be wrapped in a bool.{must, should} clause.
        use_must_clause (bool): Flag that signifies whether to use 'must' or 'should' clause.
        preserve_bool_semantics_if_one_clause (bool): Flag that signifies whether to generate a bool query even if
            there's only one clause. This happens to generate boolean query semantics. Usually not the case, but
            useful for boolean queries support.
    Returns:
        (dict): If len(queries) > 1, the bool clause, otherwise if len(queries) == 1, will return the query itself,
                while finally, if len(queries) == 0, then an empty dictionary is returned.
    """
    if not queries:
        return {}

    queries = [q for q in queries if q]

    if len(queries) == 1 and not preserve_bool_semantics_if_one_clause:
        return queries[0]

    return {"bool": {"must" if use_must_clause else "should": queries}}


def ordered(obj):
    """
    Helper to order the dictionary
    """
    # See https://stackoverflow.com/a/25851972
    if isinstance(obj, dict):
        return sorted((k, ordered(v)) for k, v in obj.items())
    if isinstance(obj, list):
        return sorted(ordered(x) for x in obj)
    else:
        return obj
