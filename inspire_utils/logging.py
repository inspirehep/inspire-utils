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

import logging


class StackTraceLogger(object):
    def __init__(self, logger):
        self.logger = logger

    def __getattr__(self, item):
        """Preserve Python logger interface."""
        return getattr(self.logger, item)

    def error(self, message, *args, **kwargs):
        """Log error with stack trace and locals information.

        By default, enables stack trace information in logging messages, so that stacktrace and locals appear in Sentry.
        """
        kwargs.setdefault('extra', {}).setdefault('stack', True)
        return self.logger.error(message, *args, **kwargs)


def getStackTraceLogger(*args, **kwargs):
    """Returns a :class:`StackTrace` logger that wraps a Python logger instance."""
    logger = logging.getLogger(*args, **kwargs)
    return StackTraceLogger(logger)
