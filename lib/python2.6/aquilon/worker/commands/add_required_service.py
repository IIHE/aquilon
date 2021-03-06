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
"""Contains the logic for `aq add required service`."""


from aquilon.exceptions_ import ArgumentError, AuthorizationException
from aquilon.aqdb.model import Archetype, Service
from aquilon.worker.broker import BrokerCommand  # pylint: disable=W0611
from aquilon.worker.commands.deploy import validate_justification


class CommandAddRequiredService(BrokerCommand):

    required_parameters = ["service", "archetype"]

    def render(self, session, service, archetype, justification, user,
               **arguments):
        if not justification:
            raise AuthorizationException("Changing the required services of "
                                         "an archetype requires "
                                         "--justification.")
        validate_justification(user, justification)
        dbarchetype = Archetype.get_unique(session, archetype, compel=True)
        dbservice = Service.get_unique(session, name=service, compel=True)
        if dbarchetype in dbservice.archetypes:
            raise ArgumentError("Service %s is already required by archetype "
                                "%s" % (service, archetype))
        dbservice.archetypes.append(dbarchetype)
        return
