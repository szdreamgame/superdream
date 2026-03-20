# Mac mini 挂载 NAS 完整指引

## 📋 背景信息

- **NAS 主机名**: yokeplay
- **NAS IP 地址**: 100.65.98.22
- **共享路径**: //yokeplay/yokeplay 或 //100.65.98.22/yokeplay
- **用户名**: openclawAI
- **密码**: xm654321.
- **域**: YOKEGAME
- **协议**: SMB 2.1
- **网络环境**: Mac mini 与 NAS 在同一局域网

---

## 方法一：命令行手动挂载

### 步骤 1：创建挂载点

```bash
sudo mkdir -p /mnt/nas
```

### 步骤 2：执行挂载命令

```bash
sudo mount -t cifs //100.65.98.22/yokeplay /mnt/nas \
  -o username=openclawAI,password=xm654321.,domain=YOKEGAME,vers=2.1
```

### 步骤 3：验证挂载

```bash
# 检查挂载状态
df -h | grep nas

# 或查看已挂载的所有文件系统
mount | grep nas
```

### 步骤 4：测试读写权限

```bash
# 测试读取
ls -la /mnt/nas

# 测试写入（创建测试文件）
touch /mnt/nas/test_file.txt

# 清理测试文件
rm /mnt/nas/test_file.txt
```

### 步骤 5：卸载 NAS（如需要）

```bash
sudo umount /mnt/nas
```

---

## 方法二：Finder 图形界面挂载

### 步骤 1：打开 Finder

点击 Dock 栏的 Finder 图标，或点击桌面空白处。

### 步骤 2：打开连接服务器对话框

- 快捷键：`Cmd + K`
- 或菜单栏：前往 → 连接服务器

### 步骤 3：输入服务器地址

在服务器地址栏输入以下任一地址：

```
smb://yokeplay/yokeplay
```

或

```
smb://100.65.98.22/yokeplay
```

### 步骤 4：点击"连接"

### 步骤 5：输入凭据

- **名称**: openclawAI
- **密码**: xm654321.
- **域/工作组**: YOKEGAME（如需要）

### 步骤 6：选择共享文件夹

选择 `yokeplay` 共享文件夹，点击"好"。

### 步骤 7：访问挂载的 NAS

- NAS 将出现在 Finder 侧边栏的"网络"或"位置"下
- 也可在桌面看到 NAS 图标（如设置了显示）

---

## 方法三：开机自动挂载配置

### 方案 A：使用 /etc/fstab（推荐）

#### 步骤 1：获取 NAS 的 UUID（可选但推荐）

```bash
# 先手动挂载一次
sudo mount -t cifs //100.65.98.22/yokeplay /mnt/nas \
  -o username=openclawAI,password=xm654321.,domain=YOKEGAME,vers=2.1

# 获取 UUID
sudo blkid
```

#### 步骤 2：创建 /etc/fstab 文件

```bash
sudo mkdir -p /etc
sudo nano /etc/fstab
```

#### 步骤 3：添加挂载配置

在文件中添加以下内容：

```
//100.65.98.22/yokeplay  /mnt/nas  cifs  username=openclawAI,password=xm654321.,domain=YOKEGAME,vers=2.1,nosuid,noowners  0  0
```

或使用主机名：

```
//yokeplay/yokeplay  /mnt/nas  cifs  username=openclawAI,password=xm654321.,domain=YOKEGAME,vers=2.1,nosuid,noowners  0  0
```

#### 步骤 4：保存并退出

- `Ctrl + O` 保存
- `Enter` 确认文件名
- `Ctrl + X` 退出

#### 步骤 5：设置 fstab 权限

```bash
sudo chmod 644 /etc/fstab
```

#### 步骤 6：测试 fstab 配置

```bash
# 先卸载
sudo umount /mnt/nas

# 测试挂载所有 fstab 条目
sudo mount -a

# 检查是否成功
df -h | grep nas
```

### 方案 B：使用登录项（图形界面）

#### 步骤 1：通过 Finder 连接 NAS

按照"方法二"的步骤连接 NAS。

#### 步骤 2：将 NAS 添加到登录项

1. 打开 **系统设置**（System Settings）
2. 进入 **通用** → **登录项**（General → Login Items）
3. 在"登录时打开"列表中，点击 `+` 号
4. 在 Finder 中选择已挂载的 NAS
5. 点击"打开"

#### 步骤 3：保存凭据到钥匙串

1. 连接 NAS 时，勾选"在钥匙串中记住密码"
2. 这样下次连接无需重新输入密码

---

## 🔍 常见问题排查

### 问题 1：挂载失败 - 权限被拒绝

**解决方案**：
```bash
# 检查用户名密码是否正确
# 确认域名称正确
# 尝试使用 IP 地址而非主机名
sudo mount -t cifs //100.65.98.22/yokeplay /mnt/nas \
  -o username=openclawAI,password=xm654321.,domain=YOKEGAME,vers=2.1
```

### 问题 2：找不到主机

**解决方案**：
```bash
# 检查网络连接
ping yokeplay
ping 100.65.98.22

# 检查是否在同一个局域网
ifconfig
```

### 问题 3：协议版本不匹配

**解决方案**：
```bash
# 尝试不同的 SMB 版本
sudo mount -t cifs //100.65.98.22/yokeplay /mnt/nas \
  -o username=openclawAI,password=xm654321.,domain=YOKEGAME,vers=2.0

# 或
sudo mount -t cifs //100.65.98.22/yokeplay /mnt/nas \
  -o username=openclawAI,password=xm654321.,domain=YOKEGAME,vers=3.0
```

### 问题 4：开机挂载失败

**解决方案**：
```bash
# 检查 fstab 语法
sudo mount -a

# 查看系统日志
log show --predicate 'eventMessage contains "mount"' --last 1h

# 确保网络已连接后再挂载（添加网络依赖）
```

### 问题 5：中文文件名乱码

**解决方案**：
```bash
# 添加 iocharset 参数
sudo mount -t cifs //100.65.98.22/yokeplay /mnt/nas \
  -o username=openclawAI,password=xm654321.,domain=YOKEGAME,vers=2.1,iocharset=utf8
```

---

## 📝 快速参考卡片

### 常用命令速查

```bash
# 创建挂载点
sudo mkdir -p /mnt/nas

# 手动挂载
sudo mount -t cifs //100.65.98.22/yokeplay /mnt/nas -o username=openclawAI,password=xm654321.,domain=YOKEGAME,vers=2.1

# 查看挂载状态
df -h | grep nas

# 卸载
sudo umount /mnt/nas

# 测试 fstab 配置
sudo mount -a
```

### Finder 快捷键

- `Cmd + K`：连接服务器
- `Cmd + Shift + G`：前往文件夹

---

## ⚠️ 安全提示

1. **密码安全**: `/etc/fstab` 中的密码是明文存储的，确保文件权限为 644
2. **网络隔离**: 确保 NAS 和 Mac mini 在安全的局域网内
3. **定期更新**: 定期更改 NAS 密码
4. **备份配置**: 备份 `/etc/fstab` 文件以防丢失

---

## 📞 需要帮助？

如遇到问题，请提供以下信息：

1. 错误消息的完整截图
2. 执行的命令
3. `df -h` 的输出
4. `ping yokeplay` 的结果

---

**文档版本**: 1.0  
**创建日期**: 2026-03-19  
**适用系统**: macOS (所有版本)
