""" The hardware package consists of all objects and tables
    that represent physical hardware devices """

import os
import sys

DIR = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, os.path.realpath(os.path.join(DIR, '..', '..', '..')))

from aquilon.aqdb.depends import get_files

__all__ = get_files(DIR)

del os
del sys

# Copyright (C) 2008 Morgan Stanley
# This module is part of Aquilon

# ex: set expandtab softtabstop=4 shiftwidth=4: -*- cpy-indent-level: 4; indent-tabs-mode: nil -*-
