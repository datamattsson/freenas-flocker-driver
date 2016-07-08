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

from flocker.node import BackendDescription, DeployerType
from freenas_blockdev import blockdev

def api_factory(cluster_id, **kwargs):

    return blockdev(cluster_id=cluster_id,
                    proto=kwargs[u'proto'],
                    url=kwargs[u'url'],
                    volume=kwargs[u'volume'])

FLOCKER_BACKEND = BackendDescription(
                        name=u'freenas_flocker_driver',
                        needs_reactor=False, needs_cluster_id=True,
                        api_factory=api_factory,
                        required_config={ u'proto', u'url', u'volume' },
                        deployer_type=DeployerType.block)
