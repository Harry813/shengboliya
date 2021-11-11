"""yimei URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path
from django.views.generic import TemplateView

from yimei import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('wxlogin/', views.wechat_login, name="wechatLogin"),
    path('wxcode/', views.wechat_code, name="wechatCode"),
    # path('superadmin/', admin.site.urls),
    path('', views.home, name="home"),
    path('promote/', views.promote_view, name="promote"),
    path('login/', views.login_view, name="login"),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name="register"),
    path('register/inv=<str:invi_code>/', views.register_view, name="registerINV"),
    path('profile/', views.profile_view, name="profile"),
    path('setting/', views.user_setting, name="setting"),
    path('verify/', views.user_id_verify, name="verify"),
    # path('detail/', views.detail_view, name="detail"),
    path('transactions/', views.transaction_view, name="transactions"),
    path('appointment/', views.appoint_view, name="appointments"),
    path('appointment/opid=<int:opid>/', views.appoint_view, name="OPappointments"),
    path('wiki/', views.wiki_index_view, name="wiki"),
    path('wiki/<str:item_code>', views.wiki_item_view, name="wikiItem"),
    path('withdrawal/', views.withdrawal_view, name="withdrawal"),
    path('operators/', views.operator_view, name="operators"),
    path('operators/filter=<str:cond>/', views.operator_filter_view, name="operatorsF"),
    path('operators/<int:opid>/', views.operator_detail_view, name="operatorsD"),
    path('operators/search/', views.operator_search_view, name="operatorsD"),
    path('partner_rule/', views.partner_rule, name="partnerRule"),
    path('private_rule/', views.private_rule, name="privateRule"),
    path('blacklist/<int:uid>/', views.blacklist_view, name="blacklist_with"),
    path('blacklist/', views.blacklist_view, name="blacklist"),
    path('tools/', views.tools_view, name="tools"),
    path('tool/blacklist/<int:page>/', views.tool_blacklist_view, name="tool_blacklist"),
    path('tool/report/<int:page>/', views.tool_report_view, name="tool_report"),
    path('tool/report/detail/<int:rep_id>/', views.tool_report_detail_view, name="tool_report_detail"),
    path('tool/report/status/<int:rep_id>/', views.tool_report_status, name="tool_report_status"),
    path('admin/login/', views.admin_login, name="ADM_Login"),
    path('admin/index/', views.admin_index, name="ADM_Index"),
    path('admin/', views.admin_index, name="ADM_Index_1"),
    path('admin/user/page<int:page>/', views.admin_user, name="ADM_User"),
    path('admin/user/uid<int:uid>/', views.admin_userEdit, name="ADM_UserEdit"),
    path('admin/user_delete/uid<int:uid>/', views.admin_userDelete, name="ADM_UserDelete"),
    path('admin/wiki/category/', views.admin_wikiCategory, name="ADM_WikiCategoryIndex"),
    path('admin/wiki/category/new/', views.admin_wikiCategoryNew, name="ADM_WikiCategoryNew"),
    path('admin/wiki/category/c=<str:cate_code>/', views.admin_wikiCategoryEdit, name="ADM_WikiCategoryEdit"),
    path('admin/wiki/category/delete/c=<str:cate_code>/', views.admin_wikiCategoryDel, name="ADM_WikiCategoryDel"),
    path('admin/wiki/item/', views.admin_wikiItem, name="ADM_WikiItemIndex"),
    path('admin/wiki/item/new/', views.admin_wikiItemNew, name="ADM_WikiItemNew"),
    path('admin/wiki/item/c=<str:item_code>/', views.admin_wikiItemEdit, name="ADM_WikiItemEdit"),
    path('admin/wiki/item/delete/c=<str:item_code>/', views.admin_wikiItemDel, name="ADM_WikiItemDel"),
    path('admin/noti/remove/path=<path:origin_page>/', views.admin_noti_remove, name="ADM_NotiRemoveAll"),
    path('admin/noti/remove/<int:noti_ind>/path=<path:origin_page>/', views.admin_noti_remove, name="ADM_NotiRemove"),
    path('admin/appointment/page<int:page>/', views.admin_appointment, name="ADM_Appointments"),
    path('admin/appointment/page<int:page>/', views.admin_appointment, name="ADM_Appointments"),
    path('admin/operators/', views.admin_operators, name="ADM_Operators"),
    path('admin/operators/new', views.admin_operatorsNew, name="ADM_OPNew"),
    path('admin/operators/op=<int:opid>', views.admin_operatorsEdit, name="ADM_OPEdit"),
    path('admin/operators/dele=<int:opid>', views.admin_operatorsDele, name="ADM_OPDele"),
    path('admin/withdrawals/page<int:page>/', views.admin_withdrawal, name="ADM_Withdrawals"),
    path('admin/withdrawal/wid=<int:wid>/', views.admin_withdrawalView, name="ADM_WithdrawalView"),
    path('admin/wechat/page<int:page>/', views.admin_wechat_view, name="ADM_Wechat"),
    path('admin/report/page<int:page>/', views.admin_report_view, name="ADM_Report"),
    path('admin/report/detail/<int:rep_id>/', views.admin_report_detail_view, name="ADM_Report_Detail"),
    path('admin/report/status/<int:rep_id>/', views.admin_report_status, name="ADM_Report_Status"),
    path(
        'MP_verify_xIDGduZfV6vPdCf8.txt/',
        TemplateView.as_view(
            template_name="MP_verify_xIDGduZfV6vPdCf8.txt",
            content_type="text/plain"
        ),
        name="wx_verify"),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

handler403 = views.perm_denied_view
handler404 = views.page_not_found_view
