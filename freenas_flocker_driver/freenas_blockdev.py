#
# Copyright 2016 Michael Mattsson. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
#

from flocker.node.agents.blockdevice import (BlockDeviceVolume,
                    IBlockDeviceAPI,
                    AlreadyAttachedVolume,
                    UnknownVolume,
                    UnattachedVolume)
                   # IProfiledBlockDeviceAPI TODO

from zope.interface import implementer
from twisted.python.filepath import FilePath
from freenas_iscsi import iscsi
from socket import gethostname
from uuid import UUID
import os

@implementer(IBlockDeviceAPI)
class blockdev(object):

    flocker_prefix = 'flocker-'

    def __init__(self, **kwargs):
        # FIXME: this won't work when loaded into Flocker
        # ns = __import__(__name__)
        # self._proto = getattr(ns, kwargs.get('proto', 'iscsi'))(**kwargs)
        if kwargs.get('proto', 'iscsi') == 'iscsi':
            self._proto = iscsi(**kwargs)
    
    def create_volume(self, dataset_id, size):

        zvol = BlockDeviceVolume(size=size, dataset_id=dataset_id,
                blockdevice_id=u"%s%s" % (self.flocker_prefix, dataset_id))

        self._proto.create_volume(zvol.blockdevice_id, size)

        return zvol
    
    def attach_volume(self, blockdevice_id, attach_to):

        try:
            vol = self._proto.attach_volume(blockdevice_id, attach_to)
        except:
            raise

        return BlockDeviceVolume(dataset_id=UUID(vol['blockdevice_id'][8:]),
                                blockdevice_id=vol[u'blockdevice_id'],
                                size=vol['size'],
                                attached_to=vol['attached_to'])
    
    def list_volumes(self):
        
        volumes = []

        for vol in self._proto.list_volumes(self.flocker_prefix):
            volumes.append(BlockDeviceVolume(
                                dataset_id=UUID(vol['blockdevice_id'][8:]),
                                blockdevice_id=vol[u'blockdevice_id'],
                                size=vol['size'],
                                attached_to=vol['attached_to']))
        return volumes

    def destroy_volume(self, blockdevice_id):

        try:
            vol = self._proto.destroy_volume(blockdevice_id)
            
            if not vol:
                raise UnknownVolume(blockdevice_id)
        except:
            raise
    
    def detach_volume(self, blockdevice_id):

        vol = self._proto.detach_volume(blockdevice_id)

        if not vol:
            raise UnknownVolume(blockdevice_id)

        if not vol['attached_to']:
            raise UnattachedVolume(blockdevice_id)

    def get_device_path(self, blockdevice_id):

        dev = self._proto.get_device_path(blockdevice_id)
        
        if not dev:
            raise UnknownVolume(blockdevice_id)

        if not os.path.exists(dev):
            raise UnattachedVolume(blockdevice_id)

        return FilePath(dev)

    def compute_instance_id(self):
        return unicode(gethostname())

    def allocation_unit(self):
        return 1

def freenas_setup(cluster_id, url, proto, volume):

    return blockdev(cluster_id=cluster_id,
                    url=url,
                    proto=proto,
                    volume=volume,
                    allocation_unit=1,
                    compute_instance_id=unicode(gethostname()))
