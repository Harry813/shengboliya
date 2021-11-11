import json
from urllib.parse import quote
import requests
from django.core.exceptions import ObjectDoesNotExist

from yimei.models import WechatVisitor, blacklist_visit, User_Profile


def get_wx_access_token (appid: str, secret: str, code: str):
    url = f"https://api.weixin.qq.com/sns/oauth2/access_token?appid={appid}&secret={secret}&code={code}&" \
          f"grant_type=authorization_code"
    r = requests.get(url)
    return r.json()


def get_user_info (access_token: str, open_id: str):
    url = f"https://api.weixin.qq.com/sns/userinfo?access_token={access_token}&openid={open_id}&lang=zh_CN"
    r = requests.get(url)
    return r.json()


def convert_string_encoding(s: str) -> str:
    return bytes(s, encoding='ISO-8859-1').decode('utf-8')


def wx_visit(open_id: str, target: User_Profile):
    wxuser = WechatVisitor.objects.get(openid=open_id)
    try:
        rec = blacklist_visit.objects.get(visitor=wxuser)
        rec.visit_total = rec.visit_total + 1
        rec.save()
    except ObjectDoesNotExist:
        rec = blacklist_visit(
            visitor=wxuser,
            blacklist_creator=target
        )
    rec.save()

