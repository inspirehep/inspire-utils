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

"""ORCID configuration loader."""

from __future__ import absolute_import, division, print_function


def test_config(monkeypatch, tmpdir):
    mock_config = tmpdir.join("inspirehep.cfg")
    mock_config.write("SERVER_NAME = '0.0.0.0'; OTHER_VARIABLE = 42")

    from inspire_utils.config import Config

    config = Config(defaults={
        'SERVER_NAME': '127.0.0.1',
        'SOME_OTHER_DEFAULT': 1234,
    })
    config.load_pyfile(mock_config.strpath)

    assert config['SERVER_NAME'] == '0.0.0.0'
    assert config['OTHER_VARIABLE'] == 42
    assert config.get('SOME_OTHER_DEFAULT') == 1234
    assert config.get('NO_SUCH_VARIABLE', 'empty') == 'empty'
