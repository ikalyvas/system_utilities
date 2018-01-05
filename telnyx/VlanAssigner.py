import sys
import csv
import operator
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
    PRIMARY_FREE = "primary_free"
    PRIMARY_RESERVED = "primary_reserved"
    SECONDARY_FREE = "secondary_free"
    SECONDARY_RESERVED = "secondary_reserved"

    def __init__(self, vlans, requests):
        self.vlans_file = open(vlans, 'rb')
        self.requests_file = open(requests, 'rb')
        self.output_file = open('output.csv','w')
        self.deviceId_to_port_vlans = defaultdict(lambda: defaultdict(lambda: []))
        self.create_hashmap(self.vlans_file)
        self.sort_vlan_pools()

    def create_hashmap(self, vlan_file):
        vlanReader = csv.reader(vlan_file, delimiter=',')
        _ = next(vlanReader)
        for line in vlanReader:
            device_id, primary_port, vlan_id = line
            vlan_obj = VlanId(int(vlan_id))
            device_id = int(device_id)
            primary_port = int(primary_port)

            if primary_port:
                self.deviceId_to_port_vlans[device_id][self.PRIMARY_FREE].append(vlan_obj)
            else:
                self.deviceId_to_port_vlans[device_id][self.SECONDARY_FREE].append(vlan_obj)

    def sort_vlan_pools(self):

        for device_id in self.deviceId_to_port_vlans.keys():
            self.deviceId_to_port_vlans[device_id][self.PRIMARY_FREE].sort(key=operator.attrgetter('vlanId'))
            self.deviceId_to_port_vlans[device_id][self.PRIMARY_RESERVED].sort(key=operator.attrgetter('vlanId'))

            self.deviceId_to_port_vlans[device_id][self.SECONDARY_FREE].sort(key=operator.attrgetter('vlanId'))
            self.deviceId_to_port_vlans[device_id][self.SECONDARY_RESERVED].sort(key=operator.attrgetter('vlanId'))

    def find_available_port(self, req_id, is_redundant_request=False):

        device_ids = sorted(self.deviceId_to_port_vlans.keys())

        if is_redundant_request:
            for device_id in device_ids:
                for vlan_obj in self.deviceId_to_port_vlans[device_id][self.PRIMARY_FREE]:
                    if any(vlan_obj.vlanId == sec_vlan_obj.vlanId for sec_vlan_obj in
                           self.deviceId_to_port_vlans[device_id][self.SECONDARY_FREE]):
                        self.output_file.write(', '.join([req_id, device_id, self.PRIMARY_PORT, vlan_obj.vlanId]))
                        self.output_file.write(', '.join([req_id, device_id, self.SECONDARY_PORT, vlan_obj.vlanId]))
                        return
            else:
                raise Exception("Does not have pair primary/secondary ports for the redundant request")


        else:
            for device_id in device_ids:
                if self.deviceId_to_port_vlans[device_id][self.PRIMARY_FREE]:
                    vlan_obj = self.deviceId_to_port_vlans[device_id][self.PRIMARY_FREE].pop(0)
                    self.deviceId_to_port_vlans[device_id][self.PRIMARY_RESERVED].append(vlan_obj)
                    self.output_file.write(', '.join([req_id, device_id, self.PRIMARY_PORT, vlan_obj.vlanId]))
                    break
            else:
                raise Exception("Does not have a vlan id on a primary port on any device for the non-redundant request")


if __name__ == '__main__':
    vlans = sys.argv[1]
    requests = sys.argv[2]
    assigner = VlanAssigner(vlans, requests)
    print assigner.deviceId_to_port_vlans['3']["secondary"]