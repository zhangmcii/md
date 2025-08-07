mac安装配置redis
参考：
1.安装HomeBrew
终端运行：   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

2.brew install redis
参考：https://redis.io/docs/latest/operate/oss_and_stack/install/install-redis/install-redis-on-mac-os/ （官网）

            https://www.cnblogs.com/shoshana-kong/p/17219474.html



1.如果你设置了 Redis 密码(1234)： 

127.0.0.1:6379> auth 1234

2.测试连通性

127.0.0.1:6379> ping
PONG

参考： https://www.howtomanageredis.com/How-To-Connect-to-a-Redis-Database.html



pycharm:
多行编辑： option+command
变为大写： command + shift + U
格式化：    option+command + L



查看文件换行符：  od -c filename
查看问价编码： file -I filename




1.设置mac环境变量
用户级别的自定义环境变量，则在文件 ~/.bash_profile 中进行设置
vim ~/.bash_profile
修改后，执行 Source ~/.bash_profile