# -*- cpy-indent-level: 4; indent-tabs-mode: nil -*-
# ex: set expandtab softtabstop=4 shiftwidth=4:
#
# Copyright (C) 2009,2010,2011,2012,2013,2016  Contributor
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

from aquilon.aqdb.model import MetaCluster
from aquilon.worker.broker import BrokerCommand
from aquilon.worker.commands.del_cluster import del_cluster


class CommandDelMetaCluster(BrokerCommand):
    requires_plenaries = True

    required_parameters = ["metacluster"]

    def render(self, session, logger, plenaries, metacluster, **_):
        dbmetacluster = MetaCluster.get_unique(session, metacluster,
                                               compel=True)
        del_cluster(session, logger, plenaries, dbmetacluster, self.config)
