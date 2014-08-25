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

def set_cname(app, cname):
  headers = {"Content-Type" : "application/json", "Authorization" : "bearer " + token}
  conn = httplib.HTTPConnection(target)
  conn.request("POST", "/apps/" + app + '/cname', '{"cname": "' + cname + '"}', headers)
  response = conn.getresponse()

token = os.environ['TSURU_TOKEN']
target = os.environ['TSURU_TARGET']

apps = [sys.argv[1], sys.argv[2]]
cnames = [get_cname(apps[1]), get_cname(apps[0])]

for i,app in enumerate(apps):
  if cnames[i] is not None:
    set_cname(app, cnames[i])
    print 'app ' + app + ' is live at ' + cnames[i]
  else:
    remove_cname(app)
