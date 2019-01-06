#!/usr/bin/env python3

import argparse
import json
import multiprocessing
import operator
import pathlib
import requests
import yaml

def request_process(user_id):
    while True:
        try:
            resp=requests.post('https://mapi.modian.com/v41/user/build_product_list',data={'to_user_id':user_id})
            break
        except Exception:
            pass
    data=resp.json()
    intermediate=[]
    for dict in [dict for dict in json.loads(data['data']) if dict['status']=='众筹中']:
        info={}
        info['path']='https://zhongchou.modian.com/item/%s.html'%dict['id']
        info['logo']=dict['logo']
        info['logo_4x3']=dict['logo_4x3']
        info['name']=dict['name']
        info['progress']=float(dict['progress'])
        info['install_money']=int(dict['install_money'])
        info['left_time']=dict['left_time']
        info['start_time']=dict['start_time']
        info['end_time']=dict['end_time']
        info['des']=dict['des']
        info['backer_money']=float(dict['backer_money'])
        info['username']=dict['username']
        info['user_icon']=dict['user_icon']
        intermediate.append(info)
    return intermediate

def main():
    parser=argparse.ArgumentParser()
    add=parser.add_argument
    add('-c','--config',type=pathlib.Path,default='modian.yml')
    add('-m','--member')
    add('-j','--jobs',type=int,default=16)
    add('-q','--quiet',action='store_true')
    add('-n','--sum',action='store_true')
    add('-N','--no-sum',action='store_true')
    args=parser.parse_args()
    config=yaml.load(open(args.config,'r').read())
    user_ids=config.values() if args.member is None else [config[args.member]]
    pool=multiprocessing.Pool(min([len(user_ids),args.jobs]))
    results=pool.map(request_process,user_ids)
    pool.close()
    pool.join()
    intermediate=[]
    for sub_list in results:
        for dict in sub_list:
            intermediate.append(dict)
    intermediate=sorted(intermediate,key=operator.itemgetter('progress'),reverse=True)
    if args.quiet:
        stdout=[]
        for dict in intermediate:
            info={}
            info['path']=dict['path']
            info['name']=dict['name']
            info['progress']=dict['progress']
            info['install_money']=dict['install_money']
            info['left_time']=dict['left_time']
            info['backer_money']=dict['backer_money']
            info['username']=dict['username']
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
