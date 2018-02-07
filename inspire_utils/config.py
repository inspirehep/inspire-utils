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

"""INSPIRE configuration loader.

Inspired by the Flask configuration loader:
https://github.com/pallets/flask/blob/40745bb338c45498ca19010175f341332ab2eefb/flask/config.py
"""

from __future__ import absolute_import, division, print_function

import os
import six


DEFAULT_CONFIG_PATHS = (
    './var/inspirehep-instance/inspirehep.cfg',
    './inspirehep.cfg',
)


class MalformedConfig(Exception):
    def __init__(self, file_path, cause):
        """Exception to be raised if pased file is invalid.

        Args:
            file_path (string): path to bad config
            cause (string): reason of failure, i.e. what exactly was the
                problem while parsing
        """
        message = six.text_type("Malformed config at {}: {}").format(
            file_path,
            cause
        )
        super(MalformedConfig, self).__init__(message)


class Config(dict):
    def __init__(self, defaults=None):
        super(Config, self).__init__(defaults or {})

    def load_pyfile(self, path):
        """Load python file as config.

        Args:
            path (string): path to the python file
        """
        with open(path) as config_file:
            contents = config_file.read()
            try:
                exec(compile(contents, path, 'exec'), self)
            except Exception as e:
                raise MalformedConfig(path, six.text_type(e))


def load_config(paths=DEFAULT_CONFIG_PATHS):
    """Attempt to load config from paths, in order.

    Args:
        paths (List[string]): list of paths to python files

    Return:
        Config: loaded config
    """
    config = Config()
    for path in paths:
        if os.path.isfile(path):
            config.load_pyfile(path)

    return config
