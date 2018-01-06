import sys
import csv
import operator
from collections import defaultdict


class Vlan(object):

    def __init__(self, vlanId, deviceId):
        self.vlanId = vlanId
        self.deviceId = deviceId
        self._is_reserved = False

    def reserve_id(self):
        self._is_reserved = True

    def release_id(self):
        self._is_reserved = False

    @property
    def is_reserved(self):
        return self._is_reserved


class VlanAssigner(object):

    PRIMARY_PORT = "1"
    SECONDARY_PORT = "0"
    PRIMARY_FREE = "primary_free"
    PRIMARY_RESERVED = "primary_reserved"
    SECONDARY_FREE = "secondary_free"
    SECONDARY_RESERVED = "secondary_reserved"

    def __init__(self, vlans):
        self.vlans_file = open(vlans, 'rb')
        self.output_file = open('output.csv','w')
        self.output_file.write('request_id,device_id,primary_port,vlan_id'+'\n')
        self.deviceId_to_port_vlans = defaultdict(lambda: defaultdict(lambda: []))
        self.create_hashmap(self.vlans_file)
        self.sort_vlan_pools()

    def create_hashmap(self, vlan_file):

        vlanReader = csv.reader(vlan_file, delimiter=',')
        _ = next(vlanReader)
        for line in vlanReader:
            device_id, primary_port, vlan_id = line
            vlan_obj = Vlan(vlan_id,device_id)
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
                    free_pair = [(vlan_obj,sec_vlan_obj) for sec_vlan_obj in self.deviceId_to_port_vlans[device_id][self.SECONDARY_FREE]
                                  if vlan_obj.vlanId == sec_vlan_obj.vlanId]
                    if free_pair:

                            self.deviceId_to_port_vlans[device_id][self.PRIMARY_FREE].remove(vlan_obj)
                            self.deviceId_to_port_vlans[device_id][self.SECONDARY_FREE].remove(sec_vlan_obj)
                            self.deviceId_to_port_vlans[device_id][self.PRIMARY_RESERVED].append(vlan_obj)
                            self.deviceId_to_port_vlans[device_id][self.SECONDARY_RESERVED].append(sec_vlan_obj)
                            self.output_file.write(', '.join([req_id, device_id, self.PRIMARY_PORT, vlan_obj.vlanId])+'\n')
                            self.output_file.write(', '.join([req_id, device_id, self.SECONDARY_PORT, sec_vlan_obj.vlanId])+'\n')
                            return

            else:
                raise Exception("Does not have pair primary/secondary ports for the redundant request")


        else:

            lowest_vlans_per_device = []
            for device_id in device_ids:
                lowest_vlans_per_device.append(self.deviceId_to_port_vlans[device_id][self.PRIMARY_FREE][0])
            lowest_vlans_per_device.sort(key=operator.attrgetter('vlanId','deviceId'))
            vlan_obj = lowest_vlans_per_device[0]
            self.deviceId_to_port_vlans[vlan_obj.deviceId][self.PRIMARY_FREE].remove(vlan_obj)
            self.deviceId_to_port_vlans[vlan_obj.deviceId][self.PRIMARY_RESERVED].append(vlan_obj)
            self.output_file.write(', '.join([req_id, vlan_obj.deviceId, self.PRIMARY_PORT, vlan_obj.vlanId])+'\n')


if __name__ == '__main__':
    vlans = sys.argv[1]
    requests = sys.argv[2]
    assigner = VlanAssigner(vlans)

    requests_reader = csv.reader(open(requests,'rb'))
    requests_header = next(requests_reader)
    for line in requests_reader:
        req_id , is_redundant = line
        assigner.find_available_port(req_id,int(is_redundant))