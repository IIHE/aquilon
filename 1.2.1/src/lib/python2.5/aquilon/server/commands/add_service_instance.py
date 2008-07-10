#!/ms/dist/python/PROJ/core/2.5.0/bin/python
# ex: set expandtab softtabstop=4 shiftwidth=4: -*- cpy-indent-level: 4; indent-tabs-mode: nil -*-
# $Header$
# $Change$
# $DateTime$
# $Author$
# Copyright (C) 2008 Morgan Stanley
#
# This module is part of Aquilon
"""Contains a wrapper for `aq add service --instance`."""


from aquilon.server.broker import BrokerCommand
from aquilon.server.commands.add_service import CommandAddService


class CommandAddServiceInstance(CommandAddService):
    """ CommandAddService already has all the necessary logic to
        handle the extra instance parameter.

    """

    required_parameters = ["service", "instance"]


#if __name__=='__main__':