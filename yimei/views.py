from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import Http404, HttpResponse, redirect, render, get_object_or_404
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.core.exceptions import PermissionDenied

from urllib.parse import quote

from .forms import *
from .api import *
from .models import *
from .panel_setting import *
from .settings import APPID, SCOPE, STATE, SECRET
from .utils import get_wx_access_token, get_user_info, convert_string_encoding, wx_visit


###########################################################
# 前端页面
###########################################################


def home(request):
    # param = {
    #     "page_title": "首页",
    #     "s": "Hello, there",
    #     "info": get_panel_info(),
    #     "active_page": "home",
    #     "bottom_nav": request.user_agent.is_mobile
    # }
    #
    # if request.user.is_authenticated:
    #     param["user"] = request.user
    # else:
    #     param["user"] = None
    #
    # if "toast_list" in request.session:
    #     param["toast_list"] = request.session["toast_list"]
    #     del request.session["toast_list"]
    # return render(request, "user/index.html", param)
    return redirect('operators')


def login_view(request):
    param = {
        "page_title": "登录",
        "info": get_panel_info(),
        "active_page": "login",
        "user": None,
        "bottom_nav": request.user_agent.is_mobile,
    }
    if request.method == 'POST':
        form = LoginForm(request.POST)
        param["form"] = form
        if form.is_valid():
            username = form.cleaned_data.get('username')
            user = User_Profile.objects.get(username=username)
            login(request, user)
            request.session["toast_list"] = [get_toast(message="登陆成功！", ty=2, color="success")]
            next_page = request.GET.get("next", "")
            if next_page:
                return HttpResponseRedirect(next_page)
            else:
                return redirect('profile')
        else:
            param["validate"] = True
            return render(request, 'user/login.html', param)
    else:
        form = LoginForm()
        param["form"] = form
    return render(request, 'user/login.html', param)


def logout_view(request):
    logout(request)
    toasts = [get_toast(message="注销成功！", ty=2, color="primary")]
    request.session["toast_list"] = toasts
    return redirect('home')


def register_view(request, invi_code=None):
    param = {
        "page_title": "注册",
        "info": get_panel_info(),
        "active_page": "register",
        "bottom_nav": request.user_agent.is_mobile,
        "user": None
    }
    if request.method == 'POST':
        if invi_code and User_Profile.objects.filter(invi_code=invi_code).exists():
            form = RegisterForm(request.POST, initial={"invi_code": invi_code})
        else:
            form = RegisterForm(request.POST)
        param["form"] = form
        if form.is_valid():
            username = form.cleaned_data["username"]
            # username = request.POST.get("username", "")
            paswd = form.cleaned_data['paswd1']
            u = User_Profile()
            u.username = username
            u.set_password(paswd)

            invi_user = form.cleaned_data['invi_code']
            if invi_user:
                u.invi_user = invi_user

            invi_code = generate_invi_code()
            u.invi_code = invi_code

            tele = form.cleaned_data['tele']
            if tele:
                u.tele = tele
            u.save()

            login(request, u)
            request.session["toast_list"] = [get_toast(message="注册成功!", ty=2, color="success")]
            return redirect('profile')
        else:
            return render(request, 'user/register.html', param)
    else:
        if invi_code and len(User_Profile.objects.filter(invi_code=invi_code)) == 1:
            form = RegisterForm(initial={"invi_code": invi_code})
        else:
            form = RegisterForm()
        param["form"] = form

    return render(request, 'user/register.html', param)


def profile_view(request):
    param = {
        "page_title": "用户中心",
        "info": get_panel_info(),
        "active_page": "profile",
        "user": None,
        "bottom_nav": request.user_agent.is_mobile,
    }
    if request.user.is_authenticated:
        u = User_Profile.objects.get(username=request.user)
        param["user"] = User_Profile.objects.get(id=request.user.id)
        param['invi_count'] = get_invi_user_count(u)
    else:
        param["user"] = None

    if "toast_list" in request.session:
        param["toast_list"] = request.session["toast_list"]
        del request.session["toast_list"]

    return render(request, "user/profile.html", param)


@login_required
def user_setting(request):
    param = {
        "page_title": "设置中心",
        "info": get_panel_info(),
        "active_page": "setting",
        "bottom_nav": request.user_agent.is_mobile,
        "user": User_Profile.objects.get(id=request.user.id)
    }
    return render(request, "user/user_setting.html", param)


@login_required
def user_id_verify(request):
    param = {
        "page_title": "设置中心 - 实名认证",
        "info": get_panel_info(),
        "active_page": "verify",
        "bottom_nav": request.user_agent.is_mobile,
    }
    if request.method == 'POST':
        form = IDVerifyForm(request.POST, initial={"request_user": request.user.id})
        param["form"] = form
        if form.is_valid():
            u = User_Profile.objects.get(id=request.user.id)
            u.id_card = form.cleaned_data.get("id_card")
            u.real_name = form.cleaned_data.get("real_name")
            u.save()
            request.session["toast_list"] = [get_toast(message="验证成功!", ty=2, color="success")]
            return redirect('setting')
        else:
            request.session["toast_list"] = [get_toast(message="验证失败!", ty=2, color="danger")]
            return render(request, 'user/user_id_verify.html', param)
    else:
        form = IDVerifyForm(initial={"request_user": request.user.id})
        param["form"] = form
    return render(request, "user/user_id_verify.html", param)


def promote_view(request):
    param = {
        "page_title": "推广中心",
        "info": get_panel_info(),
        "active_page": "promote",
        "bottom_nav": request.user_agent.is_mobile,
    }
    return render(request, "user/promote.html", param)


@login_required
def appoint_view(request, opid=None):
    param = {
        "page_title": "预约中心",
        "info": get_panel_info(),
        "active_page": "appointment",
        "bottom_nav": request.user_agent.is_mobile,
    }
    if request.method == 'POST':
        if opid is not None and Operator.objects.filter(id=opid).exists():
            form = AppointmentForm(request.POST, initial={"hospital": opid})
        else:
            form = AppointmentForm(request.POST)
        param["appoint_form"] = form
        if form.is_valid():
            f = form.save(commit=False)
            f.create_user = User_Profile.objects.get(id=request.user.id)
            f.save()
            return redirect('profile')
        else:
            return render(request, 'user/appointment.html', param)
    else:
        if opid is not None and Operator.objects.filter(id=opid).exists():
            form = AppointmentForm(initial={"hospital": opid})
        else:
            form = AppointmentForm()
        param["appoint_form"] = form
    return render(request, "user/appointment.html", param)


@login_required
def transaction_view(request):
    param = {
        "page_title": "提现中心",
        "info": get_panel_info(),
        "active_page": "appointment",
        "bottom_nav": request.user_agent.is_mobile,
        "user": User_Profile.objects.get(id=request.user.id),
        "income": Transaction.objects.filter(holder_id=request.user.id, transaction_type=1),
        "withdrawal": Transaction.objects.filter(holder_id=request.user.id, transaction_type=2)
    }
    return render(request, "user/transaction.html", param)


@login_required
def withdrawal_view(request):
    param = {
        "page_title": "提现中心",
        "info": get_panel_info(),
        "active_page": "appointment",
        "bottom_nav": request.user_agent.is_mobile,
        "user": User_Profile.objects.get(id=request.user.id),
        "applications": Withdrawal.objects.filter(applicator_id=request.user.id).order_by('update_date', 'status')[:10]
    }
    if request.method == 'POST':
        form = WithdrawalFrom(request.POST, initial={"applicator_id": request.user.id})
        param["form"] = form
        if form.is_valid():
            amount = form.cleaned_data.get("amount")
            method = form.cleaned_data.get("method")
            account = form.cleaned_data.get("account")
            w = Withdrawal(amount=amount, applicator_id=request.user.id, method=method, receive_account=account)
            w.save()

            u = User_Profile.objects.get(id=request.user.id)
            u.balance -= decimal.Decimal(amount)
            u.frozen += decimal.Decimal(amount)
            u.save()
            request.session["toast_list"] = [get_toast(message="申请提交成功!", ty=2, color="success")]
            return redirect('transactions')
        else:
            request.session["toast_list"] = [get_toast(message="申请提交失败!", ty=2, color="danger")]
            return render(request, 'user/withdrawal.html', param)
    else:
        form = WithdrawalFrom(initial={"applicator_id": request.user.id})
        param["form"] = form
    return render(request, "user/withdrawal.html", param)


def wiki_index_view(request):
    result = []
    for c in Wiki_Category.objects.filter(father=None):
        c_dict = {"code": c.code, "name": c.name, "children": []}
        for lv in Wiki_Category.objects.filter(father=c):
            lv_dict = {"code": lv.code, "name": lv.name, "children": []}
            for item in Wiki_Item.objects.filter(category=lv):
                lv_dict["children"].append(item)
            c_dict["children"].append(lv_dict)
        result.append(c_dict)

    param = {"page_title": "美容百科",
             "info": get_panel_info(),
             "active_page": "wiki",
             "bottom_nav": request.user_agent.is_mobile,
             "menu": result,
             }
    return render(request, "products/wiki.html", param)


def wiki_item_view(request, item_code):
    param = {
        "info": get_panel_info(),
        "active_page": "wiki",
        "bottom_nav": request.user_agent.is_mobile,
    }
    item = Wiki_Item.objects.get(code=item_code)
    if item is not None:
        param["page_title"] = item.name + " - 美容百科"
        param["item"] = item
        return render(request, "products/wiki_item.html", param)
    else:
        raise Http404("对不起，未找到该百科条目")


def operator_view(request):
    param = {
        "page_title": '圣博丽雅平台',
        "info": get_panel_info(),
        "active_page": "operators",
        "bottom_nav": request.user_agent.is_mobile,
        "pin_list": Operator.objects.filter(pin=True)
    }
    if request.user.is_authenticated:
        usr = User_Profile.objects.get(id=request.user.id)
        param["usr_lv"] = usr.vip_lv
    else:
        param["usr_lv"] = -1

    return render(request, "products/operators.html", param)


def operator_search_view(request):
    param = {
        "page_title": '圣博丽雅平台-搜索结构',
        "info": get_panel_info(),
        "active_page": "operators",
        "bottom_nav": request.user_agent.is_mobile,
        "pin_list": Operator.objects.filter(pin=True)
    }

    if request.user.is_authenticated:
        usr = User_Profile.objects.get(id=request.user.id)
        param["usr_lv"] = usr.vip_lv
    else:
        param["usr_lv"] = -1

    query = request.GET.get("query")
    param["op_list"] = Operator.objects.filter(Q(name__contains=query) | Q(address__contains=query))
    return render(request, "products/operators_search.html", param)


def operator_filter_view(request, cond):
    param = {"page_title": "产品中心", "info": get_panel_info(), "active_page": "operators",
             "bottom_nav": request.user_agent.is_mobile
             }
    if not request.user.is_anonymous:
        usr = User_Profile.objects.get(id=request.user.id)
        param["usr_lv"] = usr.vip_lv
    else:
        param["usr_lv"] = -1

    if cond in ["PRSTDO", "PRHOSP", "PUHOSP", "INDOCT"]:
        param["op_list"] = Operator.objects.filter(oper_type=cond)
    else:
        param["op_list"] = Operator.objects.all()

    if cond == "PRSTDO":
        param["hosp_type"] = "私人工作室"
    elif cond == "PRHOSP":
        param["hosp_type"] = "私立医院"
    elif cond == "PUHOSP":
        param["hosp_type"] = "公立医院"
    elif cond == "INDOCT":
        param["hosp_type"] = "独立医生"
    else:
        param["hosp_type"] = "所有医院"
    return render(request, "products/operators_filter.html", param)


@login_required
def operator_detail_view(request, opid):
    param = {"page_title": "产品中心", "info": get_panel_info(), "active_page": "operators",
             "inv_code": User_Profile.objects.get(id=request.user.id).invi_code,
             "bottom_nav": request.user_agent.is_mobile, "op": get_object_or_404(Operator, id=opid)
             }
    return render(request, "products/operator_detail.html", param)


def wechat_login(request):
    REDIRECT_URI = quote('https://www.shengboliya.com/wxcode/', safe='')
    url = f"https://open.weixin.qq.com/connect/oauth2/authorize?appid={APPID}&redirect_uri={REDIRECT_URI}" \
          f"&response_type=code&scope={SCOPE}&state={STATE}#wechat_redirect"
    return HttpResponseRedirect(url)


def wechat_code(request):
    CODE = request.GET.get("code")
    j = get_wx_access_token(appid=APPID, secret=SECRET, code=CODE)
    if "errcode" in j:
        return HttpResponse(f"<h1>错误-{j['errcode']}</h1><p>{j['errmsg']}</p>")

    wx_json = get_user_info(access_token=j["access_token"], open_id=j["openid"])
    if "errcode" in wx_json:
        return HttpResponse(f"<h1>错误-{wx_json['errcode']}</h1><p>{wx_json['errmsg']}</p>")

    wx_user = WechatVisitor(
        openid=wx_json["openid"],
        avatar_url=wx_json["headimgurl"],
        nickname=convert_string_encoding(wx_json["nickname"]),
        sex=int(wx_json["sex"]),
        city=wx_json["city"],
        country=wx_json["country"],
        province=wx_json["province"],
    )
    wx_user.save()
    request.session["wx_openid"] = wx_json["openid"]
    if "next" in request.session:
        url = request.session["next"]
        del request.session["next"]
        return HttpResponseRedirect(url)
    return render(request, "wx.html", {"result": wx_user.nickname})


def blacklist_view(request, uid=None):
    param = {
        "page_title": "黑名单医院查询",
        "info": get_panel_info(),
        "active_page": "blacklist",
        "bottom_nav": request.user_agent.is_mobile,
    }

    try:
        creator = User_Profile.objects.get(id=uid)
        if "wx_openid" not in request.session:
            request.session["next"] = reverse("blacklist_with", kwargs={"uid": uid})
            return redirect("wechatLogin")
    except ObjectDoesNotExist:
        creator = None
        if "wx_openid" not in request.session:
            request.session["next"] = reverse("blacklist")
            return redirect("wechatLogin")

    wx_visit(open_id=request.session["wx_openid"], target=creator)

    blacklist = Blacklist.objects.all()
    param["blacklist"] = blacklist

    if request.method == "POST":
        form = reportForm(request.POST, initial={"creator": uid, "visitor": request.session["wx_openid"]})
        param["report_form"] = form

        if form.is_valid():
            form.save()
            request.session["toast_list"] = [get_toast(message="内容递交成功！", ty=2, color="success")]
            return render(request, "user/blacklist.html", param)
        else:
            return render(request, "user/blacklist.html", param)

    else:
        form = reportForm(initial={"creator": uid, "visitor": request.session["wx_openid"]})
        param["report_form"] = form
        return render(request, "user/blacklist.html", param)


@login_required
def tools_view(request):
    param = {
        "page_title": "圣博丽雅-工具",
        "info": get_panel_info(),
        "active_page": "tools",
        "bottom_nav": request.user_agent.is_mobile,
        "uid": request.user.id
    }
    return render(request, "tool/tools.html", param)


@login_required
def tool_blacklist_view(request, page=1):
    param = {
        "page_title": "圣博丽雅-工具",
        "info": get_panel_info(),
        "active_page": "tool_blacklist",
        "bottom_nav": request.user_agent.is_mobile,
        "uid": request.user.id,
    }

    visits = blacklist_visit.objects.filter(blacklist_creator=request.user.id)
    total = 0
    for r in visits:
        total += r.visit_total
    param["visit_total"] = total

    p = Paginator(visits, 25)
    param["page_count"] = p.num_pages
    param["page_list"] = p.get_elided_page_range(p.num_pages, on_each_side=2)
    visits = p.page(page)
    param["current_page"] = page
    param["visits"] = visits
    return render(request, "tool/tool_blacklist.html", param)


@login_required
def tool_report_view(request, page=1):
    param = {
        "page_title": "圣博丽雅-工具",
        "info": get_panel_info(),
        "active_page": "tool_report",
        "bottom_nav": request.user_agent.is_mobile,
        "uid": request.user.id,
    }
    reports = BlacklistReport.objects.filter(creator=request.user.id).order_by("-status", "create_date")
    p = Paginator(reports, 10)
    param["page_count"] = p.num_pages
    param["page_list"] = p.get_elided_page_range(p.num_pages, on_each_side=2)
    reports = p.page(page)
    param["current_page"] = page
    request.session["current_page"] = page
    param["reports"] = reports
    return render(request, "tool/tool_report.html", param)


@login_required
def tool_report_detail_view(request, rep_id):
    param = {
        "page_title": "圣博丽雅-工具",
        "info": get_panel_info(),
        "active_page": "tool_report",
        "bottom_nav": request.user_agent.is_mobile,
        "uid": request.user.id,
        "rep_id": rep_id,
        "page_num": request.session.get("current_page")
    }

    rep = get_object_or_404(BlacklistReport, id=rep_id)
    param["report"] = rep

    return render(request, "tool/tool_report_detail.html", param)


@login_required
def tool_report_status(request, rep_id):
    rep = BlacklistReport.objects.get(id=rep_id)
    rep.status = not rep.status
    rep.save()
    return redirect("tool_report_detail", rep_id)

###########################################################
# 静态页面
###########################################################


def partner_rule (request):
    param = {
        "page_title": "合伙人规则",
        "info": get_panel_info(),
        "active_page": "partnerRule",
        "bottom_nav": request.user_agent.is_mobile,
    }
    return render(request, "staticPages/partner_rule.html", param)


def private_rule (request):
    param = {
        "page_title": "圣博丽雅-个人信息保护声明",
        "info": get_panel_info(),
        "active_page": "privateRule",
        "bottom_nav": request.user_agent.is_mobile,
    }
    return render(request, "staticPages/private_rule.html", param)


###########################################################
# 后台
###########################################################


# TODO: <后台> 创建后台登录页面
def admin_login (request):
    param = {
        "page_title": "管理面板-登录",
        "info": get_panel_info(),
    }
    if "adm_notifications" in request.session:
        param['adm_notifications'] = request.session["adm_notifications"]
    else:
        request.session["adm_notifications"] = []
        param["adm_notifications"] = request.session["adm_notifications"]

    if request.method == 'POST':
        form = LoginForm(request.POST)
        param["form"] = form
        if form.is_valid():
            username = form.cleaned_data.get('username')
            user = User_Profile.objects.get(username=username)
            if user.is_staff:
                login(request, user)
                request.session["toast_list"] = [get_toast(message="管理员登陆成功！", ty=2, color="success")]
                return redirect('ADM_Index')
            else:
                raise PermissionDenied("对不起，您无权访问该页面，如需获取权限请联系管理员！")

        else:
            param["validate"] = True
            return render(request, 'admin/ADM_Login.html', param)
    else:
        form = LoginForm()
        param["form"] = form
    return render(request, 'admin/ADM_Login.html', param)


# TODO: <后台> 创建后台管理总页
@login_required
def admin_index (request):
    param = {
        "page_title": "管理面板",
        "info": get_panel_info(),
        "active_page": "ADM_Index",
        "report": get_report_all(),
        "user": request.user,
        "next": request.get_full_path()
    }
    if "adm_notifications" in request.session:
        param['adm_notifications'] = request.session["adm_notifications"]
    else:
        request.session["adm_notifications"] = []
        param["adm_notifications"] = request.session["adm_notifications"]
    if request.user.is_staff or request.user.is_superuser:
        return render(request, 'admin/ADM_Index.html', param)
    else:
        raise PermissionDenied("对不起，您无权访问该页面，请联系管理员！")


@login_required
def admin_user (request, page=1):
    param = {
        "page_title": "用户管理",
        "info": get_panel_info(),
        "active_page": "ADM_User",
        "user": request.user,
        "next": request.get_full_path()
    }
    if "adm_notifications" in request.session:
        param['adm_notifications'] = request.session["adm_notifications"]
    else:
        request.session["adm_notifications"] = []
        param["adm_notifications"] = request.session["adm_notifications"]
    if request.user.is_staff or request.user.is_superuser:
        user_list = User_Profile.objects.all()
        p = Paginator(user_list, item_per_page, orphans=2)
        param["page_count"] = p.num_pages
        param["page_list"] = p.get_elided_page_range(p.num_pages, on_each_side=2)

        try:
            user_list = p.page(page)
        except PageNotAnInteger:
            user_list = p.page(1)
        except EmptyPage:
            user_list = p.page(p.num_pages)

        param["current_page"] = page

        param["user_list"] = user_list
        return render(request, 'admin/ADM_User.html', param)
    else:
        raise PermissionDenied("对不起，您无权访问该页面，请联系管理员！")


@login_required
def admin_userEdit (request, uid):
    param = {
        "page_title": "用户编辑",
        "active_page": "ADM_User",
        "info": get_panel_info(),
        "user": request.user,
        "next": request.get_full_path()
    }
    if "adm_notifications" in request.session:
        param['adm_notifications'] = request.session["adm_notifications"]
    else:
        request.session["adm_notifications"] = []
        param["adm_notifications"] = request.session["adm_notifications"]

    targ_user = User_Profile.objects.get(id=uid)
    param["targ_user"] = targ_user
    param["targ_user_inv_count"] = len(User_Profile.objects.filter(invi_user=targ_user))
    if request.user.is_staff or request.user.is_superuser:
        if request.method == 'POST':
            form1 = ADM_UserForm_basic(request.POST, instance=targ_user, prefix="basic")
            form3 = ADM_RebateForm(request.POST, prefix="rebate")

            if "InfoChange" in request.POST:
                if form1.is_valid():
                    form1.save()
                    request.session["adm_notifications"].append(
                        adm_add_notification(title="用户信息更改成功",
                                             msg="用户 {} 信息已更改".format(targ_user.get_full_name()),
                                             icon="check2",
                                             type="1",
                                             color="green"))
                    return redirect("ADM_UserEdit", uid=uid)
                else:
                    request.session["adm_notifications"].append(
                        adm_add_notification(title="用户信息更改失败",
                                             msg="错误原因: {}".format(form1.errors.as_data()),
                                             icon="x-circle",
                                             type="1",
                                             color="red"))
                    param['adm_notifications'] = request.session["adm_notifications"]
                    param["ADM_UserForm_basic"] = ADM_UserForm_basic(instance=targ_user, prefix="basic")
                    param["ADM_RebateForm"] = ADM_RebateForm(prefix="rebate")
                    return render(request, "admin/AdM_UserEdit.html", param)

            elif "Rebate" in request.POST:
                if form3.is_valid():
                    amount = decimal.Decimal(form3.cleaned_data.get("amount"))
                    appointment = form3.cleaned_data.get("appointment")
                    if appointment is not None:
                        set_rebate(user=targ_user, amount=amount, appointment=appointment,
                                   creator=User_Profile.objects.get(id=request.user.id))
                    else:
                        set_rebate(user=targ_user, amount=amount, creator=User_Profile.objects.get(id=request.user.id))
                    request.session["adm_notifications"].append(
                        adm_add_notification(title="分佣成功",
                                             msg="用户 {} 分佣{}成功".format(targ_user.get_full_name(), amount),
                                             icon="check2",
                                             type="1",
                                             color="green"))
                    return redirect("ADM_UserEdit", uid=uid)
                else:
                    request.session["adm_notifications"].append(
                        adm_add_notification(title="分佣失败",
                                             msg="错误原因: {}".format(form3.errors.as_data()),
                                             icon="x-circle",
                                             type="1",
                                             color="red"))
                    param['adm_notifications'] = request.session["adm_notifications"]
                    param["ADM_UserForm_basic"] = ADM_UserForm_basic(instance=targ_user, prefix="basic")
                    param["ADM_RebateForm"] = ADM_RebateForm(prefix="rebate")
                    return render(request, "admin/AdM_UserEdit.html", param)

            else:
                param["ADM_UserForm_basic"] = ADM_UserForm_basic(instance=targ_user, prefix="basic")
                param["ADM_RebateForm"] = ADM_RebateForm(prefix="rebate")
                return render(request, "admin/AdM_UserEdit.html", param)
        else:
            param["ADM_UserForm_basic"] = ADM_UserForm_basic(instance=targ_user, prefix="basic")
            param["ADM_RebateForm"] = ADM_RebateForm(prefix="rebate")
            return render(request, "admin/AdM_UserEdit.html", param)
    else:
        raise PermissionDenied("对不起，您无权访问该页面，请联系管理员！")


@login_required
def admin_userDelete (request, uid):
    if request.user.is_staff or request.user.is_superuser:
        User_Profile.objects.get(id=uid).delete()
        return redirect(reverse("ADM_User"))
    else:
        raise PermissionDenied("对不起，您无权访问该页面，请联系管理员！")


@login_required
def admin_wikiCategory (request):
    param = {
        "page_title": "百科项目管理",
        "info": get_panel_info(),
        "active_page": "ADM_Wiki",
        "user": request.user,
        "next": request.get_full_path()
    }
    if "adm_notifications" in request.session:
        param['adm_notifications'] = request.session["adm_notifications"]
    else:
        request.session["adm_notifications"] = []
        param["adm_notifications"] = request.session["adm_notifications"]
    if request.user.is_staff or request.user.is_superuser:
        param["category_list"] = Wiki_Category.objects.all()
        return render(request, "admin/ADM_WikiCategory.html", param)
    else:
        raise PermissionDenied("对不起，您无权访问该页面，请联系管理员！")


@login_required
def admin_wikiCategoryNew (request):
    param = {
        "page_title": "百科项目管理-增加",
        "info": get_panel_info(),
        "active_page": "ADM_Wiki",
        "user": request.user,
        "next": request.get_full_path()
    }
    if "adm_notifications" in request.session:
        param['adm_notifications'] = request.session["adm_notifications"]
    else:
        request.session["adm_notifications"] = []
        param["adm_notifications"] = request.session["adm_notifications"]
    if request.user.is_staff or request.user.is_superuser:
        if request.method == 'POST':
            form1 = ADM_WikiForm_CategoryEN(request.POST)
            if form1.is_valid():
                temp = form1.save()
                param["adm_notifications"].append(adm_add_notification(title="类目 {} 创建成功".format(temp.name),
                                                                       msg="类目创建成功",
                                                                       icon="check2",
                                                                       type="1",
                                                                       color="green"))
                return redirect(reverse("ADM_WikiCategoryIndex"))
            else:
                param["ADM_WikiCateForm"] = ADM_WikiForm_CategoryEN()
                param["adm_notifications"].append(adm_add_notification(title="类目创建失败",
                                                                       msg=form1.errors.items(),
                                                                       icon="x-octagon-fill",
                                                                       type="1",
                                                                       color="red"))
                return render(request, "admin/ADM_WikiCategoryNew.html", param)
        else:
            param["ADM_WikiCateForm"] = ADM_WikiForm_CategoryEN()
            return render(request, "admin/ADM_WikiCategoryNew.html", param)
    else:
        raise PermissionDenied("对不起，您无权访问该页面，请联系管理员！")


@login_required
def admin_wikiCategoryEdit (request, cate_code):
    param = {
        "page_title": "百科项目管理-编辑",
        "info": get_panel_info(),
        "active_page": "ADM_Wiki",
        "adm_notifications": request.session["adm_notifications"],
        "user": request.user,
        "next": request.get_full_path()
    }
    if "adm_notifications" in request.session:
        param['adm_notifications'] = request.session["adm_notifications"]
    else:
        request.session["adm_notifications"] = []
        param["adm_notifications"] = request.session["adm_notifications"]
    if request.user.is_staff or request.user.is_superuser:
        cate = Wiki_Category.objects.get(code=cate_code)
        if request.method == 'POST':
            form1 = ADM_WikiForm_CategoryEN(request.POST, instance=cate)
            if form1.is_valid():
                if form1.has_changed():
                    temp = form1.save()
                    request.session["adm_notifications"].append(
                        adm_add_notification(title="类目 {} 修改成功".format(temp.name),
                                             msg="类目 {} 已修改".format(temp.name),
                                             icon="check2",
                                             type="1",
                                             color="green"))
                return redirect("ADM_WikiCategoryIndex")
            else:
                param["ADM_WikiCateForm"] = ADM_WikiForm_CategoryEN(instance=cate)
                request.session["adm_notifications"].append(adm_add_notification(title="类目 {} 修改失败".format(cate.name),
                                                                                 msg=form1.errors.items(),
                                                                                 icon="x-octagon-fill",
                                                                                 type="1",
                                                                                 color="red"))
                param["adm_notifications"] = request.session["adm_notifications"]

                return render(request, "admin/ADM_WikiCategoryEdit.html", param)
        else:
            param["ADM_WikiCateForm"] = ADM_WikiForm_CategoryEN(instance=cate)
            return render(request, "admin/ADM_WikiCategoryEdit.html", param)
    else:
        raise PermissionDenied("对不起，您无权访问该页面，请联系管理员！")


@login_required
def admin_wikiCategoryDel (request, cate_code):
    if request.user.is_staff or request.user.is_superuser:
        try:
            item = Wiki_Category.objects.get(code=cate_code)
            Wiki_Category.delete(item)
            request.session["adm_notifications"].append(adm_add_notification(title="类目 {} 删除成功".format(item.name),
                                                                             msg="类目已删除",
                                                                             icon="check2",
                                                                             type="1",
                                                                             color="green"))
        except ObjectDoesNotExist:
            request.session["adm_notifications"].append(adm_add_notification(title="类目删除失败",
                                                                             msg="未找到该类目",
                                                                             icon="x-octagon-fill",
                                                                             type="1",
                                                                             color="red"))
        finally:
            return redirect("ADM_WikiCategoryIndex")
    else:
        raise PermissionDenied("对不起，您无权访问该页面，请联系管理员！")


@login_required
def admin_wikiItem (request):
    param = {
        "page_title": "百科条目管理",
        "info": get_panel_info(),
        "active_page": "ADM_Wiki",
        "user": request.user,
        "next": request.get_full_path()
    }
    if "adm_notifications" in request.session:
        param['adm_notifications'] = request.session["adm_notifications"]
    else:
        request.session["adm_notifications"] = []
        param["adm_notifications"] = request.session["adm_notifications"]

    if request.user.is_staff or request.user.is_superuser:
        param["wikiItem_list"] = Wiki_Item.objects.all()
        return render(request, "admin/ADM_WikiItem.html", param)
    else:
        raise PermissionDenied("对不起，您无权访问该页面，请联系管理员！")


@login_required
def admin_wikiItemNew (request):
    param = {
        "page_title": "百科类目管理-创建",
        "info": get_panel_info(),
        "active_page": "ADM_Wiki",
        "user": request.user,
        "next": request.get_full_path()
    }
    if "adm_notifications" in request.session:
        param['adm_notifications'] = request.session["adm_notifications"]
    else:
        request.session["adm_notifications"] = []
        param["adm_notifications"] = request.session["adm_notifications"]

    if request.user.is_staff or request.user.is_superuser:
        if request.method == 'POST':
            form1 = ADM_WikiForm_ItemEN(request.POST)
            if form1.is_valid():
                temp = form1.save()
                param["adm_notifications"].append(adm_add_notification(title="类目 {} 创建成功".format(temp.name),
                                                                       msg="类目 {} 创建成功".format(temp.name),
                                                                       icon="check2",
                                                                       type="1",
                                                                       color="green"))
                return HttpResponseRedirect(reverse('ADM_WikiItemIndex'))
            else:
                param["ADM_WikiItemForm"] = ADM_WikiForm_ItemEN()
                param["adm_notifications"].append(adm_add_notification(title="类目创建失败",
                                                                       msg=form1.errors.items(),
                                                                       icon="x-octagon-fill",
                                                                       type="1",
                                                                       color="red"))
                param["adm_notifications"] = request.session["adm_notifications"]
                return render(request, "admin/ADM_WikiItemNew.html", param)
        else:
            param["ADM_WikiItemForm"] = ADM_WikiForm_ItemEN()
            return render(request, "admin/ADM_WikiItemNew.html", param)
    else:
        raise PermissionDenied("对不起，您无权访问该页面，请联系管理员！")


@login_required
def admin_wikiItemEdit (request, item_code):
    param = {
        "page_title": "百科类目管理-编辑",
        "info": get_panel_info(),
        "active_page": "ADM_Wiki",
        "user": request.user,
        "next": request.get_full_path()
    }
    if "adm_notifications" in request.session:
        param['adm_notifications'] = request.session["adm_notifications"]
    else:
        request.session["adm_notifications"] = []
        param["adm_notifications"] = request.session["adm_notifications"]

    if request.user.is_staff or request.user.is_superuser:
        item = Wiki_Item.objects.get(code=item_code)
        if request.method == 'POST':
            form1 = ADM_WikiForm_ItemEN(request.POST, instance=item)
            if form1.is_valid():
                temp = form1.save()
                request.session["adm_notifications"].append(adm_add_notification(title="类目 {} 修改成功".format(temp.name),
                                                                                 msg="类目 {} 已修改".format(temp.name),
                                                                                 icon="check2",
                                                                                 type="1",
                                                                                 color="green"))
                return redirect("ADM_WikiItemIndex")
            else:
                request.session["adm_notifications"].append(adm_add_notification(title="类目 {} 修改失败".format(item.name),
                                                                                 msg=form1.errors.items(),
                                                                                 icon="x-octagon-fill",
                                                                                 type="1",
                                                                                 color="red"))
                param["adm_notifications"] = request.session["adm_notifications"]
                param["ADM_WikiItemForm"] = ADM_WikiForm_ItemEN(instance=item)
                return render(request, "admin/ADM_WikiItemEdit.html", param)
        else:
            param["ADM_WikiItemForm"] = ADM_WikiForm_ItemEN(instance=item)
            return render(request, "admin/ADM_WikiItemEdit.html", param)
    else:
        raise PermissionDenied("对不起，您无权访问该页面，请联系管理员！")


@login_required
def admin_wikiItemDel (request, item_code):
    if request.user.is_staff or request.user.is_superuser:
        try:
            item = Wiki_Item.objects.get(code=item_code)
            Wiki_Item.delete(item)
            request.session["adm_notifications"].append(adm_add_notification(title="项目 {} 删除成功".format(item.name),
                                                                             msg="项目已删除",
                                                                             icon="check2",
                                                                             type="1",
                                                                             color="green"))
        except ObjectDoesNotExist:
            request.session["adm_notifications"].append(adm_add_notification(title="项目删除失败",
                                                                             msg="未找到该项目",
                                                                             icon="x-octagon-fill",
                                                                             type="1",
                                                                             color="red"))
        finally:
            return redirect("ADM_WikiItemIndex")
    else:
        raise PermissionDenied("对不起，您无权访问该页面，请联系管理员！")


@login_required
def admin_appointment (request, page=1):
    param = {
        "page_title": "预约管理",
        "info": get_panel_info(),
        "active_page": "ADM_Appointments",
        "user": request.user,
        "next": request.get_full_path(),
    }
    if "adm_notifications" in request.session:
        param['adm_notifications'] = request.session["adm_notifications"]
    else:
        request.session["adm_notifications"] = []
        param["adm_notifications"] = request.session["adm_notifications"]

    if request.user.is_staff or request.user.is_superuser:
        appoint_list = Appointment.objects.filter(show=True)
        p = Paginator(appoint_list, item_per_page, orphans=2)
        param["page_count"] = p.num_pages
        param["page_list"] = p.get_elided_page_range(p.num_pages, on_each_side=2)

        try:
            appoint_list = p.page(page)
        except PageNotAnInteger:
            appoint_list = p.page(1)
        except EmptyPage:
            appoint_list = p.page(p.num_pages)

        param["current_page"] = page

        param["appoint_list"] = appoint_list
        return render(request, "admin/ADM_appointments.html", param)
    else:
        raise PermissionDenied("对不起，您无权访问该页面，请联系管理员！")


@login_required
def admin_appointmentView (request, appoint_id):
    param = {
        "page_title": "预约管理",
        "info": get_panel_info(),
        "active_page": "ADM_Appointments",
        "user": request.user,
        "next": request.get_full_path(),
    }
    if "adm_notifications" in request.session:
        param['adm_notifications'] = request.session["adm_notifications"]
    else:
        request.session["adm_notifications"] = []
        param["adm_notifications"] = request.session["adm_notifications"]

    if request.user.is_staff or request.user.is_superuser:
        appoint = Appointment.objects.get(id=appoint_id)
        if request.method == 'POST':
            form1 = ADM_appointmentForm(request.POST, instance=appoint)
            if form1.is_valid():
                if form1.has_changed():
                    form1.save()
                return redirect("ADM_Appointments", appoint_id)
            else:
                param["ADM_AppointForm"] = ADM_appointmentForm(instance=appoint)
                return render(request, "admin/ADM_appointment_view.html", param)
        else:
            param["ADM_AppointForm"] = ADM_appointmentForm(instance=appoint)
            return render(request, "admin/ADM_appointment_view.html", param)
    else:
        raise PermissionDenied("对不起，您无权访问该页面，请联系管理员！")


@login_required
def admin_withdrawal (request, page=1):
    param = {
        "page_title": "提现管理",
        "info": get_panel_info(),
        "active_page": "ADM_Withdrawals",
        "user": request.user,
        "next": request.get_full_path(),
    }
    if "adm_notifications" in request.session:
        param['adm_notifications'] = request.session["adm_notifications"]
    else:
        request.session["adm_notifications"] = []
    param["adm_notifications"] = request.session["adm_notifications"]

    if request.user.is_staff or request.user.is_superuser:
        withdrawal_list = Withdrawal.objects.filter(status__lt=100)
        p = Paginator(withdrawal_list, item_per_page, orphans=2)
        param["page_count"] = p.num_pages
        param["page_list"] = p.get_elided_page_range(p.num_pages, on_each_side=2)

        try:
            withdrawal_list = p.page(page)
        except PageNotAnInteger:
            withdrawal_list = p.page(1)
        except EmptyPage:
            withdrawal_list = p.page(p.num_pages)

        param["current_page"] = page

        param["withdrawal_list"] = withdrawal_list
        return render(request, "admin/ADM_Withdrawal.html", param)
    else:
        raise PermissionDenied("对不起，您无权访问该页面，请联系管理员！")


@login_required
def admin_withdrawalView (request, wid):
    param = {
        "page_title": "提现管理",
        "info": get_panel_info(),
        "active_page": "ADM_withdrawalView",
        "user": request.user,
        "next": request.get_full_path(),
    }
    if "adm_notifications" in request.session:
        param['adm_notifications'] = request.session["adm_notifications"]
    else:
        request.session["adm_notifications"] = []
    param["adm_notifications"] = request.session["adm_notifications"]

    if request.user.is_staff or request.user.is_superuser:
        withdrawal = Withdrawal.objects.get(id=wid)
        param["withdrawal"] = withdrawal
        if request.method == 'POST':
            form1 = ADM_WithdrawalForm(request.POST, instance=withdrawal)
            if form1.is_valid():
                status_code = form1.cleaned_data.get("status")
                if status_code == 100:
                    u = withdrawal.applicator
                    u.frozen -= withdrawal.amount
                    t = Transaction(transaction_type=2, note="提现成功，订单号-{}".format(withdrawal.id),
                                    holder=u, amount=withdrawal.amount)
                    t.save()
                    u.save()

                form1.save()
                request.session["adm_notifications"].append(
                    adm_add_notification(title="提现操作成功",
                                         msg="用户{}提现{}元成功".format(withdrawal.applicator.get_full_name(),
                                                                  withdrawal.amount),
                                         icon="check2",
                                         type="1",
                                         color="green"))
                return redirect("ADM_WithdrawalView", wid)
        else:
            param["ADM_WithdrawalForm"] = ADM_WithdrawalForm(instance=withdrawal)
            return render(request, "admin/ADM_WithdrawalView.html", param)
    else:
        raise PermissionDenied("对不起，您无权访问该页面，请联系管理员！")


@login_required
def admin_wechat_view(request, page=1):
    param = {
        "page_title": "OP管理",
        "info": get_panel_info(),
        "active_page": "ADM_Wechat",
        "user": request.user,
        "next": request.get_full_path(),
    }
    if "adm_notifications" in request.session:
        param['adm_notifications'] = request.session["adm_notifications"]
    else:
        request.session["adm_notifications"] = []
        param["adm_notifications"] = request.session["adm_notifications"]

    if request.user.is_staff or request.user.is_superuser:
        user_list = WechatVisitor.objects.all()
        p = Paginator(user_list, item_per_page, orphans=2)
        param["page_count"] = p.num_pages
        param["page_list"] = p.get_elided_page_range(p.num_pages, on_each_side=2)

        try:
            user_list = p.page(page)
        except PageNotAnInteger:
            user_list = p.page(1)
        except EmptyPage:
            user_list = p.page(p.num_pages)

        param["current_page"] = page

        param["user_list"] = user_list
        return render(request, 'admin/ADM_Wechat.html', param)
    else:
        raise PermissionDenied("对不起，您无权访问该页面，请联系管理员！")


@login_required
def admin_operators (request):
    param = {
        "page_title": "OP管理",
        "info": get_panel_info(),
        "active_page": "ADM_Operators",
        "user": request.user,
        "next": request.get_full_path(),
    }
    if "adm_notifications" in request.session:
        param['adm_notifications'] = request.session["adm_notifications"]
    else:
        request.session["adm_notifications"] = []
        param["adm_notifications"] = request.session["adm_notifications"]

    if request.user.is_staff or request.user.is_superuser:
        op_li = Operator.objects.all()
        # if cond in ["PRSTDO", "PRHOSP", "PUHOSP", "INDOCT"]:
        #     op_li = Operator.objects.filter(oper_type=cond)
        # else:
        #     op_li = Operator.objects.all()
        param["op_list"] = op_li
        return render(request, "admin/ADM_OP.html", param)
    else:
        raise PermissionDenied("对不起，您无权访问该页面，请联系管理员！")


@login_required
def admin_operatorsNew (request):
    param = {
        "page_title": "OP管理 - 创建",
        "info": get_panel_info(),
        "active_page": "ADM_Operators",
        "user": request.user,
        "next": request.get_full_path(),
    }
    if "adm_notifications" in request.session:
        param['adm_notifications'] = request.session["adm_notifications"]
    else:
        request.session["adm_notifications"] = []
        param["adm_notifications"] = request.session["adm_notifications"]

    if request.user.is_staff or request.user.is_superuser:
        if request.method == 'POST':
            form1 = ADM_OperatorForm(request.POST)
            if form1.is_valid():
                temp = form1.save()
                request.session["adm_notifications"].append(adm_add_notification(title="OP {} 创建成功".format(temp.name),
                                                                                 msg="OP创建成功",
                                                                                 icon="check2",
                                                                                 type="1",
                                                                                 color="green"))
                return redirect(reverse("ADM_Operators"))
            else:
                param["ADM_OPForm"] = ADM_OperatorForm()
                request.session["adm_notifications"].append(adm_add_notification(title="OP创建失败",
                                                                                 msg=form1.errors.items(),
                                                                                 icon="x-octagon-fill",
                                                                                 type="1",
                                                                                 color="red"))
                param["adm_notifications"] = request.session["adm_notifications"]
                return render(request, "admin/ADM_OPEN.html", param)
        else:
            param["ADM_OPForm"] = ADM_OperatorForm()
            return render(request, "admin/ADM_OPEN.html", param)
    else:
        raise PermissionDenied("对不起，您无权访问该页面，请联系管理员！")


@login_required
def admin_operatorsEdit (request, opid):
    param = {
        "page_title": "OP管理 - 创建",
        "info": get_panel_info(),
        "active_page": "ADM_Operators",
        "user": request.user,
        "next": request.get_full_path(),
    }
    if "adm_notifications" in request.session:
        param['adm_notifications'] = request.session["adm_notifications"]
    else:
        request.session["adm_notifications"] = []
        param["adm_notifications"] = request.session["adm_notifications"]
    if request.user.is_staff or request.user.is_superuser:
        op = Operator.objects.get(id=opid)
        if request.method == 'POST':
            form1 = ADM_OperatorForm(request.POST, instance=op)
            if form1.is_valid():
                temp = form1.save()
                param["adm_notifications"].append(adm_add_notification(title="OP {} 修改成功".format(temp.name),
                                                                       msg="OP修改成功",
                                                                       icon="check2",
                                                                       type="1",
                                                                       color="green"))
                return redirect(reverse("ADM_Operators"))
            else:
                param["ADM_OPForm"] = ADM_OperatorForm(instance=op)
                request.session["adm_notifications"].append(adm_add_notification(title="OP修改失败",
                                                                                 msg=form1.errors.items(),
                                                                                 icon="x-octagon-fill",
                                                                                 type="1",
                                                                                 color="red"))
                param["adm_notifications"] = request.session["adm_notifications"]
                return render(request, "admin/ADM_OPEN.html", param)
        else:
            param["ADM_OPForm"] = ADM_OperatorForm(instance=op)
            return render(request, "admin/ADM_OPEN.html", param)
    else:
        raise PermissionDenied("对不起，您无权访问该页面，请联系管理员！")


@login_required
def admin_operatorsDele (request, opid):
    if request.user.is_staff or request.user.is_superuser:
        try:
            op = Operator.objects.get(id=opid)
            Operator.delete(op)
            request.session["adm_notifications"].append(adm_add_notification(title="OP {} 删除成功".format(op.name),
                                                                             msg="OP已删除",
                                                                             icon="check2",
                                                                             type="1",
                                                                             color="green"))
        except ObjectDoesNotExist:
            request.session["adm_notifications"].append(adm_add_notification(title="OP删除失败",
                                                                             msg="未找到该OP",
                                                                             icon="x-octagon-fill",
                                                                             type="1",
                                                                             color="red"))
        finally:
            return redirect("ADM_Operators")
    else:
        raise PermissionDenied("对不起，您无权访问该页面，请联系管理员！")


@login_required
def admin_report_view(request, page=1):
    param = {
        "page_title": "咨询管理",
        "info": get_panel_info(),
        "active_page": "ADM_Report",
        "user": request.user,
        "next": request.get_full_path(),
    }

    if "adm_notifications" in request.session:
        param['adm_notifications'] = request.session["adm_notifications"]
    else:
        request.session["adm_notifications"] = []
        param["adm_notifications"] = request.session["adm_notifications"]

    if request.user.is_staff or request.user.is_superuser:
        reports = BlacklistReport.objects.all().order_by("-status", "create_date")
        p = Paginator(reports, 10)
        param["page_count"] = p.num_pages
        param["page_list"] = p.get_elided_page_range(p.num_pages, on_each_side=2)
        reports = p.page(page)
        param["current_page"] = page
        request.session["current_page"] = page
        param["reports"] = reports
        return render(request, "admin/ADM_Report.html", param)
    else:
        raise PermissionDenied("对不起，您无权访问该页面，请联系管理员！")


@login_required
def admin_report_detail_view(request, rep_id):
    param = {
        "page_title": "咨询管理",
        "info": get_panel_info(),
        "active_page": "ADM_Report",
        "user": request.user,
        "next": request.get_full_path(),
        "rep_id": rep_id,
        "page_num": request.session.get("current_page")
    }
    if "adm_notifications" in request.session:
        param['adm_notifications'] = request.session["adm_notifications"]
    else:
        request.session["adm_notifications"] = []
        param["adm_notifications"] = request.session["adm_notifications"]

    if request.user.is_staff or request.user.is_superuser:
        rep = get_object_or_404(BlacklistReport, id=rep_id)
        param["report"] = rep
        return render(request, "admin/ADM_Report_Detail.html", param)
    else:
        raise PermissionDenied("对不起，您无权访问该页面，请联系管理员！")


@login_required
def admin_report_status(request, rep_id):
    if request.user.is_staff or request.user.is_superuser:
        rep = BlacklistReport.objects.get(id=rep_id)
        rep.status = not rep.status
        rep.save()
        return redirect("ADM_Report_Detail", rep_id)
    else:
        raise PermissionDenied("对不起，您无权访问该页面，请联系管理员！")


@login_required
def admin_blacklist_view(request, page=1):
    param = {
        "page_title": "咨询管理",
        "info": get_panel_info(),
        "active_page": "ADM_Blacklist",
        "user": request.user,
        "next": request.get_full_path(),
    }
    if "adm_notifications" in request.session:
        param['adm_notifications'] = request.session["adm_notifications"]
    else:
        request.session["adm_notifications"] = []
        param["adm_notifications"] = request.session["adm_notifications"]

    if request.user.is_staff or request.user.is_superuser:
        blacklists = Blacklist.objects.all()
        p = Paginator(blacklists, 10)
        param["page_count"] = p.num_pages
        param["page_list"] = p.get_elided_page_range(p.num_pages, on_each_side=2)
        blacklists = p.page(page)
        param["current_page"] = page
        request.session["current_page"] = page
        param["reports"] = blacklists
        return render(request, "admin/ADM_blacklist.html", param)
    else:
        raise PermissionDenied("对不起，您无权访问该页面，请联系管理员！")


def admin_noti_remove (request, origin_page, noti_ind=None):
    if noti_ind is None:
        request.session["adm_notifications"] = []
        return HttpResponseRedirect(origin_page)
    else:
        try:
            del request.session["adm_notifications"][noti_ind]
        except IndexError:
            pass
        finally:
            return HttpResponseRedirect(origin_page)


###########################################################
# 错误信息
###########################################################


def perm_denied_view (request, exception):
    param = {"exception": exception}
    return render(request, "errors/403.html", param)


def page_not_found_view (request, exception):
    param = {"exception": exception}
    return render(request, "errors/404.html", param)
