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
    "\u2028": "",
    "\u2029": "",
    "\u202A": "",
    "\u202B": "",
    "\u202C": "",
    "\u202D": "",
    "\u202E": "",
    "\u206A": "",
    "\u206B": "",
    "\u206C": "",
    "\u206D": "",
    "\u206E": "",
    "\u206F": "",
    "\uFFF9": "",
    "\uFFFA": "",
    "\uFFFB": "",
    "\uFFFC": "",
    "\uFEFF": "",
    # Remove the result of a bad UTF-8 character
    "\uFFFF": "",
    # Language Tag Code Points:
    "\U000E0000": "",
    "\U000E0001": "",
    "\U000E0002": "",
    "\U000E0003": "",
    "\U000E0004": "",
    "\U000E0005": "",
    "\U000E0006": "",
    "\U000E0007": "",
    "\U000E0008": "",
    "\U000E0009": "",
    "\U000E000A": "",
    "\U000E000B": "",
    "\U000E000C": "",
    "\U000E000D": "",
    "\U000E000E": "",
    "\U000E000F": "",
    "\U000E0010": "",
    "\U000E0011": "",
    "\U000E0012": "",
    "\U000E0013": "",
    "\U000E0014": "",
    "\U000E0015": "",
    "\U000E0016": "",
    "\U000E0017": "",
    "\U000E0018": "",
    "\U000E0019": "",
    "\U000E001A": "",
    "\U000E001B": "",
    "\U000E001C": "",
    "\U000E001D": "",
    "\U000E001E": "",
    "\U000E001F": "",
    "\U000E0020": "",
    "\U000E0021": "",
    "\U000E0022": "",
    "\U000E0023": "",
    "\U000E0024": "",
    "\U000E0025": "",
    "\U000E0026": "",
    "\U000E0027": "",
    "\U000E0028": "",
    "\U000E0029": "",
    "\U000E002A": "",
    "\U000E002B": "",
    "\U000E002C": "",
    "\U000E002D": "",
    "\U000E002E": "",
    "\U000E002F": "",
    "\U000E0030": "",
    "\U000E0031": "",
    "\U000E0032": "",
    "\U000E0033": "",
    "\U000E0034": "",
    "\U000E0035": "",
    "\U000E0036": "",
    "\U000E0037": "",
    "\U000E0038": "",
    "\U000E0039": "",
    "\U000E003A": "",
    "\U000E003B": "",
    "\U000E003C": "",
    "\U000E003D": "",
    "\U000E003E": "",
    "\U000E003F": "",
    "\U000E0040": "",
    "\U000E0041": "",
    "\U000E0042": "",
    "\U000E0043": "",
    "\U000E0044": "",
    "\U000E0045": "",
    "\U000E0046": "",
    "\U000E0047": "",
    "\U000E0048": "",
    "\U000E0049": "",
    "\U000E004A": "",
    "\U000E004B": "",
    "\U000E004C": "",
    "\U000E004D": "",
    "\U000E004E": "",
    "\U000E004F": "",
    "\U000E0050": "",
    "\U000E0051": "",
    "\U000E0052": "",
    "\U000E0053": "",
    "\U000E0054": "",
    "\U000E0055": "",
    "\U000E0056": "",
    "\U000E0057": "",
    "\U000E0058": "",
    "\U000E0059": "",
    "\U000E005A": "",
    "\U000E005B": "",
    "\U000E005C": "",
    "\U000E005D": "",
    "\U000E005E": "",
    "\U000E005F": "",
    "\U000E0060": "",
    "\U000E0061": "",
    "\U000E0062": "",
    "\U000E0063": "",
    "\U000E0064": "",
    "\U000E0065": "",
    "\U000E0066": "",
    "\U000E0067": "",
    "\U000E0068": "",
    "\U000E0069": "",
    "\U000E006A": "",
    "\U000E006B": "",
    "\U000E006C": "",
    "\U000E006D": "",
    "\U000E006E": "",
    "\U000E006F": "",
    "\U000E0070": "",
    "\U000E0071": "",
    "\U000E0072": "",
    "\U000E0073": "",
    "\U000E0074": "",
    "\U000E0075": "",
    "\U000E0076": "",
    "\U000E0077": "",
    "\U000E0078": "",
    "\U000E0079": "",
    "\U000E007A": "",
    "\U000E007B": "",
    "\U000E007C": "",
    "\U000E007D": "",
    "\U000E007E": "",
    "\U000E007F": "",
    # Musical Notation Scoping
    "\U0001D173": "",
    "\U0001D174": "",
    "\U0001D175": "",
    "\U0001D176": "",
    "\U0001D177": "",
    "\U0001D178": "",
    "\U0001D179": "",
    "\U0001D17A": "",
    "\u0000": "",  # NULL
    "\u0001": "",  # START OF HEADING
    # START OF TEXT & END OF TEXT:
    "\u0002": "",
    "\u0003": "",
    "\u0004": "",  # END OF TRANSMISSION
    # ENQ and ACK
    "\u0005": "",
    "\u0006": "",
    "\u0007": "",  # BELL
    "\u0008": "",  # BACKSPACE
    # SHIFT-IN & SHIFT-OUT
    "\u000E": "",
    "\u000F": "",
    # Other controls:
    "\u0010": "",  # DATA LINK ESCAPE
    "\u0011": "",  # DEVICE CONTROL ONE
    "\u0012": "",  # DEVICE CONTROL TWO
    "\u0013": "",  # DEVICE CONTROL THREE
    "\u0014": "",  # DEVICE CONTROL FOUR
    "\u0015": "",  # NEGATIVE ACK
    "\u0016": "",  # SYNCRONOUS IDLE
    "\u0017": "",  # END OF TRANSMISSION BLOCK
    "\u0018": "",  # CANCEL
    "\u0019": "",  # END OF MEDIUM
    "\u001A": "",  # SUBSTITUTE
    "\u001B": "",  # ESCAPE
    "\u001C": "",  # INFORMATION SEPARATOR FOUR (file separator)
    "\u001D": "",  # INFORMATION SEPARATOR THREE (group separator)
    "\u001E": "",  # INFORMATION SEPARATOR TWO (record separator)
    "\u001F": "",  # INFORMATION SEPARATOR ONE (unit separator)
    # \r -> remove it
    "\r": "",
    # Some ff from tex:
    "\u0013\u0010": "\u00ED",
    "\x0b": "ff",
    # fi from tex:
    "\x0c": "fi",
    # ligatures from TeX:
    "\ufb00": "ff",
    "\ufb01": "fi",
    "\ufb02": "fl",
    "\ufb03": "ffi",
    "\ufb04": "ffl",
    # Superscripts from TeX
    "\u2212": "-",
    "\u2013": "-",
    # Word style speech marks:
    "\u201c ": '"',
    "\u201d": '"',
    "\u201c": '"',
    # pdftotext has problems with umlaut and prints it as diaeresis
    # followed by a letter:correct it
    # (Optional space between char and letter - fixes broken
    # line examples)
    "\u00A8 a": "\u00E4",
    "\u00A8 e": "\u00EB",
    "\u00A8 i": "\u00EF",
    "\u00A8 o": "\u00F6",
    "\u00A8 u": "\u00FC",
    "\u00A8 y": "\u00FF",
    "\u00A8 A": "\u00C4",
    "\u00A8 E": "\u00CB",
    "\u00A8 I": "\u00CF",
    "\u00A8 O": "\u00D6",
    "\u00A8 U": "\u00DC",
    "\u00A8 Y": "\u0178",
    "\xA8a": "\u00E4",
    "\xA8e": "\u00EB",
    "\xA8i": "\u00EF",
    "\xA8o": "\u00F6",
    "\xA8u": "\u00FC",
    "\xA8y": "\u00FF",
    "\xA8A": "\u00C4",
    "\xA8E": "\u00CB",
    "\xA8I": "\u00CF",
    "\xA8O": "\u00D6",
    "\xA8U": "\u00DC",
    "\xA8Y": "\u0178",
    # More umlaut mess to correct:
    "\x7fa": "\u00E4",
    "\x7fe": "\u00EB",
    "\x7fi": "\u00EF",
    "\x7fo": "\u00F6",
    "\x7fu": "\u00FC",
    "\x7fy": "\u00FF",
    "\x7fA": "\u00C4",
    "\x7fE": "\u00CB",
    "\x7fI": "\u00CF",
    "\x7fO": "\u00D6",
    "\x7fU": "\u00DC",
    "\x7fY": "\u0178",
    "\x7f a": "\u00E4",
    "\x7f e": "\u00EB",
    "\x7f i": "\u00EF",
    "\x7f o": "\u00F6",
    "\x7f u": "\u00FC",
    "\x7f y": "\u00FF",
    "\x7f A": "\u00C4",
    "\x7f E": "\u00CB",
    "\x7f I": "\u00CF",
    "\x7f O": "\u00D6",
    "\x7f U": "\u00DC",
    "\x7f Y": "\u0178",
    # pdftotext: fix accute accent:
    "\x13a": "\u00E1",
    "\x13e": "\u00E9",
    "\x13i": "\u00ED",
    "\x13o": "\u00F3",
    "\x13u": "\u00FA",
    "\x13y": "\u00FD",
    "\x13A": "\u00C1",
    "\x13E": "\u00C9",
    "\x13I": "\u00CD",
    "\x13ı": "\u00ED",  # Lower case turkish 'i' (dotless i)
    "\x13O": "\u00D3",
    "\x13U": "\u00DA",
    "\x13Y": "\u00DD",
    "\x13 a": "\u00E1",
    "\x13 e": "\u00E9",
    "\x13 i": "\u00ED",
    "\x13 o": "\u00F3",
    "\x13 u": "\u00FA",
    "\x13 y": "\u00FD",
    "\x13 A": "\u00C1",
    "\x13 E": "\u00C9",
    "\x13 I": "\u00CD",
    "\x13 ı": "\u00ED",
    "\x13 O": "\u00D3",
    "\x13 U": "\u00DA",
    "\x13 Y": "\u00DD",
    "\u00B4 a": "\u00E1",
    "\u00B4 e": "\u00E9",
    "\u00B4 i": "\u00ED",
    "\u00B4 o": "\u00F3",
    "\u00B4 u": "\u00FA",
    "\u00B4 y": "\u00FD",
    "\u00B4 A": "\u00C1",
    "\u00B4 E": "\u00C9",
    "\u00B4 I": "\u00CD",
    "\u00B4 ı": "\u00ED",
    "\u00B4 O": "\u00D3",
    "\u00B4 U": "\u00DA",
    "\u00B4 Y": "\u00DD",
    "\u00B4a": "\u00E1",
    "\u00B4e": "\u00E9",
    "\u00B4i": "\u00ED",
    "\u00B4o": "\u00F3",
    "\u00B4u": "\u00FA",
    "\u00B4y": "\u00FD",
    "\u00B4A": "\u00C1",
    "\u00B4E": "\u00C9",
    "\u00B4I": "\u00CD",
    "\u00B4ı": "\u00ED",
    "\u00B4O": "\u00D3",
    "\u00B4U": "\u00DA",
    "\u00B4Y": "\u00DD",
    # pdftotext: fix grave accent:
    "\u0060 a": "\u00E0",
    "\u0060 e": "\u00E8",
    "\u0060 i": "\u00EC",
    "\u0060 o": "\u00F2",
    "\u0060 u": "\u00F9",
    "\u0060 A": "\u00C0",
    "\u0060 E": "\u00C8",
    "\u0060 I": "\u00CC",
    "\u0060 O": "\u00D2",
    "\u0060 U": "\u00D9",
    "\u0060a": "\u00E0",
    "\u0060e": "\u00E8",
    "\u0060i": "\u00EC",
    "\u0060o": "\u00F2",
    "\u0060u": "\u00F9",
    "\u0060A": "\u00C0",
    "\u0060E": "\u00C8",
    "\u0060I": "\u00CC",
    "\u0060O": "\u00D2",
    "\u0060U": "\u00D9",
    "a´": "á",
    "i´": "í",
    "e´": "é",
    "u´": "ú",
    "o´": "ó",
    # \02C7 : caron
    "\u02C7C": "\u010C",
    "\u02C7c": "\u010D",
    "\u02C7S": "\u0160",
    "\u02C7s": "\u0161",
    "\u02C7Z": "\u017D",
    "\u02C7z": "\u017E",
    # \027 : aa (a with ring above)
    "\u02DAa": "\u00E5",
    "\u02DAA": "\u00C5",
    # \030 : cedilla
    "\u0327c": "\u00E7",
    "\u0327C": "\u00C7",
    "¸c": "ç",
    # \02DC : tilde
    "\u02DCn": "\u00F1",
    "\u02DCN": "\u00D1",
    "\u02DCo": "\u00F5",
    "\u02DCO": "\u00D5",
    "\u02DCa": "\u00E3",
    "\u02DCA": "\u00C3",
    "\u02DCs": "\u0303s",  # Combining tilde with 's'
    # Circumflex accent (caret accent)
    "aˆ": "â",
    "iˆ": "î",
    "eˆ": "ê",
    "uˆ": "û",
    "oˆ": "ô",
    "ˆa": "â",
    "ˆi": "î",
    "ˆe": "ê",
    "ˆu": "û",
    "ˆo": "ô",
}

UNDESIRABLE_STRING_REPLACEMENTS = [
    ("\u201c ", '"'),
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
