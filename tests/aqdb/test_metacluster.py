#!/usr/bin/env python2.6
# -*- cpy-indent-level: 4; indent-tabs-mode: nil -*-
# ex: set expandtab softtabstop=4 shiftwidth=4:
#
# Copyright (C) 2009,2010,2013  Contributor
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

""" tests create and delete of a machine through the session """
from utils import load_classpath, add, commit, create

load_classpath()

from aquilon.aqdb.db_factory import DbFactory
from aquilon.aqdb.model import (Building, Personality, Archetype, Cluster,
                                EsxCluster, MetaCluster, MetaClusterMember,
                                Branch)

from sqlalchemy import and_
from sqlalchemy.orm import join
from sqlalchemy.exc import IntegrityError

from nose.tools import raises

db = DbFactory()
sess = db.Session()

CLUSTER_NAME = 'test_esx_cluster'
META_NAME = 'test_meta_cluster'
NUM_CLUSTERS = 30
M2 = 'test_meta_cluster2'
M3 = 'test_meta_cluster3'


def clean_up():
    del_metas()
    del_clusters()


def del_clusters():
    clist = sess.query(Cluster).all()
    if len(clist) > 0:
        for c in clist:
            sess.delete(c)
        commit(sess)
        print 'deleted %s cluster(s)' % (len(clist))


def del_metas():
    mlist = sess.query(MetaCluster).all()
    if len(mlist) > 0:
        print '%s clusters before deleting metas' % (sess.query(Cluster).count())
        for m in mlist:
            sess.delete(m)
        commit(sess)
        print 'deleted %s metaclusters' % (len(mlist))
        print '%s clusters left after deleting metas' % (sess.query(Cluster).count())


def setup():
    clean_up()


def teardown():
    clean_up()


def test_create_clusters():
    np = sess.query(Building).filter_by(name='np').one()
    br = Branch.get_unique(sess, 'ny-prod', compel=True)

    per = sess.query(Personality).select_from(
            join(Archetype, Personality)).filter(
            and_(Archetype.name == 'windows',
                Personality.name == 'generic')).one()

    for i in xrange(NUM_CLUSTERS):
        ec = EsxCluster(name='%s%s' % (CLUSTER_NAME, i),
                        location_constraint=np, branch=br,
                        personality=per, down_hosts_threshold=2)
        add(sess, ec)
    commit(sess)

    ecs = sess.query(EsxCluster).all()
    assert len(ecs) is NUM_CLUSTERS
    print ecs[0]

    assert ecs[0].max_hosts is 8
    print 'esx cluster max hosts = %s' % (ecs[0].max_hosts)


def cluster_factory():
    clusters = sess.query(EsxCluster).all()
    size = len(clusters)
    for cl in clusters:
        yield cl

cl_factory = cluster_factory()


def test_create_metacluster():
    mc = MetaCluster(name=META_NAME)
    create(sess, mc)

    assert mc
    print mc


def test_add_meta_member():
    """ Test adding a cluster to a metacluster and cluster.metacluster """
    mc = MetaCluster.get_unique(sess, META_NAME)
    cl = cl_factory.next()

    mcm = MetaClusterMember(metacluster=mc, cluster=cl)
    create(sess, mcm)

    assert mcm
    assert len(mc.members) is 1
    print 'metacluster members %s' % (mc.members)

    assert cl.metacluster is mc
    print cl.metacluster


@raises(ValueError)
def test_add_too_many_metacluster_members():
    cl2 = cl_factory.next()
    cl3 = cl_factory.next()
    assert cl2
    assert cl3

    mc = MetaCluster.get_unique(sess, META_NAME)
    mcm2 = MetaClusterMember(metacluster=mc, cluster=cl2)
    create(sess, mcm2)
    assert mcm2

    mcm3 = MetaClusterMember(metacluster=mc, cluster=cl3)
    create(sess, mcm3)
    assert mcm3


@raises(IntegrityError, AssertionError)
def test_two_metaclusters():
    """ Test unique constraint against cluster """
    m2 = MetaCluster(name=M2)
    m3 = MetaCluster(name=M3)
    sess.add_all([m2, m3])
    commit(sess)
    assert m2, 'metacluster %s not created ' % m2
    assert m3, 'metacluster %s not created ' % m3

    cl4 = cl_factory.next()
    assert cl4

    mcm1 = MetaClusterMember(metacluster=m2, cluster=cl4)
    create(sess, mcm1)
    assert mcm1

    mcm2 = MetaClusterMember(metacluster=m3, cluster=cl4)
    create(sess, mcm1)
    assert mcm2


def test_append():
    mc = MetaCluster.get_unique(sess, M3)
    assert mc, 'no metacluster in test_append'
    assert len(mc.members) is 0
    print '%s before append test has members %s' % (mc, mc.members)

    cl5 = cl_factory.next()
    assert cl5
    print cl5

    mc.members.append(cl5)
    commit(sess)
    assert len(mc.members) is 1
    print 'members now %s' % (mc.members)


if __name__ == "__main__":
    import nose
    nose.runmodule()
