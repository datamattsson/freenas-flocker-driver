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

from freenas.api import rest
from subprocess import (check_output, call)

class iscsi(object):
    
    iscsi_dm_prefix = 'SFreeNAS_iSCSI_Disk_'
    iscsi_dm_dir = '/dev/mapper'

    def __init__(self, **kwargs):
        self.rest_api = rest(kwargs.get('url'))
        self.volume = kwargs.get('volume')
        self.target = kwargs.get('target', 1)

    def create_volume(self, zvol, size):

        try:
            self.rest_api.create_zvol(self.volume, zvol, size)
            extent = self.rest_api.create_iscsi_extent(self.volume, zvol)
        except:
            raise
    
    def attach_volume(self, name, host):

        # TODO/FIXME: adding/removing initiators from 'Associated Targets' have
        # no effect. Attaching a new volume is simply adding the extent to the
        # target and rescan

        zvol = {}

        try:    
            extent = self.rest_api.get_iscsi_extent_by_name(name)

            if extent:
                self.rest_api.create_iscsi_target_to_extent(self.target,
                        extent['id'])
                self.rest_api.update_iscsi_extent_comment(extent['id'], host)
                
                zvol = self._construct_block_dict(extent)
                self._iscsi_rescan()
        except:
            raise

        return zvol
    
    def list_volumes(self, prefix):

        extents = []
        
        for extent in self.rest_api.get_iscsi_extents_by_prefix(prefix):
            extents.append(self._construct_block_dict(extent))

        return extents

    def destroy_volume(self, name):

        zvol = {}

        try:
            extent = self.rest_api.get_iscsi_extent_by_name(name)

            if extent:
                zvol = self._construct_block_dict(extent)

                self.rest_api.delete_iscsi_extent(extent['id'])
                self.rest_api.delete_zvol(self.volume,
                        extent['iscsi_target_extent_name'])
        except:
            raise

        return zvol
    
    def detach_volume(self, name):

        zvol = {}
        
        try:    
            extent = self.rest_api.get_iscsi_extent_by_name(name)

            if extent:
                self.rest_api.delete_iscsi_target_to_extent(self.target,
                        extent['id'])
                self.rest_api.update_iscsi_extent_comment(extent['id'], '')
                
                zvol = self._construct_block_dict(extent)
                self._mpath_flush('%s%s' % (self.iscsi_dm_prefix, \
                        extent['iscsi_target_extent_serial']))
                self._iscsi_rescan()
        except:
            raise

        return zvol
    
    def get_device_path(self, name):

        extent = {}
        
        try:
            extent = self.rest_api.get_iscsi_extent_by_name(name)

            if extent['iscsi_target_extent_name'] == name:
                return '%s/%s%s' % (self.iscsi_dm_dir, self.iscsi_dm_prefix, \
                        extent['iscsi_target_extent_serial'])
        except:
            raise

        return None

    def _construct_block_dict(self, extent):

        try:
            if not extent['iscsi_target_extent_comment']:
                extent['attached_to'] = None
            else:
                extent['attached_to'] = extent['iscsi_target_extent_comment']

            extent['blockdevice_id'] = extent['iscsi_target_extent_name']
            extent['dataset_id'] = extent['iscsi_target_extent_name'][8:]
            extent['size'] = self.rest_api.get_zvol_by_name(self.volume,
                                extent['iscsi_target_extent_name']
                                )['volsize']
        except:
            raise

        return extent

    def _iscsi_rescan(self):
        try:
            call(['iscsiadm', '-m', 'node', '-R'])
            call(['multipath', '-r'])
        except:
            # This will catch OS errors if the calls return errors but are
            # non-fatal for now
            pass
    
    def _mpath_flush(self, path):
        try:
            call(['multipath', '-f', path])
        except:
            # This will catch OS errors if the calls return errors but are
            # non-fatal for now
            pass

    # FIXME pending issue report with FreeNAS
    def _get_iscsi_iname(self):
        try:
            return check_output(['iscsi-iname'])
        except:
            raise

    def _iname_in_igroup(self, iname, igroup):
        return True
