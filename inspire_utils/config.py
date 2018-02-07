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

import os


DEFAULT_CONFIG_PATHS = (
    './var/inspirehep-instance/inspirehep.cfg',
    './inspirehep.cfg',
)


class Config(dict):
    def __init__(self, defaults=None):
        super(Config, self).__init__(defaults or {})

    def load_pyfile(self, path):
        """Load python file as config.

        Args:
            path (string): path to the python file
        """
        with open(path) as config_file:
            exec(compile(config_file.read(), path, 'exec'), self)


def load_config(paths=DEFAULT_CONFIG_PATHS):
    config = Config()
    for path in paths:
        if os.path.isfile(path):
            config.load_pyfile(path)

    return config
