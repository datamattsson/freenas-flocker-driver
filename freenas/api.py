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

import requests
import json
from urlparse import urlparse

class rest(object):
    def __init__(self, base_url, **kwargs):
        
        self._http_systems = ('FreeNAS', 'TrueNAS')
        self._http_api_version = kwargs.get('version', 'v1.0')

        try:

            urlized = urlparse(base_url)

            if urlized.username:
                self._http_username = urlized.username 
            else:
                raise Exception('No username specified')

            if urlized.password:
                self._http_password = urlized.password
            else:
                raise Exception('No password specified')
            
            if urlized.hostname:
                self._http_hostname = urlized.hostname
            else:
                raise Exception('No hostname specified')
            
            if urlized.scheme:
                self._http_scheme = urlized.scheme
            else:
                raise Exception('No scheme specified')
            
            if urlized.path:
                self._http_path = urlized.path
            else:
                raise Exception('No path specified')
            
            if urlized.port:
                self._http_port = urlized.port

            self._base_url = '%s/%s' % (base_url, self._http_api_version)

        except Exception as e:
            raise Exception('Malformed base URL: %s\n' % str(e))

        try:
            req = self.get('system/version')

            if not req.get('name') in self._http_systems and \
                    self.status_code == 200:
                raise Exception('Unknown system type: %s' % req.get('name'))
        except Exception as e:
            raise Exception(str(e))

    def get(self, uri, method='get', **kwargs):

        self.status = None
        self.error_msg = None

        query = ''

        if kwargs.get('query'):

            query = '?'

            for key in kwargs['query']:
                query = query + '%s=%s&' % (key, kwargs['query'][key])
        
        try:
            if method == 'get':
                req = requests.get('%s/%s/%s' % (self._base_url, uri, query))
            if method == 'delete':
                req = requests.delete('%s/%s/%s' % (self._base_url, uri, query))

            self.status_code = req.status_code

            if self.status_code >= 400:
                self.error_msg = req.json()

            req.raise_for_status()

            if self.status_code == 204:
                return {}
            else:
                return req.json()

        except Exception as e:
            raise Exception('Error processing request: %s (API error: "%s")' % (str(e), self.error_msg))

        return {}

    def post(self, uri, payload, method='post'):
        
        self.status = None
        self.error_msg = None

        try:
            if method == 'post':
                req = requests.post('%s/%s/' % \
                        (self._base_url, uri), json=payload)
            if method == 'put':
                req = requests.put('%s/%s/' % \
                        (self._base_url, uri), json=payload)

            self.status_code = req.status_code

            if self.status_code >= 400:
                self.error_msg = req.json()

            req.raise_for_status()

            return req.json()

        except Exception as e:
            raise Exception('Error processing request: %s (API error: "%s")' % (str(e), self.error_msg))

        return {}

    def put(self, uri, payload, method='put'):
        return self.post(uri, payload, method=method)


    def delete(self, uri, method='delete', **kwargs):
        return self.get(uri, method=method, **kwargs)

    def create_zvol(self, volume, zvol, size, **kwargs):

        # TODO/FIXME: File issues requesting more create options (bs, comp,
        # sparse, reserve)

        res = {}

        payload = { 'name': zvol,
                    'volsize': size }
        try:
            res = self.post('storage/volume/%s/zvols' % volume, payload)
        except:
            raise

        return res

    def create_iscsi_extent(self, volume, zvol, **kwargs):

        # TODO/FIXME: Hardcoding 'Disk' for now, I can't think of a use case when
        # you would want to use a file backed extent anyhow.
        # TODO/FIXME: Iterate over kwargs and expand payload 
        # TODO/FIXME: Why isn't 'Disk' ZVOL?

        res = {}

        payload = { 'iscsi_target_extent_name': zvol,
                    'iscsi_target_extent_type': 'Disk',
                    'iscsi_target_extent_disk': 'zvol/%s/%s' % (volume, zvol) }
        try:
            res = self.post('services/iscsi/extent', payload)
        except:
            raise

        return res

    def create_iscsi_target_to_extent(self, target, extent):

        res = {}

        payload = { 'iscsi_target': target,
                    'iscsi_extent': extent }
        try:
            res = self.post('services/iscsi/targettoextent', payload)
        except:
            #  There might be complaints of adding t2e's that already exists but
            #  those are non-fatal. We might need to figure out what could be
            #  fatal here.
            pass

        return res
    
    def delete_iscsi_target_to_extent(self, target, extent):

        query = { 'limit': 0 }

        try:
            relations = self.get('services/iscsi/targettoextent', query=query)

            for item in relations:
                if item['iscsi_extent'] == extent and \
                        item['iscsi_target'] == target:
                    self.delete('services/iscsi/targettoextent/%s' % \
                            item['id'])
                    return
        except:
            raise
    
    def delete_iscsi_extent(self, extent_id):
        try:
            res = self.delete('services/iscsi/extent/%s' % extent_id)
        except:
            raise
    
    def delete_zvol(self, volume, zvol):
        try:
            res = self.delete('storage/volume/%s/zvols/%s' % (volume, zvol))
        except:
            raise

    def get_iscsi_extent_by_name(self, extent):

        query = { 'limit': 0 }
        
        try: 
            extents = self.get('services/iscsi/extent', query=query)

            for item in extents:
                if item['iscsi_target_extent_name'] == extent:
                    return item
        except:
            raise

        return {}
    
    def get_iscsi_extent_by_id(self, extent_id):

        extent = {}
        query = { 'limit': 1 }
        
        try: 
            extent = self.get('services/iscsi/extent/%s' % \
                    (extent_id), query=query)
        except:
            raise

        return extent

    def get_iscsi_extents_by_prefix(self, prefix):

        extents = []
        query = { 'limit': 0 }
        
        try: 
            results = self.get('services/iscsi/extent', query=query)

            for item in results:
                if item['iscsi_target_extent_name'].find(prefix) == 0:
                    extents.append(item)
        except:
            raise

        return extents

    def get_zvol_by_name(self, volume, name):

        zvol = {}

        try:
            zvol = self.get('storage/volume/%s/zvols/%s' % (volume, name))
        except:
            raise

        return zvol

    def update_iscsi_extent_comment(self, extent_id, comment):

        results = {}

        try:
            extent = self.get_iscsi_extent_by_id(extent_id)
        except:
            raise
        
        # FIXME: why is type and disk mandatory? ZVOL is "not available"
        payload = { 'iscsi_target_extent_comment': comment,
                    'iscsi_target_extent_type': 'Disk',
                    'iscsi_target_extent_disk':
                                extent['iscsi_target_extent_path'][5:]
                    }
        try:
            results = self.put('services/iscsi/extent/%s' % extent_id, payload)
        except:
            raise

        return results
