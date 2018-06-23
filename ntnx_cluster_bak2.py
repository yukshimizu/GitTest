############################################################
#
#  Script: Handle Nutanix Cluster via REST API (v2)
#  Author: Yukiya Shimizu
#  Description: Handle Nutanix Cluster
#  Language: Python3
#
############################################################

import pprint
import json
import requests

#V1_BASE_URL = "https://{}:9440/PrismGateway/services/rest/v1/"
V2_BASE_URL = "https://{}:9440/PrismGateway/services/rest/v2.0/"
POST = "post"
GET = "get"
DEBUG = True
NO_CONN = False
DISK_TYPE = ["SCSI", "IDE", "PCI"]
pp = pprint.PrettyPrinter(indent=2)


class NtnxRestApiSession:
    def __init__(self, ip_address, username, password):
        self.cluster_ip_address = ip_address
        self.username = username
        self.password = password
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


class ContainersMenu:
    def __init__(self, ntnx_rest_api):
        self.rest_api = ntnx_rest_api
        self.containers = []

    def sync_containers(self):
        # Sync NTNX storage containers information with the target cluster
        print("Getting containers information of the cluster {}".format(self.rest_api.cluster_ip_address))

        if NO_CONN:
            with open(".\\data\\containers.json", "rt") as fin:
                containers = json.load(fin)
        else:
            rest_status, containers = self.rest_api.rest_call(GET, "storage_containers", None)

        if DEBUG:
            with open(".\\debug\\containers.json", "wt") as fout:
                json.dump(containers, fout, indent=2)

        self.containers = containers.get("entities").copy()

    def get_containers(self):
        # Getter for containers list
        if not self.containers:
            self.sync_containers()

        return self.containers

    def list_containers(self):
        # Print containers list
        print("#" * 79)
        for entity in self.containers:
            print("ContainerUuid: {}".format(entity.get("storage_container_uuid")))
            print("Name: {}".format(entity.get("name")))
            print("Capacity: {}".format(entity.get("max_capacity")))
            print("-" * 79)

    def create_container(self):
        pass

    def show_menu(self):
        while True:
            print("#" * 79)
            print("NTNX Cluster Container Menu")
            print("21:  List Storage Container Information")
            print("22:  Create a New Storage Container")
            print("99:  Return to Main Menu")
            print("#" * 79)
            response = input("Please enter container operation\n")

            if response == "99":
                print("Return to Main Menu")
                break
            elif response == "21":
                self.sync_containers()
                self.list_containers()
                continue
            elif response == "22":
                continue
            else:
                print(response)
                continue
        return


class NetworksMenu:
    def __init__(self, ntnx_rest_api):
        self.rest_api = ntnx_rest_api
        self.networks = []

    def sync_networks(self):
        # Sync NTNX networks information with the target cluster
        print("Getting networks information of the cluster {}".format(self.rest_api.cluster_ip_address))

        if NO_CONN:
            with open(".\\data\\networks.json", "rt") as fin:
                networks = json.load(fin)
        else:
            rest_status, networks = self.rest_api.rest_call(GET, "networks", None)

        if DEBUG:
            with open(".\\debug\\networks.json", "wt") as fout:
                json.dump(networks, fout, indent=2)

        self.networks = networks.get("entities").copy()

    def get_networks(self):
        # Getter for networks list
        if not self.networks:
            self.sync_networks()

        return self.networks

    def list_networks(self):
        # Print networks list
        print("#" * 79)
        for entity in self.networks:
            print("VLAN ID: {}".format(entity.get("vlan_id")))
            print("Name: {}".format(entity.get("name")))
            print("NetworkUuid: {}".format(entity.get("uuid")))
            print("-" * 79)

    def create_network(self):
        pass

    def show_menu(self):
        while True:
            print("#" * 79)
            print("NTNX Cluster Networks Menu")
            print("31:  List Networks Information")
            print("32:  Create a New Network")
            print("99:  Return to Main Menu")
            print("#" * 79)
            response = input("Please enter network operation\n")

            if response == "99":
                print("Return to Main Menu")
                break
            elif response == "31":
                self.sync_networks()
                self.list_networks()
                continue
            elif response == "32":
                continue
            else:
                print(response)
                continue
        return


class VmCreationMenu:
    def __init__(self, ntnx_rest_api):
        self.rest_api = ntnx_rest_api

    def create_vm(self):
        print("#" * 79)
        print("NTNX Cluster VM Creation Menu")
        print("#" * 79)

        # Create a VmConfigDTO and create a VM via REST API
        vm_config_dto = {}
        vm_disks = []
        vm_nics = []

        while True:
            vm_config_dto["name"] = input("Please enter a VM Name:")
            vm_config_dto["num_vcpus"] = int(input("Please enter number of vCPUs for " + vm_config_dto["name"] + ":"))
            vm_config_dto["num_cores_per_vcpu"] = int(input("Please enter number of cores per vCPU:"))
            vm_config_dto["memory_mb"] = int(input("Please enter memory(mb) for " + vm_config_dto["name"] + ":"))

            print("VM Name:" + vm_config_dto["name"])
            print("Number of vCPUs:" + str(vm_config_dto["num_vcpus"]))
            print("Number of cores per vCPU:" + str(vm_config_dto["num_cores_per_vcpu"]))
            print("Memory Size(MB):" + str(vm_config_dto["memory_mb"]))

            response = input("Is it OK? [Y/N]:")
            if response == "Y":
                print("Y")
                break
            else:
                continue

        while True:
            print("Please add disks to the VM")
            vm_disks.append(self.create_vm_disk())

            response = input("Do you add more disks? [Y/N]:")
            if response == "Y":
                print("Y")
                continue
            else:
                break

        vm_config_dto["vm_disks"] = vm_disks

        while True:
            print("Please add NICs to the VM")
            vm_nics.append(self.create_vm_nic())

            response = input("Do you add more NICs? [Y/N]:")
            if response == "Y":
                print("Y")
                continue
            else:
                break

        #vm_config_dto["vm_nics"] = vm_nics

        if DEBUG:
            pp.pprint(vm_config_dto)
            with open(".\\debug\\vm_config_dto.json", "wt") as fout:
                json.dump(vm_config_dto, fout, indent=2)

        if not NO_CONN:
            rest_status, vms = self.rest_api.rest_call(POST, "vms", json.dumps(vm_config_dto))

            if DEBUG:
                with open(".\\debug\\vms.json", "wt") as fout:
                    json.dump(vms, fout, indent=2)

    def create_vm_disk(self):
        # Create a VMDiskDTO and return it
        vm_disk_dto = {}
        vm_disk_address_dto = {}
        vm_disk_create_dto = {}

        while True:
            vm_disk_address_dto["device_bus"] = input("Please enter Disk type [SCSI/IDE/PCI]:")
            if vm_disk_address_dto["device_bus"] not in DISK_TYPE:
                print("Please input [SCSI/IDE/PCI]")
                continue

            if vm_disk_address_dto["device_bus"] == "IDE":
                vm_disk_dto["is_cdrom"] = True
                vm_disk_dto["is_empty"] = True
            else:
                vm_disk_dto["is_cdrom"] = False
                vm_disk_dto["is_empty"] = False

            vm_disk_dto["is_scsi_pass_through"] = False

            print("Device Bus:" + vm_disk_address_dto["device_bus"])
            response = input("Is it OK? [Y/N]:")

            if response == "Y":
                break
            else:
                continue

        # Make user to select ContainerUuid from the list of Container
        while True:
            if vm_disk_address_dto["device_bus"] == "IDE":
                break
            else:
                print("Select a container from following containers' list")
                print("#" * 79)
                containers_dict = {}
                containers_list = ContainersMenu(self.rest_api).get_containers()
                for container in containers_list:
                    containers_dict[container["name"]] = container

                for container_name in containers_dict.keys():
                    print(container_name)

                container_name = input("Please enter a Container Name for placing the VM:")
                disk_size = input("Please enter the size(MB) of disk:")
                container_confirm = input(container_name + " (" + disk_size + " MB)? [Y/N]:")
                if container_confirm == "Y":
                    print(container_name + " is selected")
                    vm_disk_create_dto["storage_container_uuid"] = \
                        containers_dict[container_name].get("storage_container_uuid")
                    vm_disk_create_dto["size"] = int(disk_size)
                    break
                else:
                    continue

        vm_disk_dto["disk_address"] = vm_disk_address_dto
        if vm_disk_address_dto["device_bus"] != "IDE":
            vm_disk_dto["vm_disk_create"] = vm_disk_create_dto

        if DEBUG:
            pp.pprint(vm_disk_dto)

        return vm_disk_dto

    def create_vm_nic(self):
        # Create a VMNicSpecDTO and return it
        vm_nic_spec_dto = {}

        # Make user to select NetworkUuid from the list of Network
        while True:
            print("Select a network from following networks' list")
            print("#" * 79)
            networks_dict = {}
            networks_list = NetworksMenu(self.rest_api).get_networks()
            for network in networks_list:
                networks_dict[network["name"]] = network

            for network_name in networks_dict.keys():
                display_net_address = str(networks_dict[network_name].get("ip_config").get("network_address"))
                print(network_name + ":" + display_net_address)

            network_name = input("Please enter a Container Name for placing VM:")
            network_confirm = input(network_name + "? [Y/N]:")
            if network_confirm == "Y":
                print(network_name + " is selected")
                vm_nic_spec_dto["uuid"] = networks_dict[network_name].get("uuid")
                break
            else:
                continue

        while True:
            vm_nic_spec_dto["request_ip"] = False
            network_confirm = input("Do you want to request IP address?[Y/N]:")
            if network_confirm == "Y":
                request_ip_address = input("Please enter request IP address(xxx.xxx.xxx.xxx):")
                ip_address_confirm = input("IP Address: " + request_ip_address + "\nIs it OK? [Y/N]:")
                if ip_address_confirm == "Y":
                    vm_nic_spec_dto["requested_ip_address"] = request_ip_address
                    vm_nic_spec_dto["request_ip"] = True
                    break
                else:
                    continue
            else:
                break

        if DEBUG:
            pp.pprint(vm_nic_spec_dto)

        return vm_nic_spec_dto


class MainMenu:
    def __init__(self):
        print("Welcome to NTNX Cluster Handler Menu")
        tgt_cluster_ip = input("Please enter the Cluster Virtual IP Address\n")
        tgt_username = input("Please enter username for the cluster\n")
        tgt_password = input("Please enter password for the username\n")
        print("#" * 79)
        print("Cluster IP Address: " + tgt_cluster_ip)
        print("Cluster username/password: " + tgt_username + "/" + ("*" * len(tgt_password)) + "\n")

        self.rest_api = NtnxRestApiSession(tgt_cluster_ip, tgt_username, tgt_password)
        self.cluster = None

    def get_cluster(self):
        # Sync a specific NTNX cluster information with the target cluster and print it out
        print("Getting cluster information of the cluster {}".format(self.rest_api.cluster_ip_address))

        if NO_CONN:
            with open(".\\data\\cluster.json", "rt") as fin:
                self.cluster = json.load(fin)
        else:
            rest_status, self.cluster = self.rest_api.rest_call(GET, "cluster", None)

        if DEBUG:
            with open(".\\debug\\cluster.json", "wt") as fout:
                json.dump(self.cluster, fout, indent=2)

        print("#" * 79)
        print("Name: {}".format(self.cluster.get("name")))
        print("ID: {}".format(self.cluster.get("id")))
        print("Cluster External IP Address: {}".format(self.cluster.get("cluster_external_ipaddress")))
        print("Number of Nodes: {}".format(self.cluster.get("num_nodes")))
        print("Version: {}".format(self.cluster.get("version")))
        print("Hypervisor Types: {}".format(self.cluster.get("hypervisor_types")))

    def invoke_containers_menu(self):
        pass

    def invoke_networks_menu(self):
        pass

    def invoke_vms_menu(self):
        pass

    def invoke_vm_creation_menu(self):
        pass

    def main_loop(self):
        try:
            while True:
                print("#" * 79)
                print("NTNX Cluster Handler Main Menu")
                print("1:  Show Cluster Information")
                print("2:  Storage Container Operation")
                print("3:  Network Operation")
                print("4:  VMs Operation")
                print("5:  Create a VM")
                print("99: Exit Menu")
                print("#" * 79)
                response = input("Please enter cluster operation\n")

                if response == "99":
                    print("NTNX Cluster Handler Exit")
                    break
                elif response == "1":
                    self.get_cluster()
                    continue
                elif response == "2":
                    ContainersMenu(self.rest_api).show_menu()
                    continue
                elif response == "3":
                    NetworksMenu(self.rest_api).show_menu()
                    continue
                elif response == "4":
                    continue
                elif response == "5":
                    VmCreationMenu(self.rest_api).create_vm()
                    continue
                else:
                    print(response)
                    continue

        except Exception as ex:
            print(ex)
            exit(1)


if __name__ == "__main__":
    MainMenu().main_loop()
