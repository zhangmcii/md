# 网站 SSL 证书总过期？手把手带你“白嫖”全自动续期方案！

做网站最烦的是什么？不是写代码，而是正写着 Bug 呢，突然发现网站打不开了，浏览器提示“您的连接不是私有连接”。一看，得，SSL 证书又过期了。

市面上很多免费证书只有 90 天有效期，手动去云平台申请、下载、上传，简直是浪费生命。今天分享一套业界公认的“黄金方案”：**Let's Encrypt + acme.sh**。配置好后，这辈子你都不用再管证书的事儿！

### 为什么选择这个方案？

* **全自动**：申请、安装、续期全流程自动化，一次配置，终身受益。
* **零成本**：证书完全免费，受所有主流浏览器信任。
* **轻量化**：`acme.sh` 只是一个 Shell 脚本，不依赖 Python 或大体量的客户端。

---

## 🛠️ 前置准备

在开始之前，请确保：

1. 一台 Linux 服务器（Ubuntu、CentOS、Debian 都行）。

2. 你的域名（已经解析到这台服务器）。

3. 已经装好了 Nginx。

---

## 第一步：获取权限与安装 acme.sh

由于安装和证书管理涉及系统路径，我们建议直接切换到 **root** 用户操作，避免频繁的权限报错。

```shell
# 切换到 root 用户
sudo su -

# 安装 acme.sh，记得把 my@example.com 换成你自己的真实邮箱
# 邮箱用于接收证书过期提醒（虽然我们会自动续期，但双重保险更好）
curl https://get.acme.sh | sh -s email=my@example.com

```

**关键一步：** 安装完成后，为了让 `acme.sh` 命令立即生效，请重新加载配置文件：

```shell
source ~/.bashrc

```

---

## 第二步：设置默认证书签发机构

`acme.sh` 默认可能使用 ZeroSSL，但为了稳定性，我们手动将其切回 **Let's Encrypt**。

```shell
acme.sh --set-default-ca --server letsencrypt

```

---

## 第三步：签发证书（Webroot 模式）

这是最推荐小白使用的方法：**Webroot 模式**。它不需要停止 Nginx，原理是在你的网站根目录下放一个临时验证文件。

> **注意：** 请将 `example.com` 换成你的域名，将 `/var/www/html` 换成你 Nginx 配置中的真实静态资源根目录。

```shell
acme.sh --issue \
  -d example.com \
  -d www.example.com \
  --webroot /var/www/html/ \
  --ecc

```

* `-d`: 绑定域名（可以同时绑定多个）。
* `--ecc`: 生成更安全、性能更好的极小证书（主流趋势）。

**验证：** 执行 `ls ~/.acme.sh/example.com_ecc/`，如果看到 `.cer` 和 `.key` 文件，说明签发成功！

---

## 第四步：将证书“安装”到 Nginx 目录

**千万不要**直接在 Nginx 配置里引用 `~/.acme.sh/` 目录下的原文件，因为内部结构可能会变。正确做法是使用 `--install-cert` 命令将其拷贝到指定目录。

首先创建存放证书的文件夹：

```shell
mkdir -p /etc/nginx/ssl/example.com/

```

然后执行安装命令：

```shell
acme.sh --install-cert -d example.com --ecc \
--key-file       /etc/nginx/ssl/example.com/key.pem  \
--fullchain-file /etc/nginx/ssl/example.com/fullchain.pem \
--reloadcmd     "systemctl reload nginx"

```

* `--reloadcmd`: 非常关键！这告诉 acme.sh 在证书更新后，自动重启 Nginx 让新证书生效。

---

## 第五步：修改 Nginx 配置开启 HTTPS

现在证书已经就位，我们需要修改 Nginx 配置文件（通常在 `/etc/nginx/conf.d/` 或 `nginx.conf`）来启用 443 端口。

```nginx
server {
    listen 443 ssl;
    server_name example.com www.example.com;

    # 证书路径（与第四步中的路径保持一致）
    ssl_certificate     /etc/nginx/ssl/example.com/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/example.com/key.pem;

    # 安全优化配置
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;
    ssl_ciphers HIGH:!aNULL:!MD5;

    location / {
        # 这里替换成你的业务逻辑，如 proxy_pass 或 root
        root /var/www/html;
        index index.html;
    }
}

# 可选：将 80 端口自动跳转到 443
server {
    listen 80;
    server_name example.com www.example.com;
    return 301 https://$host$request_uri;
}

```

修改完后，检查并重启 Nginx：

```shell
nginx -t && systemctl restart nginx

```

---

## 第六步：一劳永逸——关于自动续期

**你不需要做任何额外操作！**

在安装 `acme.sh` 时，它已经自动在系统的 `crontab` 中添加了定时任务。你可以输入以下命令查看：

```shell
crontab -l

```

你会看到类似的一行：
`0 0 * * * "/root/.acme.sh"/acme.sh --cron --home "/root/.acme.sh" > /dev/null`

**它的逻辑是：**

1. 每天凌晨检查证书是否快到期（通常是 60 天后）。
2. 如果快到期了，自动联网重新签发。
3. 签发后，自动执行我们在第四步配置的 `--reloadcmd`，刷新 Nginx 证书。

### 🔍 常用运维命令

* **查看证书信息：** `acme.sh --info -d example.com --ecc`
* **强制手动续期：** `acme.sh --renew -d example.com --force --ecc`
* **查看 acme.sh 版本：** `acme.sh -v`

---

## 💡 小贴士

1. **防火墙配置**：确保你的服务器防火墙允许 **80** 和 **443** 端口入站。
2. **多域名签发**：如果你有多个域名，重复上述步骤即可。`acme.sh` 会非常聪明地管理每一份证书的续期时间。

现在，恭喜！你的网站现在已经拥有了永久的“安全绿锁”。