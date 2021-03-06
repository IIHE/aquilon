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
"""Module for testing the manage command."""

import unittest

if __name__ == "__main__":
    import utils
    utils.import_depends()

from brokertest import TestBrokerCommand


class TestManage(TestBrokerCommand):

    def testmanageunittest02(self):
        self.verify_buildfiles("unittest", "unittest02.one-nyp.ms.com",
                               want_exist=True)
        user = self.config.get("unittest", "user")
        # we are using --force to bypass checks because the source domain unittest
        # latest commit does not exist in template-king
        self.noouttest(["manage", "--hostname", "unittest02.one-nyp.ms.com",
                        "--sandbox", "%s/changetest1" % user, "--force"])
        self.verify_buildfiles("unittest", "unittest02.one-nyp.ms.com",
                               want_exist=False)
        command = ["cat", "--hostname", "unittest02.one-nyp.ms.com"]
        out = self.commandtest(command)
        self.matchoutput(out, '"/metadata/template/branch/name" = "changetest1";', command)
        self.matchoutput(out, '"/metadata/template/branch/type" = "sandbox";', command)
        self.matchoutput(out, '"/metadata/template/branch/author" = "%s";' % user, command)

    def testmanageunittest02B(self):
        user = self.config.get("unittest", "user")
        # we are using --force to bypass checks because the source domain unittest
        # latest commit does not exist in template-king
        self.noouttest(["manage", "--hostname", "unittest02.one-nyp.ms.com",
                        "--sandbox", "%s/changetest1" % user, "--force"])
        self.verify_buildfiles("unittest", "unittest02.one-nyp.ms.com",
                               want_exist=False)
        command = ["cat", "--hostname", "unittest02.one-nyp.ms.com"]
        out = self.commandtest(command)
        self.matchoutput(out, '"/metadata/template/branch/name" = "changetest1";', command)
        self.matchoutput(out, '"/metadata/template/branch/type" = "sandbox";', command)
        self.matchoutput(out, '"/metadata/template/branch/author" = "%s";' % user, command)

    def testfailmanageunittest02(self):
        command = ["manage", "--hostname", "unittest02.one-nyp.ms.com",
                   "--domain", "nomanage"]
        out = self.badrequesttest(command)
        self.matchoutput(out, "Managing hosts to domain nomanage is "
                         "not allowed.", command)

    def testverifymanageunittest02(self):
        user = self.config.get("unittest", "user")
        command = "show host --hostname unittest02.one-nyp.ms.com"
        out = self.commandtest(command.split(" "))
        self.matchoutput(out, "Primary Name: unittest02.one-nyp.ms.com", command)
        self.matchoutput(out, "Sandbox: %s/changetest1" % user, command)

    def testmanageserver1(self):
        # we are using --force to bypass checks because the source domain unittest
        # latest commit does not exist in template-king
        self.noouttest(["manage", "--hostname", "server1.aqd-unittest.ms.com",
                        "--domain", "unittest", "--force"])
        command = ["cat", "--hostname", "server1.aqd-unittest.ms.com"]
        out = self.commandtest(command)
        self.matchoutput(out, '"/metadata/template/branch/name" = "unittest";', command)
        self.matchoutput(out, '"/metadata/template/branch/type" = "domain";', command)

    def testverifymanageserver1(self):
        command = "show host --hostname server1.aqd-unittest.ms.com"
        out = self.commandtest(command.split(" "))
        self.matchoutput(out, "Primary Name: server1.aqd-unittest.ms.com", command)
        self.matchoutput(out, "Domain: unittest", command)

    def testverifycleanup(self):
        basedir = self.config.get("broker", "basedir")
        command = [basedir,
                   "-name", "unittest02.one-nyp.ms.com*",
                   "-path", "*/unittest/*"]
        # basedir may contain the string ".../unittest/..."
        out = ["BASEDIR" + name[len(basedir):] for name in
               self.findcommand(command)]
        self.matchclean(" ".join(out), "/unittest/",
                        "find %s" % " ".join(command))

    def testmanageunittest00(self):
        self.verify_buildfiles("unittest", "unittest00.one-nyp.ms.com",
                               want_exist=True)
        user = self.config.get("unittest", "user")
        # we are using --force to bypass checks because the source domain unittest
        # latest commit does not exist in template-king
        self.noouttest(["manage", "--hostname", "unittest00.one-nyp.ms.com",
                        "--sandbox", "%s/changetest2" % user, "--force"])
        self.verify_buildfiles("unittest", "unittest00.one-nyp.ms.com",
                               want_exist=False)

    def testverifymanageunittest00(self):
        user = self.config.get("unittest", "user")
        command = "show host --hostname unittest00.one-nyp.ms.com"
        out = self.commandtest(command.split(" "))
        self.matchoutput(out, "Primary Name: unittest00.one-nyp.ms.com", command)
        self.matchoutput(out, "Sandbox: %s/changetest2" % user, command)

    def testfailmanagevmhost(self):
        user = self.config.get("unittest", "user")
        command = ["manage", "--hostname", "evh1.aqd-unittest.ms.com",
                   "--sandbox", "%s/changetest1" % user]
        out = self.badrequesttest(command)
        self.matchoutput(out,
                         "Cluster nodes must be managed at the cluster level",
                         command)

    def testfailmanageclusterwithmc(self):
        user = self.config.get("unittest", "user")
        # we are using --force to bypass checks because the source domain unittest
        # latest commit does not exist in template-king
        command = ["manage", "--cluster", "utecl1",
                   "--sandbox", "%s/utsandbox" % user, "--force"]
        out = self.badrequesttest(command)
        self.matchoutput(out,
                         "utecl1 is member of metacluster utmc1, it must be "
                         "managed at metacluster level.", command)

    def testmanagemissingcluster(self):
        user = self.config.get("unittest", "user")
        command = ["manage", "--cluster", "cluster-does-not-exist",
                   "--sandbox", "%s/changetest1" % user]
        out = self.notfoundtest(command)
        self.matchoutput(out, "Cluster cluster-does-not-exist not found",
                         command)

    def testmanagecluster(self):
        # To compile, this needs templates from the unittest domain.
        # This test takes advantage of the fact that those templates
        # started in the utsandbox sandbox.
        self.verify_buildfiles("unittest", "clusters/utecl1", want_exist=True)
        command = ["search_host", "--cluster", "utecl1"]
        hosts = self.commandtest(command).splitlines()
        self.failUnless(hosts, "No hosts in cluster utecl1, bad test.")
        for host in hosts:
            self.verify_buildfiles("unittest", host, want_exist=True)
        user = self.config.get("unittest", "user")

        # we want to manage utecl1, but have to do it at metacluster level.
        # we are using --force to bypass checks because the source domain unittest
        # latest commit does not exist in template-king
        command = ["manage", "--cluster", "utmc1",
                   "--sandbox", "%s/utsandbox" % user, "--force"]
        self.noouttest(command)
        self.verify_buildfiles("unittest", "clusters/utecl1", want_exist=False)
        for host in hosts:
            self.verify_buildfiles("unittest", host, want_exist=False)
        command = ["compile", "--sandbox=%s/utsandbox" % user]
        self.successtest(command)
        self.verify_buildfiles("utsandbox", "clusters/utecl1",
                               want_exist=True)
        for host in hosts:
            self.verify_buildfiles("utsandbox", host, want_exist=True)

    def testfailmanagecluster(self):
        command = ["manage", "--cluster", "utecl1", "--domain", "nomanage"]
        out = self.badrequesttest(command)
        self.matchoutput(out, "Managing clusters to domain nomanage is "
                         "not allowed.", command)

    def testverifymanagecluster(self):
        user = self.config.get("unittest", "user")
        command = ["show_esx_cluster", "--cluster=utecl1"]
        out = self.commandtest(command)
        self.matchoutput(out, "Sandbox: %s/utsandbox" % user, command)

        command = ["cat", "--cluster", "utecl1"]
        out = self.commandtest(command)
        self.matchoutput(out, '"/metadata/template/branch/name" = "utsandbox";', command)
        self.matchoutput(out, '"/metadata/template/branch/type" = "sandbox";', command)
        self.matchoutput(out, '"/metadata/template/branch/author" = "%s";' % user, command)

        command = ["search_host", "--cluster=utecl1"]
        out = self.commandtest(command)
        members = out.splitlines()
        members.sort()
        self.failUnless(members, "No hosts in output of %s." % command)

        command = ["search_host", "--cluster=utecl1",
                   "--sandbox=%s/utsandbox" % user]
        out = self.commandtest(command)
        aligned = out.splitlines()
        aligned.sort()
        self.failUnlessEqual(members, aligned,
                             "Not all utecl1 cluster members (%s) are in "
                             "sandbox utsandbox (%s)." % (members, aligned))


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestManage)
    unittest.TextTestRunner(verbosity=2).run(suite)
