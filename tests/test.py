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

from freenas_blockdev import blockdev
from uuid import uuid4
import sys

url = 'http://root:freenas@192.168.65.20/api'
volume = 'tank'

try:
    api = blockdev(url=url, volume=volume)
    vid = uuid4()
    bd = api.create_volume(vid, 50 * 1024 * 1024)
    sys.stdout.write('Volume created\n')
except Exception as e:
    sys.stderr.write('Could not create volume\n (%s)' % str(e))
    raise


try:
    api.attach_volume(bd.blockdevice_id, u'zen')
    sys.stdout.write('Volume attached\n')
    try:
        api.get_device_path(bd.blockdevice_id)
        sys.stdout.write('Found device path\n')
    except Exception as e:
        sys.stderr.write('Could not find device path (%s)\n' % str(e))
        pass

    api.detach_volume(bd.blockdevice_id)
    sys.stdout.write('Volume deattached\n')

except Exception as e:
    sys.stderr.write('Could not attach/detach volume (%s)\n' % str(e))
    pass

try:
    api.destroy_volume(bd.blockdevice_id)
    sys.stdout.write('Volume destroyed\n')
except Exception as e:
    sys.stderr.write('Could not destroy volume (%s)\n' % str(e))
    pass

vols = api.list_volumes()

if False:
    for vol in vols:
        try:
            api.detach_volume(vol.blockdevice_id)
            sys.stdout.write('Volume detached\n')
        except Exception as e:
            sys.stderr.write('Volume could not detach (%s)\n' % str(e))
            pass
	    
        try:
            api.destroy_volume(vol.blockdevice_id)
            sys.stdout.write('Volume destroyed\n')
        except Exception as e:
            sys.stderr.write('Volume could not be destroyed (%s)\n' % str(e))
            pass
