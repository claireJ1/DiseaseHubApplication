import sys
sys.path.insert(0, "package/")

import json
import boto3
import os
import base64
import requests
import re
from datetime import datetime

VALIDATION_URL = 'https://afzpve4n13.execute-api.ap-southeast-2.amazonaws.com/verify_token'

def handler(event, context):

    # Check token
    try:
        token = event['headers']['authorization']
        res = requests.post(VALIDATION_URL, headers={'Authorization': token})
    except Exception as e:
        return {
            'statusCode': res.status_code,
            'body': json.dumps(str(e))
        }
    
    body = json.loads(event['body'])
    
    # Get all the objects uploaded by team BRAVO 
    s3 = boto3.client('s3')
    objs = []
    objs_D = []

    try:
        objs = s3.list_objects_v2(Bucket=os.environ['GLOBAL_S3_NAME'],
                                   Prefix='H14B_B')['Contents']
        
        if (len(objs) == 0):
            return {
                'statusCode': 400,
                'body': json.dumps('No matching file with given prefix')
            }
        else:
            objs = list(filter(lambda x: x['Size'] > 6100 and x['Size'] < 500000, objs))

    except Exception as e:
        return {
            'statusCode': 400,
            'body': json.dumps('No matching file with given prefix')
        }
    
    # Get all the objects uploaded by team Echo
    try:
        objs_D = s3.list_objects_v2(Bucket=os.environ['GLOBAL_S3_NAME'],
                                   Prefix='H09A_ECHO/WHO/')['Contents']
        
        if (len(objs_D) == 0):
            return {
                'statusCode': 400,
                'body': json.dumps('No matching file with given prefix')
            }

    except Exception as e:
        return {
            'statusCode': 400,
            'body': json.dumps('No matching file with given prefix')
        }

    objs = objs + objs_D
    get_last_modified = lambda obj: int(obj['LastModified'].strftime('%s'))
    sort_objs = sorted(objs, key=get_last_modified, reverse=True)
    sort_objs.insert(0, {'Key': 'H14B_BRAVO_1681703779.json'})

    # Try to fetch 100 events based on the given input 
    events = []
    i = 0

    while len(events) < 100 and i < len(sort_objs):
        key = sort_objs[i]['Key']
        match_event = []
        print(key)

        try:
            file_obj = s3.get_object(Bucket=os.environ['GLOBAL_S3_NAME'], Key=key)
            file_content = json.loads(file_obj['Body'].read().decode('utf-8'))        
        except Exception as e:
                    return {
                        'statusCode': 500,
                        'body': json.dumps(str(e))
                    }

        if 'H14B' in key:
            match_event = fetch_event_from_Bravo_file(file_content, body)
        else:
            match_event = fetch_event_from_Echo_file(file_content, body)

        events = events + match_event
        i += 1
    
    if len(events) > 100:
        events = events[:100]
    
    return {
        'statusCode': '200',
        'body': json.dumps({'events': events})
    }

def fetch_event_from_Bravo_file(file_content, params):

    events = []

    # Fetch Team Beta's data
    if 'events' in file_content.keys():
        for event in file_content['events']:

            # Check if attribute has disease name
            if 'disease_name' in event['attribute'].keys():
                event['event_type'] = event['attribute']['disease_name']

            # Check diease anme
            if 'disease_name' in params.keys():
                if not re.search(params['disease_name'], event['event_type'], re.IGNORECASE):
                    continue
            
            # Unify the location attribute
            if 'region_name' in event['attribute'].keys():
                event['attribute']['location'] = event['attribute'].pop('region_name')
            elif 'country' in event['attribute'].keys():
                event['attribute']['location'] = event['attribute'].pop('country')

            # Check location
            if 'country_name' in params.keys():
                if not re.search(params['country_name'], event['attribute']['location'], re.IGNORECASE):
                    continue
            
            # Check time range
            if 'timerange_start' in params.keys() and 'timerange_end' in params.keys():
                event_start = string_to_datetime(params['timerange_start'])
                event_end = string_to_datetime(params['timerange_end'])
                event_datetime = string_to_datetime(event['time_object']['timestamp'])
                if not (event_start <= event_datetime and event_datetime <= event_end):
                    continue
            
            events.append(event)
    
    return events

def fetch_event_from_Echo_file(file_content, params):

    events = []

    for attr in file_content['events'][0]['attribute']:

        event = {}
        event['attribute'] = attr
        
        # Check if attribute has disease name
        if 'disease_name' in event['attribute'].keys():
            event['event_type'] = attr['disease_name']

        # Check diease anme
        if 'disease_name' in params.keys():
            if not re.search(params['disease_name'], event['event_type'], re.IGNORECASE):
                continue
        
        # check location
        if 'country_name' in params.keys() and 'location' in event['attribute'].keys():
            # try to get the location
            if not re.search(params['country_name'], event['attribute']['location'], re.IGNORECASE):
                continue
        
        # Create time object for event
        event['time_object'] = {}
        event['time_object']['timestamp'] = event['attribute']['date']
        
        # check time range
        if 'timerange_start' in params.keys() and 'timerange_end' in params.keys():
            event_start = string_to_datetime(params['timerange_start'])
            event_end = string_to_datetime(params['timerange_end'])
            event_datetime = string_to_datetime(event['time_object']['timestamp'])
            if not (event_start <= event_datetime and event_datetime <= event_end):
                continue
        
        events.append(event)
    
    return events


# def fetch_event_from_Delta_file(file_content, params):

#     event_list = []
#      # Fetch Team Delata's data
#     if 'events' in file_content.keys():
        
#         event = file_content['events'][0]

#         # Check it is a valid disease outbreak
#         if not 'attribute' in event.keys() or not 'disease' in event['attribute'].keys() or \
#            event['attribute']['disease'] == '':
#             return []

#         # Check diease anme
#         print(event['attribute']['disease'])
#         if 'disease_name' in params.keys():
#             if not re.search(params['disease_name'], event['attribute']['disease'], re.IGNORECASE):
#                 return []
#             else:
#                 event['event_type'] = event['attribute']['disease']

#         if 'country_name' in params.keys():

#             # try to get the location
#             location = ''
#             if 'region_name' in event['attribute'].keys():
#                 location = event['attribute']['region_name']
#                 event['attribute']['location'] = event['attribute'].pop('region_name')
#             elif 'country' in event['attribute'].keys():
#                 location = event['attribute']['country']
#                 event['attribute']['location'] = event['attribute'].pop('country')
#             elif 'location' in event['attribute'].keys():
#                 location = event['attribute']['location']

#             if not re.search(params['country_name'], location, re.IGNORECASE):
#                 return []
        
#         # Check time range
#         if 'timerange_start' in params.keys() and 'timerange_end' in params.keys():
#             event_start = string_to_datetime(params['timerange_start'])
#             event_end = string_to_datetime(params['timerange_end'])
#             event_datetime = string_to_datetime(event['time_object']['timestamp'])
#             if not (event_start <= event_datetime and event_datetime <= event_end):
#                 return []
        
#         event_list.append(event)
#         return event_list
            

def string_to_datetime(date_string):
    for fmt in ('%Y-%m-%d %H:%M:%S', '%Y', '%Y-%m-%d', '%d %B %Y'):
        try:
            return datetime.strptime(date_string, fmt)
        except:
            pass

    return datetime.strptime('1800', '%Y')
