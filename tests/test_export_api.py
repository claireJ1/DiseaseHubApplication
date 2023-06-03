import pytest
import json
import sys
import datetime

sys.path.append('./code/exportS3')
from handler import fetch_event_from_Bravo_file, fetch_event_from_Echo_file

def test_cdc_datas():
    f = open('./tests/H14B_Bravo_1.json', 'r')
    file_content = json.loads(f.read())
    f.close()

    params = {'disease_name': 'coronavirus'}

    # test no events fetch from cdc since no event type(disease name) given 
    events = fetch_event_from_Bravo_file(file_content, params)
    assert len(events) == 0

def test_global_incident_datas():
    f = open('./tests/H14B_Bravo_2.json', 'r')
    file_content = json.loads(f.read())
    f.close()

    # test global incident data with Coronavirous 
    params = {'disease_name': 'coronavirus'}
    
    events = fetch_event_from_Bravo_file(file_content, params)
    assert len(events) == 6

    for event in events:
        assert event['event_type'] == 'Coronavirus'
    
    # test fetched data base on location given 
    params = {'country_name': 'united states'}
    
    events = fetch_event_from_Bravo_file(file_content, params)
    assert len(events) == 3

    for event in events:
        assert event['attribute']['location'] == 'United States'
    
    # test fetched data base on timerange given 
    params = {'timerange_start': "2023-03-27", 'timerange_end': "2023-03-28"}

    events = fetch_event_from_Bravo_file(file_content, params)
    assert len(events) == 10

    for event in events:
        event_time = datetime.datetime.strptime(event['time_object']['timestamp'], '%Y-%m-%d %H:%M:%S')
        assert event_time >= datetime.datetime(2023, 3, 27)
        assert event_time <= datetime.datetime(2023, 3, 28)

    # test fetched data with all three attributes
    params = {'country_name': 'united kingdom', 'disease_name': 'coronavirus', 'timerange_start': "2023-03-27", 'timerange_end': "2023-03-30"}

    events = fetch_event_from_Bravo_file(file_content, params)
    assert len(events) == 2

    for event in events:
        # test time range
        event_time = datetime.datetime.strptime(event['time_object']['timestamp'], '%Y-%m-%d %H:%M:%S')
        assert event_time >= datetime.datetime(2023, 3, 27)
        assert event_time <= datetime.datetime(2023, 3, 30)

        # test disease and country
        assert event['event_type'] == 'Coronavirus'
        assert event['attribute']['location'] == 'United Kingdom'


def test_ECDC():
    f = open('./tests/H14B_Bravo_3.json', 'r')
    file_content = json.loads(f.read())
    f.close()
    
    # test ECDC data with Syphilis
    params = {'disease_name': 'syphilis'}

    events = fetch_event_from_Bravo_file(file_content, params)
    assert len(events) == 18

    for event in events:
        assert 'Syphilis' in event['event_type']
    
    # test fetched data base on location given
    params = {'country_name': 'slovakia'}
     
    events = fetch_event_from_Bravo_file(file_content, params)
    assert len(events) == 1

    for event in events:
        assert event['attribute']['location'] == 'Slovakia'
    
    # test fetched data base on timerange given 
    params = {'timerange_start': '2019-01-01', 'timerange_end': "2020-12-31"}

    events = fetch_event_from_Bravo_file(file_content, params)
    assert len(events) == 10

    for event in events:
        event_time = datetime.datetime.strptime(event['time_object']['timestamp'], '%Y')
        assert event_time >= datetime.datetime(2019, 1, 1)
        assert event_time <= datetime.datetime(2020, 12, 31)
    
    # test fetched data base on timerange and disease
    params = {'disease_name': 'syphilis', 'timerange_start': "2004-01-01", 'timerange_end': "2004-12-31"}

    events = fetch_event_from_Bravo_file(file_content, params)
    assert len(events) == 8

    for event in events:
        # check time range
        event_time = datetime.datetime.strptime(event['time_object']['timestamp'], '%Y')
        assert event_time >= datetime.datetime(2004, 1, 1)
        assert event_time <= datetime.datetime(2004, 12, 31)

        # check disease name
        assert 'Syphilis' in event['event_type']

def test_Echo():
    f = open('./tests/H09A_Echo_1.json', 'r')
    file_content = json.loads(f.read())
    f.close()
    
    # test Delta data with Syphilis
    params = {'disease_name': 'Measles'}

    events = fetch_event_from_Echo_file(file_content, params)
    assert len(events) == 9

    for event in events:
        assert 'Measles' in event['event_type']

    # test fetched data base on location given
    params = {'country_name': 'uganda'}
     
    events = fetch_event_from_Echo_file(file_content, params)
    assert len(events) == 8

    for event in events:
        assert'Uganda' in event['attribute']['location']

    # test fetched data base on timerange given 
    params = {'timerange_start': "2022-07-01", 'timerange_end': "2022-08-01"}

    events = fetch_event_from_Echo_file(file_content, params)
    assert len(events) == 4

    for event in events:
        # check time range
        event_time = datetime.datetime.strptime(event['time_object']['timestamp'], '%d %B %Y')
        assert event_time >= datetime.datetime(2022, 7, 1)
        assert event_time <= datetime.datetime(2022, 8, 1)

    # test fetched data base on timerange and country
    params = {'disease_name': 'Ebola Disease', 'country_name': 'uganda'}

    events = fetch_event_from_Echo_file(file_content, params)
    assert len(events) == 6

    for event in events:
        assert 'Ebola' in event['event_type']
        assert 'Uganda' in event['attribute']['location']

# def test_Delta_file_2():
#     f = open('./tests/H14B_Delta_2.json', 'r')
#     file_content = json.loads(f.read())
#     f.close()
    
#     # test Delta data with Syphilis
#     params = {'disease_name': 'monkeypox'}

#     events = fetch_event_from_Delta_file(file_content, params)
#     assert len(events) == 1

#     for event in events:
#         assert 'monkeypox' in event['event_type']

#     # test fetched data base on location given
#     params = {'country_name': 'Korea'}
     
#     events = fetch_event_from_Delta_file(file_content, params)
#     assert len(events) == 1

#     for event in events:
#         assert 'Korea' in event['attribute']['location']

#     # test fetched data base on timerange and country
#     params = {'country_name': 'korea', 'timerange_start': "2023-04-11", 'timerange_end': "2023-04-12"}

#     events = fetch_event_from_Delta_file(file_content, params)
#     assert len(events) == 1


