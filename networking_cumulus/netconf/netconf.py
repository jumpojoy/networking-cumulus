import os
from collections import OrderedDict

from oslo_concurrency import processutils

CFG_PATH = "/etc/network/interfaces.d/"

INT_BRIDGE = 'br-int'


class ConfFile:

    def __init__(self, int_name):
        self.int_name = int_name
        self.path = _get_int_cfg_file_name(int_name)
        self.data = OrderedDict()

    def _get_int_cfg_file_name(self, int_name):
        return CFG_PATH+"%s.intf" % int_name

    def read(self):
        if not os.path.isfile(self.path):
            return

        with open(self.path, 'r') as f:
            for line in f:
                words = line.split()
                if len(words) > 0:
                    self.data[words[0]] = words[1:]

    def write(self):
        content = []
        for opt, val in self.data.items():
            content.append(opt)
            content.append(' ')
            content.append(' '.join(val))
            content.append('\n')

        with open(self.path, 'w') as f:
            f.write(''.join(content))

    def ensure_opt_contain_value(self, option, value):
        cur_values = self.data.get(option) or []
        if value not in cur_values:
            new_values = cur_values
            new_values.append(value)
            self.data[option] = new_values

    def ensure_opt_has_value(self, option, value):
        cur_value = self.data.get(option) or []
        if value not in cur_value:
            self.data[option] = [value]

    def ensure_opt_not_contain_value(self, option, value):
        cur_values = self.data[option]
        
        if value in cur_values:
            new_values = cur_values
            new_values.remove(value)
            if len(new_values) == 0:
                self.data.pop(option)
            else:
                self.data[option] = new_values

    def __enter__(self):
        if not os.path.isfile(self.path):
            self.data['auto'] = [self.int_name]
            self.data['iface'] = [self.int_name]
        else:
            self.read()
        return self
        
    def __exit__(self, type, value, traceback):
        self.write()
        kwargs = {}
        cmd = ['sudo', 'ifreload', '-c' ]
        result = processutils.execute(*cmd, **kwargs)
    

def _get_int_cfg_file_name(int_name):
    return CFG_PATH+"%s.intf" % int_name

def add_interface_to_network(segmentation_id, int_name):
    with ConfFile(INT_BRIDGE) as cfg:
        cfg.ensure_opt_contain_value('bridge-ports', int_name)

    with ConfFile(int_name) as int_cfg:
        int_cfg.ensure_opt_contain_value('bridge-access', segmentation_id)

def create_network(segmentation_id):
    with ConfFile(INT_BRIDGE) as cfg:
        cfg.ensure_opt_contain_value('bridge-vids', segmentation_id)

def remove_network(segmentation_id):
   with ConfFile(INT_BRIDGE) as cfg:
       cfg.ensure_opt_not_contain_value('bridge-vids', segmentation_id)
