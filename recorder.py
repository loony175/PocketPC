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

USER_AGENT='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36'

def live48(room_id,format,has_interval):
    if has_interval:
        time.sleep(1)
    room_ids={'snh':'9999','bej':'2001','gnz':'3001','shy':'6001','ckg':'8001'}
    try:
        room_id_=room_ids[room_id]
    except KeyError:
        return
    if format=='flv':
        protocol='http'
        path='%s.flv'%room_id_
    elif format=='rtmp':
        protocol='rtmp'
        path=room_id_
    return '%s://cyflv.ckg48.com/gaoqing/%s'%(protocol,path)

def bilibili(room_id,stream,has_interval):
    if has_interval:
        time.sleep(1)
    room_ids={'snh':'48','bej':'383045','gnz':'391199','shy':'2827401','ckg':'6015846'}
    try:
        room_id_=room_ids[room_id]
    except KeyError:
        room_id_=room_id
    base_url='https://api.live.bilibili.com/room/v1/Room'
    while True:
        try:
            resp=requests.get('%s/room_init'%base_url,params={'id':room_id_}).json()
            real_room_id=str(resp['data']['room_id'])
            resp=requests.get('%s/playUrl'%base_url,params={'cid':real_room_id,'quality':4,'platform':'web'}).json()
            break
        except Exception as e:
            logging.warning('[Bilibili] %s: %s'%(room_id_,e))
    return resp['data']['durl'][stream]['url'],room_id_

def douyu(room_id):
    room_ids={'snh':'56229','bej':'668687','gnz':'668530','shy':'1536837','ckg':'3532048'}
    try:
        room_id_=room_ids[room_id]
    except KeyError:
        room_id_=room_id
    cmd=['ykdl','-J','https://www.douyu.com/%s'%room_id_]
    while True:
        try:
            data=json.loads(subprocess.check_output(cmd).decode('gb18030'))
            break
        except subprocess.CalledProcessError:
            time.sleep(5)
    return data['streams'][data['stream_types'][0]]['src'][0]

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
        for child in bs4.BeautifulSoup(resp,'html.parser').find_all('div',class_='index_img fl pr')[0]:
            if child.name=='div' and child.get_text().strip()=='回放':
                logging.warning('[Yizhibo] %s not online.'%room_id_)
                break
            if child.name=='a':
                url='https://www.yizhibo.com%s'%child['href']
        if url:
            break
        time.sleep(1)
    cmd=['youtube-dl','-j',url]
    data=json.loads(subprocess.check_output(cmd).decode('utf-8'))
    return data['url'].replace('http://','https://')

def migu_video(room_id):
    if room_id in ['snh','bej','gnz','shy','ckg']:
        return
    cmd=['phantomjs','migu_video.js','https://tv.miguvideo.com/#/video/tv/%s'%room_id]
    while True:
        try:
            data=json.loads(subprocess.check_output(cmd).decode('utf-8'))
        except subprocess.CalledProcessError as e:
            logging.warning('[MiguVideo] %s: %s'%(room_id,e))
            time.sleep(10)
            continue
        headers={}
        for dict in data['headers']:
            headers[dict['name']]=dict['value']
        while True:
            try:
                resp=requests.get(data['content'].replace('http://','https://'),headers=headers).json()
                if resp['body']['liveStatus']=='2':
                    resp=requests.get(data['url_h'].replace('http://','https://'),headers=headers).json()
                    for rate_value in ['4','3','2','1']:
                        try:
                            rate=[dict for dict in resp['body']['rates'] if dict['rateValue']==rate_value]
                        except TypeError:
                            logging.warning('[MiguVideo] %s: %s'%(room_id,resp['message']))
                            return
                        if len(rate)==1:
                            rate_url=rate[0]['rateUrl']
                            if rate_url:
                                return rate_url
                else:
                    logging.warning('[MiguVideo] %s not online.'%room_id)
                    time.sleep(10)
                break
            except Exception as e:
                logging.warning('[MiguVideo] %s: %s'%(room_id,e))

def migu_music_1(room_id):
    if room_id in ['snh','bej','gnz','shy','ckg']:
        return
    base_url='https://c.musicapp.migu.cn/MIGUM2.0/v2.0'
    while True:
        try:
            resp=requests.get('%s/content/queryConcertSummary.do'%base_url,params={'columnId':room_id}).json()
            data=resp['data']
            if data['concertStatus']==0:
                live_id=data['liveId']
                concert_id=data['concertId']
                resp=requests.get('%s/danmaku/liveServerHosts.do'%base_url,params={'liveId':live_id,'concertId':concert_id,'liveType':1,'rateLevel':4}).json()
                return resp['data']['hosts']['liveHostAddr']
            else:
                logging.warning('[MiguMusic1] %s not online.'%room_id)
                time.sleep(1)
        except Exception as e:
            logging.warning('[MiguMusic1] %s: %s'%(room_id,e))

def migu_music_2(room_id):
    if room_id in ['snh','bej','gnz','shy','ckg']:
        return
    base_url='https://m.music.migu.cn/migu/remoting'
    while True:
        try:
            resp=requests.get('%s/live_play_tag'%base_url,params={'mapId':room_id}).json()
            live_play_visual=resp['retMsg']['livePlayVisual'][0]
            if live_play_visual['content']=='演唱会直播ID':
                content_id=live_play_visual['contentId']
                resp=requests.get('%s/get_music_playurl_tag'%base_url,params={'cid':content_id,'pid':2028593040,'rate':4}).json()
                return resp['playurl']
            else:
                logging.warning('[MiguMusic2] %s not online.'%room_id)
                time.sleep(1)
        except Exception as e:
            logging.warning('[MiguMusic2] %s: %s'%(room_id,e))

def main():
    parser=argparse.ArgumentParser()
    add=parser.add_argument
    add('arguments')
    add('--debug',action='store_true')
    add('-q','--quiet',action='store_true')
    add('-k','--ignore-errors',action='store_true')
    add('--log',action='store_true')
    add('-of','--offi-format',choices=['flv','rtmp'],default='flv')
    add('-bs','--bili-stream',type=int,choices=[0,1,2,3],default=0)
    add('-ua','--user-agent')
    add('-f','--format',choices=['ts','flv'],default='ts')
    add('-r','--remote')
    add('-t','--test',action='store_true')
    add('-c','--convert',action='store_true')
    args=parser.parse_args()
    logging.basicConfig(level=logging.WARNING,format='%(levelname)s: %(message)s')
    if args.test:
        args.remote='NUL' if platform.system()=='Windows' else '/dev/null'
    platform_=None
    method=None
    args_=args.arguments.split(',')
    if len(args_)==2 and args_[0] in ['48live','bilibili','douyu','youtube','yizhibo','migu_video','migu_music_1','migu_music_2','1','2','3','4','5','6','7','8']:
        platform_=args_[0]
        room_id=args_[1]
        if platform_ in ['1','2','3','4','5','6','7','8']:
            real_platform={'1':'48live','2':'bilibili','3':'douyu','4':'youtube','5':'yizhibo','6':'migu_video','7':'migu_music_1','8':'migu_music_2'}
            platform_=real_platform[platform_]
        methods={'48live':live48,'bilibili':bilibili,'douyu':douyu,'youtube':youtube,'yizhibo':yizhibo,'migu_video':migu_video,'migu_music_1':migu_music_1,'migu_music_2':migu_music_2}
        method=methods.get(platform_)
    input=None
    has_interval=False
    begin_time=int(time.time())
    p=None
    f=None
    line_=''
    output_sizes=[]
    regular_pattern=re.compile(r'Opening \'.*\' for reading')
    interval_pattern=re.compile(r'(403 Forbidden|404 Not Found|5XX Server Error)')
    expected_fps_pattern=re.compile(r'\, \d+(\.\d+)? fps')
    actual_fps_pattern=re.compile(r'fps=\s?\d+(\.\d+)?')
    error_pattern=re.compile(r'(Non-monotonous DTS in output stream \d+:\d+|DTS \d+ [\<\>] \d+ out of order|DTS \d+\, next:\d+ st:1 invalid dropping|missing picture in access unit with size \d+)')
    if args.remote is None:
        if platform_:
            platforms={'48live':'48Live','bilibili':'Bilibili','douyu':'Douyu','youtube':'YouTube','yizhibo':'Yizhibo','migu_video':'MiguVideo','migu_music_1':'MiguMusic1','migu_music_2':'MiguMusic2'}
            platform_name=platforms[platform_]
            room_name='%s48'%room_id.upper() if room_id in ['snh','bej','gnz','shy','ckg'] else room_id
        else:
            url_parser=parse.urlparse(args.arguments)
            platform_name=url_parser.hostname
            room_name=pathlib.Path(url_parser.path).stem
        dir=pathlib.Path('%d-%s-%s'%(int(time.time()),platform_name,room_name))
        dir.mkdir()
        count=1
    try:
        while True:
            if platform_:
                try:
                    if method==youtube:
                        now=int(time.time())
                        if input is None or now-begin_time>=21600:
                            input=method(room_id)
                            begin_time=int(time.time())
                    elif method==live48:
                        input=method(room_id,args.offi_format,has_interval)
                        has_interval=False
                    elif method==bilibili:
                        input,room_id_=method(room_id,args.bili_stream,has_interval)
                        has_interval=False
                    else:
                        input=method(room_id)
                except FileNotFoundError:
                    if args.remote is None:
                        dir.rmdir()
                    if method==migu_video:
                        message='''PhantomJS missing. See details on https://phantomjs.org/download.html
                        Adding PhantomJS to PATH is recommended after downloading it.'''
                    else:
                        message="Some required tools missing. Run 'pip install -U you-get youtube-dl' to install them."
                    sys.exit(message)
                if input is None:
                    if args.remote is None:
                        dir.rmdir()
                    sys.exit('Invalid room ID %s.'%room_id)
            else:
                if has_interval:
                    time.sleep(1)
                    has_interval=False
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
                file=dir/f'{count}.{args.format}'
                if file.exists():
                    count+=1
                output=dir/f'{count}.{args.format}'
                if args.log:
                    log=dir/f'{count}.log'
            else:
                output=args.remote
            cmd=['ffmpeg','-hide_banner','-y']
            user_agent=None
            if method in [bilibili,migu_video]:
                user_agent=USER_AGENT
            elif args.user_agent:
                user_agent=args.user_agent
            if user_agent:
                cmd.extend(['-user_agent',user_agent])
            if method==bilibili:
                cmd.extend(['-referer','https://live.bilibili.com/%s'%room_id_])
            cmd.extend(['-i',input,'-c','copy'])
            if args.remote is None:
                cmd.extend([output.as_posix()])
            else:
                cmd.extend(['-bsf:a','aac_adtstoasc','-f','flv',output])
            try:
                p=subprocess.Popen(cmd,stderr=subprocess.PIPE,bufsize=1,universal_newlines=True,encoding='utf-8')
            except FileNotFoundError:
                if args.remote is None:
                    dir.rmdir()
                sys.exit('''FFmpeg missing. See details on https://ffmpeg.org/download.html
                Adding FFmpeg to PATH is recommended after downloading it.''')
            if args.remote is None and args.log:
                f=open(log,'w')
            current_size=0
            expected_fps=0
            previous_size=0
            for size in output_sizes:
                previous_size+=size
            for line in p.stderr:
                if args.quiet:
                    m=re.match(r'^.*size=\s*(\d+)kB.*$',line.strip())
                    if m:
                        current_size=round(int(m.group(1))/1024,2)
                if not regular_pattern.search(line):
                    if args.quiet:
                        line_='%.2f MB\r'%float(previous_size+current_size)
                    else:
                        line_=line.replace('\n','\r') if actual_fps_pattern.search(line) else line
                    sys.stderr.write(line_)
                    sys.stderr.flush()
                    if args.remote is None and args.log:
                        f.write(line)
                if interval_pattern.search(line):
                    has_interval=True
                if expected_fps_pattern.search(line):
                    m=re.match(r'^.*\, (\d+(\.\d+)?) fps(\, )?.*$',line.strip())
                    if m:
                        expected_fps=float(m.group(1))
                if actual_fps_pattern.search(line) and not args.ignore_errors:
                    m=re.match(r'^.*fps=\s?(\d+(\.\d+)?).*$',line.strip())
                    if m:
                        actual_fps=m.group(1)
                        if actual_fps!='0.0' and float(actual_fps)<expected_fps:
                            p.terminate()
                            break
                if error_pattern.search(line) and not args.ignore_errors:
                    p.terminate()
                    break
            if args.quiet and current_size:
                output_sizes.append(current_size)
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
        if line_.endswith('\r'):
            sys.stderr.write('\n')
            sys.stderr.flush()
        if args.remote is None:
            if len(list(dir.iterdir()))==0:
                dir.rmdir()
            elif args.convert:
                for num in range(1,count+1):
                    file=dir/f'{num}.{args.format}'
                    if not file.exists():
                        continue
                    input=file
                    output=dir/f'{num}.mp4'
                    cmd=['ffmpeg','-hide_banner','-y','-i',input.as_posix(),'-c','copy','-bsf:a','aac_adtstoasc','-movflags','faststart',output.as_posix()]
                    try:
                        subprocess.run(cmd)
                    except KeyboardInterrupt:
                        break

if __name__=='__main__':
    main()
