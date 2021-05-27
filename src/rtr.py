#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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

import argparse
import json
import re
import sys

import requests
from requests.exceptions import ConnectionError
import yaml

from postman import create_postman


# Defines arguments.
parser = argparse.ArgumentParser(description='REST Tester')
parser.add_argument("-n", "--name", action='store_true',
                    help="Find APIs by the name.")
parser.add_argument("-nr", "--name_request", action='store_true',
                    help="Find APIs by the name and request it.")
parser.add_argument("-ne", "--name_export", action='store_true',
                    help="Find APIs by the name and export body sample.")
parser.add_argument("-u", "--uri", action='store_true',
                    help="Find APIs by the URI.")
parser.add_argument("-a", "--all", action='store_true',
                    help="Find APIs by all items.")
parser.add_argument("-l", "--list", action='store_true',
                    help="Show all APIs.")
parser.add_argument("-e", "--export", action='store_true',
                    help="Export request body sample by index.")
parser.add_argument("-r", "--root", action='store_true',
                    help="Request root.")
parser.add_argument("-m", "--multipart",
                    help="Request as multipart with the title.")
parser.add_argument("-v", "--verbose", action='store_true',
                    help="Show all headers.")
parser.add_argument("-c", "--config",
                    help="Use the configuration file.")
parser.add_argument('parameters', metavar='parameter', nargs='*',
                    help="[index] | [keyword] [path_var1 path_var2 ...] [query_params] [request_file] Index 0 is calling root.")


def print_api(index, api):
    """
    Prints API information.
    """
    uri = api.get_uri().replace(config['end_point_var'], '');
    print("%4s. [%s] %s: %s %s" 
                  % (index, api.get_folder_name(),
                    api.get_name(),
                    api.get_method(), uri))


def find_by_name(postman, key):
    """
    Finds APIs by the name.
    """
    for i in range(0, postman.count_apis()):
        api = postman.get_api(i)
        if re.search(key, api.get_name(), re.IGNORECASE):
            print_api(i, api)

def find_index_by_name(postman, key):
    """
    Finds APIs by the name.
    """
    for i in range(0, postman.count_apis()):
        api = postman.get_api(i)
        if re.search(key, api.get_name(), re.IGNORECASE):
            return i
    return -1
        
def find_by_uri(postman, key):
    """
    Finds APIs by the URI.
    """
    for i in range(0, postman.count_apis()):
        api = postman.get_api(i)
        uri = api.get_uri().replace(config['end_point_var'], '');
        if re.search(key, uri, re.IGNORECASE):
            print_api(i, api)

        
def find_by_all(postman, key):
    """
    Finds APIs by the all.
    """
    for i in range(0, postman.count_apis()):
        api = postman.get_api(i)
        uri = api.get_uri().replace(config['end_point_var'], '');
        if (re.search(key, uri, re.IGNORECASE) 
            or re.search(key, api.get_name(), re.IGNORECASE) 
            or re.search(key, api.get_request_body_sample(), re.IGNORECASE)
            or re.search(key, api.get_folder_name(), re.IGNORECASE)):
            print_api(i, api)

        
def print_all_apis(postman):
    """
    Prints all APIs.
    """
    for i in range(0, postman.count_apis()):
        api = postman.get_api(i)
        print_api(i, api)

        
def print_response(response, verbose=False):
    """
    Prints responded body.
    """
    if response.status_code and verbose:
        print("Response Code: %s" % (str(response.status_code)))
        
    if verbose:
        print("Response Headers:")
        for key in response.headers:
            print("%s: %s" % (key, response.headers[key]))
        
    if response.text:
        if verbose:
            print("Response Body:")

        if ('Content-Type' in response.headers 
            and response.headers['Content-Type'].startswith('application/json')):
            print(json.dumps(json.loads(response.text), indent=2))
        else:
            print(response.text);

    
def get_cert():
    """
    Returns CRT file if HTTPS is used.
    """
    if config['crt_file'] and config['key_file']:
        return (config['crt_file'], config['key_file'])
    else:
        return None


def request_auth(end_point):
    """
    Authenticates user and password.
    """
    path = config['auth_body_file']

    if not config['auth_uri'] or not path:
        return None
    
    with open(config['auth_body_file'], 'r') as handle:
        body = json.load(handle)
    
    headers = {'Content-Type': 'application/json'}
    try:
        r = requests.post(url=end_point + config['auth_uri'],
                          headers=headers, json=body, verify=False, cert=get_cert())
    except ConnectionError as e:
        print("Authentication Error: ")
        print(e)
        sys.exit(1)
    
    if config['auth_token_title'] in r.headers:
        return r.headers[config['auth_token_title']]
    elif 'X-Auth-Token' in r.headers:
        return r.headers['X-Auth-Token']
    elif 'X-Subject-Token' in r.headers:
        return r.headers['X-Subject-Token']
    else:
        print('Authentication failed.')
        print_response(r, True)
        sys.exit(1)

    
def request_post(uri, headers, body_file):
    """
    Requests POST uri.
    """
    body = None
    if body_file:
        with open(body_file, 'r') as handle:
            body = json.load(handle)
        headers['Content-Type'] = 'application/json'
        print("Request Body:\n" + json.dumps(body, indent=2))
    
    try:        
        r = requests.post(url=uri, headers=headers, json=body, verify=False, cert=get_cert())
    except ConnectionError as e:
        print("Calling POST Error: ")
        print(e)
        sys.exit(1)
    return r
    
def request_post_multipart(uri, headers, multipart_title, multipart_file):
    """
    Requests POST uri as multipart.
    """
    try:
        f = open(multipart_file,"rb")
        multipart_body = { multipart_title : (multipart_file, f, "application/x-binary") }
        r = requests.post(url=uri, headers=headers, files=multipart_body, verify=False, cert=get_cert())
    except ConnectionError as e:
        print("Calling POST Error: ")
        print(e)
        sys.exit(1)
    return r

def request_get(uri, headers):
    """
    Requests GET uri.
    """
    try:
        r = requests.get(url=uri, headers=headers, verify=False, cert=get_cert()) 
    except ConnectionError as e:
        print("Calling GET Error: ")
        print(e)
        sys.exit(1)
    return r

    
def request_put(uri, headers, body_file):
    """
    Requests PUT uri.
    """
    body = None
    if body_file:
        with open(body_file, 'r') as handle:
            body = json.load(handle)
        headers['Content-Type'] = 'application/json'
        
    try:
        r = requests.put(url=uri, headers=headers, json=body, verify=False, cert=get_cert())
    except ConnectionError as e:
        print("Calling PUT Error: ")
        print(e)
        sys.exit(1)
    return r

def request_put_multipart(uri, headers, multipart_title, multipart_file):
    """
    Requests PUT uri as multipart.
    """
    try:
        f = open(multipart_file,"rb")
        multipart_body = { multipart_title : (multipart_file, f, "application/x-binary") }
        r = requests.put(url=uri, headers=headers, files=multipart_body, verify=False, cert=get_cert())
    except ConnectionError as e:
        print("Calling PUT Error: ")
        print(e)
        sys.exit(1)
    return r


def request_patch(uri, headers, body_file):
    """
    Requests PATCH uri.
    """
    body = None
    if body_file:
        with open(body_file, 'r') as handle:
            body = json.load(handle)
            
        if body_file.endswith('.json') or body_file.endswith('.JSON'):
            headers['Content-Type'] = 'application/json-patch+json'
        elif body_file.endswith('.xml') or body_file.endswith('.XML'):
            headers['Content-Type'] = 'application/xml'
        
    try:
        r = requests.patch(url=uri, headers=headers, json=body, verify=False, cert=get_cert())
    except ConnectionError as e:
        print("Calling PATCH Error: ")
        print(e)
        sys.exit(1)
    return r

def request_patch_multipart(uri, headers, multipart_title, multipart_file):
    """
    Requests PATCH uri as multipart.
    """
    try:
        f = open(multipart_file,"rb")
        multipart_body = { multipart_title : (multipart_file, f, "application/x-binary") }
        r = requests.patch(url=uri, headers=headers, files=multipart_body, verify=False, cert=get_cert())
    except ConnectionError as e:
        print("Calling PATCH Error: ")
        print(e)
        sys.exit(1)
    return r



def request_delete(uri, headers, body_file):
    """
    Requests DELETE uri.
    """
    body = None
    if body_file:
        with open(body_file, 'r') as handle:
            body = json.load(handle)
            
        if body_file.endswith('.json') or body_file.endswith('.JSON'):
            headers['Content-Type'] = 'application/json'
        elif body_file.endswith('.xml') or body_file.endswith('.XML'):
            headers['Content-Type'] = 'application/xml'

    try:
        r = requests.delete(url=uri, headers=headers, json=body, verify=False, cert=get_cert())
    except ConnectionError as e:
        print("Calling DELETE Error: ")
        print(e)
        sys.exit(1)
    return r


def request(postman, parameters, multipart, verbose):
    """
    Requests Postman item.
    """
    end_point = config['end_point']
    
    param_index = 0
    index = int(parameters[param_index])
    param_index += 1

    api = postman.get_api(index)
    uri = api.get_uri().replace(config['end_point_var'], end_point)
    uri = re.sub(r'\?.*', '', uri)
    
    # Replaces variables by configuration.
    if 'path_vars' in config and config['path_vars']:
        path_vars = json.loads(config['path_vars'])
        if path_vars:
            for key in path_vars:
                uri = re.sub(key, path_vars[key], uri, 1)

    # Replaces path variables.
    while len(parameters) > param_index and uri.find('{') >= 0:
        uri = re.sub(r'{[^/]*}', parameters[param_index], uri, 1)
        param_index += 1
    
    # Query parameters
    if len(parameters) > param_index and parameters[param_index].find('=') > 0:
        uri += '?' + parameters[param_index]
        param_index += 1

    # Authentication
    token = None

    if config['auth_token_value']:
        token = config['auth_token_value']
    elif config['auth_uri'] and not uri.startswith(end_point + config['auth_uri']):
        token = request_auth(end_point)
    
    headers = api.get_headers()
    if token:
        headers[config['auth_token_title']] = token
                
    if verbose:
        print("curl -k -X %s %s -H '%s: %s' 2>/dev/null | python -m json.tool" % (api.get_method(), uri, config['auth_token_title'], token))
        print("Request Headers:")
        for key in headers:
            print("%s: %s" % (key, headers[key]))

    if api.get_method() == 'GET':
        r = request_get(uri, headers)
    elif api.get_method() == 'POST':
        if len(parameters) > param_index:
            if multipart:
                r = request_post_multipart(uri, headers, multipart, parameters[param_index])
            else:
                r = request_post(uri, headers, parameters[param_index])
            param_index += 1
        else:
            r = request_post(uri, headers, None)
    elif api.get_method() == 'DELETE':
        if len(parameters) > param_index:
            r = request_delete(uri, headers, parameters[param_index])
            param_index += 1
        else:
            r = request_delete(uri, headers, None)
    elif api.get_method() == 'PUT':
        if len(parameters) > param_index:
            if multipart:
                r = request_put_multipart(uri, headers, multipart, parameters[param_index])
            else:
                r = request_put(uri, headers, parameters[param_index])
            param_index += 1
        else:
            r = request_put(uri, headers, None)
    elif api.get_method() == 'PATCH':
        if len(parameters) > param_index:
            if multipart:
                r = request_patch_multipart(uri, headers, multipart, parameters[param_index])
            else:
                r = request_patch(uri, headers, parameters[param_index])
            param_index += 1
        else:
            r = request_patch(uri, headers, None)
    
    print_response(r, verbose)


def request_root(verbose):
    """
    Calls root uri.
    """
    print("%s %s" % ("GET", config['end_point'] + "/"))
    r = request_get(config['end_point'] + "/", None)
    print_response(r, verbose);


def export_request_sample(postman, index):
    """
    Prints a sample body in the Postman.
    """
    api = postman.get_api(index)
    print(api.get_request_body_sample())

if __name__ == '__main__':
    # Main
    args = parser.parse_args()
    
    # Reads configuration.
    config_path = 'config.yaml'
    if args.config:
        config_path = args.config
        
    with open(config_path) as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    
    # Reads postman file.
    postman = create_postman(config['postman_file']) 
    
    if args.name:
        find_by_name(postman, args.parameters[0])
    elif args.name_request:
        index = find_index_by_name(postman, args.parameters[0])
        if index != -1:
            args.parameters[0] = index
            request(postman, args.parameters, args.multipart, args.verbose)
        else:
            print("API is not found!")
            sys.exit(1)
    elif args.name_export:
        index = find_index_by_name(postman, args.parameters[0])
        if index != -1:
            export_request_sample(postman, index)
        else:
            print("API is not found!")
            sys.exit(1)
    elif args.uri:
        find_by_uri(postman, args.parameters[0])
    elif args.all:
        find_by_all(postman, args.parameters[0])
    elif args.list:
        print_all_apis(postman)
    elif args.export:
        export_request_sample(postman, args.parameters[0])
    elif args.root:
        request_root(args.verbose)
    elif len(args.parameters) == 0:
        parser.print_help(sys.stderr)
    else:
        request(postman, args.parameters, args.multipart, args.verbose)
