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
import sys
import json
import re

try:
    foo = rest('http://root:freenas@192.168.65.20/api')
except Exception as e:
    print 'foo: %s\n' % str(e)

try:
    myfs = 'foo50'
    fs = { "name": myfs }
    # Create FS
    req = foo.post('storage/volume/tank/datasets', fs)
    print json.dumps(req,indent=4)
    
    # Read FS
    req = foo.get('storage/volume/tank/datasets')
    print json.dumps(req, indent=4)

    # Delete FS
    req = foo.delete('storage/volume/tank/datasets/%s' % myfs)
    print json.dumps(req, indent=4)

    for bar in foo.get('storage/volume/tank/datasets'):
        if re.match('foo', bar['name']):
            req = foo.delete('storage/volume/tank/datasets/%s' % bar['name'])

except Exception as e:
    #print 'bar this: %s and this: %s' % (str(e), foo.error_msg)
    print str(e)

