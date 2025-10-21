## 设置ssh的共钥，本地可免密妇传输文件

## 安装(上传)nginx

## 开放公网访问端口，比如rank的前端,随想阁楼默认使用80端口，不用单独设置

## 阿里云的ssl证书重新指向到新服务器


## 安装nginx

## mysql容器怎么执行sql文件
1. 先将本地 SQL 文件复制到 MySQL 容器内
docker cp /home/ubuntu/user/blog_backend.sql mysql:/tmp/blog_backend.sql


2. 执行容器内的 SQL 文件
docker exec -it mysql mysql -uflasky -p1234 < /tmp/blog_backend.sql

或者 写进入容器docker exec -it mysql sh
再执行sql文件:  mysql -uflasky -p1234 < /tmp/blog_backend.sql

## 在/var/log/目录下创建loft目录



## 若非root用户登录，变更当前文件/文件夹的用户组以获取权限时
1.变更用户组
```
sudo chgrp -R ubuntu /var/log/loft
```
含义：loft文件夹以及自文件夹的用户组改为ubuntu用户
-R 代表递归修改文件夹内所有文件和子文件夹的组

2.变更了用户组后，赋予可写权限
```
sudo chmod -R g+w /var/log/loft
```


## 域名重新指向
1.修改阿里云的解析记录A，记录值为服务器ip
2.修改阿里云的DNS服务器地址为新的服务器的dns地址
服务器商搜索云解析
点击添加域名
3.服务器商的DNS添加A解析记录，记录值为服务器ip