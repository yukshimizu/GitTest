############################################################
#
#  Script: Handle Nutanix Cluster via REST API (v1 and v2)
#  Author: Yukiya Shimizu
#  Description: Handle Nutanix Cluster
#  Language: Python3
#
############################################################

import pprint
import json
import requests

V1_BASE_URL = "https://{}:9440/PrismGateway/services/rest/v1/"
V2_BASE_URL = "https://{}:9440/PrismGateway/services/rest/v2.0/"
POST = "post"
GET = "get"
DEBUG = True
NO_CONN = True


class NtnxRestApiSession:
    def __init__(self, ip_address, username, password):
        self.cluster_ip_address = ip_address
        self.username = username
        self.password = password
        self.v1_url = V1_BASE_URL.format(self.cluster_ip_address)
        self.v2_url = V2_BASE_URL.format(self.cluster_ip_address)
        self.session = self.get_server_session()

    def get_server_session(self):
        # Creating REST client session for server connection, after globally setting.
        # Authorization, content type, and character set for the session.
        session = requests.Session()
        session.auth = (self.username, self.password)
        session.verify = False
        session.headers.update(
            {'Content-Type': 'application/json; charset=utf-8'})
        return session

    def rest_call(self, method_type, sub_url, payload_json):
        if method_type == GET:
            request_url = self.v2_url + sub_url
            server_response = self.session.get(request_url)
        elif method_type == POST:
            request_url = self.v2_url + sub_url
            server_response = self.session.post(request_url, payload_json)
        else:
            print("method type is wrong!")
            return

        print("Response code: {}".format(server_response.status_code))
        return server_response.status_code, json.loads(server_response.text)


class VmCreationForm:
    def __init__(self, ntnx_rest_api, ntnx_networks_list, ntnx_containers_list):
        self.f_rest_api = ntnx_rest_api
        self.f_networks_list = ntnx_networks_list
        self.f_containers_list = ntnx_containers_list

    def create_vm(self):

        # Make user to select ContainerUuid from the list of Container
        while True:
            print("Select a container from following containers' list")
            container_dict = {}
            for container in self.f_containers_list.get("entities"):
                container_dict[container["name"]] = container

            for container_name in container_dict.keys():
                print(container_name)

            container_name = input("Please enter a Container Name for placing VM:")
            container_confirm = input(container_name + " [Y/N]")
            if container_confirm == "Y":
                print(container_name + " is selected")
                break
            else:
                continue

        # Make user to select NetworkUuid from the list of Network
        while True:
            print("Select a network from following networks' list")
            network_dict = {}
            for network in self.f_networks_list.get("entities"):
                network_dict[network["name"]] = network

            for network_name in network_dict.keys():
                print(network_name)

            network_name = input("Please enter a Container Name for placing VM:")
            network_confirm = input(network_name + " [Y/N]")
            if network_confirm == "Y":
                print(network_name + " is selected")
                break
            else:
                continue

    def clone_vm(self):
        pass


def show_cluster(ntnx_rest_api):
    # Display a specific NTNX cluster information
    print("Getting cluster information of the cluster {}".format(ntnx_rest_api.cluster_ip_address))

    if NO_CONN:
        with open(".\\data\\clusters.json", "rt") as fin:
            cluster = json.load(fin)
    else:
        rest_status, cluster = ntnx_rest_api.rest_call(GET, "clusters", None)

    if DEBUG:
        with open(".\\debug\\clusters.json", "wt") as fout:
            json.dump(cluster, fout, indent=2)

    print("#" * 79)
    for entity in cluster.get("entities"):
        print("Name: {}".format(entity.get("name")))
        print("ID: {}".format(entity.get("id")))
        print("Cluster External IP Address: {}".format(entity.get("cluster_external_ipaddress")))
        print("Number of Nodes: {}".format(entity.get("num_nodes")))
        print("Version: {}".format(entity.get("version")))
        print("Hypervisor Types: {}".format(entity.get("hypervisor_types")))


def get_containers_list(ntnx_rest_api):
    # List NTNX storage containers
    print("Getting containers information of the cluster {}".format(ntnx_rest_api.cluster_ip_address))

    if NO_CONN:
        with open(".\\data\\containers.json", "rt") as fin:
            containers = json.load(fin)
    else:
        rest_status, containers = ntnx_rest_api.rest_call(GET, "storage_containers", None)

    if DEBUG:
        with open(".\\debug\\containers.json", "wt") as fout:
            json.dump(containers, fout, indent=2)

    print("#" * 79)
    for entity in containers.get("entities"):
        print("ContainerUuid: {}".format(entity.get("storage_container_uuid")))
        print("Name: {}".format(entity.get("name")))
        print("Capacity: {}".format(entity.get("max_capacity")))
        print("-" * 79)
    return containers


def get_networks_list(ntnx_rest_api):
    # List NTNX networks
    print("Getting networks information of the cluster {}".format(ntnx_rest_api.cluster_ip_address))

    if NO_CONN:
        with open(".\\data\\networks.json", "rt") as fin:
            networks = json.load(fin)
    else:
        rest_status, networks = ntnx_rest_api.rest_call(GET, "networks", None)

    if DEBUG:
        with open(".\\debug\\networks.json", "wt") as fout:
            json.dump(networks, fout, indent=2)

    print("#" * 79)
    for entity in networks.get("entities"):
        print("VLAN ID: {}".format(entity.get("vlan_id")))
        print("Name: {}".format(entity.get("name")))
        print("NetworkUuid: {}".format(entity.get("uuid")))
        print("-" * 79)
    return networks


def get_vms_list(ntnx_rest_api):
    # List NTNX vms
    print("Getting VMs list on the cluster {}".format(ntnx_rest_api.cluster_ip_address))

    if NO_CONN:
        with open(".\\data\\vmslist.json", "rt") as fin:
            vms = json.load(fin)
    else:
        rest_status, vms = ntnx_rest_api.rest_call(GET, "vms", None)

    if DEBUG:
        with open(".\\debug\\vmslist.json", "wt") as fout:
            json.dump(vms, fout, indent=2)

    print("#" * 79)
    for entity in vms.get("entities"):
        print("VMuuid: {}".format(entity.get("uuid")))
        print("VMname: {}".format(entity.get("name")))
        print("Number of CPUs: {}".format(entity.get("num_vcpus")))
        print("Memory Capacity(KBytes): {}".format(entity.get("memory_mb")))
        print("Power State: {}".format(entity.get("power_state")))
        print("-" * 79)
    return vms


if __name__ == "__main__":
    try:
        print("Welcome to NTNX Cluster Handler")
        tgt_cluster_ip = input("Please enter the Cluster Virtual IP Address\n")
        tgt_username = input("Please enter username for the cluster\n")
        tgt_password = input("Please enter password for the username\n")
        print("#" * 79)
        print("Cluster IP Address: " + tgt_cluster_ip)
        print("Cluster username/password: " + tgt_username + "/" + ("*" * len(tgt_password)) + "\n")

        rest_api = NtnxRestApiSession(tgt_cluster_ip, tgt_username, tgt_password)

        while True:
            print("#" * 79)
            print("NTNX Cluster Handler Menu")
            print("1:  Show Cluster Information")
            print("2:  List Storage Container Information")
            print("3:  List NW Information")
            print("4:  List VMs Information")
            print("5:  Create a VM")
            print("99: Exit Menu")
            print("#" * 79)
            response = input("Please enter cluster operation\n")

            if response == "99":
                print("NTNX Cluster Handler Exit")
                break
            elif response == "1":
                show_cluster(rest_api)
                continue
            elif response == "2":
                containers_list = get_containers_list(rest_api)
                continue
            elif response == "3":
                networks_list = get_networks_list(rest_api)
                continue
            elif response == "4":
                vms_list = get_vms_list(rest_api)
                continue
            elif response == "5":
                vm_form = VmCreationForm(rest_api, networks_list, containers_list)
                vm_form.create_vm()
            else:
                print(response)
                continue

    except Exception as ex:
        print(ex)
        exit(1)

