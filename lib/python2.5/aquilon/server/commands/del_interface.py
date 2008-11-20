#!/ms/dist/python/PROJ/core/2.5.0/bin/python
# ex: set expandtab softtabstop=4 shiftwidth=4: -*- cpy-indent-level: 4; indent-tabs-mode: nil -*-
# Copyright (C) 2008 Morgan Stanley
#
# This module is part of Aquilon
"""Contains the logic for `aq del interface`."""


from aquilon.exceptions_ import ArgumentError
from aquilon.server.broker import BrokerCommand
from aquilon.server.dbwrappers.interface import get_interface
from aquilon.server.templates.machine import PlenaryMachineInfo


class CommandDelInterface(BrokerCommand):

    required_parameters = []

    def render(self, session, interface, machine, mac, ip, user, **arguments):
        dbinterface = get_interface(session, interface, machine, mac, ip)
        dbmachine = dbinterface.hardware_entity
        if dbmachine.host and dbinterface.bootable:
            raise ArgumentError("Cannot remove the bootable interface from a host.  Use `aq del host --hostname %s` first." % dbmachine.host.fqdn)
        session.delete(dbinterface)
        session.flush()
        session.refresh(dbmachine)

        plenary_info = PlenaryMachineInfo(dbmachine)
        plenary_info.write(self.config.get("broker", "plenarydir"), user)
        return


#if __name__=='__main__':
