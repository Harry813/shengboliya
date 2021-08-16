[TOC]



# 参数详解

## 平台设置

### 平台名称 - `platform_name`

您可以通过该参数对平台名称进行修改， 默认为`""`

>   注：请确保其类型为字符串，即用引号将其包裹

------

### 平台图标 - `platform_logo`

您可以通过该参数对平台图标进行修改，其格式为字符串。请将图片文件放在`static`文件夹下以确保其能被正常调用。默认为`""`

>   注：请确保其类型为字符串，即用引号将其包裹

## 用户相关

### 用户截流 - `user_constrain`

您可以通过修改该数值对用户所浏览的平台进行限制，目前共有一下6个种类：

| 数值 |       含义        |
| :--: | :---------------: |
| `0`  | 不做限制 （默认） |
| `1`  |     仅限电脑      |
| `2`  |     仅限平板      |
| `3`  |     仅限手机      |
| `4`  |     仅限微信      |
| `5`  |   仅限手机微信    |

>   注：如需其他限制种类可以和我联系

------

### 用户邀请码长度 - `code_length` ![server-Harry](https://img.shields.io/badge/Warning-migration_required-red)

您可以通过

------

### Appendix

```shell
uwsgi --ini uwsgi.ini 				# 启动 uwsgi
uwsgi --stop uwsgi.pid				# 关闭 uwsgi
uwsgi --reload uwsgi.pid			# 重启 uwsgi


sudo /etc/init.d/nginx start		# 启动 nginx
sudo /etc/init.d/nginx stop			# 关闭 nginx
sudo /etc/init.d/nginx restart		# 重启 nginx


lsof -i:<port>  # 查看端口号
ps aux|grep uwsgi  # 找到所有和uwsgi有关程序
killall -s INT /usr/local/bin/uwsgi

```

