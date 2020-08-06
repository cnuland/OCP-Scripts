from jinja2 import Template
import sys

if not len(sys.argv) == 5:
    print "Invalid input, expecting format python CreateProtjectINitCR <team-name> <environment> <cluster> <quota>"
    exit()
team = sys.argv[1]
env = sys.argv[2]
cluster = sys.argv[3]
quota = sys.argv[4]

template = """
apiVersion: redhatcop.redhat.io/v1alpha1
kind: ProjectInitialize
metadata:
  name: {{ team }}-{{ env }}
spec:
  team: {{ team }}
  env: {{ env }}
  cluster: {{ cluster }}
  displayName: "{{ team }} {{ env }}"
  desc: "{{ env }} environment for the {{ team }} application team"
  quotaSize: {{ quota }}"""

filename = "{}-{}.yaml".format(team, env)
Template(template).stream(team=team, env=env, cluster=cluster, quota=quota).dump(filename)