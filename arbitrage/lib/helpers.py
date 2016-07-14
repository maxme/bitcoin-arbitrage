#!/usr/bin/python
# -*- coding: utf-8 -*-
#用于进行http请求，以及MD5加密，生成签名的工具类
# import httplib
import http.client as httplib
import urllib.parse
import urllib
import json
import hashlib
import time
import math
import decimal
import hmac
import base64
import requests
import traceback

def md5(str):
    m = hashlib.md5()
    m.update(str)
    return m.hexdigest()

def requestGet(url,payload=''):
    try :
        r = requests.get(url,payload)
        if r and r.status_code == 200:
            return json.loads(r.text)
        else:
            return handle_error('API','API Error')
    except :
        return False


def requestPost(url, payload):
    try :
        r = requests.post(url,payload)
        if r and r.status_code == 200:
            return json.loads(r.text)
        else:
            return handle_error('API', r.text)
    except :
        return False

def buildSign(params, secretKey, host='haobtc'):
    if host =='haobtc' or host == 'default':
        sign = ''
        for key in sorted(params.keys()):
            sign += key + '=' + str(params[key]) +'&'
        data = sign+'secret_key='+secretKey
        return  hashlib.md5(data.encode("utf8")).hexdigest().upper()

    if host == 'okcoin':
        sign = ''
        for key in sorted(params.keys()):
            sign += key + '=' + str(params[key]) +'&'
        data = sign+'secret_key='+secretKey
        return  hashlib.md5(data.encode("utf8")).hexdigest().upper()

    if host == '':
        return

    if host == '':
        return

def httpGet(url, resource, params=''):
    try :
        conn = httplib.HTTPSConnection(url, timeout=10)
        conn.request("GET",resource + '?' + params)
        response = conn.getresponse()
        data = response.read().decode('utf-8')
        return json.loads(data)
    except:
        return False

def httpPost(url,resource,params):
    headers = {
        "Content-type" : "application/x-www-form-urlencoded",
    }
    try :
        conn = httplib.HTTPSConnection(url, timeout=10)
        temp_params = urllib.parse.urlencode(params)
        conn.request("POST", resource, temp_params, headers)
        response = conn.getresponse()
        data = response.read().decode('utf-8')
        params.clear()
        conn.close()
        return data
    except:
    # except Exception,e:  
        # print(Exception,":",e)
        traceback.print_exc()
        return False


def signature(params):
    params = sorted(params.items(), key=lambda d:d[0], reverse=False)
    message = urllib.parse.urlencode(params)
    message = message.encode('utf-8')

    m = hashlib.md5()
    m.update(message)
    m.digest()
    sig=m.hexdigest()
    return sig


def requestBody(url,host):
    arr = url.split(host)
    return arr[1]

def tradeLoad(params, secretKey, host='haobtc'):
    params['sign'] =  buildSign(params, secretKey, host)
    return params

def fen2yuan(amount , default=100):
    return (Decimal(amount)/Decimal(default)).quantize(decimal.Decimal('1E-2'))

def satoshi2btc(amount, default ='1E-4'):
    return (Decimal(amount)/Decimal(COIN)).quantize(decimal.Decimal(default))

def decimal_default(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    else:
        return str(obj)

def batchTradeFormat(arr):
    return str(arr).replace(' ','').replace("'",'"')

def str2int(num):
    return int(float(num))

def local_time(time_utc):
    u = int(time.mktime(time_utc.timetuple()))
    time_local = datetime.datetime.fromtimestamp(u, pytz.timezone('Asia/Shanghai')).strftime('%Y-%m-%d %H:%M:%S')
    return str(time_local)

def handle_error(code, message, status=404):
    resp = {'code': code, 'message': message}
    return resp
