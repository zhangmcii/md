# Nginx + acme.sh 证书自动续费故障排查与修复总结

## 一、问题现象

* HTTPS 证书已过期
* 预期使用 `acme.sh` 自动续费，但未生效
* 执行命令时报错：

  * `acme.sh: command not found`
  * `nginx.service is not active`
  * `Permission denied`
  * `Authentication is required`

---

## 二、根因总结

问题不是单点，而是多个环节同时失效：

1. `acme.sh` 主程序丢失（导致续费任务无法执行）
2. nginx 运行方式混乱（手动启动，不受 systemd 管理）
3. cron 存在，但 reload nginx 需要密码（自动续费失效）
4. 权限问题导致证书安装失败

---

## 三、完整修复步骤

---

### 1️⃣ 恢复 acme.sh

```bash
curl https://get.acme.sh | sh
source ~/.bashrc
```

验证：

```bash
acme.sh --list
```

---

### 2️⃣ 重新签发证书

```bash
acme.sh --issue -d 191718.com --nginx
```

---

### 3️⃣ 安装证书到 nginx 目录

```bash
sudo ~/.acme.sh/acme.sh --install-cert -d 191718.com \
--key-file       /etc/nginx/cert/key.pem \
--fullchain-file /etc/nginx/cert/fullchain.pem \
--reloadcmd     "systemctl reload nginx"
```

---

### 4️⃣ 修复 nginx “野生进程”问题

查看 nginx：

```bash
ps aux | grep nginx
```

杀掉旧进程：

```bash
sudo pkill nginx
```

用 systemd 启动：

```bash
sudo systemctl start nginx
sudo systemctl enable nginx
```

验证：

```bash
sudo systemctl status nginx
```

---

### 5️⃣ 修复权限问题

```bash
sudo chmod 644 /etc/nginx/cert/*
sudo rm -f /var/run/nginx.pid
```

---

### 6️⃣ 确认 nginx 配置正确

```bash
sudo nginx -t
```

---

### 7️⃣ 确认证书路径

```bash
nginx -T | grep ssl_certificate
```

应为：

```nginx
/etc/nginx/cert/fullchain.pem
/etc/nginx/cert/key.pem
```

---

### 8️⃣ 配置 cron 自动续费

检查：

```bash
crontab -l
```

应包含：

```bash
11 9 * * * "/home/ubuntu/.acme.sh"/acme.sh --cron --home "/home/ubuntu/.acme.sh" > /dev/null
```

---

### 9️⃣ 修复 sudo 权限（关键）

```bash
sudo visudo
```

添加：

```bash
ubuntu ALL=NOPASSWD: /bin/systemctl reload nginx
```

---

### 🔟 更新 reload 命令

```bash
sudo ~/.acme.sh/acme.sh --install-cert -d 191718.com \
--key-file       /etc/nginx/cert/key.pem \
--fullchain-file /etc/nginx/cert/fullchain.pem \
--reloadcmd     "sudo systemctl reload nginx"
```

---

## 四、验证自动续费是否正常

---

### 1️⃣ 测试 reload 是否免密码

```bash
sudo -n systemctl reload nginx
```

✔ 无输出 = 正常

---

### 2️⃣ 模拟续费

```bash
~/.acme.sh/acme.sh --renew -d 191718.com --force
```

确认：

* 无报错
* 执行 install-cert
* 执行 reload nginx（无密码提示）

---

### 3️⃣ 验证证书是否更新

```bash
openssl s_client -connect 191718.com:443 | openssl x509 -noout -dates
```

---

## 五、关键结论

* 证书有效期：90 天
* 自动续费触发时间：约提前 30 天
* cron 每天执行，但只在接近过期时才真正续费

---

## 六、最终状态判断标准

满足以下 4 条，即为“完全自动化”：

* ✔ cron 存在
* ✔ `acme.sh --list` 有 Renew 时间
* ✔ `sudo -n systemctl reload nginx` 无需密码
* ✔ `--renew --force` 全流程成功

---

## 七、经验总结

本次问题本质：

> 自动化链路中断（acme.sh + nginx + sudo + cron）

核心教训：

* 自动化 ≠ 配置完成
* 自动化 = **必须可验证**

---

## 八、一句话总结

> 证书续费不是“有没有任务”，而是**整条链路是否闭环（签发 → 安装 → reload）**
