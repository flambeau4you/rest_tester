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

import json
import sys

from api import ApiV1, ApiV2

def create_postman(path):
    """
    Creates a Postman instance.
    """
    # Opens root_json file
    with open(path, 'r') as handle:
        root_json = json.load(handle)
        
    if 'requests' in root_json:
        return PostmanV1(root_json)
    else: 
        return PostmanV2(root_json)

class Postman:
    """
    Postman interface.
    """
    def get_api(self, index):
        """
        Gets a API by index number.
        """
        pass
            
    def count_apis(self):
        """
        Counts APIs.
        """
        pass
    

            
class PostmanV1(Postman):
    """
    Postman version 1
    """
    root_json = None
    def __init__(self, root_json):
        self.root_json = root_json
    
    def get_api(self, index):
        index = int(index)
        if len(self.root_json['requests']) >= index:
            request = self.root_json['requests'][index]
            if 'folder' in request:
                for folder in self.root_json['folders']:
                    if folder['id'] == request['folder']:
                        folder_name = folder['name']
            return ApiV1(request, folder_name)
        else:
            print("The index is not FOUND! index: %s" %(index))
            sys.exit(1)
            
    def count_apis(self):
        return len(self.root_json['requests'])
    
class PostmanV2(Postman):
    """
    Postman version 2
    """
    root_json = None
    count = 0
    def __init__(self, root_json):
        self.root_json = root_json
        # Counts APIs.
        self.count = 0
        for i in range(0, len(self.root_json['item'])):
            folder = self.root_json['item'][i]
            self.count += len(folder['item'])
    
    def get_api(self, index):
        index = int(index)
        if index >= self.count:
            print("The index is not FOUND! Total: %s" %(self.count))
            sys.exit(1)
        else:
            cnt = 0
            for i in range(0, len(self.root_json['item'])):
                folder = self.root_json['item'][i]
                for j in range(0, len(folder['item'])):
                    if cnt == index:
                        return ApiV2(folder['item'][j], folder['name'])
                    cnt += 1
            
    def count_apis(self):
        return self.count