# ex: set expandtab softtabstop=4 shiftwidth=4: -*- cpy-indent-level: 4; indent-tabs-mode: nil -*-
#
# Copyright (C) 2009,2010  Contributor
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the EU DataGrid Software License.  You should
# have received a copy of the license with this program, and the
# license is published at
# http://eu-datagrid.web.cern.ch/eu-datagrid/license.html.
#
# THE FOLLOWING DISCLAIMER APPLIES TO ALL SOFTWARE CODE AND OTHER
# MATERIALS CONTRIBUTED IN CONNECTION WITH THIS PROGRAM.
#
# THIS SOFTWARE IS LICENSED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE AND ANY WARRANTY OF NON-INFRINGEMENT, ARE
# DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS
# BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY,
# OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT
# OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
# BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE. THIS
# SOFTWARE MAY BE REDISTRIBUTED TO OTHERS ONLY BY EFFECTIVELY USING
# THIS OR ANOTHER EQUIVALENT DISCLAIMER AS WELL AS ANY OTHER LICENSE
# TERMS THAT MAY APPLY.
"""Contains the logic for `aq reconfigure --list`."""


from aquilon.exceptions_ import ArgumentError, NotFoundException
from aquilon.server.broker import BrokerCommand
from aquilon.server.dbwrappers.host import hostname_to_host
from aquilon.aqdb.model import Archetype, Personality, OperatingSystem, Status
from aquilon.server.templates.domain import TemplateDomain
from aquilon.server.locks import lock_queue, CompileKey
from aquilon.server.services import Chooser


class CommandReconfigureList(BrokerCommand):

    required_parameters = ["list"]

    def render(self, session, logger, list, archetype, personality,
               buildstatus, osname, osversion, os, **arguments):
        dbhosts = []
        failed = []
        for host in list.splitlines():
            host = host.strip()
            if not host or host.startswith('#'):
                continue
            try:
                dbhosts.append(hostname_to_host(session, host))
            except NotFoundException, nfe:
                failed.append("%s: %s" % (host, nfe))
            except ArgumentError, ae:
                failed.append("%s: %s" % (host, ae))
        if failed:
            raise ArgumentError("Invalid hosts in list:\n%s" %
                                "\n".join(failed))
        if not dbhosts:
            raise ArgumentError("Empty list.")

        # Check all the parameters up front.
        # Some of these could be more intelligent about defaults
        # (either by checking for unique entries or relying on the list)
        # - starting simple.
        if archetype:
            dbarchetype = Archetype.get_unique(session, archetype, compel=True)
        if personality:
            if not archetype:
                raise ArgumentError("Please specify --archetype for "
                                    "personality %s." % personality)
            dbpersonality = Personality.get_unique(session, name=personality,
                                                   archetype=dbarchetype,
                                                   compel=True)
        if os:
            raise ArgumentError("Please use --osname and --osversion to "
                                "specify a new OS.")
        if osname and not osversion:
            raise ArgumentError("Please specify --osversion for OS %s." %
                                osname)
        if osversion:
            if not osname:
                raise ArgumentError("Please specify --osname to use with "
                                    "OS version %s." % osversion)
            if not archetype:
                raise ArgumentError("Please specify --archetype for OS "
                                    "%s, version %s." % (osname, osversion))
            dbos = OperatingSystem.get_unique(session, name=osname,
                                              version=osversion,
                                              archetype=dbarchetype,
                                              compel=True)
        if buildstatus:
            dbstatus = Status.get_unique(session, buildstatus, compel=True)

        domains = {}
        # Do any final cross-list or dependency checks before entering
        # the Chooser loop.
        for dbhost in dbhosts:
            if dbhost.domain in domains:
                domains[dbhost.domain].append(dbhost)
            else:
                domains[dbhost.domain] = [dbhost]
            if personality and dbhost.cluster and \
               dbhost.cluster.personality != dbpersonality:
                failed.append("%s: Cannot change personality of host "
                              "while it is a member of %s cluster %s" %
                              (dbhost.fqdn, dbhost.cluster.cluster_type,
                               dbhost.cluster.name))
        if failed:
            raise ArgumentError("Cannot modify the following hosts:\n%s" %
                                "\n".join(failed))
        if len(domains) > 1:
            keys = domains.keys()
            domain_sort = lambda x,y: cmp(len(domains[x]), len(domains[y]))
            keys.sort(cmp=domain_sort)
            stats = ["%s hosts in domain %s" %
                     (len(domains[domain]), domain.name) for domain in keys]
            raise ArgumentError("All hosts must be in the same domain:\n%s" %
                                "\n".join(stats))
        dbdomain = domains.keys()[0]

        failed = []
        choosers = []
        for dbhost in dbhosts:
            if personality:
                dbhost.personality = dbpersonality
                session.add(dbhost)
            if osversion:
                dbhost.operating_system = dbos
                session.add(dbhost)
            if buildstatus:
                dbhost.status = dbstatus
                session.add(dbhost)
        session.flush()

        logger.client_info("Verifying service bindings.")
        for dbhost in dbhosts:
            if dbhost.archetype.is_compileable:
                if arguments.get("keepbindings", None):
                    chooser = Chooser(dbhost, logger=logger,
                                      required_only=False)
                else:
                    chooser = Chooser(dbhost, logger=logger,
                                      required_only=True)
                choosers.append(chooser)
                try:
                    chooser.set_required()
                except ArgumentError, e:
                    failed.append(str(e))
        if failed:
            raise ArgumentError("The following hosts failed service "
                                "binding:\n%s" % "\n".join(failed))

        session.flush()
        logger.info("reconfigure_list processing: %s" %
                    ",".join([str(dbhost.fqdn) for dbhost in dbhosts]))

        if not choosers:
            return

        # Optimize so that duplicate service plenaries are not re-written
        templates = set()
        for chooser in choosers:
            # chooser.plenaries is a PlenaryCollection - this flattens
            # that top level.
            templates.update(chooser.plenaries.plenaries)

        # Don't bother locking until every possible check before the
        # actual writing and compile is done.  This will allow for fast
        # turnaround on errors (no need to wait for a lock if there's
        # a missing service map entry or something).
        # The lock must be over at least the domain, but could be over
        # all if (for example) service plenaries need to change.
        key = CompileKey.merge([p.get_write_key() for p in templates] +
                               [CompileKey(domain=dbdomain.name,
                                           logger=logger)])
        try:
            lock_queue.acquire(key)
            logger.client_info("Writing %s plenary templates.", len(templates))
            for template in templates:
                logger.debug("Writing %s", template)
                template.write(locked=True)
            td = TemplateDomain(dbdomain, logger=logger)
            out = td.compile(session, locked=True)
        except:
            logger.client_info("Restoring plenary templates.")
            for template in templates:
                logger.debug("Restoring %s", template)
                template.restore_stash()
            # Okay, cleaned up templates, make sure the caller knows
            # we've aborted so that DB can be appropriately rollback'd.
            raise
        finally:
            lock_queue.release(key)

        return
