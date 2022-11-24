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

import re

from elasticsearch_dsl import Q
from six import string_types

from .dedupers import dedupe_list
from .logging import getStackTraceLogger

LOGGER = getStackTraceLogger(__name__)
SPLIT_KEY_PATTERN = re.compile(r"\.|\[")


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
        elif "]" in k:
            k = k[:-1].replace("n", "-1")
            # Work around for list indexes and slices
            try:
                return v[int(k)]
            except IndexError:
                return default
            except ValueError:
                return v[
                    slice(
                        *map(
                            lambda x: int(x.strip()) if x.strip() else None,
                            k.split(":"),
                        )
                    )
                ]
        else:
            tmp = []
            for inner_v in v:
                try:
                    tmp.append(getitem(k, inner_v, default))
                except KeyError:
                    continue
            return tmp

    # Wrap a top-level list in a dict
    if isinstance(record, list):
        record = {"record": record}
        key = ".".join(["record", key])

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
    return [element["value"] for element in elements if element["schema"] == schema]


UNDESIRABLE_CHAR_REPLACEMENTS = {
    # Control characters not allowed in XML:
    u'\u2028': u"",
    u'\u2029': u"",
    u'\u202A': u"",
    u'\u202B': u"",
    u'\u202C': u"",
    u'\u202D': u"",
    u'\u202E': u"",
    u'\u206A': u"",
    u'\u206B': u"",
    u'\u206C': u"",
    u'\u206D': u"",
    u'\u206E': u"",
    u'\u206F': u"",
    u'\uFFF9': u"",
    u'\uFFFA': u"",
    u'\uFFFB': u"",
    u'\uFFFC': u"",
    u'\uFEFF': u"",
    # Remove the result of a bad UTF-8 character
    u'\uFFFF': u"",
    # Language Tag Code Points:
    u"\U000E0000": u"",
    u"\U000E0001": u"",
    u"\U000E0002": u"",
    u"\U000E0003": u"",
    u"\U000E0004": u"",
    u"\U000E0005": u"",
    u"\U000E0006": u"",
    u"\U000E0007": u"",
    u"\U000E0008": u"",
    u"\U000E0009": u"",
    u"\U000E000A": u"",
    u"\U000E000B": u"",
    u"\U000E000C": u"",
    u"\U000E000D": u"",
    u"\U000E000E": u"",
    u"\U000E000F": u"",
    u"\U000E0010": u"",
    u"\U000E0011": u"",
    u"\U000E0012": u"",
    u"\U000E0013": u"",
    u"\U000E0014": u"",
    u"\U000E0015": u"",
    u"\U000E0016": u"",
    u"\U000E0017": u"",
    u"\U000E0018": u"",
    u"\U000E0019": u"",
    u"\U000E001A": u"",
    u"\U000E001B": u"",
    u"\U000E001C": u"",
    u"\U000E001D": u"",
    u"\U000E001E": u"",
    u"\U000E001F": u"",
    u"\U000E0020": u"",
    u"\U000E0021": u"",
    u"\U000E0022": u"",
    u"\U000E0023": u"",
    u"\U000E0024": u"",
    u"\U000E0025": u"",
    u"\U000E0026": u"",
    u"\U000E0027": u"",
    u"\U000E0028": u"",
    u"\U000E0029": u"",
    u"\U000E002A": u"",
    u"\U000E002B": u"",
    u"\U000E002C": u"",
    u"\U000E002D": u"",
    u"\U000E002E": u"",
    u"\U000E002F": u"",
    u"\U000E0030": u"",
    u"\U000E0031": u"",
    u"\U000E0032": u"",
    u"\U000E0033": u"",
    u"\U000E0034": u"",
    u"\U000E0035": u"",
    u"\U000E0036": u"",
    u"\U000E0037": u"",
    u"\U000E0038": u"",
    u"\U000E0039": u"",
    u"\U000E003A": u"",
    u"\U000E003B": u"",
    u"\U000E003C": u"",
    u"\U000E003D": u"",
    u"\U000E003E": u"",
    u"\U000E003F": u"",
    u"\U000E0040": u"",
    u"\U000E0041": u"",
    u"\U000E0042": u"",
    u"\U000E0043": u"",
    u"\U000E0044": u"",
    u"\U000E0045": u"",
    u"\U000E0046": u"",
    u"\U000E0047": u"",
    u"\U000E0048": u"",
    u"\U000E0049": u"",
    u"\U000E004A": u"",
    u"\U000E004B": u"",
    u"\U000E004C": u"",
    u"\U000E004D": u"",
    u"\U000E004E": u"",
    u"\U000E004F": u"",
    u"\U000E0050": u"",
    u"\U000E0051": u"",
    u"\U000E0052": u"",
    u"\U000E0053": u"",
    u"\U000E0054": u"",
    u"\U000E0055": u"",
    u"\U000E0056": u"",
    u"\U000E0057": u"",
    u"\U000E0058": u"",
    u"\U000E0059": u"",
    u"\U000E005A": u"",
    u"\U000E005B": u"",
    u"\U000E005C": u"",
    u"\U000E005D": u"",
    u"\U000E005E": u"",
    u"\U000E005F": u"",
    u"\U000E0060": u"",
    u"\U000E0061": u"",
    u"\U000E0062": u"",
    u"\U000E0063": u"",
    u"\U000E0064": u"",
    u"\U000E0065": u"",
    u"\U000E0066": u"",
    u"\U000E0067": u"",
    u"\U000E0068": u"",
    u"\U000E0069": u"",
    u"\U000E006A": u"",
    u"\U000E006B": u"",
    u"\U000E006C": u"",
    u"\U000E006D": u"",
    u"\U000E006E": u"",
    u"\U000E006F": u"",
    u"\U000E0070": u"",
    u"\U000E0071": u"",
    u"\U000E0072": u"",
    u"\U000E0073": u"",
    u"\U000E0074": u"",
    u"\U000E0075": u"",
    u"\U000E0076": u"",
    u"\U000E0077": u"",
    u"\U000E0078": u"",
    u"\U000E0079": u"",
    u"\U000E007A": u"",
    u"\U000E007B": u"",
    u"\U000E007C": u"",
    u"\U000E007D": u"",
    u"\U000E007E": u"",
    u"\U000E007F": u"",
    # Musical Notation Scoping
    u"\U0001D173": u"",
    u"\U0001D174": u"",
    u"\U0001D175": u"",
    u"\U0001D176": u"",
    u"\U0001D177": u"",
    u"\U0001D178": u"",
    u"\U0001D179": u"",
    u"\U0001D17A": u"",
    u'\u0000': u"",  # NULL
    u'\u0001': u"",  # START OF HEADING
    # START OF TEXT & END OF TEXT:
    u'\u0002': u"",
    u'\u0003': u"",
    u'\u0004': u"",  # END OF TRANSMISSION
    # ENQ and ACK
    u'\u0005': u"",
    u'\u0006': u"",
    u'\u0007': u"",  # BELL
    u'\u0008': u"",  # BACKSPACE
    # SHIFT-IN & SHIFT-OUT
    u'\u000E': u"",
    u'\u000F': u"",
    # Other controls:
    u'\u0010': u"",  # DATA LINK ESCAPE
    u'\u0011': u"",  # DEVICE CONTROL ONE
    u'\u0012': u"",  # DEVICE CONTROL TWO
    u'\u0013': u"",  # DEVICE CONTROL THREE
    u'\u0014': u"",  # DEVICE CONTROL FOUR
    u'\u0015': u"",  # NEGATIVE ACK
    u'\u0016': u"",  # SYNCRONOUS IDLE
    u'\u0017': u"",  # END OF TRANSMISSION BLOCK
    u'\u0018': u"",  # CANCEL
    u'\u0019': u"",  # END OF MEDIUM
    u'\u001A': u"",  # SUBSTITUTE
    u'\u001B': u"",  # ESCAPE
    u'\u001C': u"",  # INFORMATION SEPARATOR FOUR (file separator)
    u'\u001D': u"",  # INFORMATION SEPARATOR THREE (group separator)
    u'\u001E': u"",  # INFORMATION SEPARATOR TWO (record separator)
    u'\u001F': u"",  # INFORMATION SEPARATOR ONE (unit separator)
    # \r -> remove it
    u'\r': u"",
    # Some ff from tex:
    u'\u0013\u0010': u'\u00ED',
    u'\x0b': u'ff',
    # fi from tex:
    u'\x0c': u'fi',
    # ligatures from TeX:
    u'\ufb00': u'ff',
    u'\ufb01': u'fi',
    u'\ufb02': u'fl',
    u'\ufb03': u'ffi',
    u'\ufb04': u'ffl',
    # Superscripts from TeX
    u'\u2212': u'-',
    u'\u2013': u'-',
    # Word style speech marks:
    u'\u201c ': u'"',
    u'\u201d': u'"',
    u'\u201c': u'"',
    # pdftotext has problems with umlaut and prints it as diaeresis
    # followed by a letter:correct it
    # (Optional space between char and letter - fixes broken
    # line examples)
    u'\u00A8 a': u'\u00E4',
    u'\u00A8 e': u'\u00EB',
    u'\u00A8 i': u'\u00EF',
    u'\u00A8 o': u'\u00F6',
    u'\u00A8 u': u'\u00FC',
    u'\u00A8 y': u'\u00FF',
    u'\u00A8 A': u'\u00C4',
    u'\u00A8 E': u'\u00CB',
    u'\u00A8 I': u'\u00CF',
    u'\u00A8 O': u'\u00D6',
    u'\u00A8 U': u'\u00DC',
    u'\u00A8 Y': u'\u0178',
    u'\xA8a': u'\u00E4',
    u'\xA8e': u'\u00EB',
    u'\xA8i': u'\u00EF',
    u'\xA8o': u'\u00F6',
    u'\xA8u': u'\u00FC',
    u'\xA8y': u'\u00FF',
    u'\xA8A': u'\u00C4',
    u'\xA8E': u'\u00CB',
    u'\xA8I': u'\u00CF',
    u'\xA8O': u'\u00D6',
    u'\xA8U': u'\u00DC',
    u'\xA8Y': u'\u0178',
    # More umlaut mess to correct:
    u'\x7fa': u'\u00E4',
    u'\x7fe': u'\u00EB',
    u'\x7fi': u'\u00EF',
    u'\x7fo': u'\u00F6',
    u'\x7fu': u'\u00FC',
    u'\x7fy': u'\u00FF',
    u'\x7fA': u'\u00C4',
    u'\x7fE': u'\u00CB',
    u'\x7fI': u'\u00CF',
    u'\x7fO': u'\u00D6',
    u'\x7fU': u'\u00DC',
    u'\x7fY': u'\u0178',
    u'\x7f a': u'\u00E4',
    u'\x7f e': u'\u00EB',
    u'\x7f i': u'\u00EF',
    u'\x7f o': u'\u00F6',
    u'\x7f u': u'\u00FC',
    u'\x7f y': u'\u00FF',
    u'\x7f A': u'\u00C4',
    u'\x7f E': u'\u00CB',
    u'\x7f I': u'\u00CF',
    u'\x7f O': u'\u00D6',
    u'\x7f U': u'\u00DC',
    u'\x7f Y': u'\u0178',
    # pdftotext: fix accute accent:
    u'\x13a': u'\u00E1',
    u'\x13e': u'\u00E9',
    u'\x13i': u'\u00ED',
    u'\x13o': u'\u00F3',
    u'\x13u': u'\u00FA',
    u'\x13y': u'\u00FD',
    u'\x13A': u'\u00C1',
    u'\x13E': u'\u00C9',
    u'\x13I': u'\u00CD',
    u'\x13ı': u'\u00ED',  # Lower case turkish 'i' (dotless i)
    u'\x13O': u'\u00D3',
    u'\x13U': u'\u00DA',
    u'\x13Y': u'\u00DD',
    u'\x13 a': u'\u00E1',
    u'\x13 e': u'\u00E9',
    u'\x13 i': u'\u00ED',
    u'\x13 o': u'\u00F3',
    u'\x13 u': u'\u00FA',
    u'\x13 y': u'\u00FD',
    u'\x13 A': u'\u00C1',
    u'\x13 E': u'\u00C9',
    u'\x13 I': u'\u00CD',
    u'\x13 ı': u'\u00ED',
    u'\x13 O': u'\u00D3',
    u'\x13 U': u'\u00DA',
    u'\x13 Y': u'\u00DD',
    u'\u00B4 a': u'\u00E1',
    u'\u00B4 e': u'\u00E9',
    u'\u00B4 i': u'\u00ED',
    u'\u00B4 o': u'\u00F3',
    u'\u00B4 u': u'\u00FA',
    u'\u00B4 y': u'\u00FD',
    u'\u00B4 A': u'\u00C1',
    u'\u00B4 E': u'\u00C9',
    u'\u00B4 I': u'\u00CD',
    u'\u00B4 ı': u'\u00ED',
    u'\u00B4 O': u'\u00D3',
    u'\u00B4 U': u'\u00DA',
    u'\u00B4 Y': u'\u00DD',
    u'\u00B4a': u'\u00E1',
    u'\u00B4e': u'\u00E9',
    u'\u00B4i': u'\u00ED',
    u'\u00B4o': u'\u00F3',
    u'\u00B4u': u'\u00FA',
    u'\u00B4y': u'\u00FD',
    u'\u00B4A': u'\u00C1',
    u'\u00B4E': u'\u00C9',
    u'\u00B4I': u'\u00CD',
    u'\u00B4ı': u'\u00ED',
    u'\u00B4O': u'\u00D3',
    u'\u00B4U': u'\u00DA',
    u'\u00B4Y': u'\u00DD',
    # pdftotext: fix grave accent:
    u'\u0060 a': u'\u00E0',
    u'\u0060 e': u'\u00E8',
    u'\u0060 i': u'\u00EC',
    u'\u0060 o': u'\u00F2',
    u'\u0060 u': u'\u00F9',
    u'\u0060 A': u'\u00C0',
    u'\u0060 E': u'\u00C8',
    u'\u0060 I': u'\u00CC',
    u'\u0060 O': u'\u00D2',
    u'\u0060 U': u'\u00D9',
    u'\u0060a': u'\u00E0',
    u'\u0060e': u'\u00E8',
    u'\u0060i': u'\u00EC',
    u'\u0060o': u'\u00F2',
    u'\u0060u': u'\u00F9',
    u'\u0060A': u'\u00C0',
    u'\u0060E': u'\u00C8',
    u'\u0060I': u'\u00CC',
    u'\u0060O': u'\u00D2',
    u'\u0060U': u'\u00D9',
    u'a´': u'á',
    u'i´': u'í',
    u'e´': u'é',
    u'u´': u'ú',
    u'o´': u'ó',
    # \02C7 : caron
    u'\u02C7C': u'\u010C',
    u'\u02C7c': u'\u010D',
    u'\u02C7S': u'\u0160',
    u'\u02C7s': u'\u0161',
    u'\u02C7Z': u'\u017D',
    u'\u02C7z': u'\u017E',
    # \027 : aa (a with ring above)
    u'\u02DAa': u'\u00E5',
    u'\u02DAA': u'\u00C5',
    # \030 : cedilla
    u'\u0327c': u'\u00E7',
    u'\u0327C': u'\u00C7',
    u'¸c': u'ç',
    # \02DC : tilde
    u'\u02DCn': u'\u00F1',
    u'\u02DCN': u'\u00D1',
    u'\u02DCo': u'\u00F5',
    u'\u02DCO': u'\u00D5',
    u'\u02DCa': u'\u00E3',
    u'\u02DCA': u'\u00C3',
    u'\u02DCs': u'\u0303s',  # Combining tilde with 's'
    # Circumflex accent (caret accent)
    u'aˆ': u'â',
    u'iˆ': u'î',
    u'eˆ': u'ê',
    u'uˆ': u'û',
    u'oˆ': u'ô',
    u'ˆa': u'â',
    u'ˆi': u'î',
    u'ˆe': u'ê',
    u'ˆu': u'û',
    u'ˆo': u'ô',
}

UNDESIRABLE_STRING_REPLACEMENTS = [
    (u'\u201c ', '"'),
]


def replace_undesirable_characters(line):
    """
    Replace certain bad characters in a text line.
    @param line: (string) the text line in which bad characters are to
                 be replaced.
    @return: (string) the text line after the bad characters have been
                      replaced.
    """
    # These are separate because we want a particular order
    for bad_string, replacement in UNDESIRABLE_STRING_REPLACEMENTS:
        line = line.replace(bad_string, replacement)

    for bad_char, replacement in UNDESIRABLE_CHAR_REPLACEMENTS.items():
        line = line.replace(bad_char, replacement)

    return line


def _match_lit_author_affiliation(raw_aff, literature_search_object):
    query = Q(
        "nested",
        path="authors",
        query=(
            Q("match", authors__raw_affiliations__value=raw_aff) &
            Q("exists", field="authors.affiliations.value")
        ),
        inner_hits={},
    )
    query_filters = Q("term", _collections="Literature") & Q("term", curated=True)
    result = (
        literature_search_object.query(query)
        .filter(query_filters)
        .highlight("authors.raw_affiliations.value", fragment_size=len(raw_aff))
        .source(["control_number"])
        .params(size=20)
        .execute()
        .hits
    )
    return result


def _clean_up_affiliation_data(affiliations):
    cleaned_affiliations = []
    for aff in affiliations:
        cleaned_affiliations.append(
            {key: val for key, val in aff.items() if key in ["value", "record"]}
        )
    return cleaned_affiliations


def _find_unambiguous_affiliation(result, wf_id):
    for matched_author in result:
        matched_author_data = matched_author.meta.inner_hits.authors.hits[0].to_dict()
        matched_author_raw_affs = matched_author_data["raw_affiliations"]
        matched_author_affs = matched_author_data["affiliations"]
        matched_aff = []
        if len(matched_author_raw_affs) == 1:
            matched_aff = matched_author_affs
        elif len(matched_author_raw_affs) == len(matched_author_affs):
            matched_aff = _extract_matched_aff_from_highlight(
                matched_author.meta.highlight["authors.raw_affiliations.value"],
                matched_author_raw_affs,
                matched_author_affs,
            )
        if matched_aff:
            message = u"Found matching affiliation, literature recid: {lit_recid}, raw_affiliations: {matched_author_raw_affs}, matched affiliations: {matched_aff}".format(
                lit_recid=matched_author["control_number"],
                matched_author_raw_affs=matched_author_raw_affs,
                matched_aff=matched_aff,
            )
            if wf_id:
                message += u" workflow_id: {workflow_id}".format(
                    workflow_id=wf_id
                )
            LOGGER.info(message)
            return _clean_up_affiliation_data(matched_aff)


def _raw_aff_highlight_len(highlighted_raw_aff):
    matches = re.findall(r"<em>(.*?)</em>", highlighted_raw_aff)
    return sum(len(match) for match in matches)


def _extract_matched_aff_from_highlight(
    highlighted_raw_affs, author_raw_affs, author_affs
):
    raw_aff_highlight_lenghts = [
        _raw_aff_highlight_len(raw_aff) for raw_aff in highlighted_raw_affs
    ]
    longest_highlight_idx = raw_aff_highlight_lenghts.index(
        max(raw_aff_highlight_lenghts)
    )
    extracted_raw_aff = re.sub(
        "<em>|</em>", "", highlighted_raw_affs[longest_highlight_idx]
    )
    for raw_aff, aff in zip(author_raw_affs, author_affs):
        if raw_aff["value"] == extracted_raw_aff:
            return [aff]


def normalize_affiliations(data, literature_search_object, **kwargs):
    """
    Normalizes author raw affiliations in literature record.
    Params:
        data (dict): data contaning list of authors with affiliations to normalize
        literature_search_object (elasticsearch_dsl.search.Search): Search request to elasticsearch.

    Returns:
        normalized_affiliations: list containing normalized affiliations for each author
        ambiguous_affiliations: not matched (not normalized) affiliations
    """
    wf_id = kwargs.get('wf_id')
    matched_affiliations = {}
    normalized_affiliations = []
    ambiguous_affiliations = []
    for author in data.get("authors", []):
        author_affiliations = author.get("affiliations", [])
        if author_affiliations:
            normalized_affiliations.append(author_affiliations)
            continue
        raw_affs = get_value(author, "raw_affiliations.value", [])
        for raw_aff in raw_affs:
            if raw_aff in matched_affiliations:
                author_affiliations.extend(matched_affiliations[raw_aff])
                continue
            matched_author_affiliations_hits = _match_lit_author_affiliation(
                raw_aff, literature_search_object
            )
            matched_author_affiliations = _find_unambiguous_affiliation(
                matched_author_affiliations_hits, wf_id
            )
            if matched_author_affiliations:
                matched_affiliations[raw_aff] = matched_author_affiliations
                author_affiliations.extend(matched_author_affiliations)
            else:
                ambiguous_affiliations.append(raw_aff)
        normalized_affiliations.append(dedupe_list(author_affiliations))
    return (
        normalized_affiliations,
        ambiguous_affiliations,
    )
