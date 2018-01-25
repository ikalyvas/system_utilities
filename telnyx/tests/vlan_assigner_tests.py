import unittest
from mock import MagicMock, patch, mock_open, call
import VlanAssigner

class TestsVlanAssigner(unittest.TestCase):

    def setUp(self):
        self.reader =  [['device_id', 'primary_port', 'vlan_id'],
                  ['0', '1', '2'],
                  ['0', '1', '5'],
                  ['0', '1', '8'],
                  ['0', '0', '2'],
                  ['0', '0', '3'],
                  ['0', '0', '4'],
                  ['0', '0', '6'],
                  ['0', '0', '7'],
                  ['0', '0', '8'],
                  ['0', '0', '1'],
                  ['1', '1', '1'],
                  ['1', '1', '5'],
                  ['1', '1', '6'],
                  ['1', '1', '9'],
                  ['1', '0', '1'],
                  ['1', '0', '4'],
                  ['1', '0', '5'],
                  ['1', '0', '7'],
                  ['2', '1', '1'],
                  ['2', '1', '4'],
                  ['2', '1', '1'],
                  ]

    def tearDown(self):
        pass

    @patch('VlanAssigner.VlanAssigner._create_hashmap')
    @patch('VlanAssigner.open')
    def test_create_files_OK(self, mock_op, mock_create_hash):

        VlanAssigner.VlanAssigner('test_vlans.csv')
        mock_op.assert_has_calls([call('test_vlans.csv', 'rb'),
                                  call('output.csv', 'w')
                                  ])

    @patch('VlanAssigner.VlanAssigner._create_hashmap')
    @patch('VlanAssigner.open')
    def test_create_files_raisesExceptionIfFileHasIssues(self, mock_op, mock_create_hash):

        mock_op.side_effect = IOError('Cannot find file')
        self.assertRaisesRegexp(IOError, 'Cannot find file',
                                VlanAssigner.VlanAssigner, ('test_vlans.csv',))



    @patch('VlanAssigner.open')
    @patch('VlanAssigner.csv')
    def test_create_hashmap_OK(self, mock_csv, mock_op):

        mock_csv.reader.return_value = iter(self.reader)
        a = VlanAssigner.VlanAssigner('test_vlans.csv')

        self.assertEqual(sorted(a.deviceId_to_port_vlans.keys()),
                         ['0', '1', '2']
                         )
        self.assertEqual(sorted(a.deviceId_to_port_vlans['0'][a.PRIMARY_FREE]),
                         [2, 5, 8]
                         )
        self.assertEqual(sorted(a.deviceId_to_port_vlans['0'][a.SECONDARY_FREE]),
                         [1, 2, 3, 4, 6, 7, 8])

        self.assertEqual(sorted(a.deviceId_to_port_vlans['1'][a.PRIMARY_FREE]),
                         [1, 5, 6, 9])
        self.assertEqual(sorted(a.deviceId_to_port_vlans['1'][a.SECONDARY_FREE]),
                         [1, 4, 5, 7])

        self.assertEqual(sorted(a.deviceId_to_port_vlans['2'][a.PRIMARY_FREE]),
                         [1, 1, 4])
        self.assertEqual(sorted(a.deviceId_to_port_vlans['2'][a.SECONDARY_FREE]),
                         [])

    #@patch('VlanAssigner.open')
    #@patch('VlanAssigner.csv')
    def test_findAvailablePort_nonRedundant(self):

        assigner = VlanAssigner.VlanAssigner('test_vlans.csv')

        assigner.find_available_port(req_id='1', is_redundant_request=False)

        self.assertEqual(assigner.deviceId_to_port_vlans['0'])

        #assigner.deviceId_to_port_vlans['0'][assigner.PRIMARY_FREE] = [2, 5, 8]
        #assigner.deviceId_to_port_vlans['0'][assigner.SECONDARY_FREE] = [1, 2, 3, 4, 6, 7, 8]
        #assigner.deviceId_to_port_vlans[]
