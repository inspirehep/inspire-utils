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

from itertools import product

from nameparser import HumanName
from nameparser.config import Constants
import six
from unidecode import unidecode

from .logging import getStackTraceLogger

LOGGER = getStackTraceLogger(__name__)

_LASTNAME_NON_LASTNAME_SEPARATORS = [u' ', u', ']
_NAMES_MAX_NUMBER_THRESHOLD = 5
"""Threshold for skipping the combinatorial expansion of names (when generating name variations). """


def _prepare_nameparser_constants():
    """Prepare nameparser Constants.

    Remove nameparser's titles and use our own and add as suffixes the roman numerals.
    Configuration is the same for all names (i.e. instances).
    """
    constants = Constants()
    roman_numeral_suffixes = [u'v', u'vi', u'vii', u'viii', u'ix', u'x',
                              u'xii', u'xiii', u'xiv', u'xv']
    titles = [u'Dr', u'Prof', u'Professor', u'Sir', u'Editor', u'Ed', u'Mr',
              u'Mrs', u'Ms', u'Chair', u'Co-Chair', u'Chairs', u'co-Chairs']
    constants.titles.remove(*constants.titles).add(*titles)
    constants.suffix_not_acronyms.add(*roman_numeral_suffixes)
    return constants


class ParsedName(object):
    """Class for representing a name.

    After construction, the instance exposes the fields exposed by `HumanName` instance, i.e.
    `title`, `first`, `middle`, `last`, `suffix`.
    """
    constants = _prepare_nameparser_constants()
    """The default constants configuration for `HumanName` to use for parsing all names."""

    def __init__(self, name, constants=None):
        """Create a ParsedName instance.

        Args:
            name (Union[str, HumanName]): The name to be parsed (must be non empty nor None).
            constants (:class:`nameparser.config.Constants`): Configuration for `HumanName` instantiation.
                (Can be None, if provided it overwrites the default one generated in
                :method:`prepare_nameparser_constants`.)
        """
        if not constants:
            constants = ParsedName.constants

        if isinstance(name, HumanName):
            self._parsed_name = name
        else:
            self._parsed_name = HumanName(name, constants=constants)
            self._parsed_name.capitalize()

    def __iter__(self):
        return self._parsed_name

    def __len__(self):
        return len(self._parsed_name)

    def __repr__(self):
        return repr(self._parsed_name)

    def __str__(self):
        return str(self._parsed_name)

    @property
    def first_initials(self):
        return u' '.join(self.first_initials_list)

    @property
    def first(self):
        return u'{} {}'.format(self._parsed_name.first, self._parsed_name.middle).strip()

    @property
    def first_initials_list(self):
        names = self.first_list
        return [(name[0] + u'.') for name in names]

    @property
    def first_list(self):
        return self._parsed_name.first_list + self._parsed_name.middle_list

    @property
    def last(self):
        return self._parsed_name.last

    @property
    def last_list(self):
        return self._parsed_name.last_list

    @property
    def suffix(self):
        return self._parsed_name.suffix

    @property
    def suffix_list(self):
        return self._parsed_name.suffix_list

    @classmethod
    def loads(cls, name):
        """Load a parsed name from a string.

        Raises:
            TypeError: when name isn't a type of `six.string_types`.
            ValueError: when name is empty or None.
        """
        if not isinstance(name, six.string_types):
            raise TypeError(u'arguments to {classname} must be of type {string_types}'.format(
                classname=cls.__name__, string_types=repr(six.string_types)
            ))
        if not name or name.isspace():
            raise ValueError('name must not be empty')

        return cls(name)

    def dumps(self):
        """Dump the name to string, after normalizing it."""
        def _is_initial(author_name):
            return len(author_name) == 1 or u'.' in author_name

        def _ensure_dotted_initials(author_name):
            if _is_initial(author_name) \
                    and u'.' not in author_name:
                seq = (author_name, u'.')
                author_name = u''.join(seq)
            return author_name

        def _ensure_dotted_suffixes(author_suffix):
            if u'.' not in author_suffix:
                seq = (author_suffix, u'.')
                author_suffix = u''.join(seq)
            return author_suffix

        def _is_roman_numeral(suffix):
            """Controls that the user's input only contains valid roman numerals"""
            valid_roman_numerals = [u'M', u'D', u'C', u'L', u'X',
                                    u'V', u'I', u'(', u')']
            return all(letters in valid_roman_numerals
                       for letters in suffix.upper())

        first_and_middle_names = iter(_ensure_dotted_initials(name) for name in self.first_list)
        try:
            prev = next(first_and_middle_names)
        except StopIteration:
            LOGGER.warning(u"Cannot process %s properly",
                           self._parsed_name.original)
            prev = self._parsed_name.original
        names_with_spaces = [prev]

        for name in first_and_middle_names:
            if not _is_initial(name) or not _is_initial(prev):
                names_with_spaces.append(' ')
            prev = name
            names_with_spaces.append(prev)

        normalized_names = u''.join(names_with_spaces)

        if _is_roman_numeral(self.suffix):
            suffix = self.suffix.upper()
        else:
            suffix = _ensure_dotted_suffixes(self.suffix)

        final_name = u', '.join(
            part for part in (self.last, normalized_names.strip(), suffix)
            if part)

        # Replace unicode curly apostrophe to normal apostrophe.
        final_name = final_name.replace(u'’', '\'')

        return final_name

    def pprint(self, initials_only=False):
        """Pretty print the name.

        Args:
            initials_only (bool): ``True`` if we want the first names to be displayed with
            only the initial followed by a dot. ``False`` otherwise.

        Examples:
            >>> ParsedName('Lieber, Stanley Martin').pprint()
            u'Stanley Martin Lieber'
            >>> ParsedName('Lieber, Stanley Martin').pprint(initials_only=True)
            u'S. M. Lieber'
            >>> ParsedName('Downey, Robert Jr.').pprint(initials_only=True)
            u'R. Downey Jr.'

        """
        last_name = self.last
        suffixes = ', ' + self.suffix if self.suffix else ''

        if initials_only and last_name != u'':
            first_names = self.first_initials
        else:
            first_names = self.first

        return u'{} {}{}'.format(first_names, last_name, suffixes).strip()

    @classmethod
    def from_parts(
        cls,
        first=None,
        last=None,
        middle=None,
        suffix=None,
        title=None
    ):
        name = HumanName()
        name.first = first
        name.middle = middle
        name.last = last
        name.suffix = suffix
        name.title = title
        return ParsedName(name)


def normalize_name(name):
    """Normalize name.

    Args:
        name (six.text_type): The name to be normalized.

    Returns:
        str: The normalized name.
    """
    if not name or name.isspace():
        return None

    return ParsedName.loads(name).dumps()


def _generate_non_lastnames_variations(non_lastnames):
    """Generate variations for all non-lastnames.

    E.g. For 'John Richard', this method generates: [
        'John', 'J', 'Richard', 'R', 'John Richard', 'John R', 'J Richard', 'J R',
    ]
    """
    if not non_lastnames:
        return []

    # Generate name transformations in place for all non lastnames. Transformations include:
    # 1. Drop non last name, 2. use initial, 3. use full non lastname
    for idx, non_lastname in enumerate(non_lastnames):
        non_lastnames[idx] = (u'', non_lastname[0], non_lastname)

    # Generate the cartesian product of the transformed non lastnames and flatten them.
    return [
        (u' '.join(var_elem for var_elem in variation if var_elem)).strip()
        for variation in product(*non_lastnames)
    ]


def _generate_lastnames_variations(lastnames):
    """Generate variations for lastnames.

    Note:
        This method follows the assumption that the first last name is the main one.
        E.g. For 'Caro Estevez', this method generates: ['Caro', 'Caro Estevez'].
        In the case the lastnames are dashed, it splits them in two.
    """
    if not lastnames:
        return []

    split_lastnames = [split_lastname for lastname in lastnames for split_lastname in lastname.split('-')]

    lastnames_variations = split_lastnames
    if len(split_lastnames) > 1:
        # Generate lastnames concatenation if there are more than one lastname after split.
        lastnames_variations.append(u' '.join([lastname for lastname in split_lastnames]))

    return lastnames_variations


def generate_name_variations(name):
    """Generate name variations for a given name.

    Args:
        name (six.text_type): The name whose variations are to be generated.

    Returns:
        list: All the name variations for the given name.

    Notes:
        Uses `unidecode` for doing unicode characters transliteration to ASCII ones. This was chosen so that we can map
        both full names of authors in HEP records and user's input to the same space and thus make exact queries work.
    """
    def _update_name_variations_with_product(set_a, set_b):
        name_variations.update([
            unidecode((names_variation[0] +
                       separator +
                       names_variation[1]).strip(''.join(_LASTNAME_NON_LASTNAME_SEPARATORS))).lower()
            for names_variation
            in product(set_a, set_b)
            for separator
            in _LASTNAME_NON_LASTNAME_SEPARATORS
        ])

    parsed_name = ParsedName.loads(name)

    # Handle rare-case of single-name
    if len(parsed_name) == 1:
        return [parsed_name.dumps().lower()]

    name_variations = set()

    # We need to filter out empty entries, since HumanName for this name `Perelstein,, Maxim` returns a first_list with
    # an empty string element.
    non_lastnames = [
        non_lastname
        for non_lastname
        in parsed_name.first_list + parsed_name.suffix_list
        if non_lastname
    ]

    # This is needed because due to erroneous data (e.g. having many authors in a single authors field) ends up
    # requiring a lot of memory (due to combinatorial expansion of all non lastnames).
    # The policy is to use the input as a name variation, since this data will have to be curated.
    if len(non_lastnames) > _NAMES_MAX_NUMBER_THRESHOLD or len(parsed_name.last_list) > _NAMES_MAX_NUMBER_THRESHOLD:
        LOGGER.error('Skipping name variations generation - too many names in: "%s"', name)
        return [name]

    non_lastnames_variations = \
        _generate_non_lastnames_variations(non_lastnames)
    lastnames_variations = _generate_lastnames_variations(parsed_name.last_list)

    # Create variations where lastnames comes first and is separated from non lastnames either by space or comma.
    _update_name_variations_with_product(lastnames_variations, non_lastnames_variations)

    # Second part of transformations - having the lastnames in the end.
    _update_name_variations_with_product(non_lastnames_variations, lastnames_variations)

    return list(name_variations)


def format_name(name, initials_only=False):
    """Format a schema-compliant name string in a human-friendy format.

    This is a convenience wrapper around :ref:`ParsedName`, which should be
    used instead if more features are needed.

    Args:
        name (str): The name to format, in pretty much any format.
        initials_only (bool): ``True`` if we want the first names to be displayed with only the initial followed by a dot. ``False`` otherwise.

    Examples:
    >>> format_name('Lieber, Stanley Martin')
    u'Stanley Martin Lieber'
    >>> format_name('Lieber, Stanley Martin', initials_only=True)
    u'S. M. Lieber'
    >>> format_name('Downey, Robert Jr.', initials_only=True)
    u'R. Downey Jr.'
    """
    return ParsedName.loads(name).pprint(initials_only)
