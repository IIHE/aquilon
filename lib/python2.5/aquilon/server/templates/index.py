
import os
import time
import socket
import xml.etree.ElementTree as ET
from aquilon.server.dbwrappers.service import get_service
from twisted.python import log
from aquilon.server.processes import write_file


CCM_NOTIF = 1
CDB_NOTIF = 2

NOTIFICATION_TYPES = {
        CCM_NOTIF : "ccm",
        CDB_NOTIF : "cdb"
}

try:
    CDPPORT = socket.getservbyname("cdp")
except:
    CDPPORT = 7777

def build_index(config, session, profilesdir, clientNotify=True):
    '''
    Create an index of what profiles are available

    Compare the mtimes of everything in profiledir against
    an index file (profiles-info.xml). Produce a new index
    and send out notifications to "server modules" (as defined
    within the broker configuration). If clientNotify
    is True, then individual notifications are also sent
    to each host. If clientNotify is False, then the server modules
    will still be notified, but there is no processing of the
    individual hosts. Note that the broker has a config option
    send_notifications, which if false will turn off notifications
    unconditionally. Only if the broker config allows will the
    clientNotify be checked.

    '''
    profile_index = "profiles-info.xml"

    old_object_index = {}
    index_path = os.path.join(profilesdir, profile_index)
    if os.path.exists(index_path):
        try:
            tree = ET.parse(index_path)
            for profile in tree.getiterator("profile"):
                if (profile.text and profile.attrib.has_key("mtime")):
                    obj = profile.text.strip()
                    if obj:
                        if obj.endswith(".xml"):
                            obj = obj[:-4]
                        old_object_index[obj] = int(profile.attrib["mtime"])
        except Exception, e:
            log.msg("Error processing %s, continuing: %s" % (index_path, e))

    # object_index ties namespaced files to mtime
    object_index = {}
    # modified_index stores the subset of namespaced names that
    # have changed since the last index. The values are unused.
    modified_index = {}

    for root, _dirs, files in os.walk(profilesdir):
        for profile in files:
            if profile == profile_index:
                continue
            if not profile.endswith(".xml"):
                continue
            obj = os.path.join(root, profile[:-4])
            # Remove the common prefix: our profilesdir, so that the
            # remaining object name is relative to that root (+1 in order
            # to remove the slash separator)
            obj = obj[len(profilesdir)+1:]
            object_index[obj] = os.path.getmtime(
                    os.path.join(root, profile))
            if (old_object_index.has_key(obj) and
                object_index[obj] > old_object_index[obj]):
                modified_index[obj] = object_index[obj]
 
    content = []
    content.append("<?xml version='1.0' encoding='utf-8'?>")
    content.append("<profiles>")
    for obj, mtime in object_index.items():
        content.append("<profile mtime='%d'>%s.xml</profile>"
                % (mtime, obj))
    content.append("</profiles>")

    write_file(index_path, "\n".join(content))

    if config.has_option("broker", "server_notifications"):
        service_modules = {}
        for service in config.get("broker", "server_notifications").split():
            if service.strip():
                try:
                    # service may be unknown
                    srvinfo = get_service(session, service)
                    for instance in srvinfo.instances:
                        for sis in instance.servers:
                            service_modules[sis.system.fqdn] = 1
                except Exception, e:
                    log.msg("failed to lookup up server module %s: %s" % (service, e))
        count = send_notification(CDB_NOTIF, service_modules.keys())
        log.msg("sent %d server notifications" % count)

    if (config.has_option("broker", "client_notifications")
        and config.getboolean("broker", "client_notifications")
        and clientNotify):
        count = send_notification(CCM_NOTIF, modified_index.keys())
        log.msg("sent %d client notifications" % count)

def send_notification(ntype, modified):
    '''send CDP notification messages to a list of hosts.

    This are sent synchronously, but we don't wait (or care) for any
    reply, so it shouldn't be a problem. type should be CCM_NOTIF or CDB_NOTIF.
    'modified' is a dict of object names that may be namespaced. Object
    names that cannot be looked up in DNS are silently ignored.
    Returns the number of notifications that were sent.
    '''

    success = 0
    for obj in modified:
        # We need to clean the name, since it might
        # be namespaced. This (in effect) globalizes
        # all names. Perhaps we might want to do some
        # checks based on the namespace. Not for now.
        (_ns, _sep, host) = obj.rpartition('/')

        try:
            ip = socket.gethostbyname(host)
            packet = NOTIFICATION_TYPES[ntype] + "\0" + str(int(time.time()))
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.sendto(packet, (ip, CDPPORT))
            success = success + 1

        except socket.gaierror:
            # This hostname is unknown, so we silently
            # discard the notification.
            pass

        except Exception, e:
            log.msg("Error notifying %s: %s" % (host, e))

    return success
