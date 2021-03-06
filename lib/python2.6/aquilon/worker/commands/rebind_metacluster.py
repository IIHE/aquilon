# -*- cpy-indent-level: 4; indent-tabs-mode: nil -*-
# ex: set expandtab softtabstop=4 shiftwidth=4:
#
# Copyright (C) 2009,2010,2011,2012,2013  Contributor
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


from aquilon.exceptions_ import ArgumentError
from aquilon.worker.broker import BrokerCommand  # pylint: disable=W0611
from aquilon.aqdb.model import MetaCluster, Cluster
from aquilon.worker.templates.cluster import PlenaryCluster


class CommandRebindMetaCluster(BrokerCommand):

    required_parameters = ["metacluster", "cluster"]

    def render(self, session, logger, metacluster, cluster, **arguments):
        dbcluster = Cluster.get_unique(session, cluster, compel=True)
        dbmetacluster = MetaCluster.get_unique(session, metacluster,
                                               compel=True)
        old_metacluster = None
        if dbcluster.metacluster and dbcluster.metacluster != dbmetacluster:
            if dbcluster.machines:
                raise ArgumentError("Cannot move cluster to a new metacluster "
                                    "while virtual machines are attached.")
            old_metacluster = dbcluster.metacluster
            old_metacluster.members.remove(dbcluster)
            session.expire(dbcluster, ['_metacluster'])
        if not dbcluster.metacluster:
            dbmetacluster.validate_membership(dbcluster)
            dbmetacluster.members.append(dbcluster)

        session.flush()

        plenary = PlenaryCluster(dbcluster, logger=logger)
        plenary.write()

        return
