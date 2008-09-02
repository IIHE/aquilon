#!/ms/dist/python/PROJ/core/2.5.0/bin/python
# ex: set expandtab softtabstop=4 shiftwidth=4: -*- cpy-indent-level: 4; indent-tabs-mode: nil -*-
# $Header$
# $Change$
# $DateTime$
# $Author$
# Copyright (C) 2008 Morgan Stanley
#
# This module is part of Aquilon
"""Contains the logic for `aq get`."""


from aquilon.server.broker import (format_results, add_transaction, az_check,
                                   BrokerCommand)
from aquilon.server.dbwrappers.domain import verify_domain


class CommandGet(BrokerCommand):

    required_parameters = ["domain"]

    @add_transaction
    @az_check
    def render(self, session, domain, **arguments):
        # Verify that it exists before returning the command to pull.
        dbdomain = verify_domain(session, domain,
                self.config.get("broker", "servername"))
        remote_command = """env PATH="%(path)s:$PATH" NO_PROXY=* git clone '%(url)s/%(domain)s/.git' '%(domain)s' && cd '%(domain)s' && ( env PATH="%(path)s:$PATH" git checkout -b '%(domain)s' || true )""" % {
                "path":self.config.get("broker", "git_path"),
                "url":self.config.get("broker", "git_templates_url"),
                "domain":dbdomain.name}
        return str(remote_command)


#if __name__=='__main__':