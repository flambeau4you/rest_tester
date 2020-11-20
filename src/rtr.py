#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import json
import re
import requests
from requests.exceptions import ConnectionError
import sys
import yaml

from postman import create_postman


# Defines arguments.
parser = argparse.ArgumentParser(description='REST Tester')
parser.add_argument("-n", "--name", action='store_true', 
                    help="Find APIs by the name.")
parser.add_argument("-u", "--url", action='store_true', 
                    help="Find APIs by the URL.")
parser.add_argument("-a", "--all", action='store_true', 
                    help="Find APIs by all items.")
parser.add_argument("-l", "--list", action='store_true', 
                    help="Show all APIs.")
parser.add_argument("-e", "--export", action='store_true', 
                    help="Export request body sample by index.")
parser.add_argument("-r", "--root", action='store_true', 
                    help="Request root.")
parser.add_argument("-v", "--verbose", action='store_true', 
                    help="Show all headers.")
parser.add_argument("-c", "--config",  
                    help="Use the config file.")
parser.add_argument('parameters', metavar='parameter', nargs='*',
                    help="[index] | [keyword] [path_var1 path_var2 ...] [query_params] [request_file] Index 0 is calling root.")


def print_api(index, api):
    """
    Prints API information.
    """
    url = api.get_url().replace(config['end_point_var'], '');
    print("%4s. [%s] %s: %s %s" 
                  %(index, api.get_folder_name().encode('utf-8').decode(),
                    api.get_name().encode('utf-8').decode(), 
                    api.get_method().encode('utf-8').decode(), url.encode('utf-8').decode()))

def find_by_name(postman, key):
    """
    Finds APIs by the name.
    """
    for i in range(0, postman.count_apis()):
        api = postman.get_api(i)
        if re.search(key, api.get_name(), re.IGNORECASE):
            print_api(i, api)
        
def find_by_url(postman, key):
    """
    Finds APIs by the URL.
    """
    for i in range(0, postman.count_apis()):
        api = postman.get_api(i)
        url = api.get_url().replace(config['end_point_var'], '');
        if re.search(key, url, re.IGNORECASE):
            print_api(i, api)
        
def find_by_all(postman, key):
    """
    Finds APIs by the all.
    """
    for i in range(0, postman.count_apis()):
        api = postman.get_api(i)
        url = api.get_url().replace(config['end_point_var'], '');
        if (re.search(key, url, re.IGNORECASE) 
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
    Prints responsed body.
    """
    if response.status_code and verbose:
        print("Response Code: %s" %(str(response.status_code)))
        
    if verbose:
        print("Response Headers:")
        for key in response.headers:
            print("%s: %s" %(key, response.headers[key]))
        
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

    if not config['auth_url'] or not path:
        return None
    
    with open(config['auth_body_file'], 'r') as handle:
        body = json.load(handle)
    
    headers = {'Content-Type': 'application/json'}
    try:
        r = requests.post(url = end_point + config['auth_url'], 
                          headers = headers, json = body, verify = False, cert = get_cert())
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
    
def request_post(url, headers, body_file):
    """
    Requests POST URL.
    """
    body = None
    if body_file:
        with open(body_file, 'r') as handle:
            body = json.load(handle)
        headers['Content-Type'] = 'application/json'
        print("Request Body:\n" + json.dumps(body, indent=2))
    
    try:
        r = requests.post(url = url, headers = headers, json = body, verify = False, cert = get_cert())
    except ConnectionError as e:
        print("Calling POST Error: ")
        print(e)
        sys.exit(1)
    return r

def request_get(url, headers):
    """
    Requests GET URL.
    """
    try:
        r = requests.get(url = url, headers = headers, verify = False, cert = get_cert()) 
    except ConnectionError as e:
        print("Calling GET Error: ")
        print(e)
        sys.exit(1)
    return r
    
def request_put(url, headers, body_file):
    """
    Requests PUT URL.
    """
    body = None
    if body_file:
        with open(body_file, 'r') as handle:
            body = json.load(handle)
        headers['Content-Type'] = 'application/json'
        
    try:
        r = requests.put(url = url, headers = headers, json = body, verify = False, cert = get_cert())
    except ConnectionError as e:
        print("Calling PUT Error: ")
        print(e)
        sys.exit(1)
    return r

def request_patch(url, headers, body_file):
    """
    Requets PATCH URL.
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
        r = requests.patch(url = url, headers = headers, json = body, verify = False, cert = get_cert())
    except ConnectionError as e:
        print("Calling PATCH Error: ")
        print(e)
        sys.exit(1)
    return r

def request_delete(url, headers, body_file):
    """
    Requests DELETE URL.
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
        r = requests.delete(url = url, headers = headers, json = body, verify = False, cert = get_cert())
    except ConnectionError as e:
        print("Calling DELETE Error: ")
        print(e)
        sys.exit(1)
    return r

def request(postman, parameters, verbose):
    """
    Requests Postman item.
    """
    end_point = config['end_point']
    
    param_index = 0
    index = int(parameters[param_index])
    param_index += 1

    api = postman.get_api(index)
    url = api.get_url().replace(config['end_point_var'], end_point)
    url = re.sub(r'\?.*', '', url)
    
    # Replaces varialbles by config.
    if 'path_vars' in config and config['path_vars']:
        path_vars = json.loads(config['path_vars'])
        if path_vars:
            for key in path_vars:
                url = re.sub(key, path_vars[key], url, 1)

    # Replaces path variables.
    while len(parameters) > param_index and url.find('{') >= 0:
        url = re.sub(r'{[^/]*}', parameters[param_index], url, 1)
        param_index += 1
    
    # Query paramters
    if len(parameters) > param_index and parameters[param_index].find('=') > 0:
        url += '?' + parameters[param_index]
        param_index += 1

    # Authentication
    token = None

    if config['auth_url'] and not url.startswith(end_point + config['auth_url']):
        token = request_auth(end_point)
    
    headers = api.get_headers()
    if token:
        headers[config['auth_token_title']] = token
                
    if verbose:
        print("%s %s" %(api.get_method(), url))
        print("Request Headers:")
        for key in headers:
            print("%s: %s" %(key, headers[key]))

    if api.get_method() == 'GET':
        r = request_get(url, headers)
    elif api.get_method() == 'POST':
        if len(parameters) > param_index:
            r = request_post(url, headers, parameters[param_index])
            param_index += 1
        else:
            r = request_post(url, headers, None)
    elif api.get_method() == 'DELETE':
        if len(parameters) > param_index:
            r = request_delete(url, headers, parameters[param_index])
            param_index += 1
        else:
            r = request_delete(url, headers, None)
    elif api.get_method() == 'PUT':
        if len(parameters) > param_index:
            r = request_put(url, headers, parameters[param_index])
            param_index += 1
        else:
            r = request_put(url, headers, None)
    elif api.get_method() == 'PATCH':
        if len(parameters) > param_index:
            r = request_patch(url, headers, parameters[param_index])
            param_index += 1
        else:
            r = request_patch(url, headers, None)
    
    print_response(r, verbose)

def request_root(verbose):
    """
    Calls root URL.
    """
    print("%s %s" %("GET", config['end_point'] + "/"))
    r = request_get(config['end_point'] + "/", None)
    print_response(r, verbose);

def export_request_sample(postman, index):
    """
    Prints a sample body in the Postman.
    """
    api = postman.get_api(index)
    print(api.get_request_body_sample())

# Main
args = parser.parse_args()

# Reads configuration.
config_path = 'rtr_config.yaml'
if args.config:
    config_path = args.config
    
with open(config_path) as f:
    config = yaml.load(f, Loader=yaml.FullLoader)

# Reads postman file.
postman = create_postman(config['postman_file']) 

if args.name:
    find_by_name(postman, args.parameters[0])
elif args.url:
    find_by_url(postman, args.parameters[0])
elif args.all:
    find_by_all(postman, args.parameters[0])
elif args.list:
    print_all_apis(postman)
elif args.export:
    export_request_sample(postman, args.parameters[0])
elif args.root:
    request_root(args.verbose)
else:
    request(postman, args.parameters, args.verbose)
