import sys
import csv
from collections import defaultdict
import logging


class VlanAssigner(object):

    FORMAT = '%(asctime)-15s %(levelname)s %(message)s'

    PRIMARY_PORT = "1"
    SECONDARY_PORT = "0"
    PRIMARY_FREE = "primary_free"
    PRIMARY_RESERVED = "primary_reserved"
    SECONDARY_FREE = "secondary_free"
    SECONDARY_RESERVED = "secondary_reserved"

    def __init__(self, vlans):

        logging.basicConfig(level=logging.DEBUG,
                            format=self.FORMAT,
                            filename=self.__class__.__name__+'.log',
                            filemode='a'
                            )
        self.logger = logging.getLogger('vlanAssigner')
        self.deviceId_to_port_vlans = defaultdict(lambda: defaultdict(lambda: []))
        self.vlans_file = None
        self.output_file = None
        self._create_files(vlans)
        self._create_hashmap(self.vlans_file)
        self._sort_vlan_pools()

    def __del__(self):

        self.vlans_file.close()
        self.output_file.close()

    def _create_files(self, vlans):
        try:
            self.vlans_file = open(vlans, 'rb')
            self.output_file = open('output.csv', 'w')
            self.output_file.write('request_id,device_id,primary_port,vlan_id'+'\n')
        except IOError as e:
            self.logger.exception('Could not create the files for input/output')
            raise

    def _create_hashmap(self, vlan_file):

        self.logger.info('Constructing the hashmap to hold the vlans')
        vlanReader = csv.reader(vlan_file, delimiter=',')
        _ = next(vlanReader)
        for line in vlanReader:
            device_id, primary_port, vlan_id = line
            vlan_id = int(vlan_id)
            primary_port = int(primary_port)

            if primary_port:
                self.deviceId_to_port_vlans[device_id][self.PRIMARY_FREE].append(vlan_id)
            else:
                self.deviceId_to_port_vlans[device_id][self.SECONDARY_FREE].append(vlan_id)

    def _sort_vlan_pools(self):

        for device_id in self.deviceId_to_port_vlans.keys():
            self.deviceId_to_port_vlans[device_id][self.PRIMARY_FREE].sort()
            self.deviceId_to_port_vlans[device_id][self.PRIMARY_RESERVED].sort()
            self.deviceId_to_port_vlans[device_id][self.SECONDARY_FREE].sort()
            self.deviceId_to_port_vlans[device_id][self.SECONDARY_RESERVED].sort()

    def find_available_port(self, req_id, is_redundant_request=False):

        free_pairs = []

        if is_redundant_request:
            for device_id in self.deviceId_to_port_vlans.iterkeys():
                    common_set = set(self.deviceId_to_port_vlans[device_id][self.PRIMARY_FREE]) & \
                              set(self.deviceId_to_port_vlans[device_id][self.SECONDARY_FREE])
                    if common_set:
                        free_pairs.append((device_id, min(common_set)))
            if free_pairs:
                free_pairs.sort(key=lambda x: (x[1], x[0]))
                device_id, vlan_id = free_pairs[0]
                self.deviceId_to_port_vlans[device_id][self.PRIMARY_FREE].remove(vlan_id)
                self.deviceId_to_port_vlans[device_id][self.SECONDARY_FREE].remove(vlan_id)
                self.deviceId_to_port_vlans[device_id][self.PRIMARY_RESERVED].append(vlan_id)
                self.deviceId_to_port_vlans[device_id][self.SECONDARY_RESERVED].append(vlan_id)
                self.output_file.write(','.join([req_id, device_id, self.SECONDARY_PORT, str(vlan_id)])+'\n')
                self.output_file.write(','.join([req_id, device_id, self.PRIMARY_PORT, str(vlan_id)])+'\n')

            else:
                raise Exception('There is no pair of primary/secondary free port available.')

        else:

            lowest_vlans_per_device = []
            for device_id in self.deviceId_to_port_vlans.iterkeys():
                lowest_vlans_per_device.append((device_id,
                                                self.deviceId_to_port_vlans[device_id][self.PRIMARY_FREE][0])
                                               )
            lowest_vlans_per_device.sort(key=lambda x: (x[1], x[0]))
            device_id, vlan_id = lowest_vlans_per_device[0]
            self.deviceId_to_port_vlans[device_id][self.PRIMARY_FREE].remove(vlan_id)
            self.deviceId_to_port_vlans[device_id][self.PRIMARY_RESERVED].append(vlan_id)
            self.output_file.write(','.join([req_id, device_id, self.PRIMARY_PORT, str(vlan_id)])+'\n')


if __name__ == '__main__':
    import time
    start = time.time()
    vlans = sys.argv[1]
    requests = sys.argv[2]
    assigner = VlanAssigner(vlans)

    requests_reader = csv.reader(open(requests, 'rb'))
    requests_header = next(requests_reader)
    for line in requests_reader:
        req_id, is_redundant = line
        assigner.find_available_port(req_id, int(is_redundant))

    end = time.time()
    print 'Execution took %d' % (end - start)