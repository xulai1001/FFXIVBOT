# -*- coding: utf-8 -*-
from django.shortcuts import render, Http404, HttpResponseRedirect
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.template import Context, RequestContext, loader
from django.http import HttpResponse
from django.http import JsonResponse
from django.db.models import Q
from django.core.files.base import ContentFile
from django.utils import timezone
from collections import OrderedDict
from django.views.decorators.csrf import csrf_exempt
import os, datetime
import pytz
import re
import json
import pymysql
import time
from FFXIVBOT.models import *
from hashlib import md5
import math
import requests
import base64
import random,sys
from random import choice
import traceback  
import codecs
import html
import hmac
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import urllib, traceback
# Create your views here.
from FFXIVBOT.models import *

# ffwall count
ffwall_count = FFwall.objects.count()
ts_reply = 0

# crawler for pzz
options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920x1080")

#Base Constant
QQPOST_URL = 'http://localhost:5700'
TATARU_URL = "http://tataru.diemoe.net/api/cq_http_api.php?key=7d772a0bc35d0f7b17e96b60435013a5"
ACCESS_TOKEN = "************"
SECRET_KEY = "*********"

#ff14.huijiwiki.com
FF14WIKI_BASE_URL = "https://ff14.huijiwiki.com"
FF14WIKI_API_URL = "https://cdn.huijiwiki.com/ff14/api.php"

#sorry API
SORRY_BASE_URL = "https://sorry.xuty.tk"

QQBOT_LIST = [2746433796]

def send_group_msg(group_id,msg,at_user_id=None):
    if at_user_id:
        try:
            msg = "[CQ:at,qq=%s] "%(at_user_id)+msg
        except: pass
    jdata = {"group_id":group_id,"message":msg,"user_id":at_user_id}
    print("jdata:%s"%(json.dumps(jdata)))
    if group_id:
        s=requests.post(url=QQPOST_URL+'/send_group_msg?access_token=2ASdOeYCOyp',data=jdata,timeout=10)
    else:
        s=requests.post(url=QQPOST_URL+"/send_private_msg?access_token=2ASdOeYCOyp",data=jdata,timeout=10)
    res_json = json.loads(s.text)
    return res_json
    
# send_group_msg(23429055, u"库兰兰Bot已经启动！请多指教！@_@", 188223673)

@csrf_exempt
def qqpost(req):
    try:
        receive = json.loads(req.body.decode())
       #  print(receive)
       # sig = hmac.new(b'pinkpink', req.body, 'sha1').hexdigest()
       # received_sig = req.META.get("HTTP_X_SIGNATURE","unknow")[len('sha1='):]
       # print(sig, received_sig)
       # if(sig == received_sig): # 这里如果签名不对会返回204，原因不明
        if receive["user_id"] in QQBOT_LIST:
            print("-- BOT: not answering --")
            return HttpResponse(status=204)
        else:
            if (receive["post_type"] == "message"):
                return reply_curran(req)
                
            # 加群屏蔽功能处理，保留
            if (receive["post_type"] == "request"):
                if (receive["request_type"] == "friend"):	#Add Friend
                    qq = receive["user_id"]
                    reqmsg = receive["message"]
                    reqmsg = str(reqmsg).upper()
                    reply_data = {"approve": "FFXIV" in reqmsg or "FF14" in reqmsg}
                    return JsonResponse(reply_data)
                if (receive["request_type"] == "group" and receive["sub_type"] == "invite"):	#Add Group
                    reply_data = {"approve":False}
                    return JsonResponse(reply_data)
            if (receive["post_type"] == "event"):
                if (receive["event"] == "group_increase"):
                    group_id = receive["group_id"]
                    user_id = receive["user_id"]
                    group_list = QQGroup.objects.filter(group_id=group_id)
                    if len(group_list)>0:
                        group = group_list[0]
                        msg = group.welcome_msg.strip()
                        if(msg!=""):
                            send_group_msg(group_id,msg,user_id)
                            # reply_data = {"reply":msg}
                            # return JsonResponse(reply_data)

        return HttpResponse(status=204)
    except Exception as e:
        traceback.print_exc() 

def forward_tataru(req):
    return requests.post(TATARU_URL, data=req).json()

def reply_curran(req):
    recv = json.loads(req.body.decode())
    global ts_reply
    answered = False
    cr_debug = False
    forward = False
    args = recv["message"].split()    
    print(recv)
    if "-dbg" in args: cr_debug = True
    ret = {"reply": ""}
    
    # disable group at
    if recv["message_type"] != "private": ret["at_sender"] = False
    
    # commands
    try:
        # help
        if args[0] == "/help":
            ret["reply"] = """
/ffwall 服务器 玩家名- 云吸光战(数据来源：三周年活动)，不提供名字则随机
/p - 查询ulk强风时间(数据来源：https://xivwb.gitee.io)
/draw - 我的回合，抽卡！(数据来源：ygopro 2)
/about - 关于库兰兰 & 塔塔露
↓塔塔露的帮助"""
            answered = True
            forward = True
        # about
        if args[0] == "/about":
            d = {
                "url":"https://www.ourocg.cn/Cards/View-1667",
                "title":"黑魔导师 库兰",
                "content":"属性：暗 种族：魔法师 攻击：1200 防御：0",
                "image":"https://gss3.bdstatic.com/-Po3dSag_xI4khGkpoWK1HF6hhy/baike/c0%3Dbaike80%2C5%2C5%2C80%2C26/sign=9e3ca6c29525bc313f5009ca3fb6e6d4/8b82b9014a90f603c044ef4b3512b31bb151edc2.jpg",
            }
            ret["reply"] = "[CQ:share,url=%s,title=%s,content=%s,image=%s]" % (d["url"], d["title"], d["content"], d["image"])
            answered = True
            forward = True
        # ffwall
        if args[0] == "/ffwall":
             # ret["reply"] = ffwall_count.__str__()
            if len(args) >= 3:
                items = FFwall.objects.filter(GroupName=args[1], RoleName=args[2])
            elif len(args) >= 2:
                items = FFwall.objects.filter(RoleName=args[1])
            else:
                items = FFwall.objects.filter(Id=random.randint(1, ffwall_count))
            if items:
                img = items[0].BigImage
                if len(args) >= 2:
                    ret["reply"] = "[CQ:image,file=%s]\n%s %s" % (img, items[0].GroupName, items[0].RoleName)
                else:
                    ret["reply"] = "[CQ:image,file=%s]" % (img)                
            else:
                ret["reply"] = "没有找到玩家:%s（须参加过三周年活动）" % args[-1]
            answered = True
        # pazuzu
        if args[0] == "/p":
            # grabbed from https://xivwb.gitee.io/#eure-1
            br = webdriver.Chrome(chrome_options=options, executable_path='/usr/bin/chromedriver') # latest version for chrome
            br.get("https://xivwb.gitee.io/#eure-1")
            br.implicitly_wait(10)
            # print("***** %s" % br.page_source)
            lines = br.find_elements_by_xpath("//div[@class='match']/table/tbody/tr")
            t = []
            for li in lines[:3]:
                items = li.find_elements_by_xpath("td")
                ts = time.mktime(time.strptime(items[0].text.split(" ")[1], "%H:%M:%S"))
                dt = datetime.datetime.fromtimestamp(ts, pytz.timezone("utc")).astimezone(pytz.timezone("Asia/Shanghai"))
                dt = dt - datetime.timedelta(minutes=6)
                t.append(u"【强风】 %s 持续 %s" % (dt.strftime("%H:%M:%S"), items[2].text))
            ret["reply"] = "\n".join(t)
            answered = True
            br.quit()
        # yugioh card draw
        if args[0] == "/draw":
            # data from my-cards v2
            filename = choice(os.listdir("card"))
            idx = int(filename.split(".")[0])
            text_item = YGOText.objects.using("mycard").filter(id=idx)
            if text_item:
                data_item = YGOData.objects.using("mycard").filter(id=idx)
                results = ["[CQ:image,file=card\\%s]" % filename, text_item[0].name]
                d = data_item[0]
                if d.level > 0 and d.level < 20:
                    results.append("☆%d ATK %d / DEF %d" % (d.level, d.atk, d.dfd))
                results.append(text_item[0].desc)
                ret["reply"] = "\r\n".join(results)
                print(results)
                answered = True
    except:
        ret["reply"] = traceback.format_exc()
        cr_debug = True
        answered = True

    # post-process
    if answered:
        # flow control
#        if recv["time"] - ts_reply < 10:
        if False:   # MASKED
            ret["reply"] = u"[请稍候]库兰兰cd中..."
            return JsonResponse(ret)
        else:
            ts_reply = recv["time"]
            if cr_debug:
                send_group_msg(None, "Group:%d\nrecv: %s\nargs: %s\nreturn: %s" % (recv.get("group_id", None), json.dumps(recv), json.dumps(args), json.dumps(ret)), at_user_id=recv["user_id"])
            if forward:
                rep = ret["reply"]
                ret = forward_tataru(req)
                send_group_msg(recv.get("group_id", None), rep, at_user_id=recv["user_id"])
            return JsonResponse(ret)
    elif args[0].startswith("/"):
        print("** redirect to tataru **")
        return HttpResponse(requests.post(TATARU_URL, data=req))
    else:
        return HttpResponse(status=204)
    
