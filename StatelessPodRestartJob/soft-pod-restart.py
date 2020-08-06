import subprocess
import os
import json

def bash_command_pipe(cmd): 
  ps = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
  return ps.communicate()[0]

def bash_command(cmd): 
  return subprocess.check_output(cmd)

token = os.getenv('TOKEN')
namespace = os.getenv('NAMESPACE')
dc = os.getenv('DEPLOYMENT')
bash_command_pipe('oc login https://kubernetes.default.svc.cluster.local --token="{}" --insecure-skip-tls-verify=true > /dev/null 2>&1'.format(token))
data = bash_command_pipe("oc rollout latest {} -n {}".format(dc, namespace))