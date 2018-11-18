#!/usr/bin/env python3

import argparse
import json
import m3u8
import requests
import subprocess
import sys
import urllib

def main():
    parser=argparse.ArgumentParser()
    add=parser.add_argument
    add('id',type=int)
    args=parser.parse_args()
    cmd=['phantomjs','miguvideo.js','https://tv.miguvideo.com/#/video/tv/%d'%args.id]
    try:
        data=json.loads(subprocess.check_output(cmd).decode('utf-8'))
    except FileNotFoundError:
        sys.exit('PhantomJS missing. See details on https://phantomjs.org/download.html\nAdding PhantomJS to PATH is recommended after downloading it.')
    headers={}
    for dict in data['headers']:
        headers[dict['name']]=dict['value']
    resp=requests.get(data['content'].replace('http://','https://'),headers=headers).json()
    if resp['body']['liveStatus']=='3':
        resp=requests.get(data['url_h'].replace('http://','https://'),headers=headers).json()
        for rate_value in ['4','3','2','1']:
            rate=[dict for dict in resp['body']['rates'] if dict['rateValue']==rate_value]
            if len(rate)==1:
                rate_url=rate[0]['rateUrl']
                if rate_url!='':
                    break
        try:
            print(m3u8.load(rate_url).playlists[0].absolute_uri)
        except urllib.error.HTTPError as e:
            print(e)
            print('Maybe you are outside mainland China?')

if __name__=='__main__':
    main()
