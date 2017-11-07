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

from lxml import etree

import six


def force_list(data):
    """Force ``data`` to become a list.

    You should use this method whenever you don't want to deal with the
    fact that ``NoneType`` can't be iterated over. For example, instead
    of writing::

        bar = foo.get('bar')
        if bar is not None:
            for el in bar:
                ...

    you can write::

        for el in force_list(foo.get('bar')):
            ...

    Args:
        data: any Python object.

    Returns:
        list: a list representation of ``data``.

    Examples:
        >>> force_list(None)
        []
        >>> force_list('foo')
        ['foo']
        >>> force_list(('foo', 'bar'))
        ['foo', 'bar']
        >>> force_list(['foo', 'bar', 'baz'])
        ['foo', 'bar', 'baz']

    """
    if data is None:
        return []
    elif not isinstance(data, (list, tuple, set)):
        return [data]
    elif isinstance(data, (tuple, set)):
        return list(data)
    return data


def maybe_float(el):
    """Return a ``float`` if possible, otherwise ``None``.

    Args:
        el: any Python object.

    Returns:
        float: a ``float`` parsed from the object, or ``None``.

    Examples:
        >>> maybe_float('35.0499505')
        35.0499505

    """
    try:
        return float(el)
    except (TypeError, ValueError):
        pass


def maybe_int(el):
    """Return an ``int`` if possible, otherwise ``None``.

    Args:
        el: any Python object.

    Returns:
        Union[int, NoneType]: an ``int`` parsed from the object, or ``None``.

    Examples:
        >>> maybe_int('10')
        10

    """
    try:
        return int(el)
    except (TypeError, ValueError):
        pass


def remove_tags(dirty, allowed_tags=(), allowed_trees=(), strip=None):
    """Selectively remove tags.

    This removes all tags in ``dirty``, stripping also the contents of tags
    matching the XPath selector in ``strip``, and keeping all tags that are
    subtags of tags in ``allowed_trees`` and tags in ``allowed_tags``.

    Args:
        dirty(Union[str, scrapy.selector.Selector, lxml.etree._Element]): the
            input to clean up.
        allowed_tags(Container): tags to be kept in the output, but not necessarily
            its subtags.
        allowed_trees(Container): tags to be kept, along with all its subtags,
            in the output.
        strip(str): optional xpath selector. If it matches a tag, its
            contents will also be stripped. Useful axes are ``@`` for attribute access
            and ``self`` to select a given tag.

    Returns:
        str: the textual content of ``dirty``, with some tags kept and some text
        removed.

    Examples:
        >>> tag = '<p><b><i>Only</i></b> this text remains.<span class="hidden">Not this one.</span></p>'
        >>> remove_tags(tag, allowed_tree=('b',), strip='@class="hidden"')
        u'<b><i>Only</i></b> this text remains.'
        >>> remove_tags(tag, allowed_tags=('b',), strip='@class="hidden"')
        u'<b>Only</b> this text remains.'
        >>> remove_tags(tag, allowed_tags=('b',), strip='self::span')
        u'<b>Only</b> this text remains.'
    """
    if isinstance(dirty, six.string_types):
        element = etree.fromstring(u''.join(('<DUMMYROOTTAG>', dirty, '</DUMMYROOTTAG>')))
    elif isinstance(dirty, etree._Element):
        element = dirty
    else:  # assuming scrapy Selector
        element = dirty.root

    if element.tag in allowed_trees:
        return etree.tostring(element, encoding='unicode')

    tail = element.tail or u''

    if strip and element.xpath(strip):
        return tail

    subtext = u''.join(
        remove_tags(child, allowed_tags=allowed_tags, allowed_trees=allowed_trees, strip=strip)
        for child in element
    )
    text = element.text or u''

    if element.tag in allowed_tags:
        for child in element:
            element.remove(child)
        element.text = u''.join((text, subtext))
        return etree.tostring(element, encoding='unicode')

    return u''.join((text, subtext, tail))
