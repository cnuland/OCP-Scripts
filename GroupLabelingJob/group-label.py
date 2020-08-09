import subprocess
import os
import json
import requests
import sys

session = requests.Session()
session.verify = False
session.headers = {
    'Accept': 'application/json',
}

def bash_command(cmd): 
  ps = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,universal_newlines=True)
  return ps.communicate()[0]

token = bash_command("cat /var/run/secrets/kubernetes.io/serviceaccount/token")
if token is not None:
  session.headers['Authorization'] = 'Bearer {0}'.format(token)

# URL Base
base_url = "https://kubernetes.default.svc.cluster.local/api/v1"
users_base_url = "https://kubernetes.default.svc.cluster.local/apis/user.openshift.io/v1"
namespace = bash_command("cat /var/run/secrets/kubernetes.io/serviceaccount/namespace")
cm = session.get(base_url + "/namespaces/{}/configmaps/group-labels".format(namespace))
cm.raise_for_status()

if cm.status_code != 200:
  print("Failed to get ConfigMap: {}".format(cm.status_code))
  sys.exit(1)

groups = json.loads(cm.json()["data"]["group-labels.json"])
print("Checking labels in Groups:")
for group in groups:
  name = group["name"]
  dest_group = session.get(users_base_url + "/groups/{}".format(name))
  if dest_group.status_code == 200:
    data = dest_group.json()
    labels = group["labels"]
    for label in labels:
      print("Checking for label:{}".format(label))
      key = label["key"]
      value = label["value"]
      found = False
      if "labels" in data["metadata"]:
        for dest_label in data["metadata"]["labels"]:
          if key in dest_label:
            found = True
      if not found:
        session.headers["Content-Type"] = "application/merge-patch+json"
        print("Adding labels to group {}".format(name))
        patch_request = session.patch(url="{}/groups/{}".format(users_base_url, name), data="{{\"metadata\":{{\"labels\":{{\"{key}\":\"{value}\"}}}}}}".format(key=key, value=value))
        if patch_request.status_code != 200:
          print("Error updating labels: Status code: {0}".format(patch_request.status_code))