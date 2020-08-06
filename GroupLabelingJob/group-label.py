import subprocess
import os
import json

def bash_command_pipe(cmd): 
  ps = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
  return ps.communicate()[0]

def bash_command(cmd): 
  return subprocess.check_output(cmd)

token = os.getenv('TOKEN')
bash_command_pipe('oc login https://kubernetes.default.svc.cluster.local --token="{}" --insecure-skip-tls-verify=true > /dev/null 2>&1'.format(token))
data = bash_command_pipe("oc get cm -n namespace-configuration-operator group-labels -o json | jq -r \".data[]\"")
groups = json.loads(data)
print("Checking labels on Groups:")
for group in groups:
  name = group["name"]
  print(name)
  oc=bash_command_pipe('oc get group {} -o name --ignore-not-found=true | cut -c 25-'.format(name))
  print(oc)
  if oc:
    labels = group["labels"]
    for label in labels:
      print("Checking for label:{}".format(label))
      key = label["key"]
      value = label["value"]
      oc = bash_command_pipe('oc get group {} --template "{{{{ .metadata.labels.{} }}}}"'.format(name, key))
      if "<no value>" in str(oc):
        print("Adding labels to group {}".format(name))
        bash_command_pipe('oc label group {} {}={}'.format(name, key, value))