import datetime
import re
from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from pypinyin import lazy_pinyin, Style
from .api import get_id_verify_status, bank_re
from .models import *
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from .panel_setting import *


class LoginForm(forms.Form):
    username = forms.CharField(max_length=150,
                               min_length=6,
                               label="用户名",
                               widget=forms.TextInput(attrs={'class': 'form-control',
                                                             'placeholder': "Username",
                                                             'aria-describedby': "id_usernameFeedback"}),
                               help_text=usenm_helptxt,
                               error_messages={
                                   "required": usrnm_errmsg_require,
                                   "min_length": usrnm_errmsg_min_length,
                                   "max_length": usrnm_errmsg_max_length
                               })
    paswd = forms.CharField(min_length=8,
                            label="密码",
                            widget=forms.widgets.PasswordInput(attrs={'class': 'form-control',
                                                                      'placeholder': "Password"}),
                            help_text=paswd_helptxt,
                            error_messages={
                                "required": paswd_errmsg_require,
                                "min_length": paswd_errmsg_length
                            })

    next = forms.HiddenInput()

    def clean_username (self):
        username = self.cleaned_data.get('username')
        if User_Profile.objects.filter(username=username):
            return username
        else:
            raise ValidationError(usrnm_errmsg_NOT_exist, code="usrnmNotExist")

    def clean_paswd (self):
        paswd = self.cleaned_data.get('paswd')
        username = self.cleaned_data.get('username')
        u = authenticate(username=username, password=paswd)
        if u is not None:
            return paswd
        else:
            raise ValidationError(unpw_errmsg_mismatch, code="unpwNotMatch")


class RegisterForm(forms.Form):
    username = forms.CharField(max_length=150,
                               min_length=6,
                               label="用户名",
                               widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Username"}),
                               help_text=usenm_helptxt,
                               error_messages={
                                   "required": usrnm_errmsg_require,
                                   "min_length": usrnm_errmsg_min_length,
                                   "max_length": usrnm_errmsg_max_length
                               })
    paswd1 = forms.CharField(min_length=8,
                             label="密码",
                             widget=forms.widgets.TextInput(
                                 attrs={'class': 'form-control', 'placeholder': "VerifyCode"}),
                             help_text=paswd_helptxt,
                             error_messages={
                                 "required": paswd_errmsg_require,
                                 "min_length": paswd_errmsg_length
                             })

    paswd2 = forms.CharField(min_length=8,
                             label="确认",
                             widget=forms.widgets.PasswordInput(attrs={'class': 'form-control',
                                                                       'placeholder': "Confirm"}),
                             help_text=confirm_helptxt,
                             error_messages={
                                 "required": paswd_errmsg_require,
                                 "min_length": paswd_errmsg_length
                             })

    # veri_code = forms.CharField(min_length=8,
    #                             label="验证码",
    #                             widget=forms.widgets.PasswordInput(attrs={'class': 'form-control',
    #                                                                       'placeholder': "Confirm"}),
    #                             help_text=confirm_helptxt,
    #                             error_messages={
    #                                 "required": paswd_errmsg_require,
    #                                 "min_length": paswd_errmsg_length
    #                             },
    #                             required=False)

    tele = forms.CharField(max_length=13,
                           label="手机",
                           widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Telephone"}),
                           error_messages={
                               "required": tell_errmsg_require
                           })

    invi_code = forms.CharField(max_length=code_length,
                                label="邀请码",
                                widget=forms.TextInput(attrs={'class': 'form-control',
                                                              'placeholder': "Invitation Code"}),
                                error_messages={
                                    "required": paswd_errmsg_require,
                                    "min_length": paswd_errmsg_length
                                },
                                help_text="若没有可不填",
                                required=False)

    def clean_paswd1 (self):
        pwd = self.cleaned_data.get('paswd1')
        if validate_password(pwd) is None:
            return pwd

    def clean_paswd2 (self):
        paswd1 = self.cleaned_data.get('paswd1')
        paswd2 = self.cleaned_data.get('paswd2')
        if paswd1 == paswd2:
            return paswd2
        else:
            raise forms.ValidationError(paswd_errmsg_NOT_match, code="paswdNotMatch")

    def clean_tele (self):
        tele = self.cleaned_data.get('tele')
        reg = re.compile(r"1[3|4|5|7|8][0-9]{9}")
        if reg.match(tele):
            if User_Profile.objects.filter(tele=tele).exists():
                raise forms.ValidationError(tell_errmsg_exist,
                                            code='mobileAlreadyExist')
            else:
                return tele
        else:
            raise forms.ValidationError(tell_errmsg_invalid, code='mobileInvalid')

    def clean_invi_code (self):
        invi_code = self.cleaned_data.get('invi_code')
        if invi_code != "":
            try:
                u = User_Profile.objects.get(invi_code=invi_code)
                return u
            except ObjectDoesNotExist:
                raise forms.ValidationError(invi_errmsg_NOT_exist, code="inviNotExist")
        else:
            return None


class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        exclude = ("status", "create_time", "show")
        # widgets = {"create_user": forms.HiddenInput()}

    def __init__ (self, *args, **kwargs):
        super(AppointmentForm, self).__init__(*args, **kwargs)
        self.fields["create_user"].widget = forms.HiddenInput()
        self.fields["create_user"].required = False


class IDVerifyForm(forms.Form):
    real_name = forms.CharField(max_length=20,
                                min_length=2,
                                label="真实姓名",
                                widget=forms.TextInput(attrs={
                                    'class': 'form-control',
                                    'placeholder': '真实姓名'
                                }))

    id_card = forms.CharField(max_length=18,
                              min_length=18,
                              label="身份证号",
                              validators=[IDValidator],
                              widget=forms.TextInput(attrs={
                                  'class': 'form-control',
                                  'placeholder': '身份证号'
                              }))

    request_user = forms.ModelChoiceField(queryset=User_Profile.objects.all(),
                                          empty_label=None)

    def clean (self):
        cleaned_data = super().clean()
        name = cleaned_data.get("real_name")
        id_card = cleaned_data.get("id_card")
        user = cleaned_data.get("request_user")
        if user.get_id_status():
            raise ValidationError("已绑定身份证号码,需要更改请联系管理员", code="IDLocked")
        else:
            status = get_id_verify_status(name=name, id_card=id_card)
            if status == 200:
                return cleaned_data
            else:
                raise ValidationError("验证失败，请重试!", code="VerificationFail")


class WithdrawalFrom(forms.Form):
    applicator_id = forms.IntegerField(
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "applicator_id"
        })
    )
    amount = forms.IntegerField(label="提现金额",
                                widget=forms.TextInput(attrs={
                                    "class": "form-control",
                                    "placeholder": "amount"
                                }))
    method = forms.IntegerField(label="提现方式")
    account = forms.CharField(label="账户",
                              widget=forms.TextInput(attrs={
                                  "class": "form-control",
                                  "placeholder": "account"
                              }))

    def clean_method (self):
        method = self.cleaned_data.get("method")
        if method not in [1, 2, 3]:
            raise forms.ValidationError(message="支付方法不可用", code="MethodInvalid")
        else:
            return method

    def clean_account (self):
        method = self.cleaned_data.get("method")
        account = self.cleaned_data.get("account")
        if method == 1:
            reg = re.compile(r"/^([1-9])(\d{14}|\d{18})$/")
            if reg.match(account):
                return account
            else:
                raise forms.ValidationError("银行账号格式错误，请重试", code='bankIDInvalid')
        else:
            return account

    def clean_applicator_id (self):
        applicator_id = self.cleaned_data.get("applicator_id")
        if User_Profile.objects.get(id=applicator_id):
            return applicator_id
        else:
            raise ValidationError(message="查无此账号，请重新登陆或联系管理员", code="InvalidID")

    def clean_amount (self):
        amount = self.cleaned_data.get("amount")
        applicator_id = self.cleaned_data.get("applicator_id")
        applicator = User_Profile.objects.get(id=applicator_id)
        if amount > applicator.balance:
            raise ValidationError(message="提现金额超过账户总余额", code="WithdrawalOverLimit")
        else:
            return amount

    def clean (self):
        cleaned_data = super().clean()
        if Withdrawal.objects.filter(applicator_id=cleaned_data.get("applicator_id"),
                                     create_date=datetime.date.today()):
            raise ValidationError(message="每位用户每日仅可发起一次提现申请", code="MultipleApplications")
        else:
            return cleaned_data


class ADM_UserForm(forms.Form):
    inv_type_list = (
        ("UNM", "用户名"),
        ("KEY", "邀请码")
    )

    username = forms.CharField(max_length=150,
                               min_length=6,
                               label="用户名",
                               widget=forms.TextInput(attrs={'class': 'form-control',
                                                             'placeholder': '用户名'}),
                               help_text=usenm_helptxt,
                               error_messages={
                                   "required": usrnm_errmsg_require,
                                   "min_length": usrnm_errmsg_min_length,
                                   "max_length": usrnm_errmsg_max_length
                               }
                               )

    email = forms.CharField(max_length=150,
                            min_length=1,
                            label="邮箱",
                            widget=forms.TextInput(attrs={'class': 'form-control'})
                            )

    tele = forms.CharField(max_length=13,
                           label="手机",
                           widget=forms.TextInput(attrs={'class': 'form-control'}),
                           error_messages={
                               "required": tell_errmsg_require
                           }
                           )

    inv_code = forms.CharField(max_length=code_length,
                               label="邀请码",
                               widget=forms.TextInput(attrs={'class': 'form-control'}))

    inv_type = forms.ChoiceField(choices=inv_type_list,
                                 label="邀请方式",
                                 widget=forms.Select(attrs={'class': 'form-control'}),
                                 required=False
                                 )

    inv_target = forms.CharField(max_length=150,
                                 label="邀请人",
                                 widget=forms.TextInput(attrs={'class': 'form-control'}),
                                 required=False
                                 )

    def clean_inv_code (self):
        c = self.cleaned_data.get('inv_code')
        reg = re.compile("^[A-Za-z0-9]+$")
        if reg.match(c):
            if User_Profile.objects.filter(inv_code=c).exists():
                raise forms.ValidationError("邀请码已存在", code='invCodeAlreadyExist')
            else:
                if len(c) != code_length:
                    raise forms.ValidationError("邀请码格式错误", code="invCodeInvalid")
                else:
                    return c
        else:
            raise forms.ValidationError("邀请码格式错误", code="invCodeInvalid")

    def clean_tele (self):
        tele = self.cleaned_data.get('tele')
        reg = re.compile("1[3|4|5|7|8][0-9]{9}")
        if reg.match(tele):
            if User_Profile.objects.filter(tele=tele).exists():
                raise forms.ValidationError(tell_errmsg_exist, code='mobileAlreadyExist')
            else:
                return tele
        else:
            raise forms.ValidationError(tell_errmsg_invalid, code='mobileInvalid')

    def clean_inv_target (self):
        inv_type = self.cleaned_data.get('inv_type')
        inv_targ = self.cleaned_data.get('inv_target')

        if inv_targ != "":
            if inv_type == "UID":
                try:
                    return User_Profile.objects.get(id=inv_targ)
                except ObjectDoesNotExist:
                    raise forms.ValidationError("用户不存在，请重新输入", code="user_not_exist")
            elif inv_type == "UNM":
                try:
                    return User_Profile.objects.get(username=inv_targ)
                except ObjectDoesNotExist:
                    raise forms.ValidationError("用户不存在，请重新输入", code="user_not_exist")
            elif inv_type == "KEY":
                try:
                    return User_Profile.objects.get(inv_code=inv_targ)
                except ObjectDoesNotExist:
                    raise forms.ValidationError("用户不存在，请重新输入", code="user_not_exist")
        else:
            return None


class ADM_UserForm_basic(forms.ModelForm):
    class Meta:
        model = User_Profile
        fields = ['email', 'nick', 'tele', "vip_lv"]


class ADM_UserForm_delete(forms.Form):
    confirm_input = forms.CharField(max_length=10,
                                    widget=forms.Select(attrs={'class': 'form-control'}),
                                    required=False)

    def clean_confirm_input (self):
        t = self.cleaned_data.get("confirm_input")
        return t == "删除" or t == "Delete"


class ADM_UserForm_paswdChange(forms.Form):
    paswd1 = forms.CharField(min_length=8,
                             label="输入新密码",
                             widget=forms.widgets.PasswordInput(
                                 attrs={'class': 'form-control'}),
                             help_text=paswd_helptxt,
                             error_messages={
                                 "required": paswd_errmsg_require,
                                 "min_length": paswd_errmsg_length
                             })

    paswd2 = forms.CharField(min_length=8,
                             label="再次输入密码",
                             widget=forms.widgets.PasswordInput(attrs={'class': 'form-control'}),
                             help_text=confirm_helptxt,
                             error_messages={
                                 "required": paswd_errmsg_require,
                                 "min_length": paswd_errmsg_length
                             })

    def clean_paswd1 (self):
        pwd = self.cleaned_data.get('paswd1')
        if validate_password(pwd) is None:
            return pwd

    def clean_paswd2 (self):
        paswd1 = self.cleaned_data.get('paswd1')
        paswd2 = self.cleaned_data.get('paswd2')
        if paswd1 == paswd2:
            return paswd2
        else:
            raise forms.ValidationError(paswd_errmsg_NOT_match, code="paswdNotMatch")


class ADM_WikiForm_CategoryEN(forms.ModelForm):
    def clean_code (self):
        c = self.cleaned_data.get("code").upper()
        reg = re.compile("^[A-Z]+$")
        if reg.match(c):
            return c
        else:
            raise forms.ValidationError("项目编码格式有误", code='cateCodeInvalidFormat')

    def clean_father (self):
        father = self.cleaned_data.get("father")
        if father is None:
            return None
        else:
            return father

    class Meta:
        model = Wiki_Category
        fields = ("code", "name", "father")
        help_texts = {
            "name": "类目显示的名称，请保证其唯一性",
            "code": "请使用3至10个大写英文字母进行组合，请保证其唯一性",
            "father": "请选择一条父级类目，默认为空"
        }

    def __init__ (self, *args, **kwargs):
        super(ADM_WikiForm_CategoryEN, self).__init__(*args, **kwargs)
        if self.instance is not None:
            self.fields["father"].queryset = Wiki_Category.objects.filter(father=None).exclude(
                code=self.instance.code)


class ADM_appointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = "__all__"


class ADM_WikiForm_ItemEN(forms.ModelForm):
    def clean_code (self):
        c = self.cleaned_data.get("code").upper()
        reg = re.compile("^[A-Z]+$")
        if reg.match(c):
            if self.instance:
                if Wiki_Item.objects.filter(code=c).exists():
                    raise forms.ValidationError("项目编码已存在", code='ItemCodeAlreadyExist')
                else:
                    return c
            else:
                if Wiki_Item.objects.filter(code=c).exists():
                    raise forms.ValidationError("项目编码已存在", code='ItemCodeAlreadyExist')
                else:
                    return c
        else:
            raise forms.ValidationError("项目编码格式有误", code='ItemCodeInvalidFormat')

    def clean_category (self):
        category = self.cleaned_data.get("category")
        if category is None:
            return None
        else:
            return category

    class Meta:
        model = Wiki_Item
        fields = ("category", "code", "name", "description", "pros", "cons", "method", "effect",
                  "precautions", "patient", "attention", "secure", "duration", "last", "anesthesia", "recover",
                  "period", "operator", "opermethod", "pain", "price")
        help_texts = {
            "code": "请使用3至10个大写英文字母进行组合",
        }


class ADM_OperatorForm(forms.ModelForm):
    class Meta:
        model = Operator
        fields = "__all__"
        labels = {
            "verified": "是否点亮验证标签",
            "pin": "是否加入推荐位"
        }


class ADM_RebateForm(forms.Form):
    amount = forms.DecimalField(max_digits=9, decimal_places=2, label="分佣金额")
    appointment = forms.ModelChoiceField(queryset=Appointment.objects.filter(status="FINISH"), required=False,
                                         label="相关预约")
    note = forms.CharField(max_length=500, label="备注", required=False)


class ADM_WithdrawalForm(forms.ModelForm):
    class Meta:
        model = Withdrawal
        fields = ["status"]
