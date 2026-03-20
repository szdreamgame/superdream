# NFS 挂载配置 - 待潘总确认

## 📋 快速确认清单

请潘总确认以下信息以完成 NFS 挂载:

### 选项 A: 使用 NFS (推荐)

**需要在 Synology NAS 上配置:**

1. ✅ 启用 NFS 服务
   - 路径：控制面板 → 文件服务 → NFS → 启用

2. ✅ 配置共享文件夹的 NFS 权限
   - 路径：控制面板 → 共享文件夹 → 选择共享 → 编辑 → NFS 权限
   - 添加客户端：`100.82.219.91` (阿里云 VPS 的 Tailscale IP)
   - 权限：读写 (Read/Write)

3. ✅ 确认共享路径名称
   - 请提供完整的 NFS 导出路径，例如：
     - `/volume1/openclaw`
     - `/volume1/video_production`
     - `/volume1/shared_workspace`
     - 或其他

**配置完成后执行的命令:**
```bash
# 挂载 NFS
mount -t nfs 100.65.98.22:/<请提供路径> /mnt/nas

# 验证
df -h | grep /mnt/nas

# 配置开机自动挂载
echo "100.65.98.22:/<请提供路径>  /mnt/nas  nfs  defaults,_netdev  0  0" >> /etc/fstab
mount -a
```

---

### 选项 B: 使用 SMB/CIFS (备选)

**需要提供:**
- 共享名称：`_____________`
- 用户名：`_____________`
- 密码：`_____________`

**配置完成后执行的命令:**
```bash
# 创建凭证文件
cat > /root/.smbcredentials <<EOF
username=<用户名>
password=<密码>
EOF
chmod 600 /root/.smbcredentials

# 挂载 SMB
mount.cifs //100.65.98.22/<共享名称> /mnt/nas \
    -o credentials=/root/.smbcredentials,vers=3.0,iocharset=utf8,file_mode=0777,dir_mode=0777

# 配置开机自动挂载
echo "//100.65.98.22/<共享名称>  /mnt/nas  cifs  credentials=/root/.smbcredentials,vers=3.0,iocharset=utf8,file_mode=0777,dir_mode=0777,_netdev  0  0" >> /etc/fstab
mount -a
```

---

## 🖥️ Mac mini 挂载指引

### macOS SMB 挂载 (推荐)

```bash
# 手动挂载
mkdir -p /Volumes/nas-openclaw
mount_smbfs //<用户名>:<密码>@100.65.98.22/<共享名称> /Volumes/nas-openclaw

# 或使用 Finder (最简单)
# Cmd+K → smb://100.65.98.22/<共享名称> → 输入凭证 → 记住密码
```

### macOS NFS 挂载

```bash
# 手动挂载
mkdir -p /Volumes/nas-openclaw
mount_nfs 100.65.98.22:/<NFS 路径> /Volumes/nas-openclaw
```

---

## 📁 已创建的目录结构

本地已准备好目录结构 (在 `/mnt/nas/openclaw/`):

```
/mnt/nas/openclaw/
├── workspace/      # 工作区同步
├── logs/
│   ├── aliyun/     # 阿里云日志
│   └── macmini/    # Mac mini 日志
├── backups/        # 备份
├── config/         # 配置
└── media/          # 媒体
```

---

## 📞 需要的信息

**请提供以下任一:**

### NFS 方式:
```
NFS 共享路径：/volume1/_____________
```

### SMB 方式:
```
共享名称：_____________
用户名：_____________
密码：_____________
```

---

## ✅ 验证步骤

配置完成后将执行:

1. 挂载测试
2. 读写测试
3. 配置开机自动挂载
4. 验证重启后自动挂载
5. 提供 Mac mini 详细挂载指引

---

*等待潘总提供配置信息...*
