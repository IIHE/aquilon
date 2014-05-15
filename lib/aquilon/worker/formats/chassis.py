# -*- cpy-indent-level: 4; indent-tabs-mode: nil -*-
# ex: set expandtab softtabstop=4 shiftwidth=4:
#
# Copyright (C) 2008,2009,2010,2011,2013,2014  Contributor
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
"""Chassis formatter."""

from aquilon.aqdb.model import Chassis
from aquilon.worker.formats.formatters import ObjectFormatter
from aquilon.worker.formats.hardware_entity import HardwareEntityFormatter


class ChassisFormatter(HardwareEntityFormatter):
    def format_raw(self, chassis, indent=""):
        details = [super(ChassisFormatter, self).format_raw(chassis, indent)]

        for slot in chassis.slots:
            if slot.machine:
                details.append(indent + "  Slot #%d: %s" % (slot.slot_number,
                                                            slot.machine.label))
            else:
                details.append(indent + "  Slot #%d Unknown" % slot.slot_number)

        return "\n".join(details)

ObjectFormatter.handlers[Chassis] = ChassisFormatter()
