import commands
oc=commands.getstatusoutput('oc get namespaces -o name | cut -c 11-')
namespaces = oc[1].split("\n")
for ns in namespaces:
    if not ns.startswith("openshift") and not ns.startswith("kube") and not ns.startswith("default"):
        oc=commands.getstatusoutput('oc get quota  --ignore-not-found=true --namespace {}'.format(ns))
        if not oc[1]:
            print(ns)