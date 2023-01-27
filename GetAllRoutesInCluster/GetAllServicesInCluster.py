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
        cmd = 'oc get services -o name --namespace {} | cut -c 9-'.format(ns)
        output = bash_command_pipe(cmd)
        svcs = output.split("\n")
        if output and len(svcs) > 0:
            print('{}:'.format(ns))
	    counter = 0
            for svc in svcs:
                if svc:
                    cmd = 'oc get services/{} --template={{{{.metadata.name}}}} --ignore-not-found=true --namespace {}'.format(svc, ns)
                    output = bash_command_pipe(cmd)
                    if output and not "jenkins" in output:
                       print(output)
                       counter+=1
            print('Total services in namespace:' + str(counter))
