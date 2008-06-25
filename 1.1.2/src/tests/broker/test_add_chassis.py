#!/ms/dist/python/PROJ/core/2.5.0/bin/python
# ex: set expandtab softtabstop=4 shiftwidth=4: -*- cpy-indent-level: 4; indent-tabs-mode: nil -*-
# $Header$
# $Change$
# $DateTime$
# $Author$
# Copyright (C) 2008 Morgan Stanley
#
# This module is part of Aquilon
"""Module for testing the add chassis command."""

import os
import sys
import unittest

if __name__ == "__main__":
    BINDIR = os.path.dirname(os.path.realpath(sys.argv[0]))
    SRCDIR = os.path.join(BINDIR, "..", "..")
    sys.path.append(os.path.join(SRCDIR, "lib", "python2.5"))

from brokertest import TestBrokerCommand


class TestAddChassis(TestBrokerCommand):

    def testaddut3c5(self):
        command = "add chassis --name ut3c5 --rack ut3"
        self.noouttest(command.split(" "))

    def testverifyaddut3c5(self):
        command = "show chassis --name ut3c5"
        out = self.commandtest(command.split(" "))
        self.matchoutput(out, "Chassis: ut3c5", command)

    def testaddut3c1(self):
        command = "add chassis --name ut3c1 --rack ut3"
        self.noouttest(command.split(" "))

    def testverifyaddut3c1(self):
        command = "show chassis --name ut3c1"
        out = self.commandtest(command.split(" "))
        self.matchoutput(out, "Chassis: ut3c1", command)


if __name__=='__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestAddChassis)
    unittest.TextTestRunner(verbosity=2).run(suite)
