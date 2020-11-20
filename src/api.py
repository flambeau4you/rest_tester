class Api:
    version = 0
    api_json = None
    folder_name = None
    def __init__(self, api_json, folder_name):
        self.api_json = api_json
        self.folder_name = folder_name
            
    def get_name(self):
        return self.api_json['name']
    
    def get_method(self):
        pass
    
    def get_url(self):
        pass
            
    def get_headers(self):
        pass
            
    def get_request_body_sample(self):
        pass
    
    def get_folder_name(self):
        return self.folder_name
    

class ApiV1(Api):
    def __init__(self, api_json, folder_name):
        Api.__init__(self, api_json, folder_name)

    def get_method(self):
        return self.api_json['method']
            
    def get_url(self):
        return self.api_json['url']
            
    def get_headers(self):
        return {}
            
    def get_request_body_sample(self):
        return self.api_json['rawModeData']
    
class ApiV2(Api):
    def __init__(self, api_json, folder_name):
        Api.__init__(self, api_json, folder_name)

    def get_method(self):
        return self.api_json['request']['method']

    def get_url(self):
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