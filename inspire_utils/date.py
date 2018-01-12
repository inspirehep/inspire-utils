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

"""Utils to handle dates in INSPIRE."""

from __future__ import absolute_import, division, print_function

import datetime
import itertools
from functools import total_ordering

import six
from babel import dates
from dateutil.parser import parse as parse_date


@total_ordering
@six.python_2_unicode_compatible
class PartialDate(object):
    """Class for representing a partial date.

    The standard constructor assumes that all date parts are known (or not
    present) and have already been converted to `int` s. For more flexibility,
    see :ref:`PartialDate.from_parts` and :ref:`PartialDate.parse`.

    Two `PartialDate` s can be compared and a more complete date is considered
    smaller than the same date with parts removed.

    Raises:
        TypeError: when the date parts are not `int` s or `None`.
        ValueError: when the date is not valid.

    """
    def __init__(self, year, month=None, day=None):
        well_typed = all(isinstance(part, int) or part is None for part in (year, month, day))
        if not well_typed:
            raise TypeError(u'arguments to {classname} must be of type int or None'.format(
                classname=type(self).__name__))
        if year is None or year < 1000:
            raise ValueError('year must be an int >= 1000')
        if day and not month:
            raise TypeError('month must not be None if day is not None')
        # delegate validation of number of months/days to datetime
        completion = (part or 1 for part in (year, month, day))
        datetime.date(*completion)

        self.year = year
        self.month = month
        self.day = day

    def __repr__(self):
        return u'PartialDate(year={self.year}, month={self.month}, day={self.day})'.format(self=self)

    def __eq__(self, other):
        return self.year == other.year and self.month == other.month and self.day == other.day

    def __lt__(self, other):
        self_month = self.month or 99
        self_day = self.day or 99
        other_month = other.month or 99
        other_day = other.day or 99

        return (self.year, self_month, self_day) < (other.year, other_month, other_day)

    def __str__(self):
        return self.pprint()

    @classmethod
    def loads(cls, string):
        """Load a date from a string in a record.

        This can also be used to validate a date.

        Examples:
            >>> PartialDate.loads('1686-06')
            PartialDate(year=1686, month=6, day=None)
            >>> PartialDate.loads('1686-42')
            Traceback (most recent call last):
            ...
            ValueError: month must be in 1..12

        """
        parts = (int(part) for part in string.split('-'))
        return cls(*parts)

    def dumps(self):
        """Dump the date for serialization into the record.

        Returns:
            str: normalized date, in the form ``YYYY-MM-DD``, ``YYYY-MM`` or
                ``YYYY`` (depending on the information present in the date)

        """
        non_empty = itertools.takewhile(bool, (self.year, self.month, self.day))
        # XXX: this only handles dates after 1000, which should be sufficient
        formatted = (u'{:02d}'.format(part) for part in non_empty)
        date = '-'.join(formatted)

        return date

    @classmethod
    def parse(cls, date, **kwargs):
        """Parse a date given in arbitrary format.

        This attempts to parse the input date, given in an arbitrary format

        Args:
            date(str): date to normalize
            **kwargs: these are passed to the `dateutil.parser.parse` function
                which is used internally to parse the date. Most notably, the
                `yearfirst` and `datefirst` flags can be used if the ordering
                of the date parts is known.

        Returns:
            PartialDate: an object holding the parsed date.

        Raises:
            ValueError: when the date cannot be parsed or no year is present.

        Examples:
            >>> PartialDate.parse('30 Jun 1686')
            PartialDate(year=1686, month=6, day=30)

        """
        # In order to detect partial dates, parse twice with different defaults
        # and compare the results.
        default_date1 = datetime.datetime(1, 1, 1)
        default_date2 = datetime.datetime(2, 2, 2)

        parsed_date1 = parse_date(date, default=default_date1, **kwargs)
        parsed_date2 = parse_date(date, default=default_date2, **kwargs)

        has_year = parsed_date1.year == parsed_date2.year
        has_month = parsed_date1.month == parsed_date2.month
        has_day = parsed_date1.day == parsed_date2.day

        if has_year:
            year = parsed_date1.year
        else:
            raise ValueError('date does not contain a year')
        month = parsed_date1.month if has_month else None
        day = parsed_date1.day if has_day else None

        return cls(year, month, day)

    @classmethod
    def from_parts(cls, year, month=None, day=None):
        """Build a PartialDate from its parts.

        Unlike the standard constructor, the parts don't have to be `int` s but
        can be strings containing textual month information.

        Examples:
            >>> PartialDate.from_parts('1686', 'June', '30')
            PartialDate(year=1686, month=6, day=30)

        """
        # XXX: 0 is not a valid year/month/day
        non_empty = itertools.takewhile(
            bool, (str(part) if part else None for part in (year, month, day))
        )
        return cls.parse(u'-'.join(non_empty), yearfirst=True)

    def pprint(self):
        """Pretty print the date.

        Examples:
            >>> PartialDate(1686, 6, 30).pprint()
            u'Jun 30, 1686'

        """
        if not self.month:
            return dates.format_date(datetime.date(self.year, 1, 1), 'YYYY', locale='en')
        if not self.day:
            return dates.format_date(datetime.date(self.year, self.month, 1), 'MMM, YYYY', locale='en')
        return dates.format_date(datetime.date(self.year, self.month, self.day), 'MMM d, YYYY', locale='en')


def normalize_date(date, **kwargs):
    """Normalize a date to the be schema-compliant.

    This is a convenience wrapper around :ref:`PartialDate`, which should be
    used instead if more features are needed.

    Note:
        When ``date`` is ``None`` this returns ``None`` instead of raising
        an exception because this makes ``DoJSON``'s code simpler, as it
        already knows how to strip ``None`` values at the end.

    Args:
        date(str): date to normalize
        **kwargs: these are passed to the `dateutil.parser.parse` function
            that is used internally to parse the date. Most notably, the
            `yearfirst` and `datefirst` flags can be used if the ordering
            of the date parts is know.

    Returns:
        str: normalized date, in the form ``YYYY-MM-DD``, ``YYYY-MM`` or
            ``YYYY`` (depending on the information present in the date).

    Raises:
        ValueError: when the date cannot be parsed or no year is present.

    Examples:
        >>> normalize_date(None)
        >>> normalize_date('30 Jun 1686')
        '1686-06-30'

    """
    if date is None:
        return

    return PartialDate.parse(date, **kwargs).dumps()


def format_date(date):
    """Format a schema-compliant date string in a human-friendy format.

    This is a convenience wrapper around :ref:`PartialDate`, which should be
    used instead if more features are needed.
    """
    return PartialDate.loads(date).pprint()


def earliest_date(dates):
    """Return the earliest among the schema-compliant dates.

    This is a convenience wrapper around :ref:`PartialDate`, which should be
    used instead if more features are needed.
    """
    return min(PartialDate.loads(date) for date in dates).dumps()
