#!/usr/bin/env python
# Author Christopher J. Nuland
# Modified script created by Andy Block

import argparse
import json
import requests
import sys
import urllib3
import subprocess
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

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
missing_images = {}
found_images = {}

for repository in source_org_repositories.json()['repositories']:

    if source_repositories is None or repository['name'] in source_repositories:

        source_repo_tags = source_quay_session.get(
            source_base_url + "/repository/{0}/{1}/tag?onlyActiveTags=true".format(source_organization, repository['name']))
        # source_repo_tags.raise_for_status()

        if source_repo_tags.status_code != 200:
            print("Error finding repository {0} on source. Status code: {1}".format(
                repository['name'], source_org.status_code))
            continue

	dest_repo_tags = destination_quay_session.get(                                                                                                                     
            destination_base_url + "/repository/{0}/{1}/tag?onlyActiveTags=true".format(destination_organization, repository['name']))
        # source_repo_tags.raise_for_status()
                                                                                                                                                                        
        if dest_repo_tags.status_code != 200:
            print("Error finding repository {0} on destination. Status code: {1}".format(
                repository['name'], destination_org.status_code))
            continue

        source_tags = [str(t['name']) for t in source_repo_tags.json()['tags']]
	dest_tags = [str(t['name']) for t in dest_repo_tags.json()['tags']]
        found = []
        missing = []
        for tag in source_tags:
            destination_image = "{0}/{1}/{2}:{3}".format(
                destination_host, destination_organization, repository['name'], tag)
	    if tag in dest_tags:
                found.append(destination_image)
            else:
                missing.append(destination_image)
        found_images.update({"{}".format(repository["name"]):found})
        missing_images.update({"{}".format(repository["name"]):missing})
print("Images Migrated To {0}".format(destination_host))
for repo in found_images:
    images = found_images[repo]
    if images:
        print("Repository:{0}".format(repo))
        for image in images:
            print(image)
    print("\n")
print("\n")
print("Images Failed Migration to {0}".format(destination_host))
for repo in missing_images:
    images = missing_images[repo]
    if images:
        print("Repository:{0}".format(repo))
        for image in images:
            print(image)
    print("\n")
