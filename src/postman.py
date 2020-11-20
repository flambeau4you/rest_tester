import json
import sys

from api import ApiV1, ApiV2

def create_postman(path):
    # Opens root_json file
    with open(path, 'r') as handle:
        root_json = json.load(handle)
        
    if 'requests' in root_json:
        return PostmanV1(root_json)
    else: 
        return PostmanV2(root_json)

class Postman:
    def get_api(self, index):
        pass
            
    def count_apis(self):
        pass
    

            
class PostmanV1(Postman):
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