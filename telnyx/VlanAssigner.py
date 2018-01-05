import sys
import csv
from collections import defaultdict


class VlanId(object):

    def __init__(self, vlanId):
        self.vlanId = vlanId
        self._is_reserved = False

    def reserve_id(self):
        self._is_reserved = True

    def release_id(self):
        self._is_reserved = False

    @property
    def is_reserved(self):
        return self._is_reserved


class VlanAssigner(object):

    PRIMARY_PORT = 1
    SECONDARY_PORT = 0

    def __init__(self, vlans, requests):
        self.vlans_file = open(vlans, 'rb')
        self.requests_file = open(requests, 'rb')
        self.output_file = open('output.csv','w')

        self.deviceId_to_port_vlans = defaultdict(lambda: defaultdict(lambda: []))

        self.create_hashmap(self.vlans_file)

    def create_hashmap(self, vlan_file):
        vlanReader = csv.reader(vlan_file, delimiter=',')
        header = next(vlanReader)
        for line in vlanReader:
            device_id, primary_port, vlan_id = line
            vlan_obj = VlanId(int(vlan_id))

            if primary_port:
                self.deviceId_to_port_vlans[device_id]["primary"].append(vlan_obj)
            else:
                self.deviceId_to_port_vlans[device_id]["secondary"].append(vlan_obj)

    def find_available_port(self, req_id, is_redundant_request=False):

        if is_redundant_request:

        else:
            for device_id in sorted(self.deviceId_to_port_vlans.keys()):
                for vlan_obj in self.deviceId_to_port_vlans[device_id]["primary"]:
                    if vlan_obj.is_reserved:
                        continue
                    else:
                        self.output_file.write(', '.join([req_id, device_id, self.PRIMARY_PORT, vlan_obj.vlanId]))
                        vlan_obj.reserve_id()


    def create_request(self, req_id):

        self.output_file.write()



if __name__ == '__main__':
    vlans = sys.argv[1]
    requests = sys.argv[2]
    assigner = VlanAssigner(vlans, requests)
    print assigner.deviceId_to_port_vlans['3']["secondary"]