#!/usr/bin/env python3

import argparse
import json
import m3u8
import pathlib
import requests
import subprocess
import sys
import urllib.error
from urllib import parse

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
    resp=requests.get('%s/live_play_tag'%base_url,params={'mapId':id}).json()
    live_play_visual=resp['retMsg']['livePlayVisual'][0]
    content_id=live_play_visual['contentId']
    content=live_play_visual['content']
    if content=='拉流':
        ll_time=live_play_visual['llTime'].split('&')
        begin=ll_time[0]
        end=ll_time[1]
        resp=requests.get('%s/get_playbackurl_tag'%base_url,params={'cid':content_id,'pid':2028593040,'rate':4,'begin':begin,'end':end}).json()
        return resp['playurl']
    elif content=='MVID':
        resp=requests.post('%s/mv_detail_tag'%base_url,data={'cpid':content_id}).json()
        for entry in resp['data']['videoUrlMap']['entry']:
            if entry['key'] in ['050012','050015']:
                return entry['value']
        return
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
        if pathlib.Path(parse.urlparse(url).path).suffix=='.m3u8':
            try:
                print(m3u8.load(url).playlists[0].absolute_uri)
            except urllib.error.HTTPError as e:
                print(e)
                print('Maybe you are outside mainland China?')
        else:
            print(url)

if __name__=='__main__':
    main()
