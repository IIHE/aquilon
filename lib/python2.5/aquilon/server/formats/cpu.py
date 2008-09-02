#!/ms/dist/python/PROJ/core/2.5.0/bin/python
# ex: set expandtab softtabstop=4 shiftwidth=4: -*- cpy-indent-level: 4; indent-tabs-mode: nil -*-
# $Header$
# $Change$
# $DateTime$
# $Author$
# Copyright (C) 2008 Morgan Stanley
#
# This module is part of Aquilon
"""Cpu formatter."""


from aquilon.server.formats.formatters import ObjectFormatter
from aquilon.aqdb.hw.cpu import Cpu


class CpuFormatter(ObjectFormatter):
    def format_raw(self, cpu, indent=""):
        details = [indent + "Cpu: %s %s %d MHz" %
                (cpu.vendor.name, cpu.name, cpu.speed)]
        if cpu.comments:
            details.append(indent + "  Comments: %s" % cpu.comments)
        return "\n".join(details)

ObjectFormatter.handlers[Cpu] = CpuFormatter()


#if __name__=='__main__':