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
import datetime
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

# crawler for pzz
options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920x1080")

#Base Constant
QQPOST_URL = 'http://localhost:5700'
ACCESS_TOKEN = "************"
SECRET_KEY = "*********"

#random.org
RANDOMORG_TOKEN = "******************************************"

#whatanime.ga
WHATANIME_TOKEN = "******************************************"
WHATANIME_API_URL = "https://whatanime.ga/api/search?token="+WHATANIME_TOKEN

#ff14.huijiwiki.com
FF14WIKI_BASE_URL = "https://ff14.huijiwiki.com"
FF14WIKI_API_URL = "https://cdn.huijiwiki.com/ff14/api.php"

#sorry API
SORRY_BASE_URL = "https://sorry.xuty.tk"
#Tuling API
TULING_API_URL = "http://openapi.tuling123.com/openapi/api/v2"
TULING_API_KEY = "************************************"
#Baidu Cloud API
BAIDU_IMAGE_API_KEY = "*********************************"
BAIDU_IMAGE_SECRET_KEY = "*********************************"
BAIDU_IMAGE_ACCESS_TOKEN_URL = 'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=%s&client_secret=%s'%(BAIDU_IMAGE_API_KEY,BAIDU_IMAGE_SECRET_KEY)
BAIDU_IMAGE_ACCESS_TOKEN = "******************************************************************"
BAIDU_IMAGE_CENSOR_URL = 'https://aip.baidubce.com/rest/2.0/solution/v1/img_censor/user_defined?access_token='+BAIDU_IMAGE_ACCESS_TOKEN

QQBOT_LIST = [2746433796]

def refresh_baidu_access_token():
    r = requests.post(url=BAIDU_RECORD_ACCESS_TOKEN_URL)
    r = json.loads(r.text)
    print(r)
    
def get_item_info(url):
    r = requests.get(url,timeout=3)
    bs = BeautifulSoup(r.text,"html.parser")
    item_info = bs.find_all(class_='infobox-item ff14-content-box')[0]
    item_title = item_info.find_all(class_='infobox-item--name-title')[0]
    item_title_text = item_title.get_text().strip()
    if item_title.img and item_title.img.attrs["alt"]=="Hq.png":
        item_title_text += "(HQ)"
    print("item_title_text:%s"%(item_title_text))
    item_img = item_info.find_all(class_='item-icon--img')[0]
    item_img_url = item_img.img.attrs['src'] if item_img and item_img.img else ""
    item_content = item_info.find_all(class_='ff14-content-box-block')[0]
    #print(item_info.prettify())
    item_content_text = item_title_text
    try:
        item_content_text = item_content.p.get_text().strip()
    except Exception as e:
        traceback.print_exc() 
    res_data = {
        "url":url,
        "title":item_title_text,
        "content":item_content_text,
        "image":item_img_url,
    }
    return res_data

def search_item(name):
    search_url = FF14WIKI_API_URL+"?format=json&action=parse&title=ItemSearch&text={{ItemSearch|name=%s}}"%(name)
    r = requests.get(search_url,timeout=3)
    res_data = json.loads(r.text)
    bs = BeautifulSoup(res_data["parse"]["text"]["*"],"html.parser")
    if("没有" in bs.p.string):
        return False
    res_num = int(bs.p.string.split(" ")[1])
    item_names = bs.find_all(class_="item-name")
    if len(item_names) == 1:
        item_name = item_names[0].a.string
        item_url = FF14WIKI_BASE_URL + item_names[0].a.attrs['href']
        print("%s %s"%(item_name,item_url))
        res_data = get_item_info(item_url)
    else:
        item_img = bs.find_all(class_="item-icon--img")[0]
        item_img_url = item_img.img.attrs['src']
        search_url = FF14WIKI_BASE_URL+"/wiki/ItemSearch?name="+urllib.parse.quote(name)
        res_data = {
            "url":search_url,
            "title":"%s 的搜索结果"%(name),
            "content":"在最终幻想XIV中找到了 %s 个物品"%(res_num),
            "image":item_img_url,
        }
    print("res_data:%s"%(res_data))
    return res_data

def check_contain_chinese(check_str):
    for ch in check_str:
        if u'\u4e00' <= ch <= u'\u9fff':
            return True
    return False

def get_group_member_info(group_id,user_id):
    jdata = {"group_id":group_id,"user_id":user_id}
    s = requests.post(url=QQPOST_URL+'/get_group_member_info?access_token='+ACCESS_TOKEN,data=jdata,timeout=10)
    res_json = json.loads(s.text)
    return res_json["data"]

def send_group_msg(group_id,msg,at_user_id=None):
    if at_user_id:
        msg = "[CQ:at,qq=%s] "%(at_user_id)+msg
    jdata = {"group_id":group_id,"message":msg}
    print("jdata:%s"%(json.dumps(jdata)))
    s=requests.post(url=QQPOST_URL+'/send_group_msg?access_token=2ASdOeYCOyp',data=jdata,timeout=10)
    res_json = json.loads(s.text)
    return res_json
    
send_group_msg(23429055, u"库兰兰Bot已经启动！请多指教！@_@", 188223673)

def group_ban(group_id,user_id,duration=60):
    jdata = {"group_id":group_id,"user_id":user_id,"duration":duration}
    s=requests.post(url=QQPOST_URL+'/set_group_ban?access_token=2ASdOeYCOyp',data=jdata,timeout=10)
    res_json = json.loads(s.text)
    return res_json

def send_like(user_id,times=1):
    jdata = {"user_id":user_id,"times":times}
    print("like_data:%s"%(json.dumps(jdata)))
    s=requests.post(url=QQPOST_URL+'/send_like?access_token=2ASdOeYCOyp',data=jdata,timeout=10)
    res_json = json.loads(s.text)
    print("like_res:%s"%(json.dumps(res_json)))
    return res_json

def delete_msg(message_id):
    jdata = {"message_id":message_id}
    s=requests.post(url=QQPOST_URL+'/delete_msg?access_token=2ASdOeYCOyp',data=jdata,timeout=10)
    res_json = json.loads(s.text)
    return res_json
    
def image_censor_url(image_url):
    data = {
        "imgUrl":image_url
    }
    r = requests.post(url=BAIDU_IMAGE_CENSOR_URL,data=data)
    print(r.text)
    return json.loads(r.text)

def image_censor(receive):
    tmp = receive["message"]
    tmp = tmp[tmp.find("url="):-1]
    tmp = tmp.replace("url=","")
    img_url = tmp.replace("]","")
    censor_res = image_censor_url(img_url)
    if("error_msg" in censor_res.keys()):
        return
    if(censor_res["conclusion"]=="不合规" or censor_res["conclusion"]=="疑似"):
        cnt = 0
        msg = "[CQ:at,qq=%s]"%(receive["user_id"])+" 所发图片由于：\n"
        for item in censor_res["data"]:
            if("公众" in item["msg"] or "政治敏感" in item["msg"]):
                msg += "%s：\n"%(item["msg"])
                for star in item["stars"]:
                    msg += "    %.2f%%%s\n"%(float(star["probability"])*100,star["name"])
            else:
                msg += "%.2f%%%s\n"%(float(item["probability"])*100,item["msg"])
            if(("色情" in item["msg"] or "政治敏感" in item["msg"])):
                cnt += 1
        msg += "而触发图片审核机制，请管理员处理。"
        if(cnt > 0):
            send_group_msg(receive["group_id"],msg)

def get_record(file_name):
    jdata = {"file":file_name,"out_format":"wav"}
    s=requests.post(url=QQPOST_URL+'/get_record?access_token=2ASdOeYCOyp',data=jdata,timeout=10)
    res_json = json.loads(s.text)
    return res_json

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
                if (receive["message"].find('/help')==0):
                   # print("here")
                   # msg = "/cat : 云吸猫\n/gakki : 云吸gakki\n/like : 赞\n/random(gate) : 掷骰子\n/search $item : 在最终幻想XIV中查询物品$item\n/dps $boss $job $dps : 在最终幻想XIV中查询DPS在对应BOSS与职业的logs排名（国际服同期数据）\n/anime $img : 查询$img对应番剧(只支持1M以内静态全屏截图)\n/gif : 生成沙雕GIF\n/about : 关于獭獭\n/donate : 援助作者"
                    msg = "/p：查询ulk强风时间(抓取自https://xivwb.gitee.io/)\n/ffwall：云吸光战(大雾)\n/random(/gate) : 掷骰子/挖宝选门\n/find $item : 在最终幻想XIV中查询物品$item\n/g : 生成沙雕GIF\n/about : 关于库兰兰"

                    msg = msg.strip()
                    reply_data = {"reply":msg}
                    if(receive["message_type"]=="group"):
                        reply_data["at_sender"] = "false"
                    # print(reply_data)
                    return JsonResponse(reply_data)
                #Group Chat Func
#                if (receive["message"] == '/cat'):
#                    reply_data = {"reply":[{"type":"image","data":{"file":"cat/%s.jpg"%(random.randint(0,750))}}]}
#                    if(receive["message_type"]=="group"):
#                        reply_data["at_sender"] = "false"
#                    return JsonResponse(reply_data)

                if (receive["message"].find('/find')==0):
                    name = receive["message"].replace('/find','')
                    name = name.strip()
                    res_data = search_item(name)
                    if res_data:
                        reply_data = {"reply":[{"type":"share","data":res_data}]}
                    else:
                        reply_data = {"reply":"在最终幻想XIV中没有找到 %s"%(name)}
                    return JsonResponse(reply_data)
                if (receive["message"].find('/about')==0):
                    res_data = {
                        "url":"https://www.ourocg.cn/Cards/View-1667",
                        "title":"黑魔导师 库兰",
                        "content":"属性：暗 种族：魔法师 攻击：1200 防御：0",
                        "image":"https://gss3.bdstatic.com/-Po3dSag_xI4khGkpoWK1HF6hhy/baike/c0%3Dbaike80%2C5%2C5%2C80%2C26/sign=9e3ca6c29525bc313f5009ca3fb6e6d4/8b82b9014a90f603c044ef4b3512b31bb151edc2.jpg",
                    }
                    reply_data = {"reply":[{"type":"share","data":res_data}]}
                    if(receive["message_type"]=="group"):
                        reply_data["at_sender"] = "false"
                    return JsonResponse(reply_data)
#                if (receive["message"].find('/donate')==0):
                    #reply_data = {"reply":[{"type":"text","data":{"text":"我很可爱(*╹▽╹*)请给我钱（来租服务器养活獭獭）"}},{"type":"image","data":{"file":"alipay.jpg"}}],"at_sender":"false"}
#                    reply_data = {"reply":[{"type":"text","data":{"text":"獭獭很可爱(*╹▽╹*)不用给钱啦獭獭已经买了好多零食"}}],"at_sender":"false"}
#                    return JsonResponse(reply_data)

                if (receive["message"].find('/gate')==0):
                    try:
                        num = int(receive["message"].replace("/gate",""))
                    except:
                        num = 2
                    num = min(num, 3)
                    gate = random.randint(0,num-1)
                    choose_list = [i for i in range(num)]
                    random.shuffle(choose_list)
                    gate_idx = choose_list.index(gate)
                    gate_msg = "左边" if gate_idx==0 else "右边" if gate_idx==1 else "中间"
                    reply_data = {"reply":"掐指一算，[CQ:at,qq=%s]不应该走%s门，不要信库兰的就对了！"%(receive["user_id"],gate_msg),"at_sender":"false"}
                    print("reply_data:%s"%(reply_data))
                    return JsonResponse(reply_data)
                if (receive["message"].find('/random')==0):
                    min_lim = 1
                    max_lim = 999
                    try:
                        num = int(receive["message"].replace("/random",""))
                    except:
                        num = 1
                    num = min(num,6)
                    post_data = {"jsonrpc":"2.0","method":"generateIntegers","params":{"apiKey":RANDOMORG_TOKEN,"n":num,"min":min_lim,"max":max_lim,"replacement":"true"},"id":1}
                    try:
                        s=requests.post(url='https://api.random.org/json-rpc/1/invoke',data=json.dumps(post_data),timeout=0.5)
                        res_jdata = json.loads(s.text)
                        if ("error" in res_jdata):
                            msg = res_jdata["error"]["message"]
                        else:
                            msg = ""
                            num_list = res_jdata["result"]["random"]["data"]
                            for item in num_list:
                                msg = msg + "%s "%(item)
                            msg = msg.strip()
                    except Exception as e:
                        traceback.print_exc()
                        msg = str(random.randint(1,1000))#+"(pseudo-random)"
                    reply_data = {"reply":"[CQ:at,qq=%s]掷出了"%(receive["user_id"])+msg+"点！","at_sender":"false"}
                    print("reply_data:%s"%(reply_data))
                    return JsonResponse(reply_data)
                if (receive["message"].find('/g ')==0):
                    sorry_dict = {"sorry":"好啊|就算你是一流工程师|就算你出报告再完美|我叫你改报告你就要改|毕竟我是客户|客户了不起啊|sorry 客户真的了不起|以后叫他天天改报告|天天改 天天改","wangjingze":"我就是饿死|死外边 从这跳下去|也不会吃你们一点东西|真香","jinkela":"金坷垃好处都有啥|谁说对了就给他|肥料掺了金坷垃|不流失 不蒸发 零浪费|肥料掺了金坷垃|能吸收两米下的氮磷钾","marmot":"啊~|啊~~~","dagong":"没有钱啊 肯定要做的啊|不做的话没有钱用|那你不会去打工啊|有手有脚的|打工是不可能打工的|这辈子不可能打工的","diandongche":"戴帽子的首先进里边去|开始拿剪刀出来 拿那个手机|手机上有电筒 用手机照射|寻找那个比较新的电动车|六月六号 两名男子再次出现|民警立即将两人抓获"}
                    sorry_name = {"sorry":"为所欲为","wangjingze":"王境泽","jinkela":"金坷垃","marmot":"土拨鼠","dagong":"窃格瓦拉","diandongche":"偷电动车"}
                    receive_msg = receive["message"].replace('/g','',1).strip()
                    if receive_msg=="list":
                        msg = ""
                        for (k,v) in sorry_dict.items():
                            msg = msg + "%s : %s\n"%(k,sorry_name[k])
                    else:
                        now_template = ""
                        for (k,v) in sorry_dict.items():
                            if (receive_msg.find(k)==0):
                                now_template = k
                                break
                        if (now_template=="" or len(receive_msg)==0 or receive_msg=="help"):
                            msg = "/g list : 目前可用模板\n/gif $template example : 查看模板$template的样例\n/gif $template $msg0|$msg1|... : 按照$msg0,$msg1...生成沙雕GIF\nPowered by sorry.xuty.tk"
                        else:
                            receive_msg = receive_msg.replace(now_template,"",1).strip()
                            if(receive_msg=="example"):
                                msg = sorry_dict[now_template]
                            else:
                                msgs = receive_msg.split('|')
                                cnt = 0
                                gen_data = {}
                                for sentence in msgs:
                                    sentence = sentence.strip()
                                    if(sentence==""):
                                        continue
                                    gen_data[str(cnt)] = sentence
                                    print("sentence#%s:%s"%(cnt,sentence))
                                    cnt += 1
                                if(cnt==0):
                                    msg = "至少包含一条字幕消息"
                                else:
                                    print("gen_data:%s"%(json.dumps(gen_data)))
                                    url = SORRY_BASE_URL + "/api/%s/make"%(now_template)
                                    try:
                                        s = requests.post(url=url,data=json.dumps(gen_data),timeout=2)
                                        img_url = SORRY_BASE_URL + s.text
                                        print("img_url:%s"%(img_url))
                                        msg = '[CQ:image,file='+img_url+']'
                                    except Exception as e:
                                        msg = "SORRY API ERROR:%s"%(e)
                                        print(msg)
                                        reply_data = {"reply":msg}  
                                        return JsonResponse(reply_data) 
                    msg = msg.strip()
                    reply_data = {"reply":msg}
                    if(receive["message_type"]=="group"):
                        reply_data["at_sender"] = "false"
                    return JsonResponse(reply_data)

                #Private message
                if (receive["message_type"]=="private"):
                    if("[CQ:record,file=" in receive["message"]):
                        tmp = receive["message"]
                        tmp = tmp[tmp.find("file="):-1]
                        tmp = tmp.replace("file=","")
                        file_name = tmp.replace("]","")
                        jres = get_record(file_name)
                        if(jres["status"]=="ok"):
                            out_file = jres["data"]["file"]
                            record_url = QQPOST_URL+'/data/record/%s?access_token=2ASdOeYCOyp'%(out_file)
                            r = requests.get(url=record_url)
                            print("out_file:%s"%(jres["data"]["file"]))
                            if(r.status_code==200):
                                pass
                        else:
                            print("jres:%s"%(json.dumps(jres)))
                # other situations
                return reply_curran(receive)
                
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

def reply_curran(recv):
    answered = False
    cr_debug = False
    args = recv["message"].split(" ")    
    # print(args)
    if "-dbg" in args: cr_debug = True
    ret = {"reply": ""}
    
    # disable group at
    if recv["message_type"] != "private": ret["at_sender"] = False
    
    # commands
    try:
        # ffwall
        if args[0] == "/ffwall":
             # ret["reply"] = ffwall_count.__str__()
            if len(args) >= 3:
                items = FFwall.objects.filter(GroupName=args[1], RoleName=args[2])
            else:
                items = FFwall.objects.filter(Id=random.randint(1, ffwall_count))
            if items:
                img = items[0].BigImage
                ret["reply"] = {"type":"image","data":{"file":img} }
            else:
                ret["reply"] = "没有找到玩家:%s（须参加过三周年活动）" % args[2]
            answered = True
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
                dt = datetime.datetime.fromtimestamp(ts, pytz.timezone("Asia/Shanghai"))
                t.append(u"【强风】 %s 持续 %s" % (dt.strftime("%H:%M:%S"), items[2].text))
            ret["reply"] = "\n".join(t)
            answered = True
            br.quit()
    except:
        ret["reply"] = traceback.format_exc()
        cr_debug = True
        answered = True

    # post-process
    if answered:
        if cr_debug:
            ret["reply"] += "\nrecv: %s\nargs: %s\nreturn: %s" % (json.dumps(recv), json.dumps(args), json.dumps(ret))
        return JsonResponse(ret)
    else:
        return HttpResponse(status=204)
    
