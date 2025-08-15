import isbnlib
import pytest

from inspire_utils.isbn import normalize_isbn

isbn_ok = {
    '012345672X': '9780123456724',
    '9780387308869': '9780387308869',
    '9780393334777': '9780393334777',
    '9781593273880': '9781593273880',
    '9788478447749': '9788478447749'
}

isbn_nok = [
    'X123456781',
    '012345678X',
    '9780123456780',
    '9780123456781',
    '9790123456780',
    '9790123456781',
    '9890123456781',
    '',
]


@pytest.mark.parametrize(('isbn_input', 'expected'), list(isbn_ok.items()))
def test_normalize_valid(isbn_input, expected):
    normalized = normalize_isbn(isbn_input)
    assert normalized == expected
    assert isbnlib.is_isbn13(normalized)


@pytest.mark.parametrize("isbn_input", isbn_nok)
def test_normalize_invalid(isbn_input):
    normalized = normalize_isbn(isbn_input)
    assert normalized == isbn_input


def test_normalize_with_hyphens():
    isbn_with_hyphens = "978-0-387-30886-9"
    expected = "9780387308869"
    normalized = normalize_isbn(isbn_with_hyphens)
    assert normalized == expected


def test_normalize_with_spaces():
    isbn_with_spaces = "978 0 393 33477 7"
    expected = "9780393334777"
    normalized = normalize_isbn(isbn_with_spaces)
    assert normalized == expected


def test_normalize_lowercase():
    isbn_lowercase = "012345672x"
    expected = "9780123456724"
    normalized = normalize_isbn(isbn_lowercase)
    assert normalized == expected


def test_normalize_empty_string():
    isbn_empty = ""
    normalized = normalize_isbn(isbn_empty)
    assert normalized == isbn_empty
