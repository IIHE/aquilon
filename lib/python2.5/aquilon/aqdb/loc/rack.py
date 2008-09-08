#!/ms/dist/python/PROJ/core/2.5.0/bin/python
""" Rack is a subclass of Location """


import sys
import os

if __name__ == '__main__':
    DIR = os.path.dirname(os.path.realpath(__file__))
    sys.path.insert(0, os.path.realpath(os.path.join(DIR, '..', '..', '..')))
    import aquilon.aqdb.depends

from sqlalchemy import Column, Integer, Numeric, ForeignKey

from aquilon.aqdb.loc.location import Location, location
from aquilon.aqdb.column_types.aqstr import AqStr

class Rack(Location):
    """ Rack is a subtype of location """
    __tablename__ = 'rack'
    __mapper_args__ = {'polymorphic_identity' : 'rack'}
    id = Column(Integer,
                ForeignKey('location.id', name = 'rack_loc_fk',
                           ondelete = 'CASCADE'), primary_key=True)
    #TODO: POSTHASTE: constrain to alphabetic in row, and make both non-nullable
    rack_row    = Column(AqStr(4), nullable = True)
    rack_column = Column(Integer,  nullable = True)
    
    #vendor      = Column(Integer, ForeignKey(Vendor.c.id, 
        #name = '', nullable = True
        
    #waiting to decide on how to make comp room effective
    #comp_room   = Column(AqStr(16))

rack = Rack.__table__
rack.primary_key.name = 'rack_pk'
table = rack

def populate(db, *args, **kw):

    from aquilon.aqdb.loc.building import Building

    s = db.session()

    rack.create(checkfirst = True)

    if len(s.query(Rack).all()) < 1:
        bldg = {}
        for c in s.query(Building).all():
            bldg[c.name] = c

        for b in bldg.keys():
            nm = '%s1'%(b)
            a = Rack(name = nm, fullname = 'Rack %s'%(nm),
                     parent = bldg[b], comments = 'AutoPopulated')
            s.add(a)

        s.commit()
        print 'created %s racks'%(len(s.query(Rack).all()))


# Copyright (C) 2008 Morgan Stanley
# This module is part of Aquilon

# ex: set expandtab softtabstop=4 shiftwidth=4: -*- cpy-indent-level: 4; indent-tabs-mode: nil -*-

