#!/ms/dist/python/PROJ/core/2.5.0/bin/python
# ex: set expandtab softtabstop=4 shiftwidth=4: -*- cpy-indent-level: 4; indent-tabs-mode: nil -*-
# Copyright (C) 2008 Morgan Stanley
#
# This module is part of Aquilon
"""Contains the logic for `aq show domain --all`."""


from aquilon.server.broker import BrokerCommand
from aquilon.aqdb.sy.domain import Domain


class CommandShowDomainAll(BrokerCommand):

    def render(self, session, **arguments):
        return session.query(Domain).all()


#if __name__=='__main__':
