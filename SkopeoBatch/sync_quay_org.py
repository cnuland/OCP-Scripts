#!/usr/bin/env python

import argparse
import json
import requests
import sys
import urllib3
import subprocess
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

######################################################################
# Name: Quay Organization Synchronization Script
# Description: Synchronizes repositories within an organization from a source to target Quay environment
# Prerequisites:
#   * Source and Destination Organization previously created
#   * Quay API Token for Source and Destination
#   * Credentials to pull or push images (if required)
#
# Example:
#  $ ./sync_quay_org.py -sh <source_host> -h <destination_host> -st <source_api_token> -dt <destination_api_token -so <source_organization> -do <destination_organization> -sc <source_registry_credentials> -dc <destination_registry_credentials>
#
#########################################################################


parser = argparse.ArgumentParser(description='Synchronize Quay Organization.')
parser.add_argument("-st", "--source-token",
                    help="Source Quay Token", required=True)
parser.add_argument("-dt", "--destination-token",
                    help="Destination Quay Token", required=True)
parser.add_argument("-sh", "--source-host",
                    help="Source Quay Host", required=True)
parser.add_argument('-sr', '--source-repositories',
                    nargs='+', help="Source Repositories to Limit")
parser.add_argument("-dh", "--destination-host",
                    help="Destination Quay Host", required=True)
parser.add_argument("-sc", "--source-credentials",
                    help="Source Quay Credentials in format <user>:<password>")
parser.add_argument("-dc", "--destination-credentials",
                    help="Destination Quay Credentials in format <user>:<password>")
parser.add_argument("-so", "--source-organization",
                    help="Source Quay Organization", required=True)
parser.add_argument("-do", "--destination-organization",
                    help="Destination Quay Organization", required=True)
args = parser.parse_args()

source_host = args.source_host
destination_host = args.destination_host
source_token = args.source_token
destination_token = args.destination_token
source_organization = args.source_organization
destination_organization = args.destination_organization
source_repositories = args.source_repositories
source_credentials = args.source_credentials
destination_credentials = args.destination_credentials

source_quay_session = requests.Session()
source_quay_session.verify = False
source_quay_session.headers = {
    'Accept': 'application/json',
    'Authorization': 'Bearer {0}'.format(source_token),
}

if source_token is not None:
    source_quay_session.headers['Authorization'] = 'Bearer {0}'.format(
        source_token)

destination_quay_session = requests.Session()
destination_quay_session.verify = False
destination_quay_session.headers = {
    'Accept': 'application/json',
}

if destination_token is not None:
    destination_quay_session.headers['Authorization'] = 'Bearer {0}'.format(
        destination_token)

# Base URL's
source_base_url = "https://{0}/api/v1".format(source_host)
destination_base_url = "https://{0}/api/v1".format(destination_host)

# Validate Source and Destination Organizations
source_org = source_quay_session.get(
    source_base_url + "/organization/{0}".format(source_organization))
# source_org.raise_for_status()

if source_org.status_code != 200:
    print("Error Accessing Source Organization. Status code: {0}".format(
        source_org.status_code))
    sys.exit(1)

destination_org = destination_quay_session.get(
    destination_base_url + "/organization/{0}".format(destination_organization))
# destination_org.raise_for_status()

if destination_org.status_code != 200:
    print("Error Accessing Destination Organization. Status code: {0}".format(
        destination_org.status_code))
    sys.exit(1)

source_org_repositories = source_quay_session.get(
    source_base_url + "/repository?namespace={0}".format(source_organization))
# source_org_repositories.raise_for_status()

if source_org_repositories.status_code != 200:
    print("Error Accessing Source Organization Repositories. Status code: {0}".format(
        source_org.status_code))
    sys.exit(1)

source_repos = {}

for repository in source_org_repositories.json()['repositories']:

    if source_repositories is None or repository['name'] in source_repositories:

        source_repo_tags = source_quay_session.get(
            source_base_url + "/repository/{0}/{1}/tag?onlyActiveTags=true".format(source_organization, repository['name']))
        # source_repo_tags.raise_for_status()

        if source_repo_tags.status_code != 200:
            print("Error Retrieving Tag for {0}. Status code: {1}".format(
                repository['name'], source_org.status_code))
            sys.exit(1)

        tags = [str(t['name']) for t in source_repo_tags.json()['tags']]

        source_repos[repository['name']] = tags

        if source_credentials is not None:
            source_credentials_arg = "--src-creds={0}".format(
                source_credentials)
        else:
            source_credentials_arg = ""

        if destination_credentials is not None:
            destination_credentials_arg = "--dest-creds={0}".format(
                destination_credentials)
        else:
            destination_credentials_arg = ""

        for tag in tags:

            source_image = "{0}/{1}/{2}:{3}".format(
                source_host, source_organization, repository['name'], tag)

            destination_image = "{0}/{1}/{2}:{3}".format(
                destination_host, destination_organization, repository['name'], tag)

            print("\nCopying from {0} to {1}".format(
                source_image, destination_image))

            cmd = ["/bin/bash", "-c", "skopeo copy --src-tls-verify=false --dest-tls-verify=false {0} {1} docker://{2} docker://{3}".format(
                source_credentials_arg, destination_credentials_arg, source_image, destination_image)]

            job = subprocess.Popen(
                cmd,
                shell=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                close_fds=True,
            )

            # Poll process for new output until finished
            stdout = ""
            stderr = ""
            while True:
                stdout_nextline = job.stdout.readline()
                stdout = stdout + stdout_nextline
                stderr_nextline = job.stderr.readline()
                stderr = stderr + stderr_nextline
                if stdout_nextline == "" and stderr_nextline == "" and job.poll() is not None:
                    break
                print("Skopeo [STDERR]: {0}".format(stderr_nextline))
                print("Skopeo [STDOUT]: {0}".format(stdout_nextline))
            job.communicate()

            if job.returncode != 0:
                print("Error Copying Image: Error Code: {0}".format(
                    job.returncode))
                sys.exit(1)
