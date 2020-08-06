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
        cmd = 'oc get routes -o name --namespace {} | cut -c 26-'.format(ns)
        output = bash_command_pipe(cmd)
        routes = output.split("\n")
        if output and len(routes) > 0:
            print('{}:'.format(ns))
            for route in routes:
                if route:
                    cmd = 'oc get route/{} --template={{{{.spec.host}}}} --ignore-not-found=true --namespace {}'.format(route, ns)
                    output = bash_command(cmd)
                    if output and not "jenkins" in output:
                        print(output)
