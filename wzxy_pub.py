from datetime import datetime
import json
import requests

JWSESSION = ""
dayHeatList = []


def login(username, password):
    loginUrl = "https://gw.wozaixiaoyuan.com/basicinfo/mobile/login/username"
    header = {
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.13(0x18000d32) NetType/WIFI Language/zh_CN miniProgram",
        "Content-Type": "application/json;charset=UTF-8",
        "Content-Length": "2",
        "Host": "gw.wozaixiaoyuan.com",
        "Accept-Language": "en-us,en",
        "Accept": "application/json, text/plain, */*",
    }
    body = "{}"
    url = f"{loginUrl}?username={username}&password={password}"
    session = requests.session()
    response = session.post(url=url, data=body, headers=header)
    res = json.loads(response.text)
    cookies = response.cookies.get_dict()
    if res["code"] == 0:
        print("使用账号信息登录成功!")
        jwsession = cookies.get("JWSESSION")
        print("jwsession:" + jwsession + "\n")
        return jwsession
    else:
        print("使用账号信息登录成失败!")
        # print(res)
        return False


def getTodayHeatList(jwsession):
    print("获取打卡列表中...")
    headers = {
        "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.13(0x18000d32) NetType/WIFI Language/zh_CN miniProgram",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
        "Accept-Encoding": "gzip, deflate, br",
        "Content-Type": "application/json;charset=UTF-8",
        "JWSESSION": jwsession,
        "Connection": "keep-alive",
        "Referer": "https://gw.wozaixiaoyuan.com/h5/mobile/health/index/health",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "DNT": "1",
        "Sec-GPC": "1",
        "TE": "trailers"
    }
    cookies = {
        "JWSESSION": jwsession,
        "WZXYSESSION": jwsession
    }
    url = "https://gw.wozaixiaoyuan.com/health/mobile/health/getBatch"
    session = requests.session()
    response = session.post(url=url, headers=headers, cookies=cookies)
    res = json.loads(response.text)
    if res["code"] == 0:
        print("获取列表成功")
    else:
        print("获取列表失败")
    # print(res)


    # print("打卡列表:")

    for item in res.get("data").get("list"):
        id = item.get("id")
        startTime = item.get("start")
        endTime = item.get("end")
        dayHeathListData = {"id": id, "sTime": startTime, "eTime": endTime}
        dayHeatList.append(dayHeathListData)
        '''
        for key, value in item.items():
            print(key + ":", value)
        print("---------------------------")
        '''
    return res

def doTodayHeatList(jwsession, id):
    print("进行打卡中...")
    url = "https://gw.wozaixiaoyuan.com/health/mobile/health/save?batch=" + id
    headers = {
        "Host": "gw.wozaixiaoyuan.com",
        "content-length": "306",
        "accept": "application/json, text/plain, */*",
        "jwsession": jwsession,
        "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.13(0x18000d32) NetType/WIFI Language/zh_CN miniProgram",
        "content-type": "application/json;charset=UTF-8",
        "origin": "https://gw.wozaixiaoyuan.com",
        "x-requested-with": "com.tencent.mm",
        "sec-fetch-site": "same-origin",
        "sec-fetch-mode": "cors",
        "sec-fetch-dest": "empty",
        "referer": "https://gw.wozaixiaoyuan.com/h5/mobile/health/index/health/detail?id=" + id,
        "accept-encoding": "gzip, deflate",
        "accept-language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        "cookie": "JWSESSION=" + jwsession + "; WZXYSESSION=" + jwsession
    }

    data = {
        "t1": "正常（37.3℃以下）",
        "t2": "无下列情况，身体健康",
        "t3": "无下列情况，身体健康",
        "t4": "无",
        "type": 0,
        "locationMode": 0,
        "location": "中国/......",
        "locationType": 0
    }
    session = requests.session()
    response = session.post(url, headers=headers, json=data)
    res = json.loads(response.text)
    # print(res)
    if res["code"] == 0:
        print(f"[{id}]打卡成功")
        sendNotice(f"[{id}]健康打卡成功！")
        return True
    else:
        print(f"[{id}]打卡失败:" + res["message"])
        sendNotice(f"[{id}]健康打卡失败：" + res["message"])
        return False


def sendNotice(content):
    formatted_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    contents = f"[{formatted_datetime}]\n {content}"
    url = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key="

    data = {
        "msgtype": "text",
        "text": {
            "content": contents
        }
    }
    headers = {
        "content_type": "Content-Type: application/json",
    }
    response = requests.post(url, headers=headers, json=data)
    res = json.loads(response.text)
    #print(res)
    if res["errcode"] == 0:
        print("发送通知成功！")
        return True
    else:
        print("发送通知失败:" + res.get("errmsg"))
        return False


def main():
    jwsession = login("", "")
    # print(jwsession)
    getTodayHeatList(jwsession)
    now = datetime.now()
    for item in dayHeatList:
        if datetime.strptime(item.get("sTime"), "%H:%M").time() <= now.time() <= datetime.strptime(item.get("eTime"),
                                                                                                  "%H:%M").time():
            print(
                f"当前时间:{now.time()}\n[{item.get('id')}]:{item.get('sTime')}-{item.get('eTime')}\n在打卡范围内。")
            sendNotice(
                f"当前时间:{now.time()}\n[{item.get('id')}]:{item.get('sTime')}-{item.get('eTime')}\n在打卡范围内。")
            doTodayHeatList(jwsession, item.get(id))
        else:
            print(
                f"当前时间:{now.time()}\n[{item.get('id')}]:{item.get('sTime')}-{item.get('eTime')}\n不在打卡范围内。")
            sendNotice(
                f"当前时间:{now.time()}\n[{item.get('id')}]:{item.get('sTime')}-{item.get('eTime')}\n不在打卡范围内。")


if __name__ == '__main__':
    main()
