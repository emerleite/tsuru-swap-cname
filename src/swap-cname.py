#!/usr/bin/env python

import os
import sys
import httplib
import json

if len(sys.argv) != 3:
  print """ERROR: wrong number of arguments.

Usage: tsuru swap-cname app1-name app2-name

Swap cname between two apps."""
  sys.exit(1)

def get_cname(app):
  headers = {"Authorization" : "bearer " + token}
  conn = httplib.HTTPConnection(target)
  conn.request("GET", "/apps/" + app, "", headers)
  response = conn.getresponse()
  data = json.loads(response.read())
  if len(data.get("cname")) == 0:
    return None
  return data.get("cname")

def remove_cname(app):
  headers = {"Authorization" : "bearer " + token}
  conn = httplib.HTTPConnection(target)
  conn.request("DELETE", "/apps/" + app + '/cname', '', headers)
  response = conn.getresponse()
  if response.status != 200:
    return False
  return True

def set_cname(app, cname):
  headers = {"Content-Type" : "application/json", "Authorization" : "bearer " + token}
  conn = httplib.HTTPConnection(target)
  conn.request("POST", "/apps/" + app + '/cname', '{"cname": "' + cname + '"}', headers)
  response = conn.getresponse()
  if response.status != 200:
    return False
  return True

token = os.environ['TSURU_TOKEN']
target = os.environ['TSURU_TARGET']

app1 = sys.argv[1]
app2 = sys.argv[2]

cname1 = get_cname(app1)
cname2 = get_cname(app1)

apps = [sys.argv[1], sys.argv[2]]
cnames = [get_cname(apps[1]), get_cname(apps[0])]

#reverse if first is not None
if cnames[0] is not None:
  cnames.reverse()
  apps.reverse()

cname = cnames[1]

if not remove_cname(apps[0]):
  print "Error removing cname of %s. Aborting..." % apps[0]
  sys.exit(1)

if set_cname(apps[1], cname):
  print 'app ' + apps[1] + ' is live at ' + cname
else:
  print "Error adding cname of %s. Aborting..." % apps[1]
  set_cname(apps[0], cname)
