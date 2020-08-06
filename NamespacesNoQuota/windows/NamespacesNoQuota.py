import subprocess

def bash_command_pipe(cmd): 
    ps = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    return ps.communicate()[0]

def bash_command(cmd): 
    return subprocess.check_output(cmd)

output = bash_command_pipe("oc get namespaces -o name | cut -c 11-")
namespaces = output.split("\n")
for ns in namespaces:
    if not ns.startswith("openshift") and not ns.startswith("kube") and not ns.startswith("default"):
        if not ns:
            continue
        cmd = 'oc get quota --ignore-not-found=true --namespace {}'.format(ns)
        oc = bash_command(cmd)
        if not oc:
            print(ns)
