# -*- cpy-indent-level: 4; indent-tabs-mode: nil -*-
# ex: set expandtab softtabstop=4 shiftwidth=4:
#
# Copyright (C) 2008,2009,2010,2011,2013,2015  Contributor
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
"""Contains the logic for `aq search hardware`."""

from sqlalchemy.orm import subqueryload, joinedload, undefer

from aquilon.aqdb.model import HardwareEntity
from aquilon.worker.broker import BrokerCommand  # pylint: disable=W0611
from aquilon.worker.dbwrappers.hardware_entity import (
    search_hardware_entity_query)
from aquilon.worker.formats.list import StringAttributeList


class CommandSearchHardware(BrokerCommand):

    required_parameters = []

    def render(self, session, fullinfo, style, **arguments):
        if fullinfo or style != "raw":
            q = search_hardware_entity_query(session, HardwareEntity, **arguments)
            q = q.options(undefer('comments'),
                          subqueryload('host'),
                          undefer('host.comments'),
                          joinedload('host.personality_stage'),
                          joinedload('location'),
                          subqueryload('interfaces'),
                          joinedload('interfaces.assignments'),
                          joinedload('interfaces.assignments.dns_records'))
            return q.all()
        else:
            q = search_hardware_entity_query(session, HardwareEntity.label, **arguments)
            return StringAttributeList(q.all(), "label")
