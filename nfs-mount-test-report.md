# NFS 挂载测试报告

**测试时间**: 2026-03-19 20:45 CST  
**测试服务器**: 阿里云 VPS (超梦)  
**服务器 Tailscale IP**: 100.82.219.91  
**NAS 设备**: Synology DSM (yokeplay)  
**NAS Tailscale IP**: 100.65.98.22  

---

## 1. 网络连通性测试

### 1.1 基础连通性
- ✅ **Ping 测试**: NAS 可达 (延迟 ~23ms)
- ✅ **NFS 工具**: nfs-utils 已安装 (`/usr/sbin/mount.nfs`)
- ✅ **CIFS 工具**: cifs-utils 已安装 (`/usr/sbin/mount.cifs`)
- ✅ **挂载点**: `/mnt/nas` 已存在

### 1.2 NFS 服务探测
- ❌ **showmount -e**: RPC 超时 (无法列出可用共享)
- ❌ **rpcinfo -p**: 连接超时 (RPC 端口映射器不可达)

**分析**: RPC 超时可能表示:
1. NAS 上 NFS 服务未启用
2. NAS 防火墙阻止了 RPC 端口 (111, 2049)
3. NFS 配置中未授权此客户端 IP

---

## 2. NFS 挂载测试 (所有尝试均失败)

### 2.1 测试的共享路径

以下所有路径均返回 "access denied by server":

```
/                      # NFS 根目录
/openclaw              # OpenClaw 共享
/nas                   # NAS 共享
/shared                # 共享文件夹
/data                  # 数据目录
/backup                # 备份目录
/media                 # 媒体目录
/volume1               # Synology 卷
/volume1/openclaw      # OpenClaw (volume1)
/volume1/nas           # NAS (volume1)
/volume1/public        # 公共目录
/volume1/home          # 家目录
/volume1/homes         # 家目录 (复数)
/volume1/shared        # 共享 (volume1)
/volume1/OpenClaw      # OpenClaw (大写)
/volume1/openclaw_shared  # OpenClaw 共享 (完整)
/volume1/video         # 视频目录
/mnt/nas               # 挂载点路径
```

### 2.2 使用的挂载选项

尝试了以下组合:
- `-t nfs` (NFS v3)
- `-t nfs4` (NFS v4)
- `-o tcp` (TCP 传输)
- `-o vers=3,tcp` (强制 NFS v3)
- `-o vers=4,tcp` (强制 NFS v4)
- `-o soft,timeo=30` (软挂载，超时 30 秒)
- `-o tcp,soft,timeo=30` (组合选项)

**结果**: 所有尝试均失败，错误信息: `mount.nfs: access denied by server`

---

## 3. SMB/CIFS 挂载测试

### 3.1 Guest 访问测试
```bash
mount.cifs //100.65.98.22/openclaw /mnt/nas -o guest
```
**结果**: ❌ Permission denied (需要身份验证)

### 3.2 需要的信息
- 用户名：待提供
- 密码：待提供
- 共享名称：待确认

---

## 4. 问题诊断

### 4.1 可能的问题

1. **NAS 端 NFS 未正确配置**
   - NFS 服务可能未启用
   - 共享文件夹未开启 NFS 权限
   - 客户端 IP 未加入白名单

2. **网络/防火墙问题**
   - RPC 端口 (111) 被阻止
   - NFS 端口 (2049) 被阻止
   - Tailscale 路由配置问题

3. **共享路径不匹配**
   - 实际导出路径与我们尝试的路径不同
   - 需要使用特定的共享名称

### 4.2 需要在 Synology NAS 上进行的配置

请潘总在 Synology DSM 上确认以下配置:

#### 步骤 1: 启用 NFS 服务
```
控制面板 → 文件服务 → NFS → ✓ 启用 NFS 服务
```

#### 步骤 2: 配置共享文件夹的 NFS 权限
```
控制面板 → 共享文件夹 → 选择共享 → 编辑 → NFS 权限 → 新增

配置示例:
- 主机名或 IP: 100.82.219.91 (阿里云 Tailscale IP)
- 权限：读写 (Read/Write)
- 异步：✓ 启用
- 允许用户访问：✓ 启用
- 无权限限制：✓ 启用 (或配置具体用户)
```

#### 步骤 3: 确认共享路径
```
控制面板 → 共享文件夹 → 查看共享名称

可能的共享名称:
- openclaw
- openclaw_data
- video_production
- shared_workspace
- 或其他自定义名称
```

#### 步骤 4: 检查防火墙设置
```
控制面板 → 安全性 → 防火墙 → 编辑规则

确保允许:
- 端口 111 (TCP/UDP) - RPC
- 端口 2049 (TCP/UDP) - NFS
- 或允许来自 100.82.219.91 的所有流量
```

---

## 5. 需要的信息

请潘总提供以下信息以完成 NFS 挂载配置:

### 5.1 NFS 共享信息
```
共享名称：_________________
(在 Synology DSM 控制面板 → 共享文件夹中查看)

完整导出路径：_________________
(例如：/volume1/openclaw 或 /volume1/video_production)
```

### 5.2 或者使用 SMB 方式 (备选方案)

如果 NFS 配置复杂，可以使用 SMB/CIFS:

```
共享名称：_________________
用户名：_________________
密码：_________________
```

---

## 6. 配置完成后的挂载命令

### 6.1 NFS 挂载 (推荐)

```bash
# 手动挂载
mount -t nfs 100.65.98.22:/<共享路径> /mnt/nas

# 示例 (待确认路径):
mount -t nfs 100.65.98.22:/volume1/openclaw /mnt/nas

# 验证
df -h | grep /mnt/nas
```

### 6.2 SMB 挂载 (备选)

```bash
# 创建凭证文件
cat > /root/.smbcredentials <<EOF
username=<用户名>
password=<密码>
EOF
chmod 600 /root/.smbcredentials

# 手动挂载
mount.cifs //100.65.98.22/<共享名称> /mnt/nas \
    -o credentials=/root/.smbcredentials,vers=3.0,iocharset=utf8,file_mode=0777,dir_mode=0777

# 验证
df -h | grep /mnt/nas
```

---

## 7. 开机自动挂载配置

### 7.1 NFS 方式 (/etc/fstab)

```bash
# 备份 fstab
cp /etc/fstab /etc/fstab.bak

# 添加 NFS 挂载条目
echo "100.65.98.22:/<共享路径>  /mnt/nas  nfs  defaults,_netdev  0  0" >> /etc/fstab

# 测试配置
mount -a

# 验证
df -h | grep /mnt/nas
```

### 7.2 SMB 方式 (/etc/fstab)

```bash
# 备份 fstab
cp /etc/fstab /etc/fstab.bak

# 添加 SMB 挂载条目
echo "//100.65.98.22/<共享名称>  /mnt/nas  cifs  credentials=/root/.smbcredentials,vers=3.0,iocharset=utf8,file_mode=0777,dir_mode=0777,_netdev  0  0" >> /etc/fstab

# 测试配置
mount -a

# 验证
df -h | grep /mnt/nas
```

---

## 8. 共享目录结构

挂载成功后将创建以下目录结构:

```
/mnt/nas/openclaw/
├── workspace/      # OpenClaw 工作区同步
├── logs/           # 集中日志存储
│   ├── aliyun/     # 阿里云实例日志
│   └── macmini/    # Mac mini 实例日志
├── backups/        # 备份文件
├── config/         # 共享配置文件
└── media/          # 媒体资源
```

**注意**: 根据之前的检查，`/mnt/nas/openclaw/` 目录已存在，可能是之前测试创建的。

---

## 9. Mac mini 挂载指引

### 9.1 macOS SMB 挂载 (推荐)

```bash
# 创建挂载点
mkdir -p /Volumes/nas-openclaw

# 手动挂载
mount_smbfs //<用户名>:<密码>@100.65.98.22/<共享名称> /Volumes/nas-openclaw

# 或使用 Finder (最简单)
# 1. Finder → 前往 → 连接服务器 (Cmd+K)
# 2. 输入：smb://100.65.98.22/<共享名称>
# 3. 输入用户名和密码
# 4. 勾选"在钥匙串中记住密码"
```

### 9.2 macOS NFS 挂载

```bash
# 创建挂载点
mkdir -p /Volumes/nas-openclaw

# 手动挂载
mount_nfs 100.65.98.22:/<共享路径> /Volumes/nas-openclaw

# 开机自动挂载 (/etc/fstab)
# 注意：macOS 的 fstab 需要先创建
sudo mkdir -p /etc
echo "100.65.98.22:/<共享路径>  /Volumes/nas-openclaw  nfs  rw,bg,rsize=8192,wsize=8192  0  0" | sudo tee -a /etc/fstab
```

### 9.3 macOS 开机自动挂载 (推荐方式)

**方法 1: 使用自动挂载 (autofs)**
```bash
# 编辑 /etc/auto_master
echo "/- auto_nas" | sudo tee -a /etc/auto_master

# 创建 /etc/auto_nas
echo "/Volumes/nas-openclaw -fstype=smbfs,username=<用户名>,password=<密码> ://100.65.98.22/<共享名称>" | sudo tee /etc/auto_nas

# 重启自动挂载
sudo automount -vc
```

**方法 2: 使用登录脚本 (最简单)**
```bash
# 创建启动脚本
cat > ~/Library/LaunchScripts/com.nas.mount.plist <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.nas.mount</string>
    <key>ProgramArguments</key>
    <array>
        <string>/bin/sh</string>
        <string>-c</string>
        <string>mount_smbfs //<用户名>:<密码>@100.65.98.22/<共享名称> /Volumes/nas-openclaw</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>
EOF

# 加载启动项
launchctl load ~/Library/LaunchScripts/com.nas.mount.plist
```

---

## 10. 测试验证

挂载配置完成后，执行以下测试:

```bash
# 1. 验证挂载状态
df -h | grep /mnt/nas

# 2. 测试写入
echo "NFS test $(date)" > /mnt/nas/openclaw/test-write.txt

# 3. 测试读取
cat /mnt/nas/openclaw/test-write.txt

# 4. 测试权限
ls -la /mnt/nas/openclaw/

# 5. 创建目录结构
mkdir -p /mnt/nas/openclaw/{workspace,logs/{aliyun,macmini},backups,config,media}

# 6. 验证目录
tree /mnt/nas/openclaw/

# 7. 清理测试文件
rm /mnt/nas/openclaw/test-write.txt

# 8. 测试开机自动挂载
reboot
# 重启后检查
df -h | grep /mnt/nas
```

---

## 11. 故障排查

### 11.1 NFS 挂载失败

```bash
# 检查 NFS 服务状态
rpcinfo -p 100.65.98.22

# 检查共享导出
showmount -e 100.65.98.22

# 查看内核日志
dmesg | grep -i nfs

# 查看系统日志
journalctl -u nfs-client.target

# 测试不同 NFS 版本
mount -t nfs -o vers=3,tcp 100.65.98.22:/path /mnt/nas
mount -t nfs -o vers=4,tcp 100.65.98.22:/path /mnt/nas
```

### 11.2 SMB 挂载失败

```bash
# 检查凭证
cat /root/.smbcredentials

# 尝试不同 SMB 版本
mount.cifs //100.65.98.22/share /mnt/nas -o credentials=/root/.smbcredentials,vers=2.0
mount.cifs //100.65.98.22/share /mnt/nas -o credentials=/root/.smbcredentials,vers=3.0

# 查看内核日志
dmesg | grep -i cifs

# 查看系统日志
journalctl | grep -i cifs
```

### 11.3 权限问题

```bash
# 检查挂载选项
mount | grep /mnt/nas

# 重新挂载调整权限
mount -o remount,file_mode=0777,dir_mode=0777 /mnt/nas

# 检查文件权限
ls -la /mnt/nas/
```

---

## 12. 下一步操作

1. ⏳ **等待潘总提供 NFS 共享路径或 SMB 凭证**
2. ⏳ **确认 NAS 上 NFS 服务已启用并配置客户端白名单**
3. ⏳ **执行挂载命令并验证**
4. ⏳ **配置 /etc/fstab 开机自动挂载**
5. ⏳ **创建共享目录结构**
6. ⏳ **在 Mac mini 上配置类似挂载**

---

## 13. 联系信息

如有问题，请提供:
- Synology DSM 版本
- NFS 共享完整路径
- 或 SMB 共享名称和凭证
- 任何错误信息截图

---

*报告生成时间：2026-03-19 20:45 CST*
