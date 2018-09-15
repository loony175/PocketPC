#!/usr/bin/env python3

import argparse
import base64
import json
import pathlib
import re
import requests
import subprocess
import sys
import yaml

HEADERS={'User-Agent':'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1'}

def main():
    parser=argparse.ArgumentParser()
    add=parser.add_argument
    add('member')
    add('-c','--config',type=pathlib.Path,default='douyin.yml')
    add('-q','--quiet',action='store_true')
    add('-n','--sum',action='store_true')
    add('-N','--no-sum',action='store_true')
    args=parser.parse_args()
    user_id=yaml.load(open(args.config,'r').read())[args.member]
    max_cursor=0
    cmd=['node','byted-acrawler.js',str(user_id)]
    try:
        signature=subprocess.check_output(cmd).decode('utf-8')
    except FileNotFoundError:
        sys.exit('Node.js missing. See details on https://nodejs.org/en/download/current/')
    resp=requests.get('https://www.douyin.com/share/user/%d'%user_id,headers=HEADERS).text
    dytk=re.search('dytk: \'(?P<dytk>.*)\'',resp).group('dytk')
    has_more=1
    intermediate=[]
    while has_more==1:
        resp=requests.get('https://www.amemv.com/aweme/v1/aweme/post/',params={'user_id':str(user_id),'count':'21','max_cursor':str(max_cursor),'aid':'1128','_signature':signature,'dytk':dytk},headers=HEADERS).json()
        for dict in resp['aweme_list']:
            info={}
            share_desc={}
            share_desc['raw']=dict['share_info']['share_desc']
            share_desc['base64']=bytes.decode(base64.b64encode(str.encode(share_desc['raw'])))
            info['share_desc']=share_desc
            info['play_addr']=dict['video']['play_addr']['url_list'][0]
            info['height']=dict['video']['height']
            info['cover']=dict['video']['cover']['url_list'][0]
            info['dynamic_cover']=dict['video']['dynamic_cover']['url_list'][0].replace('http://','https://')
            info['width']=dict['video']['width']
            intermediate.append(info)
        has_more=resp['has_more']
        max_cursor=resp['max_cursor']
    if args.quiet:
        stdout=[]
        for dict in intermediate:
            info={}
            info['share_desc']=dict['share_desc']['raw']
            info['play_addr']=dict['play_addr']
            stdout.append(info)
    else:
        stdout=intermediate
    if not args.sum:
        print(json.dumps(stdout,indent=2,ensure_ascii=False))
        if not args.no_sum:
            print('%d objects found.'%len(stdout))
    else:
        print(len(stdout))

if __name__=='__main__':
    main()
