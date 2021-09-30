# Backup slack messages

import logging
import os
import pickle
import time
import requests
import cgi

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


def fetch_conversations_history(client, channel_id, limit, cursor):
    res = None
    while True:
        try:
            res = client.conversations_history(channel=channel_id, limit=limit, cursor=cursor)
            break
        except SlackApiError as e:
            if e.response['ok'] == False and 'Retry-After' in e.response.headers and e.response.headers['Retry-After']:
                wait_time = float(e.response.headers["Retry-After"])
                print('Hit rate limit, backing off for ' + str(wait_time) + ' seconds')
                time.sleep(wait_time)
                continue
            else:
                raise e
    return res


def fetch_history(client, channel_id, output_path):
    history = []
    next_cursor = None
    while True:
        res = fetch_conversations_history(client, channel_id, 200, next_cursor)
        assert res['ok'] == True
        history += res['messages']
        if not res['has_more']:
            break
        next_cursor = res['response_metadata']['next_cursor']

    with open(output_path, 'wb') as handle:
        pickle.dump(history, handle, protocol=pickle.HIGHEST_PROTOCOL)

    return len(history)


def fetch_conversations_list(client, types):
    conversations = None
    while True:
        try:
            conversations = client.conversations_list(types=types)
            break
        except SlackApiError as e:
            if e.response['ok'] == False and 'Retry-After' in e.response.headers and e.response.headers['Retry-After']:
                print('Hit rate limit, backing off')
                wait_time = float(e.response.headers["Retry-After"])
                time.sleep(wait_time)
                continue
            else:
                raise e

    return conversations

# TODO: NOT handling pagination here
def fetch_users_list(client):
    users = None
    while True:
        try:
            users = client.users_list()
            break
        except SlackApiError as e:
            if e.response['ok'] == False and 'Retry-After' in e.response.headers and e.response.headers['Retry-After']:
                print('Hit rate limit, backing off')
                wait_time = float(e.response.headers["Retry-After"])
                time.sleep(wait_time)
                continue
            else:
                raise e

    return users

# TODO: NOT handling pagination here
def fetch_files(client, cid, output_dir, token):
    fls = None
    count = 0
    while True:
        try:
            fls = client.files_list(channel=cid, limit=200)['files']
            break
        except SlackApiError as e:
            if e.response['ok'] == False and 'Retry-After' in e.response.headers and e.response.headers['Retry-After']:
                print('Hit rate limit, backing off')
                wait_time = float(e.response.headers["Retry-After"])
                time.sleep(wait_time)
                continue
            else:
                raise e

    meta_path = os.path.join(output_dir, 'files.meta.%s.pickle' % (cid))
    with open(meta_path, 'wb') as handle:
        pickle.dump(fls, handle, protocol=pickle.HIGHEST_PROTOCOL)

    for fl in fls:
        if 'url_private_download' not in fl:
            continue
        url = fl['url_private_download']
        resp = requests.get(url, headers={'Authorization': 'Bearer %s' % token})
        assert resp.status_code == 200
        original_name = 'unknown'
        if 'Content-Disposition' in resp.headers:
            params = cgi.parse_header(resp.headers['Content-Disposition'])[-1]
            if 'filename' in params:
                original_name = params['filename']

        output_path = os.path.join(output_dir, 'file.%s.%s' % (fl['id'], original_name))
        open(output_path, 'wb').write(resp.content)
        count += 1
        time.sleep(0.1)

    return count



user_token = os.environ.get("SLACK_TOKEN")
if not user_token:
    print('Set the SLACK_TOKEN environment variable')
    exit(-1)

client = WebClient(token=user_token)
logger = logging.getLogger(__name__)

channel_ids = []
channel_names = []
# Get channel ids
try:
    # TODO: Not handling pagingated converation list responses
    conversations = fetch_conversations_list(client, 'public_channel,private_channel,mpim,im')
    assert conversations['ok'] == True

    for channel in conversations['channels']:
        channel_ids.append(channel['id'])
        name = None
        if 'is_im' in channel and channel['is_im']:
            name = channel['user']
        else:
            name = channel['name']
        channel_names.append(name)

    print(channel_ids)

    

    for i in range(len(channel_ids)):
        cid = channel_ids[i]
        cname = channel_names[i]
        output_path = './history/' + cname + '.pickle'

        count = fetch_history(client, cid, output_path)

        print('Fetched ' + str(count) + ' messages from ' + cname)


    users_meta = fetch_users_list(client)

    with open('./history/user-metadata.pickle', 'wb') as handle:
        pickle.dump(users_meta, handle, protocol=pickle.HIGHEST_PROTOCOL)
    print('Fetched users metadata')

    # Download files
    for i in range(len(channel_ids)):
        cid = channel_ids[i]
        cname = channel_names[i]
        if cname == 'USLACKBOT':
            continue

        count = fetch_files(client, cid, './history/', user_token)

        print('Fetched ' + str(count) + ' files from ' + cname)



except SlackApiError as e:
    print(f"Error: {e}")



