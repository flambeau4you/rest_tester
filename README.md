# REST Tester

## Introduction

REST Tester is a command line tool to test REST APIs.
It uses Postman exported JSON files to find API and test.
It useful to use command for speed.

## Files

1. rtr.py: The main script file.
1. rtr_config.yaml: Configuration file.
1. auth.json: A request body file to request authentication.

## Installation

### Python

Install Python if it was installed.
And install additional modules as below.

```
pip install requests
pip install pyyaml
```

### Copy Files

1. Copy all files to any directories you want.
1. Export Postman JSON file.
1. Copy a Postman JSON file to the same directory.

If the Postman file format version is 2.x, the APIs must have folders.
Version 2.x format can have multiple depths folders.
But only one depth folder can be supported.
If the APIs don't have any folders, export as version 1 (old) format.

### Configuration

Edit the rtr_config.py and auth.json to the web service system.

```
end_point: http://192.168.0.100:8080
postman_file: postman.json
auth_url: /auth/tokens
auth_body_file: auth.json
end_point_var: "{{domain}}"
auth_token_title: X-Auth-Token
auth_token_value:
path_vars:
```

1. end_point: Prefix part of the URL. There are a protocal, host address, and port number. 
1. postman_file: Exported Postman JSON file. The 2.1 format is not supported.
1. auth_body_file: A JSON file as the request body to authenticate.
1. end_point_var: The variable name to be changed with the END_POINT.
1. auth_token_title: The token title name in headers.
1. auth_token_value: Use this token value instead of calling authentication.
1. path_vars: Variables will be replaces in URLs.
It is JSON format.

Below is a example of the path_vars.

```
path_vars: |
  {
    '{{project_id}}': '1234'
  }

Before URL: /v1/{{project_id}}/requirements
After URL: /v1/1234/requirements
```

If the auth_url or auth_body_file is not seted, the authentication will be not executed.
Otherwise, always get authentication token firstly to test any APIs.

## Execute

Firstly go to the installed directory.

### Find APIs

Find APIs to want to execute.
All is mean of name, URL, and request body sample in the Postman file.
The case is insensitive.

1. Find by name: ./rtr.py -n STRING
1. Find by URL: ./rtr.py -n STRING
1. Find by ALL: ./rtr.py -n STRING
1. List all APIs: ./rtr.ph -l

The outputs are as below.

```
$ ./rtr.py -n user
 394. List User: GET /v1/users?name=&address=
 395. Create User: POST /v1/users
 396. Delete User: DELETE /v1/users/{user_id}
 397. Read User detail: GET /v1/users/{user_id}?include=
 398. Update User: PUT /v1/users/{user_id}
```

Left numbers without a dot is the ID to test.

## Test GET, DELETE API

### Syntax

> ./rtr.py ID [path_variable1 path_variable2 ...] [query_parameters]

The path variable is start with '{' and end with '}'.

The query parameters are one string regardless of count.

### Example

* List: ./rtr 394 'address=wall street&name=jane'
* Read: ./rtr 396 100203 'include=address&include=email'

Output Example:

```
$ ./rtr 394 'address=wall street&name=jane'
GET http://192.168.0.100:8080/v1/users
Response Code: 200
Response Body:
{
  "users": [
    {
      "id": "100203",
      "name": "Jane",
      "address": "10, Wall street",
      "created_at": "2018-05-30 18:07:24" 
    }
  ]
}
```

## Test POST, PUT, PATCH API

JSON format is only supported for requesting body.

### Syntax

> ./rtr.py ID [path_variable1 path_variable2 ...] [query_parameters] [request_body_file]

The request body is always last.

### Example

* Create: ./rtr 395 user.json
* Update: ./rtr 398 100203 user.json

Output Example:

```
$ ./rtr 395 user.json
POST http://192.168.0.100:8080/v1/users
Response Code: 201
Response Body:
{
  "user": {
    "id": "100203"
  }
}
```

## Export Request Body Sample

The request body sample in the Postman file can be exported.

Syntax:

> ./rtr.py -e ID

Output Example:

```
$ ./rtr.py -e 395
{
  "user": {
    "name": "Jane",
    "address": "10, Wall street"
  }
}
```

Save as a file:

```
$ ./rtr.py -e 395 > user.json
```

## Documentation

1. [Project Overview](docs/010_project_overview.md)
1. [Requirements](docs/030_requirements.md)
1. [Technology](docs/110_technology.md)
1. [Design](docs/120_design.md)
