#!/usr/bin/env python2.6
# -*- cpy-indent-level: 4; indent-tabs-mode: nil -*-
# ex: set expandtab softtabstop=4 shiftwidth=4:
#
# Copyright (C) 2008,2009,2010,2011,2012,2013  Contributor
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Module for testing the search system command."""

import unittest

if __name__ == "__main__":
    import utils
    utils.import_depends()

from brokertest import TestBrokerCommand


class TestSearchSystem(TestBrokerCommand):

    def testfqdnavailable(self):
        command = "search system --fqdn unittest00.one-nyp.ms.com"
        out = self.commandtest(command.split(" "))

    def testfqdnunavailablerealdomain(self):
        command = "search system --fqdn does-not-exist.one-nyp.ms.com"
        self.noouttest(command.split(" "))

    def testfqdnunavailablefakedomain(self):
        command = "search system --fqdn unittest00.does-not-exist.ms.com"
        out = self.notfoundtest(command.split(" "))
        self.matchoutput(out, "DNS Domain does-not-exist.ms.com", command)

#    def testfqdnavailablefull(self):
#        command = "search system --fqdn unittest00.one-nyp.ms.com --fullinfo"
#        out = self.commandtest(command.split(" "))
#        self.matchoutput(out, "Primary Name: unittest00.one-nyp.ms.com", command)
#        self.matchoutput(out, "Blade: ut3c1n3", command)

    def testdnsdomainavailable(self):
        command = "search system --dns_domain aqd-unittest.ms.com"
        out = self.commandtest(command.split(" "))
        self.matchoutput(out, "ut3gd1r01.aqd-unittest.ms.com", command)
        self.matchoutput(out, "ut3c1.aqd-unittest.ms.com", command)
        self.matchoutput(out, "ut3c5.aqd-unittest.ms.com", command)

    def testdnsdomainunavailable(self):
        command = "search system --dns_domain does-not-exist.ms.com"
        out = self.notfoundtest(command.split(" "))
        self.matchoutput(out, "DNS Domain does-not-exist.ms.com not found",
                         command)

    def testshortnameavailable(self):
        command = "search system --shortname unittest00"
        out = self.commandtest(command.split(" "))
        self.matchoutput(out, "unittest00.one-nyp.ms.com", command)

    def testshortnameunavailable(self):
        command = "search system --shortname does-not-exist"
        self.noouttest(command.split(" "))

#   def testtypechassis(self):
#       command = "search system --type chassis"
#       out = self.commandtest(command.split(" "))
#       self.matchoutput(out, "ut3c5.aqd-unittest.ms.com", command)
#       self.matchclean(out, "unittest00.one-nyp.ms.com", command)

#   def testtypetorswitch(self):
#       # Deprecated.
#       command = "search system --type tor_switch"
#       out = self.commandtest(command.split(" "))
#       self.matchoutput(out, "ut3gd1r01.aqd-unittest.ms.com", command)
#       self.matchclean(out, "unittest02.one-nyp.ms.com", command)

    def testipavailable(self):
        command = "search system --ip %s" % self.net.unknown[0].usable[2]
        out = self.commandtest(command.split(" "))
        self.matchoutput(out, "unittest00.one-nyp.ms.com", command)

    def testipunavailable(self):
        command = "search system --ip 199.98.16.4"
        self.noouttest(command.split(" "))

    def testnetworkipavailable(self):
        command = "search system --networkip %s" % self.net.unknown[0].ip
        out = self.commandtest(command.split(" "))
        self.matchoutput(out, "ut3c5.aqd-unittest.ms.com", command)
        self.matchoutput(out, "unittest00.one-nyp.ms.com", command)
        self.matchoutput(out, "unittest00-e1.one-nyp.ms.com", command)
        self.matchoutput(out, "unittest00r.one-nyp.ms.com", command)
        self.matchoutput(out, "unittest01.one-nyp.ms.com", command)
        self.matchoutput(out, "unittest02.one-nyp.ms.com", command)
        self.matchoutput(out, "unittest02rsa.one-nyp.ms.com", command)

    def testnetworkipunavailable(self):
        command = "search system --networkip 199.98.16.0"
        out = self.notfoundtest(command.split(" "))
        self.matchoutput(out, "Network with address 199.98.16.0 not found",
                         command)

#   def testmacavailable(self):
#       command = "search system --mac %s" % self.net.unknown[0].usable[2].mac
#       out = self.commandtest(command.split(" "))
#       self.matchoutput(out, "unittest00.one-nyp.ms.com", command)

#   def testmacunavailable(self):
#       command = "search system --mac 02:02:c7:62:10:04"
#       self.noouttest(command.split(" "))

    def testall(self):
        command = "search system --all"
        out = self.commandtest(command.split(" "))
        # This is a good sampling, but not the full output
        self.matchoutput(out, "unittest00.one-nyp.ms.com", command)
        self.matchoutput(out, "unittest00r.one-nyp.ms.com", command)
        self.matchoutput(out, "unittest00-e1.one-nyp.ms.com", command)
        self.matchoutput(out, "unittest01.one-nyp.ms.com", command)
        self.matchoutput(out, "unittest02.one-nyp.ms.com", command)
        self.matchoutput(out, "unittest02rsa.one-nyp.ms.com", command)
        self.matchoutput(out, self.aurora_with_node, command)
        self.matchoutput(out, self.aurora_without_node, command)
        self.matchoutput(out, "ut3gd1r01.aqd-unittest.ms.com", command)
        self.matchoutput(out, "ut3c1.aqd-unittest.ms.com", command)

#    def testallfull(self):
#        command = "search system --all --fullinfo"
#        out = self.commandtest(command.split(" "))
#        # This is a good sampling, but not the full output
#        self.matchoutput(out, "Blade: ut3c1n3", command)
#        self.matchoutput(out, "Primary Name: unittest00.one-nyp.ms.com", command)
#        self.matchoutput(out, "unittest00r.one-nyp.ms.com", command)
#        self.matchoutput(out, "unittest00-e1.one-nyp.ms.com", command)
#        self.matchoutput(out, "Blade: ut3c1n4", command)
#        self.matchoutput(out, "Primary Name: unittest01.one-nyp.ms.com", command)
#        self.matchoutput(out, "Blade: ut3c5n10", command)
#        self.matchoutput(out, "Primary Name: unittest02.one-nyp.ms.com", command)
#        self.matchoutput(out, "unittest02rsa.one-nyp.ms.com", command)
#        self.matchoutput(out, "Aurora_node: %s" % self.aurora_with_node,
#                         command)
#        self.matchoutput(out, "Primary Name: %s.ms.com" % self.aurora_with_node,
#                         command)
#        self.matchoutput(out, "Aurora_node: %s" % self.aurora_without_node,
#                         command)
#        self.matchoutput(out, "Primary Name: %s.ms.com" % self.aurora_without_node,
#                         command)
#        self.matchoutput(out, "Switch: ut3gd1r01", command)
#        self.matchoutput(out, "Chassis: ut3c1", command)


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestSearchSystem)
    unittest.TextTestRunner(verbosity=2).run(suite)
