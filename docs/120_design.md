# Design

## Configuration Items

1. End point
1. Postman file
1. Authentication

## Python File

* rtr.py: Main script.
* postman.py: Handle Postman JSON file.
* api.py: A API object.

## Postman JSON Structure

1. There are three formats, old one, 2.0, and latest 2.1 formats.
Support all the formats.
1. If APIs aren't ordered by folders, don't care about that.
Don't sort.

### Old Format

1. Folder ID: folders[].id
1. Folder Name: folders[].name
1. Name: requests[].name
1. Method: requests[].method
All capitals.
1. URL: requests[].url
It includes query parameters.
Ex: {{domain}}/v1/students/{student_id}?name=&age=
1. Request body: requests[].rawModeData
1. Request Folder ID: requests[].folder

### 2.0 Format

All APIs must have a one depth folder.

1. Folder Name: item[].name
1. Name: item[].item[].name
1. Method: item[].item[].request.method
1. URL:
  1. All: item[].item[].request.url
  It includes query parameters.
  1. Particles: item[].item[].request.url.path[]
1. Query parameter:
  1. Key: item[].item[].request.body.query[].key
  1. Value: item[].item[].request.body.query[].value
1. Request body: item[].item[].request.body.raw
1. Header key: item[].item[].request.header[].key
1. Header value: item[].item[].request.header[].value

### 2.1 Format

All items are same as 2.0 format except below items.

1. URL All: item[].item[].request.url.raw
