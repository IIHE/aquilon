#!/ms/dist/python/PROJ/core/2.5.0/bin/python
# ex: set expandtab softtabstop=4 shiftwidth=4: -*- cpy-indent-level: 4; indent-tabs-mode: nil -*-
# $Header$
# $Change$
# $DateTime$
# $Author$
# Copyright (C) 2008 Morgan Stanley
#
# This module is part of Aquilon
import os

""" we'll be passing this to everything else. Do this first in case other
    modules have imports left over from early stage development. """

from db_factory import db_factory

dbf = db_factory()
print dbf.dsn
from depends import Base
Base.metadata.bind = dbf.engine

from depends import *
from debug import *
from admin import *

import table_maker
import update_dns_domain
import update_user_princ
import add_data

import migrate.changeset

def upgrade():
    ### STEP 1
    # Full export == safety net
    ##CHEATING here, losing patience
    DSN = 'cdb/cdb@LNPO_AQUILON_NY'
    exp = 'exp %s FILE=EXPORT/%s.dmp OWNER=%s DIRECT=n'%(DSN,
                                    dbf.schema, dbf.schema)
    exp += ' consistent=y statistics=none'.upper()

    print "%s"%(exp)
    msg = "\tis this the correct export statement? :"
    if not utils.confirm(prompt=msg, resp=False):
        print 'exiting.'
        sys.exit(1)

    print 'running %s'%(exp)
    rc = 0
    rc = os.system(exp)
    if rc != 0:
        print >>sys.stderr, "Command returned %d, aborting." % rc
        sys.exit(rc)

    ### STEP 2: DROP THE STUFF WE DON'T NEED, other arbitrary sql here.

    # Drop table ip_addr, network table
    d_ip     = 'DROP TABLE IP_ADDR CASCADE CONSTRAINTS'
    d_iseq   = 'DROP SEQUENCE IP_ADDR_ID_SEQ'
    d_net    = 'DROP TABLE NETWORK CASCADE CONSTRAINTS'
    d_nseq   = 'DROP SEQUENCE NETWORK_ID_SEQ'
    d_svc_i  = 'DROP TABLE SERVICE_INSTANCE CASCADE CONSTRAINTS'
    d_svc_sq = 'DROP SEQUENCE SERVICE_INSTANCE_ID_SEQ'
    r_cgf_id = 'ALTER INDEX IX_CFG_PATH_RELATIVE_PATH RENAME TO CFG_PATH_RP_IDX'

    drops = [d_ip, d_iseq, d_net, d_nseq, d_svc_i, d_svc_sq]

    for d in drops:
        debug(d)
        dbf.safe_execute(d)

    # STEP 3: make the new stuff
    table_maker.upgrade(dbf)

    #STEP 4: rename constraints, ignore errors
    constraints.rename_non_null_check_constraints(dbf)

    #Step 5:More sensitive stuff: table surgery to dns_domain and user_principal
    update_dns_domain.upgrade(dbf)
    update_user_princ.upgrade(dbf)

    #STEP 6: populate/repopulate tables (some 'new' tables were in the old schema)
    add_data.upgrade(dbf)

    #REPOPULATE NETWORK!!! got lazy here, due to config and namespace pollution
    print "Don't forget to cd aqdb dir  and run network.py"

#def downgrade():

""" A cheap downgrade script would be
    (1) run drop_tables_and_constraints()
    (2) run import
"""
if __name__ == '__main__':
    upgrade()