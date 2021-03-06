# -*- generated by 1.0.4 -*-
import da
_config_object = {}
import sys
import subprocess
import time
from configparser import ConfigParser

class Node_(da.NodeProcess):

    def __init__(self, procimpl, props):
        super().__init__(procimpl, props)
        self._events.extend([])

    def run(self):
        config = ConfigParser()
        config.read(sys.argv[1])
        config_file = sys.argv[1]
        nclients = int(config.get('SystemConfiguration', 'no_of_clients'))
        ncoordinators = int(config.get('SystemConfiguration', 'no_of_coordinators'))
        nworkers = int(config.get('SystemConfiguration', 'no_of_workers_per_coordinator'))
        node_name = 'Master'
        cmd = (((('python -m da -n ' + node_name) + ' --master -f --logfilename logs/') + node_name) + '.log -L info -D src/Master.da')
        subprocess.Popen(cmd, creationflags=subprocess.CREATE_NEW_CONSOLE)
        time.sleep(1)
        node_name = 'Database'
        cmd = (((('python -m da -n ' + node_name) + ' -f --logfilename logs/') + node_name) + '.log -L info -D src/Database.da')
        subprocess.Popen(cmd, creationflags=subprocess.CREATE_NEW_CONSOLE)
        time.sleep(1)
        node_name = 'Client'
        cmd = (((('python -m da -n ' + node_name) + ' -f --logfilename logs/') + node_name) + '.log -L info -D src/Client.da')
        subprocess.Popen(cmd, creationflags=subprocess.CREATE_NEW_CONSOLE)
        for i in range(ncoordinators):
            node_name = ('Coordinator_' + str((i + 1)))
            cmd = (((('python -m da -n ' + node_name) + ' -f --logfilename logs/') + node_name) + '.log -L info -D src/Coordinator.da')
            subprocess.Popen(cmd, creationflags=subprocess.CREATE_NEW_CONSOLE)
        print('Nodes Configured, please proceed!!')
