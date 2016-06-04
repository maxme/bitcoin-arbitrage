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
        if r.status_code == 200:
            return json.loads(r.text)
        else:
            return handle_error('API','API Error')
    except :
        return False


def requestPost(url, payload):
    try :
        r = requests.post(url,payload)
        if r.status_code == 200:
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


def okcoin_error(code):
    error_code = {
    "10000":"Required field, can not be null",
    "10001":"Request frequency too high",
    "10002":"System error",
    "10003":"Not in reqest list, please try again later",
    "10004":"IP not allowed to access the resource",
    "10005":"'secretKey' does not exist",
    "10006":"'partner' does not exist",
    "10007":"Signature does not match",
    "10008":"Illegal parameter",
    "10009":"Order does not exist",
    "10010":"Insufficient funds",
    "10011":"Amount too low",
    "10012":"Only btc_cny ltc_cny supported",
    "10013":"Only support https request",
    "10014":"Order price must be between 0 and 1,000,000",
    "10015":"Order price differs from current market price too much",
    "10016":"Insufficient coins balance",
    "10017":"API authorization error",
    "10018":"borrow amount less than lower limit [cny:100,btc:0.1,ltc:1]",
    "10019":"loan agreement not checked",
    "10020":"rate cannot exceed 1%",
    "10021":"rate cannot less than 0.01%",
    "10023":"fail to get latest ticker",
    "10024":"balance not sufficient",
    "10025":"quota is full, cannot borrow temporarily",
    "10026":"Loan (including reserved loan) and margin cannot be withdrawn",
    "10027":"Cannot withdraw within 24 hrs of authentication information modification",
    "10028":"Withdrawal amount exceeds daily limit",
    "10029":"Account has unpaid loan, please cancel/pay off the loan before withdraw",
    "10031":"Deposits can only be withdrawn after 6 confirmations",
    "10032":"Please enabled phone/google authenticator",
    "10033":"Fee higher than maximum network transaction fee",
    "10034":"Fee lower than minimum network transaction fee",
    "10035":"Insufficient BTC/LTC",
    "10036":"Withdrawal amount too low",
    "10037":"Trade password not set",
    "10040":"Withdrawal cancellation fails",
    "10041":"Withdrawal address not approved",
    "10042":"Admin password error",
    "10043":"Account equity error, withdrawal failure",
    "10044":"fail to cancel borrowing order",
    "10047":"this function is disabled for sub-account",
    "10048":"withdrawal information does not exist",
    "10049":"User can not have more than 50 unfilled small orders (amount<0.5BTC)",
    "10050":"can't cancel more than once",
    "10100":"User account frozen",
    "10216":"Non-available API",
    }
    return error_code[str(code)]
