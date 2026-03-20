# NFS 挂载测试结果报告

**测试时间**: 2026-03-19 21:08 CST  
**测试服务器**: 阿里云 VPS (100.82.219.91)  
**NAS 设备**: Synology DSM (100.65.98.22, Tailscale)  

---

## 1. 测试结果摘要

| 测试项 | 状态 | 说明 |
|--------|------|------|
| NFS 端口 2049 连通性 | ✅ 通过 | 端口开放，网络可达 |
| RPC 服务查询 (rpcinfo) | ⚠️ 超时 | RPCbind 可能被防火墙阻挡 |
| NFS 导出查询 (showmount) | ⚠️ 超时 | mountd 端口可能被阻挡 |
| NFS v4 挂载 | ❌ 失败 | 服务器拒绝访问 (access denied) |
| NFS v3 挂载 | ❌ 失败 | 服务器拒绝访问 (access denied) |
| SMB 挂载 | ❌ 失败 | 需要身份验证凭证 |

---

## 2. 详细测试过程

### 2.1 网络连通性测试

```bash
# 测试 NFS 端口 2049
timeout 5 bash -c 'echo > /dev/tcp/100.65.98.22/2049'
# 结果：✅ Port 2049 is open
```

**结论**: NFS 主端口已开放，防火墙配置正确。

### 2.2 RPC 服务查询

```bash
rpcinfo -p 100.65.98.22
# 结果：⚠️ 命令超时（无响应）
```

**分析**: RPCbind 服务可能未响应或被防火墙阻挡。NFS v4 不依赖 RPC，但 NFS v3 需要。

### 2.3 NFS 导出查询

```bash
/usr/sbin/showmount -e 100.65.98.22
# 结果：⚠️ 命令超时（无响应）
```

**分析**: mountd 服务端口（通常 892）可能被阻挡。

### 2.4 NFS 挂载尝试

**尝试的路径**:
```bash
# NFS v4
mount -t nfs 100.65.98.22:/volume1/游可玩/openclawAIteam /mnt/nas
# 结果：❌ access denied by server

mount -t nfs 100.65.98.22:/openclawAIteam /mnt/nas
# 结果：❌ access denied by server

mount -t nfs4 100.65.98.22:/volume1/游可玩/openclawAIteam /mnt/nas
# 结果：❌ access denied by server

# NFS v3
mount -t nfs -o vers=3 100.65.98.22:/volume1/游可玩/openclawAIteam /mnt/nas
# 结果：❌ access denied by server

mount -t nfs -o vers=3,nolock 100.65.98.22:/volume1/openclawAIteam /mnt/nas
# 结果：❌ access denied by server

# 其他路径尝试
mount -t nfs 100.65.98.22:/volume1 /mnt/nas
# 结果：❌ access denied by server

mount -t nfs 100.65.98.22:/ /mnt/nas
# 结果：❌ access denied by server
```

**详细错误信息**:
```
mount.nfs: mount(2): Permission denied
mount.nfs: trying 100.65.98.22 prog 100003 vers 3 prot TCP port 2049
mount.nfs: trying 100.65.98.22 prog 100005 vers 3 prot UDP port 892
mount.nfs: access denied by server while mounting ...
```

**结论**: NFS 服务器可达，但**拒绝所有客户端的访问请求**。这是 NAS 端的权限配置问题，不是网络/防火墙问题。

---

## 3. 问题诊断

### 根本原因

**NFS 服务端权限未配置**。虽然防火墙已放行 NFS 端口，但 Synology NAS 的 NFS 服务没有将当前客户端 IP 加入白名单。

**客户端 IP**: `100.82.219.91` (阿里云 VPS 的 Tailscale IP)

### 需要在 NAS 端完成的配置

1. **启用 NFS 服务**
   - 路径：控制面板 → 文件服务 → NFS → 启用 NFS

2. **配置共享文件夹的 NFS 权限**
   - 路径：控制面板 → 共享文件夹 → 选择目标共享 → 编辑 → NFS 权限
   - 点击"新增"
   - 主机名/IP: `100.82.219.91`
   - 权限：读写
   - 其他选项：
     - ✓ 允许用户访问此共享文件夹
     - ✓ 启用异步 (async)
     - 安全选项：sys (默认)

3. **确认共享路径**
   - 完整路径格式：`/volume1/<共享文件夹名称>`
   - 示例：`/volume1/openclawAIteam` 或 `/volume1/游可玩/openclawAIteam`

---

## 4. 配置完成后的挂载命令

### 4.1 手动挂载测试

```bash
# 确保挂载点存在
mkdir -p /mnt/nas

# NFS v4 挂载 (推荐)
mount -t nfs 100.65.98.22:/volume1/openclawAIteam /mnt/nas

# 或使用完整路径（如果共享文件夹在中文目录下）
mount -t nfs 100.65.98.22:/volume1/游可玩/openclawAIteam /mnt/nas
```

### 4.2 验证挂载

```bash
# 检查挂载状态
df -h /mnt/nas

# 预期输出示例:
# 100.65.98.22:/volume1/openclawAIteam  10T  2.1T  7.9T  21% /mnt/nas

# 测试读写权限
echo "test $(date)" > /mnt/nas/test-aliyun.txt
cat /mnt/nas/test-aliyun.txt
rm /mnt/nas/test-aliyun.txt

# 查看目录结构
ls -la /mnt/nas/
```

### 4.3 配置开机自动挂载

```bash
# 备份 fstab
cp /etc/fstab /etc/fstab.bak

# 添加 NFS 挂载条目
echo "100.65.98.22:/volume1/openclawAIteam  /mnt/nas  nfs  defaults,_netdev  0  0" >> /etc/fstab

# 测试 fstab 配置
mount -a --dry-run

# 如果无错误，执行实际挂载
mount -a

# 验证
df -h | grep /mnt/nas
```

### 4.4 验证重启后自动挂载

```bash
# 重启服务器
reboot

# 重启后检查
df -h | grep /mnt/nas
```

---

## 5. Mac mini 挂载指引

Mac mini IP: `100.102.241.1` (Tailscale)

### 5.1 macOS NFS 手动挂载

```bash
# 创建挂载点
mkdir -p /Volumes/nas-openclaw

# NFS 挂载
mount_nfs 100.65.98.22:/volume1/openclawAIteam /Volumes/nas-openclaw

# 验证
df -h | grep nas-openclaw
```

### 5.2 macOS Finder 挂载 (最简单)

1. 打开 Finder
2. 按 `Cmd + K` 或选择"前往" → "连接服务器"
3. 输入：`nfs://100.65.98.22/volume1/openclawAIteam`
4. 点击"连接"

### 5.3 macOS 开机自动挂载

**方法 1: 使用 autofs (推荐)**

```bash
# 编辑 /etc/auto_master，添加一行:
# /-              auto_nfs

# 创建 /etc/auto_nfs 文件:
# /Volumes/nas-openclaw  -fstype=nfs,rw  100.65.98.22:/volume1/openclawAIteam

# 重启 autofs 服务
sudo automount -vc
```

**方法 2: 使用登录脚本**

```bash
# 创建 ~/Library/LaunchAgents/com.nas.mount.plist
# (需要配置 plist 文件，在登录时执行 mount_nfs 命令)
```

**方法 3: 使用第三方工具**

- 使用 Mounty 或 OSXFUSE 等工具配置自动挂载

---

## 6. 备选方案：SMB/CIFS

如果 NFS 配置困难，可以使用 SMB 协议（需要凭证）。

### 6.1 阿里云服务器 SMB 挂载

```bash
# 创建凭证文件
cat > /root/.smbcredentials <<EOF
username=<NAS 用户名>
password=<NAS 密码>
EOF
chmod 600 /root/.smbcredentials

# 挂载 SMB
mount.cifs //100.65.98.22/openclawAIteam /mnt/nas \
    -o credentials=/root/.smbcredentials,vers=3.0,iocharset=utf8,file_mode=0777,dir_mode=0777

# 配置 fstab
echo "//100.65.98.22/openclawAIteam  /mnt/nas  cifs  credentials=/root/.smbcredentials,vers=3.0,iocharset=utf8,file_mode=0777,dir_mode=0777,_netdev  0  0" >> /etc/fstab
```

### 6.2 Mac mini SMB 挂载

```bash
# 手动挂载
mkdir -p /Volumes/nas-openclaw
mount_smbfs //<用户名>:<密码>@100.65.98.22/openclawAIteam /Volumes/nas-openclaw

# 或使用 Finder: Cmd+K → smb://100.65.98.22/openclawAIteam
```

---

## 7. 下一步行动

### 立即可执行 (等待 NAS 配置完成后):

1. [ ] 在 Synology NAS 上配置 NFS 权限（添加客户端 100.82.219.91）
2. [ ] 确认共享文件夹的准确路径
3. [ ] 在阿里云服务器上执行挂载命令
4. [ ] 验证读写权限
5. [ ] 配置 /etc/fstab 开机自动挂载
6. [ ] 重启验证自动挂载
7. [ ] 在 Mac mini 上执行类似配置

### 需要潘总确认的信息:

- [ ] NFS 共享文件夹的准确路径（例如：`/volume1/openclawAIteam`）
- [ ] 是否已在 NAS 上添加客户端 IP `100.82.219.91` 到 NFS 白名单
- [ ] 如使用 SMB，需要提供用户名/密码

---

## 8. 故障排查命令

```bash
# 查看 NFS 挂载详情
mount | grep nfs
nfsstat -m

# 查看内核日志
dmesg | grep -i nfs

# 测试 NFS 连接
rpcinfo -p 100.65.98.22

# 重新挂载（调整权限）
mount -o remount /mnt/nas

# 强制卸载（如卡住）
umount -l /mnt/nas
```

---

**报告生成**: 2026-03-19 21:10 CST  
**测试执行**: 承道 (OpenClaw Subagent)
