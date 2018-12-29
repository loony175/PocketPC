#!/usr/bin/env python3

import arrow
import json
import operator
import requests

def main():
    tzinfo='Asia/Shanghai'
    time_format='%Y-%m-%d %H:%M:%S'
    json_={}
    json_['memberInfoUtime']=arrow.get(2012,10,14,tzinfo=tzinfo).strftime(time_format)
    now=arrow.now(tzinfo).strftime(time_format)
    for key in ['functionUtime','groupUtime','memberPropertyUtime','musicAlbumUtime','musicUtime','periodUtime','talkUtime','teamUtime','urlUtime','videoTypeUtime','videoUtime']:
        json_[key]=now
    resp=requests.post('https://psync.48.cn/syncsystem/api/cache/v1/update/overview',headers={'Content-Type':'application/json','version':'5.3.2','os':'android'},json=json_).json()
    data=sorted(resp['content']['memberInfo'],key=operator.itemgetter('member_id'))
    members=[dict['real_name'] for dict in data]
    duplicate_names=[]
    for member in set(members):
        if members.count(member)>1:
            duplicate_names.append(member)
    members={}
    for dict in data:
        member_name=dict['nick_name'] if dict['real_name'] in duplicate_names else dict['real_name']
        members[member_name]=dict['member_id']
    f=open('member_id.json','w')
    f.write(json.dumps(members,indent=2,ensure_ascii=False))
    f.write('\n')
    f.close()

if __name__=='__main__':
    main()
