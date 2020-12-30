# Copyright 2020 Jung Bong-Hwa
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

class Api:
    """
    API interface
    """
    version = 0
    api_json = None
    folder_name = None
    def __init__(self, api_json, folder_name):
        self.api_json = api_json
        self.folder_name = folder_name
            
    def get_name(self):
        """
        Gets name.
        """
        return self.api_json['name']
    
    def get_method(self):
        """
        Gets HTTP method. GET, POST, UPDATE, PATCH, or DELETE
        """
        pass
    
    def get_uri(self):
        """
        Gets URI.
        """
        pass
            
    def get_headers(self):
        """
        Gets headers.
        """
        pass
            
    def get_request_body_sample(self):
        """
        Gets requesting sample body.
        """
        pass
    
    def get_folder_name(self):
        """
        Gets folder name.
        """
        return self.folder_name
    

class ApiV1(Api):
    """
    Postman API version 1
    """
    def __init__(self, api_json, folder_name):
        Api.__init__(self, api_json, folder_name)

    def get_method(self):
        return self.api_json['method']
            
    def get_uri(self):
        return self.api_json['url']
            
    def get_headers(self):
        return {}
            
    def get_request_body_sample(self):
        return self.api_json['rawModeData']
    
class ApiV2(Api):
    """
    Postman API version 2 or 2.1
    """
    def __init__(self, api_json, folder_name):
        Api.__init__(self, api_json, folder_name)

    def get_method(self):
        return self.api_json['request']['method']

    def get_uri(self):
        if 'raw' in self.api_json['request']['url']:
            # 2.1 format
            return self.api_json['request']['url']['raw']
        else:
            # 2.0 format.
            return self.api_json['request']['url']
            
    def get_headers(self):
        headers = {}
        for header in self.api_json['request']['header']:
            headers[header['key']] = header['value']
        return headers
            
    def get_request_body_sample(self):
        return self.api_json['request']['body']['raw']