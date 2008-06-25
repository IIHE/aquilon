#!/ms/dist/python/PROJ/core/2.5.0/bin/python
# ex: set expandtab softtabstop=4 shiftwidth=4: -*- cpy-indent-level: 4; indent-tabs-mode: nil -*-
# $Header$
# $Change$
# $DateTime$
# $Author$
# Copyright (C) 2008 Morgan Stanley
#
# This module is part of Aquilon
"""Status formatter."""


from aquilon.server.formats.formatters import ObjectFormatter
from aquilon.aqdb.hardware import Status


class StatusFormatter(ObjectFormatter):
    def format_raw(self, status, indent=""):
        details = [ indent + "Status: %s" % status.name ]
        if status.comments:
            details.append(indent + "  Comments: %s" % status.comments)
        return "\n".join(details)

ObjectFormatter.handlers[Status] = StatusFormatter()


#if __name__=='__main__':