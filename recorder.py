#!/usr/bin/env python3

import argparse
from dns import resolver
import json
import pathlib
import platform
import random
import re
import requests
import subprocess
import sys
import time
from urllib import parse

def live48(group_name):
    time.sleep(1)
    id={'snh48':9999,'bej48':2001,'gnz48':3001,'shy48':6001,'ckg48':8001}
    return 'http://cyflv.ckg48.com/chaoqing/%d.flv'%id[group_name]

def bilibili(group_name):
    id={'snh48':48,'bej48':383045,'gnz48':391199,'shy48':2827401,'ckg48':6015846}
    cmd=['you-get','--json','https://live.bilibili.com/%d'%id[group_name]]
    while True:
        try:
            data=json.loads(subprocess.check_output(cmd).decode('utf-8'))
            break
        except subprocess.CalledProcessError:
            pass
    return data['streams']['live']['src'][0]

def douyu(group_name):
    id={'snh48':56229,'bej48':668687,'gnz48':668530,'shy48':1536837,'ckg48':3532048}
    cmd=['you-get','--json','https://www.douyu.com/%d'%id[group_name]]
    while True:
        try:
            data=subprocess.check_output(cmd).decode('utf-8')
            break
        except subprocess.CalledProcessError:
            time.sleep(5)
    return re.search('(https?://.*\.flv[^\']*)',data).group(1).replace('http://','https://')

def youtube(group_name):
    id={'snh48':'UClwRU9iNX7UbzyuVzvZTSkA'}
    cmd=['youtube-dl','-j','https://www.youtube.com/channel/%s/live'%id[group_name]]
    while True:
        try:
            data=json.loads(subprocess.check_output(cmd).decode('utf-8'))
            break
        except subprocess.CalledProcessError:
            pass
    return data['url']

def main():
    parser=argparse.ArgumentParser()
    add=parser.add_argument
    add('platform',choices=['48live','bilibili','douyu','youtube','1','2','3','4'])
    add('group_name',choices=['snh48','bej48','gnz48','shy48','ckg48','1','2','3','4','5'])
    add('--debug',action='store_true')
    add('-r','--remote')
    add('-t','--test',action='store_true')
    add('-c','--convert',action='store_true')
    args=parser.parse_args()
    if args.test:
        if platform.system()=='Windows':
            args.remote='NUL'
        else:
            args.remote='/dev/null'
    real_platform={'1':'48live','2':'bilibili','3':'douyu','4':'youtube'}
    real_group_name={'1':'snh48','2':'bej48','3':'gnz48','4':'shy48','5':'ckg48'}
    for num in ['1','2','3','4','5']:
        if args.platform==num:
            args.platform=real_platform[args.platform]
        if args.group_name==num:
            args.group_name=real_group_name[args.group_name]
    dict={'48live':live48,'bilibili':bilibili,'douyu':douyu,'youtube':youtube}
    method=dict.get(args.platform)
    input=None
    should_retry=False
    begin_time=int(time.time())
    p=None
    regular_pattern=re.compile('Opening \'.*\' for reading')
    retry_pattern=re.compile(r'(403 Forbidden|404 Not Found)')
    error_pattern=re.compile(r'(Non-monotonous DTS in output stream|st:1 invalid dropping|invalid dropping st:1)')
    if args.remote is None:
        count=1
        platform_={'48live':'48Live','bilibili':'Bilibili','douyu':'Douyu','youtube':'YouTube'}
        group_name={'snh48':'SNH48','bej48':'BEJ48','gnz48':'GNZ48','shy48':'SHY48','ckg48':'CKG48'}
        dir=pathlib.Path('%d-%s-%s'%(int(time.time()),platform_[args.platform],group_name[args.group_name]))
        dir.mkdir()
    try:
        while True:
            sum_error=0
            try:
                if method==bilibili:
                    if input is None or should_retry:
                        input=method(args.group_name)
                        should_retry=False
                elif method==youtube:
                    now=int(time.time())
                    if input is None or now-begin_time>=21600:
                        input=method(args.group_name)
                        begin_time=int(time.time())
                else:
                    input=method(args.group_name)
            except FileNotFoundError:
                if args.remote is None:
                    dir.rmdir()
                sys.exit('Some required tools missing. Run \'pip install -U youtube-dl you-get\' to install them.')
            if args.debug:
                if args.remote is None:
                    dir.rmdir()
                host=parse.urlparse(input).hostname
                ips=[]
                for line in resolver.query(host,'A').response.answer:
                    for item in line.items:
                        try:
                            ips.append(item.address)
                        except AttributeError:
                            pass
                ip=random.choice(ips)
                resp=requests.get('https://freeapi.ipip.net/%s'%ip).json()
                info={}
                info['host']=host
                info['ip']=ip
                info['country']=resp[0]
                info['province']=resp[1]
                info['city']=resp[2]
                info['county']=resp[3]
                info['idc']=resp[4]
                sys.exit(json.dumps(info,indent=2,ensure_ascii=False))
            if args.remote is None:
                file=dir/f'{count}.ts'
                if file.exists():
                    count+=1
                output=dir/f'{count}.ts'
                cmd=['ffmpeg','-hide_banner','-y','-i',input,'-c','copy',output.as_posix()]
            else:
                output=args.remote
                cmd=['ffmpeg','-hide_banner','-y','-i',input,'-c','copy','-bsf:a','aac_adtstoasc','-f','flv',output]
            try:
                p=subprocess.Popen(cmd,stderr=subprocess.PIPE,bufsize=1,universal_newlines=True,encoding='utf-8')
            except FileNotFoundError:
                if args.remote is None:
                    dir.rmdir()
                sys.exit('FFmpeg missing. See details on https://ffmpeg.org/download.html\nAdding FFmpeg to PATH is recommended after downloading it.')
            for line in p.stderr:
                if not regular_pattern.search(line):
                    sys.stderr.write(line)
                    sys.stderr.flush()
                if method==bilibili and retry_pattern.search(line):
                    should_retry=True
                if error_pattern.search(line):
                    sum_error+=1
                    if sum_error>=2:
                        p.terminate()
                        break
            p=None
            if args.remote is None and output.exists() and output.stat().st_size<=1572864:
                while True:
                    try:
                        output.unlink()
                        break
                    except PermissionError:
                        pass
    except KeyboardInterrupt:
        if p:
            p.terminate()
        if args.remote is None:
            if len(list(dir.iterdir()))==0:
                dir.rmdir()
            else:
                if args.convert:
                    for num in range(1,count+1):
                        file=dir/f'{num}.ts'
                        if file.exists():
                            input=file
                            output=dir/f'{num}.mp4'
                            cmd=['ffmpeg','-hide_banner','-y','-i',input.as_posix(),'-c','copy','-bsf:a','aac_adtstoasc','-movflags','faststart',output.as_posix()]
                            try:
                                subprocess.run(cmd)
                            except KeyboardInterrupt:
                                break

if __name__=='__main__':
    main()
