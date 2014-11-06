# -*- cpy-indent-level: 4; indent-tabs-mode: nil -*-
# ex: set expandtab softtabstop=4 shiftwidth=4:
#
# Copyright (C) 2008,2009,2010,2011,2013  Contributor
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
"""Contains the logic for `aq del personality`."""

from aquilon.exceptions_ import ArgumentError
from aquilon.aqdb.model import Personality, Host, Cluster
from aquilon.worker.broker import BrokerCommand
from aquilon.worker.templates import Plenary


class CommandDelPersonality(BrokerCommand):

    required_parameters = ["personality", "archetype"]

    def render(self, session, logger, personality, archetype, **arguments):
        dbpersona = Personality.get_unique(session, name=personality,
                                           archetype=archetype, compel=True)

        if dbpersona.is_cluster:
            q = session.query(Cluster.id)
        else:
            q = session.query(Host.hardware_entity_id)
        q = q.filter_by(personality_stage=dbpersona)
        if q.count():
            raise ArgumentError("{0} is still in use and cannot be deleted."
                                .format(dbpersona))

        plenary = Plenary.get_plenary(dbpersona, logger=logger)
        session.delete(dbpersona)
        session.flush()
        plenary.remove()

        return
