#!/usr/bin/env python3

import argparse
import bs4
from dns import resolver
import json
import logging
import pathlib
import platform
import random
import re
import requests
import subprocess
import sys
import time
from urllib import parse

HEADERS={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.67 Safari/537.36'}

def live48(room_id):
    time.sleep(1)
    room_ids={'snh':'9999','bej':'2001','gnz':'3001','shy':'6001','ckg':'8001'}
    try:
        room_id_=room_ids[room_id]
    except KeyError:
        return
    return 'http://cyflv.ckg48.com/chaoqing/%s.flv'%room_id_

def bilibili(room_id):
    room_ids={'snh':'48','bej':'383045','gnz':'391199','shy':'2827401','ckg':'6015846'}
    try:
        room_id_=room_ids[room_id]
    except KeyError:
        room_id_=room_id
    while True:
        while True:
            try:
                resp=requests.get('https://live.bilibili.com/%s'%room_id_,headers=HEADERS).text
                break
            except Exception as e:
                logging.warning('[Bilibili] %s: %s'%(room_id_,e))
        for item in bs4.BeautifulSoup(resp,'html.parser').find_all('script'):
            m=re.match(r'^window\.__NEPTUNE_IS_MY_WAIFU__=(?P<json>.*)$',item.get_text())
            if m:
                data=json.loads(m.group('json'))
                break
        try:
            return data['playUrlRes']['data']['durl'][0]['url']
        except KeyError:
            logging.warning('[Bilibili] %s not online.'%room_id_)

def douyu(room_id):
    room_ids={'snh':'56229','bej':'668687','gnz':'668530','shy':'1536837','ckg':'3532048'}
    try:
        room_id_=room_ids[room_id]
    except KeyError:
        room_id_=room_id
    cmd=['you-get','--json','https://www.douyu.com/%s'%room_id_]
    while True:
        try:
            data=subprocess.check_output(cmd).decode('utf-8')
            break
        except subprocess.CalledProcessError:
            time.sleep(5)
    return re.search('(https?://.*\.flv[^\']*)',data).group(1).replace('http://','https://')

def youtube(room_id):
    room_ids={'snh':'UClwRU9iNX7UbzyuVzvZTSkA'}
    try:
        room_id_=room_ids[room_id]
    except KeyError:
        if room_id in ['bej','gnz','shy','ckg']:
            return
        else:
            room_id_=room_id
    cmd=['youtube-dl','-j','https://www.youtube.com/channel/%s/live'%room_id_]
    while True:
        try:
            data=json.loads(subprocess.check_output(cmd).decode('utf-8'))
            break
        except subprocess.CalledProcessError:
            pass
    return data['url']

def yizhibo(room_id):
    room_ids={'snh':'6009826','bej':'48461479','gnz':'51699551','shy':'186412394','ckg':'275204728'}
    try:
        room_id_=room_ids[room_id]
    except KeyError:
        room_id_=room_id
    url=None
    while True:
        while True:
            try:
                resp=requests.get('https://www.yizhibo.com/member/personel/user_works',params={'memberid':room_id_}).text
                break
            except Exception as e:
                logging.warning('[Yizhibo] %s: %s'%(room_id_,e))
        item=bs4.BeautifulSoup(resp,'html.parser').find_all('div',class_='index_img fl pr')[0]
        for child in item.children:
            if child.name=='div' and child.get_text().strip()=='回放':
                logging.warning('[Yizhibo] %s not online.'%room_id_)
                break
            if child.name=='a':
                url='https://www.yizhibo.com%s'%child['href']
        if url:
            break
    cmd=['youtube-dl','-j',url]
    data=json.loads(subprocess.check_output(cmd).decode('utf-8'))
    return data['url'].replace('http://','https://')

def miguvideo(room_id):
    if room_id in ['snh','bej','gnz','shy','ckg']:
        return
    cmd=['phantomjs','miguvideo.js','https://tv.miguvideo.com/#/video/tv/%s'%room_id]
    while True:
        data=json.loads(subprocess.check_output(cmd).decode('utf-8'))
        headers={}
        for dict in data['headers']:
            headers[dict['name']]=dict['value']
        while True:
            try:
                resp=requests.get(data['content'].replace('http://','https://'),headers=headers).json()
                break
            except Exception as e:
                logging.warning('[MiguVideo] %s: %s'%(room_id,e))
        if resp['body']['liveStatus']=='2':
            while True:
                try:
                    resp=requests.get(data['content'].replace('http://','https://'),headers=headers).json()
                    break
                except Exception as e:
                    logging.warning('[MiguVideo] %s: %s'%(room_id,e))
            return [dict['rateUrl'] for dict in resp['body']['rates'] if dict['rateUrl']!=''][0]
        else:
            logging.warning('[MiguVideo] %s not online.'%room_id)
            time.sleep(5)

def main():
    parser=argparse.ArgumentParser()
    add=parser.add_argument
    add('arguments')
    add('--debug',action='store_true')
    add('--log',action='store_true')
    add('-r','--remote')
    add('-t','--test',action='store_true')
    add('-c','--convert',action='store_true')
    args=parser.parse_args()
    logging.basicConfig(level=logging.WARNING,format='%(levelname)s: %(message)s')
    if args.test:
        if platform.system()=='Windows':
            args.remote='NUL'
        else:
            args.remote='/dev/null'
    platform_=None
    method=None
    args_=args.arguments.split(',')
    if len(args_)==2 and args_[0] in ['48live','bilibili','douyu','youtube','yizhibo','miguvideo','1','2','3','4','5','6']:
        platform_=args_[0]
        room_id=args_[1]
        if platform_ in ['1','2','3','4','5','6']:
            real_platform={'1':'48live','2':'bilibili','3':'douyu','4':'youtube','5':'yizhibo','6':'miguvideo'}
            platform_=real_platform[platform_]
        methods={'48live':live48,'bilibili':bilibili,'douyu':douyu,'youtube':youtube,'yizhibo':yizhibo,'miguvideo':miguvideo}
        method=methods.get(platform_)
    input=None
    should_retry=False
    begin_time=int(time.time())
    p=None
    f=None
    regular_pattern=re.compile(r'Opening \'.*\' for reading')
    retry_pattern=re.compile(r'(403 Forbidden|404 Not Found)')
    error_pattern=re.compile(r'(Non-monotonous DTS in output stream|st:1 invalid dropping|invalid dropping st:1)')
    if args.remote is None:
        if platform_:
            platforms={'48live':'48Live','bilibili':'Bilibili','douyu':'Douyu','youtube':'YouTube','yizhibo':'Yizhibo','miguvideo':'MiguVideo'}
            platform_name=platforms[platform_]
            if room_id in ['snh','bej','gnz','shy','ckg']:
                room_name='%s48'%room_id.upper()
            else:
                room_name=room_id
        else:
            url_parser=parse.urlparse(args.arguments)
            platform_name=url_parser.hostname
            room_name=pathlib.Path(url_parser.path).stem
        dir=pathlib.Path('%d-%s-%s'%(int(time.time()),platform_name,room_name))
        dir.mkdir()
        count=1
    try:
        while True:
            sum_error=0
            if platform_:
                try:
                    if method==bilibili:
                        if input is None or should_retry:
                            input=method(room_id)
                            should_retry=False
                    elif method==youtube:
                        now=int(time.time())
                        if input is None or now-begin_time>=21600:
                            input=method(room_id)
                            begin_time=int(time.time())
                    elif method==miguvideo:
                        now=int(time.time())
                        if input is None or now-begin_time>=7200:
                            input=method(room_id)
                            begin_time=int(time.time())
                    else:
                        input=method(room_id)
                except FileNotFoundError:
                    if args.remote is None:
                        dir.rmdir()
                    if method==miguvideo:
                        message='PhantomJS missing. See details on https://phantomjs.org/download.html\nAdding PhantomJS to PATH is recommended after downloading it.'
                    else:
                        message='Some required tools missing. Run \'pip install -U you-get youtube-dl\' to install them.'
                    sys.exit(message)
                if input is None:
                    if args.remote is None:
                        dir.rmdir()
                    sys.exit('Invalid room ID %s.'%room_id)
            else:
                time.sleep(1)
                input=args.arguments
            if args.debug:
                if args.remote is None:
                    dir.rmdir()
                host=parse.urlparse(input).hostname
                while True:
                    try:
                        ans=resolver.query(host,'A').response.answer
                        break
                    except dns.resolver.NXDOMAIN:
                        pass
                ips=[]
                for line in ans:
                    for item in line.items:
                        try:
                            ips.append(item.address)
                        except AttributeError:
                            pass
                ip=random.choice(ips)
                resp=requests.get('https://freeapi.ipip.net/%s'%ip).json()
                info={}
                info['url']=input
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
                if args.log:
                    log=dir/f'{count}.log'
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
            if args.remote is None and args.log:
                f=open(log,'w')
            for line in p.stderr:
                if not regular_pattern.search(line):
                    sys.stderr.write(line)
                    sys.stderr.flush()
                    if args.remote is None and args.log:
                        f.write(line)
                if method==bilibili and retry_pattern.search(line):
                    should_retry=True
                if error_pattern.search(line):
                    sum_error+=1
                    if sum_error>=2:
                        p.terminate()
                        break
            p=None
            if args.remote is None:
                if args.log:
                    f.close()
                    f=None
                if output.exists() and output.stat().st_size<=1572864:
                    while True:
                        try:
                            output.unlink()
                            break
                        except PermissionError:
                            pass
                if args.log and not output.exists():
                    while True:
                        try:
                            log.unlink()
                            break
                        except PermissionError:
                            pass
    except KeyboardInterrupt:
        if p:
            p.terminate()
        if f:
            f.close()
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
