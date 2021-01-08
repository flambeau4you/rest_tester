import unittest
import rtr
import api

class TestRtr(unittest.TestCase):
    def test_print_api_Api_Print(self):
        api_json = {
                "name": "[Image] List Image",
                "request": {
                    "method": "GET",
                    "header": [
                        {
                            "key": "X-Requested-With",
                            "value": "XMLHttpRequest"
                        },
                        {
                            "key": "Content-Type",
                            "value": "application/json"
                        },
                        {
                            "key": "X-Auth-Token",
                            "value": "{{X-AUTH-TOKEN}}"
                        }
                    ],
                    "url": {
                        "raw": "{{IMAGE_URI}}/v2/images",
                        "host": [
                            "{{IMAGE_URI}}"
                        ],
                        "path": [
                            "v2",
                            "images"
                        ]
                    }
                },
                "response": []
            }
        rtr.config = {}
        rtr.config['end_point_var'] = ''
        api_obj = api.ApiV2(api_json, "image")
        self.assertTrue(api_obj != None)
        rtr.print_api(10, api_obj)

if __name__ == '__main__':
    unittest.main()