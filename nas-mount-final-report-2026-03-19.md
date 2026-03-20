# NAS 挂载最终报告 - 路径修正

**执行时间**: 2026-03-19 21:24 CST  
**执行者**: 承道 (OpenClaw Subagent)  
**服务器**: 阿里云 VPS (100.82.219.91)  
**NAS 设备**: Synology DSM (yokeplay / 100.65.98.22)

---

## 1. 背景 - 路径理解修正

潘总指出之前的路径理解错误：

**Windows SMB 路径**: `\\yokeplay\游可玩\openclawAIteam`
- 主机：yokeplay
- 顶级共享：**游可玩**
- 子目录：openclawAIteam

**正确的路径结构**:
```
NAS (yokeplay / 100.65.98.22)
└── 游可玩 (共享文件夹)
    └── openclawAIteam (子目录)
```

---

## 2. 测试结果

### 2.1 NFS 挂载测试

| 尝试路径 | 结果 | 错误信息 |
|----------|------|----------|
| `/volume1/游可玩` | ❌ | access denied |
| `/游可玩` | ❌ | access denied |
| `/volume1/openclawAIteam` | ❌ | access denied |
| `/openclawAIteam` | ❌ | access denied |
| `/volume1` | ❌ | access denied |
| `/` | ❌ | access denied |

**NFS 端口测试**: ✅ 端口 2049 开放  
**根本原因**: NAS 端 NFS 权限未配置客户端 IP 白名单

### 2.2 SMB/CIFS 挂载测试

| 共享名 | 结果 | 错误信息 |
|--------|------|----------|
| `游可玩` | ❌ | Permission denied (13) |
| `openclawAIteam` | ❌ | Permission denied (13) |
| `shared` | ❌ | Permission denied (13) |

**凭证文件**: `/root/.smbcredentials` 存在  
**凭证内容**: username=openclawAI, password=xm654321.  
**根本原因**: 凭证可能过期/不正确，或共享名不匹配

---

## 3. 问题诊断

### 3.1 NFS 问题

**现象**: 所有 NFS 挂载尝试返回 "access denied by server"

**原因**: Synology NAS 的 NFS 服务需要配置客户端 IP 白名单

**需要在 NAS 端完成的配置**:

1. 登录 Synology DSM (https://100.65.98.22:5001)

2. 启用 NFS 服务:
   ```
   控制面板 → 文件服务 → NFS → ✓ 启用 NFS 服务
   ```

3. 配置共享文件夹 NFS 权限:
   ```
   控制面板 → 共享文件夹 → "游可玩" → 编辑 → NFS 权限 → 新增
   
   配置:
   - 主机名或 IP: 100.82.219.91 (阿里云 VPS Tailscale IP)
   - 权限：读写 (Read/Write)
   - 异步：✓ 启用
   - 允许用户访问：✓ 启用
   ```

4. 确认共享路径:
   ```
   控制面板 → 共享文件夹 → 查看"游可玩"的路径
   通常是：/volume1/游可玩
   ```

### 3.2 SMB 问题

**现象**: 所有 SMB 挂载尝试返回 "Permission denied (13)"

**可能原因**:
1. 凭证文件中的用户名/密码不正确或已过期
2. 共享名"游可玩"在 SMB 协议中需要使用英文或特定格式
3. SMB 服务需要重新配置权限

**需要确认的信息**:
- SMB 共享的准确名称（可能不是中文名）
- 正确的用户名和密码
- 用户 openclawAI 是否有权限访问"游可玩"共享

---

## 4. 正确的挂载命令 (待 NAS 配置完成后执行)

### 4.1 NFS 方式 (推荐)

```bash
# 1. 确保挂载点存在
mkdir -p /mnt/nas

# 2. 挂载 NFS (使用正确的路径)
mount -t nfs 100.65.98.22:/volume1/游可玩 /mnt/nas

# 3. 验证挂载
df -h | grep /mnt/nas

# 4. 访问子目录
ls -la /mnt/nas/openclawAIteam/

# 5. 创建目录结构
mkdir -p /mnt/nas/openclawAIteam/openclaw/{workspace,logs/{aliyun,macmini},backups,config,media}

# 6. 测试读写
echo "test $(date)" > /mnt/nas/openclawAIteam/test.txt
cat /mnt/nas/openclawAIteam/test.txt
rm /mnt/nas/openclawAIteam/test.txt
```

### 4.2 配置开机自动挂载 (NFS)

```bash
# 1. 备份 fstab
cp /etc/fstab /etc/fstab.bak

# 2. 添加 NFS 挂载条目
echo "100.65.98.22:/volume1/游可玩  /mnt/nas  nfs  defaults,_netdev  0  0" >> /etc/fstab

# 3. 测试配置
mount -a --dry-run

# 4. 如无错误，执行挂载
mount -a

# 5. 验证
df -h | grep /mnt/nas

# 6. 重启验证
reboot
# 重启后检查
df -h | grep /mnt/nas
```

### 4.3 SMB 方式 (备选)

```bash
# 1. 更新凭证文件 (如需要)
cat > /root/.smbcredentials <<EOF
username=<正确的用户名>
password=<正确的密码>
EOF
chmod 600 /root/.smbcredentials

# 2. 挂载 SMB
/usr/sbin/mount.cifs //100.65.98.22/游可玩 /mnt/nas \
    -o credentials=/root/.smbcredentials,vers=3.0,iocharset=utf8,file_mode=0777,dir_mode=0777

# 3. 验证
df -h | grep /mnt/nas

# 4. 访问子目录
ls -la /mnt/nas/openclawAIteam/
```

### 4.4 配置开机自动挂载 (SMB)

```bash
# 1. 备份 fstab
cp /etc/fstab /etc/fstab.bak

# 2. 添加 SMB 挂载条目
echo "//100.65.98.22/游可玩  /mnt/nas  cifs  credentials=/root/.smbcredentials,vers=3.0,iocharset=utf8,file_mode=0777,dir_mode=0777,_netdev  0  0" >> /etc/fstab

# 3. 测试配置
mount -a --dry-run

# 4. 如无错误，执行挂载
mount -a

# 5. 验证
df -h | grep /mnt/nas
```

---

## 5. 目录结构

挂载成功后，目录结构应为:

```
/mnt/nas/                    # 挂载点 (挂载"游可玩"共享)
└── openclawAIteam/          # 子目录
    ├── workspace/           # OpenClaw 工作区同步
    ├── logs/                # 集中日志存储
    │   ├── aliyun/          # 阿里云实例日志
    │   └── macmini/         # Mac mini 实例日志
    ├── backups/             # 备份文件
    ├── config/              # 共享配置文件
    └── media/               # 媒体资源
```

**注意**: 
- NFS 挂载的是共享根目录"游可玩"
- openclawAIteam 是子目录，不是独立共享
- 访问路径是 `/mnt/nas/openclawAIteam/`

---

## 6. Mac mini 挂载指引

**Mac mini Tailscale IP**: 100.102.241.1

### 6.1 macOS NFS 手动挂载

```bash
# 1. 创建挂载点
mkdir -p /Volumes/nas-openclaw

# 2. NFS 挂载
mount_nfs 100.65.98.22:/volume1/游可玩 /Volumes/nas-openclaw

# 3. 验证
df -h | grep nas-openclaw

# 4. 访问子目录
ls -la /Volumes/nas-openclaw/openclawAIteam/
```

### 6.2 macOS Finder 挂载 (最简单)

**NFS 方式**:
1. 打开 Finder
2. 按 `Cmd + K` 或选择"前往" → "连接服务器"
3. 输入：`nfs://100.65.98.22/volume1/游可玩`
4. 点击"连接"
5. 访问 openclawAIteam 子目录

**SMB 方式**:
1. 打开 Finder
2. 按 `Cmd + K`
3. 输入：`smb://100.65.98.22/游可玩`
4. 输入用户名和密码
5. 勾选"在钥匙串中记住密码"
6. 访问 openclawAIteam 子目录

### 6.3 macOS 开机自动挂载 (NFS)

```bash
# 1. 创建 /etc/fstab (如不存在)
sudo mkdir -p /etc

# 2. 添加 NFS 挂载条目
echo "100.65.98.22:/volume1/游可玩  /Volumes/nas-openclaw  nfs  rw,bg,rsize=8192,wsize=8192  0  0" | sudo tee -a /etc/fstab

# 3. 创建挂载点
sudo mkdir -p /Volumes/nas-openclaw

# 4. 测试挂载
sudo mount -a

# 5. 验证
df -h | grep nas-openclaw
```

### 6.4 macOS 开机自动挂载 (SMB - 推荐)

**使用自动挂载 (autofs)**:

```bash
# 1. 编辑 /etc/auto_master
echo "/- auto_nas" | sudo tee -a /etc/auto_master

# 2. 创建 /etc/auto_nas
cat <<EOF | sudo tee /etc/auto_nas
/Volumes/nas-openclaw -fstype=smbfs,username=<用户名>,password=<密码> ://100.65.98.22/游可玩
EOF

# 3. 重启自动挂载
sudo automount -vc

# 4. 验证
ls /Volumes/nas-openclaw/
```

---

## 7. 下一步行动

### 需要潘总完成 (NAS 端配置):

- [ ] **登录 Synology DSM**: https://100.65.98.22:5001
- [ ] **启用 NFS 服务**: 控制面板 → 文件服务 → NFS
- [ ] **配置 NFS 权限**: 共享文件夹"游可玩" → 编辑 → NFS 权限
- [ ] **添加客户端 IP**: 100.82.219.91 (阿里云 VPS)
- [ ] **确认共享路径**: 确认"游可玩"的完整路径 (如 /volume1/游可玩)
- [ ] **或提供 SMB 凭证**: 正确的用户名和密码

### 配置完成后执行 (阿里云服务器):

- [ ] 执行 NFS 挂载命令
- [ ] 验证挂载: `df -h | grep /mnt/nas`
- [ ] 访问子目录: `ls -la /mnt/nas/openclawAIteam/`
- [ ] 创建目录结构
- [ ] 测试读写权限
- [ ] 配置 /etc/fstab
- [ ] 重启验证自动挂载

### Mac mini 配置:

- [ ] 执行 NFS 或 SMB 挂载
- [ ] 验证访问
- [ ] 配置开机自动挂载

---

## 8. 故障排查命令

### NFS 故障排查:

```bash
# 检查 NFS 挂载详情
mount | grep nfs
nfsstat -m

# 查看内核日志
dmesg | grep -i nfs

# 测试 NFS 连接
rpcinfo -p 100.65.98.22

# 强制卸载 (如卡住)
umount -l /mnt/nas

# 重新挂载
mount -o remount /mnt/nas
```

### SMB 故障排查:

```bash
# 检查凭证
cat /root/.smbcredentials

# 尝试不同 SMB 版本
/usr/sbin/mount.cifs //100.65.98.22/游可玩 /mnt/nas -o credentials=/root/.smbcredentials,vers=2.0
/usr/sbin/mount.cifs //100.65.98.22/游可玩 /mnt/nas -o credentials=/root/.smbcredentials,vers=3.0

# 查看内核日志
dmesg | grep -i cifs
```

---

## 9. 总结

**正确的 NFS 导出路径**: `100.65.98.22:/volume1/游可玩` (待 NAS 配置)

**挂载命令**:
```bash
mount -t nfs 100.65.98.22:/volume1/游可玩 /mnt/nas
```

**目录结构**:
```
/mnt/nas/openclawAIteam/
├── workspace/
├── logs/{aliyun,macmini}/
├── backups/
├── config/
└── media/
```

**关键**: NAS 端必须先配置 NFS 客户端白名单 (100.82.219.91)

---

*报告生成时间：2026-03-19 21:24 CST*
