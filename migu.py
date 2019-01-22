#!/usr/bin/env python3

import argparse
import json
import m3u8
import requests
import subprocess
import sys
import urllib

def migu_video(id):
    cmd=['phantomjs','migu_video.js','https://tv.miguvideo.com/#/video/tv/%d'%id]
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
                if rate_url:
                    return rate_url
    else:
        return

def migu_music_1(id):
    base_url='https://c.musicapp.migu.cn/MIGUM2.0/v2.0'
    resp=requests.get('%s/content/queryConcertSummary.do'%base_url,params={'columnId':id}).json()
    data=resp['data']
    if data['concertStatus']==2:
        live_id=data['liveId']
        concert_id=data['concertId']
        resp=requests.get('%s/danmaku/liveServerHosts.do'%base_url,params={'liveId':live_id,'concertId':concert_id,'liveType':1,'rateLevel':4}).json()
        return resp['data']['hosts']['liveHostAddr']
    else:
        return

def migu_music_2(id):
    base_url='https://m.music.migu.cn/migu/remoting'
    resp=requests.get('%s/live_control_tag'%base_url,params={'pageid':id,'pagediv':'LIVE1'}).json()
    data=resp['data']
    if data['contentType']==20:
        content_value=data['contentValue'].split('&')
        cid=content_value[0]
        begin=content_value[1]
        end=content_value[2]
        resp=requests.get('%s/get_playbackurl_tag'%base_url,params={'cid':cid,'pid':2028593040,'rate':4,'begin':begin,'end':end}).json()
        return resp['playurl']
    else:
        return

def main():
    parser=argparse.ArgumentParser()
    add=parser.add_argument
    add('platform',choices=['migu_video','migu_music_1','migu_music_2','1','2','3'])
    add('id',type=int)
    args=parser.parse_args()
    if args.platform in ['1','2','3']:
        real_platform={'1':'migu_video','2':'migu_music_1','3':'migu_music_2'}
        args.platform=real_platform[args.platform]
    methods={'migu_video':migu_video,'migu_music_1':migu_music_1,'migu_music_2':migu_music_2}
    method=methods.get(args.platform)
    url=method(args.id)
    if url:
        try:
            print(m3u8.load(url).playlists[0].absolute_uri)
        except urllib.error.HTTPError as e:
            print(e)
            print('Maybe you are outside mainland China?')

if __name__=='__main__':
    main()
