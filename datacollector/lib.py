from datacollector.models import *

import datetime
import hashlib
import os
import re


def validate_authorization_header(headers):
    '''Params:
    headers : dict of request headers and keys
    
    Return the auth_token if there is a valid Authorization header; 
    None otherwise.
    '''
    auth_header_name = 'HTTP_AUTHORIZATION'
    if auth_header_name not in headers:     
        return None
    
    auth_header = headers[auth_header_name]
    regex_header = re.compile(r'^Bearer ([a-zA-Z0-9]+)$')
    if not auth_header or not regex_header.findall(auth_header):
        return None
    
    return regex_header.findall(auth_header)[0]

def authenticate(auth_token):
    '''Params:
    auth_token : string. The hex access token.
    
    Return a Subject object if the auth_token is a valid; False otherwise.
    '''
    today = datetime.datetime.now()
    rows = Subject.objects.filter(auth_token=auth_token, auth_token_expirydate__gt=today)
    if len(rows) == 1:
        return rows[0]
    return False

def generate_md5_checksum(filepath):
    '''Params:
    filepath : string, absolute path to a file
    
    Return:
    If the file exists, an md5 hash of the raw file data. Otherwise, None.
    '''
    
    hash_md5 = hashlib.md5()
    if os.path.exists(filepath):
        with open(filepath, "rb") as f:
            # Read in sequential chunks of bytes instead of the whole file 
            # at once, in case the file is too big
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    return None

