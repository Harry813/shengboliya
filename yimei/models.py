import uuid
from django.contrib.auth.models import User, AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.validators import *
from django.db import models
from django.core.exceptions import *
from django.db.models import UniqueConstraint

from .panel_setting import *
from django.utils.translation import gettext_lazy as _
from uuid import UUID
from .validators import *


class Location(models.Model):
    code = models.CharField(max_length=6, primary_key=True)
    name = models.CharField(max_length=50)
    level = models.IntegerField()
    parent = models.ForeignKey(to="Location", on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        verbose_name = "地域"
        verbose_name_plural = verbose_name
        ordering = ['code']

    def get_full_name (self):
        if self.parent is None:
            return self.name
        else:
            a = self.parent
            if a.parent is None:
                return "{}-{}".format(a.name, self.name)
            else:
                return "{}-{}-{}".format(a.parent.name, a.name, self.name)

    def __str__ (self):
        return "{}, {}".format(self.code, self.get_full_name())


class User_Profile(AbstractUser):
    username = models.CharField(_('用户名'), unique=True, max_length=150,
                                error_messages={"max_length": usrnm_errmsg_max_length},
                                validators=[RegexValidator(regex="^[A-Za-z0-9]+$",
                                                           message=usrnm_errmsg_invalid),
                                            MinLengthValidator(limit_value=5,
                                                               message=usrnm_errmsg_min_length)])
    email = models.EmailField(_('邮箱地址'), blank=True, null=True)

    nick = models.CharField(_("昵称"), max_length=50, default="", blank=True, null=True)
    tele = models.CharField(max_length=11, verbose_name="手机", blank=True, null=True,
                            validators=[TeleValidator])

    invi_code = models.CharField(max_length=20, verbose_name="邀请码", unique=True)
    invi_user = models.ForeignKey("User_Profile", on_delete=models.CASCADE, verbose_name="邀请者", blank=True, null=True,
                                  editable=False)

    loca = models.ForeignKey("Location", on_delete=models.CASCADE, verbose_name="区域", default=None, blank=True,
                             null=True)

    vip_lv = models.PositiveSmallIntegerField(verbose_name="VIP等级", default=0, choices=VIP_level)

    real_name = models.CharField(max_length=15, verbose_name="真实姓名", blank=True)
    id_card = models.CharField(max_length=18, verbose_name="身份证号码", blank=True)

    balance = models.DecimalField(max_digits=9, decimal_places=2, verbose_name="总收入", default=0,
                                  validators=[MinValueValidator(0)])
    frozen = models.DecimalField(max_digits=9, decimal_places=2, verbose_name="冻结", default=0)
    today = models.DecimalField(max_digits=9, decimal_places=2, verbose_name="今日收入", default=0)

    class Meta:
        verbose_name = '用户'
        verbose_name_plural = verbose_name

    def get_full_name (self):
        if self.nick:
            return self.nick
        else:
            return self.username

    get_full_name.short_description = "姓名"

    def get_id_status (self):
        return self.id_card != "" and self.real_name != ""

    get_id_status.short_description = "实名认证状态"

    def get_covered_name (self):
        if self.real_name:
            covered_name = self.real_name[0] + "*" * (len(self.real_name) - 1)
            return covered_name
        else:
            return None

    def get_covered_id (self):
        if self.id_card:
            return self.id_card[:3] + "*" * (len(self.id_card) - 3 - 4) + self.id_card[-4:]
        else:
            return None

    def get_covered_tele (self):
        if self.tele:
            return self.tele[:3] + "*" * (len(self.tele) - 3 - 4) + self.tele[-4:]
        else:
            return None


# Operator 辅助函数
def oper_logo_path (instance, filename):
    return "{0}/Logo/{1}".format(instance.id, filename)


def oper_license_path (instance, filename):
    return "{0}/License/{1}".format(instance.id, filename)


def oper_certificate_path (instance, filename):
    return "{0}/Certificate/{1}".format(instance.id, filename)


class Operator(models.Model):
    oper_type_list = (("PRSTDO", "私人工作室"),
                      ("PRHOSP", "私立医院"),
                      ("PUHOSP", "公立医院"),
                      ("INDOCT", "独立医生"))

    name = models.CharField(max_length=50, verbose_name="名称", default="")
    tele = models.CharField(max_length=11, verbose_name="联系电话", blank=True, null=True,
                            validators=[TeleValidator])
    logo = models.ImageField(upload_to=oper_logo_path, verbose_name="图标", blank=True, null=True,
                             validators=[ImageExtensionValidator], help_text=image_helptxt)
    address = models.CharField(max_length=150, verbose_name="地址", help_text="- 至多150字符", blank=True, null=True)
    city = models.CharField(max_length=20, verbose_name="城市", blank=True, null=True)
    province = models.CharField(max_length=20, verbose_name="省份", blank=True, null=True)
    zip_code = models.CharField(max_length=6, verbose_name="邮编", blank=True, null=True)
    description = models.TextField(verbose_name="医院简介", blank=True, null=True)

    oper_type = models.TextField(max_length=6, choices=oper_type_list, verbose_name="类型")
    oper_license = models.ImageField(upload_to=oper_license_path, verbose_name="营业执照",
                                     validators=[ImageExtensionValidator],
                                     blank=True, null=True, help_text=image_helptxt)
    oper_certificate = models.ImageField(upload_to=oper_certificate_path, verbose_name="医疗许可证",
                                         validators=[ImageExtensionValidator],
                                         blank=True, null=True, help_text=image_helptxt)

    star = models.DecimalField(decimal_places=1, max_digits=2,
                               validators=(MaxValueValidator(5), MinValueValidator(0)), verbose_name="星级", default=0)
    effect = models.DecimalField(decimal_places=1, max_digits=2,
                                 validators=(MaxValueValidator(5), MinValueValidator(0)), verbose_name="效果", default=0)
    service = models.DecimalField(decimal_places=1, max_digits=2,
                                  validators=(MaxValueValidator(5), MinValueValidator(0)), verbose_name="服务",
                                  default=0)
    proficiency = models.DecimalField(decimal_places=1, max_digits=2,
                                      validators=(MaxValueValidator(5), MinValueValidator(0)),
                                      verbose_name="专业", default=0)

    verified = models.BooleanField(default=False, verbose_name="认证")
    pin = models.BooleanField(default=False, verbose_name="推荐")

    rebate_lv0 = models.IntegerField(verbose_name="普通用户返佣额度", default=0,
                                     validators=(MaxValueValidator(100), MinValueValidator(0)),
                                     help_text="请输入正整数，如返佣比例30%，则输入30即可")
    rebate_lv1 = models.IntegerField(verbose_name="一级用户返佣额度", default=0,
                                     validators=(MaxValueValidator(100), MinValueValidator(0)))
    rebate_lv2 = models.IntegerField(verbose_name="二级用户返佣额度", default=0,
                                     validators=(MaxValueValidator(100), MinValueValidator(0)))
    rebate_time = models.CharField(max_length=20, verbose_name="返佣时间", blank=True, null=True)

    def __str__ (self):
        return self.name

    def max_rebate (self):
        return max(self.rebate_lv0, self.rebate_lv1, self.rebate_lv2)


class Wiki_Category(models.Model):
    code = models.CharField(max_length=10, verbose_name="类目编码", primary_key=True, blank=True)
    name = models.CharField(max_length=30, verbose_name="类目名称")
    father = models.ForeignKey(to="Wiki_Category", on_delete=models.CASCADE, verbose_name="类目父类",
                               blank=True, null=True, limit_choices_to={"father__isnull": True})

    def __str__ (self):
        return self.name


class Wiki_Item(models.Model):
    code = models.CharField(max_length=10, verbose_name="项目编码", primary_key=True)
    category = models.ForeignKey(to="Wiki_Category", on_delete=models.CASCADE,
                                 verbose_name="类别", limit_choices_to={"father__isnull": False})
    name = models.CharField(max_length=30, verbose_name="项目名称")
    description = models.TextField(verbose_name="项目简介", blank=True, null=True)
    pros = models.TextField(verbose_name="项目优点", blank=True, null=True)
    cons = models.TextField(verbose_name="项目缺点", blank=True, null=True)
    method = models.TextField(verbose_name="治疗方法", blank=True, null=True)
    effect = models.TextField(verbose_name="治疗效果", blank=True, null=True)
    precautions = models.TextField(verbose_name="注意事项", blank=True, null=True)
    patient = models.TextField(verbose_name="适合人群", blank=True, null=True)
    attention = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(5)],
                                    verbose_name="关注度")
    secure = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(5)],
                                 verbose_name="安全度")

    duration = models.CharField(max_length=50, verbose_name="治疗时长", blank=True, null=True)
    last = models.CharField(max_length=50, verbose_name="效果持续", blank=True, null=True)
    recover = models.CharField(max_length=50, verbose_name="恢复时间", blank=True, null=True)
    anesthesia = models.CharField(max_length=50, verbose_name="麻醉方式", blank=True, null=True)
    period = models.CharField(max_length=50, verbose_name="治疗周期", blank=True, null=True)
    operator = models.CharField(max_length=50, verbose_name="操作人员资质", blank=True, null=True)
    opermethod = models.CharField(max_length=50, verbose_name="操作方式", blank=True, null=True)
    pain = models.CharField(max_length=50, verbose_name="疼痛感", blank=True, null=True)

    price = models.CharField(max_length=50, verbose_name="价格", blank=True, null=True)

    def __str__ (self):
        return self.name


class Appointment(models.Model):
    Status_code = (
        ("SUBMIT", "已提交申请"),
        ("ACCEPT", "已接受申请"),
        ("PRCESS", "申请处理中"),
        ("REJECT", "已拒绝申请"),
        ("SUCESS", "预约成功！"),
        ("FAILED", "预约失败！"),
        ("FINISH", "预约完成！")
    )

    name = models.CharField(max_length=10, verbose_name="顾客姓名")
    appoint_date = models.DateField(verbose_name="预约日期")
    appoint_time = models.TimeField(verbose_name="预约时间")
    project = models.CharField(max_length=20, verbose_name="项目名称")
    hospital = models.ForeignKey(to="Operator", on_delete=models.CASCADE, verbose_name="医院名称")

    accompany = models.CharField(max_length=10, verbose_name="陪同人员", null=True, blank=True)
    pre_project = models.CharField(max_length=20, verbose_name="铺垫项目", null=True, blank=True)
    consumption = models.CharField(max_length=20, verbose_name="消费预计", null=True, blank=True)
    customer_amount = models.CharField(max_length=20, verbose_name="顾客数量", null=True, blank=True)
    precautions = models.TextField(max_length=300, verbose_name="注意事项", null=True, blank=True)

    status = models.CharField(max_length=10, verbose_name="预约状态", choices=Status_code, default="SUBMIT")
    show = models.BooleanField(default=True, verbose_name="显示")

    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    create_user = models.ForeignKey(to="User_Profile", on_delete=models.CASCADE, verbose_name="创建者")


class Transaction(models.Model):
    transaction_type_list = ((1, "收入"),
                             (2, "提现"))

    id = models.UUIDField(primary_key=True, verbose_name="订单号", default=uuid.uuid4, editable=False)
    amount = models.DecimalField(verbose_name="交易额", max_digits=9, decimal_places=2)
    transaction_type = models.IntegerField(verbose_name="类型", choices=transaction_type_list)
    holder = models.ForeignKey(to="User_Profile", on_delete=models.CASCADE, verbose_name="账户持有者")
    appointment = models.ForeignKey(to="Appointment", on_delete=models.CASCADE, verbose_name="相关预约",
                                    blank=True, null=True)
    note = models.TextField(verbose_name="备注", blank=True, null=True)
    create_date = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")


# todo: 增加提现申请功能
class Withdrawal (models.Model):
    status_list = ((1, "已提交申请"),
                   (2, "审核处理中"),
                   (3, "已放款，请查收"),
                   (100, "交易完成"),
                   (101, "交易取消"),
                   (102, "审核失败"))

    payment_method = ((1, "银行转账"),
                      (2, "支付宝"),
                      (3, "微信"))

    create_date = models.DateField(auto_now_add=True, verbose_name="创建时间")
    update_date = models.DateTimeField(auto_now=True, verbose_name="最后更改时间")
    amount = models.IntegerField(verbose_name="提现金额",
                                 validators=[MinValueValidator(withdrawal_min,
                                                               message="提现金额低于下限{}元".format(withdrawal_min)),
                                             MaxValueValidator(withdrawal_max,
                                                               message="提现金额高于上限{}元".format(withdrawal_max))])

    method = models.IntegerField(choices=payment_method, verbose_name="支付方法")
    receive_account = models.CharField(max_length=200, verbose_name="账号")

    status = models.IntegerField(verbose_name="交易状态", choices=status_list, default=1)
    applicator = models.ForeignKey(verbose_name="申请人", on_delete=models.CASCADE, to="User_Profile")

    UniqueConstraint(fields=["create_date", "applicator"], name="每日提现约束")


class Blacklist(models.Model):
    name = models.CharField(
        verbose_name="医院\\项目\\医生名称",
        max_length=50
    )

    address = models.CharField(
        verbose_name="地址",
        max_length=150
    )

    tag = models.CharField(
        verbose_name="标签",
        max_length=150,
        help_text="请用逗号分隔标签"
    )

    def get_tag_as_string(self):
        return self.tag.replace(",", "  ").replace("，", "  ")


class BlacklistReport(models.Model):
    name = models.CharField(
        verbose_name="医美项目或医院，医生名称",
        max_length=150
    )

    query = models.TextField(
        verbose_name="查询问题",
        help_text="如：是否有客诉或者项目价格是否合规等问题"
    )

    tele = models.CharField(
        max_length=11,
        verbose_name="手机",
        validators=[TeleValidator],
        help_text="请留下您的手机号，客服人员将尽快联系您",
    )

    wechat = models.CharField(
        verbose_name="微信号",
        max_length=150,
        blank=True
    )

    status = models.BooleanField(
        verbose_name="状态",
        default=True
    )

    visitor = models.CharField(
        verbose_name="访问者微信OPEN_ID",
        max_length=128,
        blank=True,
        null=True
    )

    creator = models.IntegerField(
        verbose_name="创建者ID",
        blank=True,
        null=True
    )

    create_date = models.DateTimeField(
        verbose_name="创建时间",
        auto_now_add=True,
    )

    last_update = models.DateTimeField(
        verbose_name="最后更新",
        auto_now=True,
    )

    @property
    def is_open(self):
        return self.status is True

    @property
    def is_close(self):
        return self.status is False

    @property
    def avatar_url(self):
        if self.visitor is not None:
            return WechatVisitor.objects.get(openid=self.visitor).avatar_url
        else:
            return None

    @property
    def nickname(self):
        if self.visitor is not None:
            return WechatVisitor.objects.get(openid=self.visitor).nickname
        else:
            return None

    @property
    def get_creator(self):
        if self.creator is not None:
            return User_Profile.objects.get(id=self.creator).get_full_name()
        else:
            return None

    @property
    def query_short(self):
        if len(self.query) > 30:
            return self.query[:30] + "……"
        else:
            return self.query


class WechatVisitor(models.Model):
    openid = models.CharField(
        max_length=128,
        primary_key=True
    )

    avatar_url = models.CharField(
        max_length=500,
        verbose_name="头像"
    )

    nickname = models.CharField(
        max_length=50,
        verbose_name="用户昵称"
    )

    sex = models.IntegerField(
        choices=(
            (0, "未知"),
            (1, "男性"),
            (2, "女性"),
        ),
        verbose_name="性别"
    )
    
    city = models.CharField(
        max_length=50,
        verbose_name="所在城市"
    )

    province = models.CharField(
        max_length=50,
        verbose_name="所在省份"
    )

    country = models.CharField(
        max_length=15,
        verbose_name="所在国家"
    )

    def get_address(self):
        s = ""
        if self.country != "":
            s += self.country
        else:
            s += "??"

        if self.province != "":
            s += f"-{self.province}"
        else:
            s += "??"

        if self.city != "":
            s += f"-{self.city}"
        else:
            s += "??"

        if s == "??????":
            s = "??"
        return s
    

class blacklist_visit(models.Model):
    visitor = models.ForeignKey(
        to=WechatVisitor,
        on_delete=models.CASCADE
    )

    blacklist_creator = models.ForeignKey(
        to=User_Profile,
        on_delete=models.CASCADE
    )

    visit_time = models.DateTimeField(
        auto_now=True,
        verbose_name="上次浏览"
    )

    visit_total = models.IntegerField(
        default=1,
        verbose_name="浏览次数"
    )

    class Meta:
        unique_together = ("visitor", "blacklist_creator")
