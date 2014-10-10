#! /usr/bin/env python

import os
import sys
import httplib
import json
import time
from urlparse import urlparse


class SwapCname(object):
    def __init__(self, token, target):
        self.token = token
        self.target = target

    def get_cname(self, app):
        headers = {"Authorization" : "bearer " + self.token}
        conn = httplib.HTTPConnection(self.target)
        conn.request("GET", "/apps/" + app, "", headers)
        response = conn.getresponse()
        data = json.loads(response.read())
        if len(data.get("cname")) == 0:
            return None
        return data.get("cname")

    def remove_cname(self, app, cname):
        headers = {"Authorization" : "bearer " + self.token}
        conn = httplib.HTTPConnection(self.target)
        conn.request("DELETE", "/apps/" + app + '/cname', '{"cname": ' + json.dumps(cname) + '}', headers)
        response = conn.getresponse()
        if response.status != 200:
            return False
        return True

    def set_cname(self, app, cname):
        headers = {"Content-Type" : "application/json", "Authorization" : "bearer " + self.token}
        conn = httplib.HTTPConnection(self.target)
        conn.request("POST", "/apps/" + app + '/cname', '{"cname": ' + json.dumps(cname) + '}', headers)
        response = conn.getresponse()
        if response.status != 200:
            return False
        return True

    def total_units(self, app):
        headers = {"Authorization" : "bearer " + self.token}
        conn = httplib.HTTPConnection(self.target)
        conn.request("GET", "/apps/" + app, "", headers)
        response = conn.getresponse()
        data = json.loads(response.read())
        return len(data.get('units'))

    def remove_units(self, app):
        units = str(self.total_units(app)-1)
        print """
        Removing %s units from %s ...""" % (units, app)

        headers = {"Authorization" : "bearer " + self.token}
        conn = httplib.HTTPConnection(self.target)
        conn.request("DELETE", "/apps/" + app + '/units', units, headers)
        response = conn.getresponse()
        if response.status != 200:
            print "Error removing units from %s. You'll need to remove manually." % app
            return False

        while (self.total_units(app) > 1):
            print "  Waiting for %s units to go down..." % app

            time.sleep(1)
        return True

    def add_units(self, app, current_units):
        units = str(int(current_units) - self.total_units(app))
        print """
        Adding %s units to %s ...""" % (units, app)

        headers = {"Authorization" : "bearer " + self.token}
        conn = httplib.HTTPConnection(self.target)
        conn.request("PUT", "/apps/" + app + '/units', units, headers)
        response = conn.getresponse()
        if response.status != 200:
            print "Error adding units to %s. Aborting..." % app
            return False
        return True

    def swap(self, apps, cname):
        print """
        Changing live application to %s ...""" % apps[1]

        if not self.add_units(apps[1], self.total_units(apps[0])):
            sys.exit()

        if not self.remove_cname(apps[0], cname):
            print "Error removing cname of %s. Aborting..." % apps[0]
            self.remove_units(apps[1])
            sys.exit()

        if self.set_cname(apps[1], cname):
            self.remove_units(apps[0])

            print """
            Application %s is live at %s ...
            """ % (apps[1], ','.join(cname))

        else:
            print "Error adding cname of %s. Aborting..." % apps[1]
            self.set_cname(apps[0], cname)
            self.remove_units(apps[1])


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print """ERROR: wrong number of arguments.

        Usage: tsuru swap-cname app1-name app2-name

        Swap cname between two apps."""
        sys.exit(1)

    token = os.environ['TSURU_TOKEN']
    target = urlparse(os.environ['TSURU_TARGET']).hostname

    swap_cname = SwapCname(token, target)

    app1 = sys.argv[1]
    app2 = sys.argv[2]

    apps = [app1, app2]
    cnames = [swap_cname.get_cname(apps[1]), swap_cname.get_cname(apps[0])]

    #reverse if first is not None
    if cnames[0] is not None:
        cnames.reverse()
        apps.reverse()

    cname = cnames[1]

    swap_cname.swap(apps, cname)
