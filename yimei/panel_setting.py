####################################################################################################
# 平台设置                                                                                          #
####################################################################################################
platform_name = "圣博丽雅"        # 平台名称
platform_logo = "/images/bootstrap-solid.svg"
user_constrain = 0          # 对用户平台进行截流， 还有其他需要可以告诉我
code_length = 8             # 邀请码长度， 小于256
item_per_page = 10

####################################################################################################
# 平台设置                                                                                          #
####################################################################################################
withdrawal_min = 100            # 最小提现金额
withdrawal_max = 10000000       # 最大提现金额

####################################################################################################
# 信息分类                                                                                          #
####################################################################################################
VIP_level = ((0, "普通用户"),
             (1, "VIP I"),
             (2, "VIP II"))

####################################################################################################
# 文字信息                                                                                          #
####################################################################################################
usenm_helptxt = "用户名需:\n- 仅包含大小写英文字母与数字\n- 包含至少5个字符"
usrnm_errmsg_require = "该位置不能为空"
usrnm_errmsg_max_length = "用户名长度不得超过150个字符"
usrnm_errmsg_min_length = "用户名长度不得少于5个字符"
usrnm_errmsg_NOT_exist = "用户名不存在"
usrnm_errmsg_invalid = "用户名格式错误（·至少5个字符 ·仅包含英文大小写与数字）"
usrnm_errmsg_already_exist = """用户已存在，请<a href='{% url "login" %}'>登录</a>"""
unpw_errmsg_mismatch = "用户名密码不匹配"

paswd_helptxt = "密码需:\n- 包含至少8个字符\n- 包含至少1个大写英文字母，1个小写英文字母，一个数字\n- 请勿使用常见密码组合"
paswd_errmsg_require = "该位置不能为空"
paswd_errmsg_length = "超过字数上限"
paswd_errmsg_NOT_match = "两次输入密码不匹配"

confirm_helptxt = "请再次输入密码"

id_helptext = "请填写身份证号码"
id_invalid = "请重新确认您身份证号码的格式"

tell_errmsg_exist = """手机号已被注册，请前往<a href='{% url "login" %}'>登录</a>"""
tell_errmsg_invalid = "手机号码格式不正确"
tell_errmsg_require = "该位置不能为空"

invi_errmsg_NOT_exist = "未找到用户，请查看后重试"
invi_errmsg_require = "请填写邀请码"

image_helptxt = "仅接受以下格式图片: *.png, *.jpg, *.jpeg"
