
# 自动续费免费的ssl证书
Let’s Encrypt（完全免费，自动续期）

这是业界最主流的免费 SSL 解决方案：
- 完全免费
- 受所有主流浏览器信任
- 支持自动续期
- 适合生产环境使用
- 使用 ACME 协议自动生成证书


由于我是以普通用户登录linux上，在后续步骤中因为缺少权限导致无法安装，所以一开始先su到root，然后再安装acme.sh。
```shell
sudo su
```

## 安装 acme.sh
```shell
# my@example.com替换为自己的邮箱地址
curl https://get.acme.sh | sh -s email=my@example.com
```

或者
```shell
# my@example.com替换为自己的邮箱地址
wget -O -  https://get.acme.sh | sh -s email=my@example.com
```


## 使用命令前,切换为bash
```shell
bash
```

## 设置证书类型为letsencrypt
```shell
acme.sh --set-default-ca --server letsencrypt
```


## 直接签发：
```shell
# /usr/share/nginx/html/ 替换为自己项目的静态根目录
acme.sh --issue -d 191718.com  --webroot  /usr/share/nginx/html/  --ecc --server letsencrypt
```

## 检查证书存在：
```shell
ls /root/.acme.sh/191718.com*
```
输出：
```
191718.com.cer  191718.com.conf  191718.com.csr  191718.com.csr.conf  191718.com.key  backup  ca.cer  fullchain.cer
```
结果中有*.cer 和*.key， 说明是成功签发了。这两个文件在后续的安装步骤中需要。如果缺少*.cer，说明前面未签发成功，重新执行acme.sh --issue ...

## 安装证书
```shell
acme.sh  --install-cert -d 191718.com --key-file  /etc/nginx/cert/key.pem --fullchain-file  /etc/nginx/cert/fullchain.pem --reloadcmd “service nginx reload”
```

## nginx 配置 HTTPS

```
server {
    listen 443 ssl;
    server_name example.com;

    # 换成自己存放证书的目录
    ssl_certificate     /etc/nginx/ssl/example.com/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/example.com/key.pem;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

```

## 查看已安装证书信息
```shell
acme.sh --info -d 191718.com
```


## 自动续期是默认开启的（不用你操心）
acme.sh 安装时已经帮你加了 cron：
```shell
crontab -l
```

你会类似看到：
```shell
0 0 * * * "/root/.acme.sh"/acme.sh --cron --home "/root/.acme.sh"
```
含义：
- 每天跑一次
- 证书快过期才会自动续
- 续完自动 reload nginx

