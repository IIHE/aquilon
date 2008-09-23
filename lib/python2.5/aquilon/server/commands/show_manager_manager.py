#!/ms/dist/python/PROJ/core/2.5.0/bin/python
# ex: set expandtab softtabstop=4 shiftwidth=4: -*- cpy-indent-level: 4; indent-tabs-mode: nil -*-
# Copyright (C) 2008 Morgan Stanley
#
# This module is part of Aquilon
"""Contains the logic for `aq show manager --manager`."""


from aquilon.server.broker import (add_transaction, az_check, format_results,
                                   BrokerCommand)
from aquilon.server.dbwrappers.system import get_system
from aquilon.aqdb.sy.manager import Manager


class CommandShowManagerManager(BrokerCommand):

    required_parameters = ["manager"]

    @add_transaction
    @az_check
    @format_results
    def render(self, session, manager, **kwargs):
        return get_system(session, manager, Manager, 'Manager')


#if __name__=='__main__':