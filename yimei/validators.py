from django.core.validators import FileExtensionValidator, RegexValidator
from yimei.panel_setting import *


ImageExtensionValidator = FileExtensionValidator(["jpeg", "jpg", "png"])
TeleValidator = RegexValidator(regex=r"1(3|4|5|6|7|8|9)\d{9}",
                               message=tell_errmsg_invalid,
                               code="TellInvalid")
IDValidator = RegexValidator(regex=r"[1-9]\d{5}(18|19|([23]\d))\d{2}((0[1-9])|(10|11|12))(([0-2]["
                                   r"1-9])|10|20|30|31)\d{3}[0-9Xx]",
                             message=id_invalid,
                             code="IDInvalid")
