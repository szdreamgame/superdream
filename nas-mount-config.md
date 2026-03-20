# NAS 共享存储配置报告

**生成时间**: 2026-03-19 20:22 CST  
**NAS 设备**: Synology DSM (yokeplay)  
**NAS IP**: 100.65.98.22 (Tailscale)  
**阿里云服务器**: 100.82.219.91

---

## 1. 调查结果

### 1.1 网络连通性
- ✅ NAS 可达 (ping 成功)
- ✅ NFS 端口 2049 开放
- ✅ SMB 端口 445, 139 开放
- ✅ Synology DSM Web 界面 (端口 5000/5001) 可访问

### 1.2 协议测试

**NFS 测试**:
- ❌ `showmount -e` RPC 超时 (NFS 服务可能未启用或未正确配置)
- ❌ 所有常见共享路径返回 "access denied"
  - /volume1/homes, /volume1/public, /volume1/shared, etc.

**SMB 测试**:
- ✅ cifs-utils 已安装
- ❌ 所有共享需要身份验证 (guest 访问被拒绝)

### 1.3 已安装工具
- ✅ `/usr/sbin/mount.nfs` (nfs-utils)
- ✅ `/usr/sbin/mount.cifs` (cifs-utils)

---

## 2. 需要提供的 NAS 配置信息

请提供以下信息以完成挂载配置：

### 2.1 共享路径
```
NAS 共享名称：_________________
(例如：openclaw, shared, volume1/openclaw 等)
```

### 2.2 访问协议
```
□ NFS (需要 NAS 端配置 NFS 权限和客户端 IP 白名单)
□ SMB/CIFS (需要用户名/密码)
```

### 2.3 身份验证 (如选择 SMB)
```
用户名：_________________
密码：_________________
```

### 2.4 NFS 客户端授权 (如选择 NFS)
```
需要在 Synology NAS 上配置:
1. 文件服务 → NFS → 启用 NFS
2. 共享文件夹 → 编辑 → NFS 权限
3. 添加客户端：100.82.219.91 (阿里云 Tailscale IP)
4. 权限：读写 (rw)
```

---

## 3. 挂载命令 (待配置)

### 3.1 SMB 挂载命令 (推荐)

```bash
# 手动挂载
mkdir -p /mnt/nas
mount.cifs //100.65.98.22/<共享名称> /mnt/nas \
    -o username=<用户名>,password=<密码>,vers=3.0,iocharset=utf8,file_mode=0777,dir_mode=0777

# 测试读写
touch /mnt/nas/testfile && echo "SMB 挂载成功" && rm /mnt/nas/testfile
```

### 3.2 NFS 挂载命令

```bash
# 手动挂载
mkdir -p /mnt/nas
mount -t nfs 100.65.98.22:/volume1/<共享名称> /mnt/nas

# 测试读写
touch /mnt/nas/testfile && echo "NFS 挂载成功" && rm /mnt/nas/testfile
```

---

## 4. 开机自动挂载配置

### 4.1 创建凭证文件 (仅 SMB)

```bash
# 创建凭证文件
cat > /root/.smbcredentials <<EOF
username=<用户名>
password=<密码>
EOF
chmod 600 /root/.smbcredentials
```

### 4.2 配置 /etc/fstab

**SMB 方式**:
```
//100.65.98.22/<共享名称>  /mnt/nas  cifs  credentials=/root/.smbcredentials,vers=3.0,iocharset=utf8,file_mode=0777,dir_mode=0777,_netdev  0  0
```

**NFS 方式**:
```
100.65.98.22:/volume1/<共享名称>  /mnt/nas  nfs  defaults,_netdev  0  0
```

### 4.3 测试 fstab 配置

```bash
# 测试挂载 (不实际挂载，只检查配置)
mount -a --dry-run

# 实际挂载
mount -a

# 验证
df -h | grep /mnt/nas
```

---

## 5. 共享目录结构

已创建目录结构 (在 /mnt/nas/openclaw/):

```
/mnt/nas/openclaw/
├── workspace/      # 工作区同步
├── logs/           # 集中日志
│   ├── aliyun/     # 阿里云实例日志
│   └── macmini/    # Mac mini 实例日志
├── backups/        # 备份存储
├── config/         # 共享配置
└── media/          # 媒体文件
```

---

## 6. Mac mini 挂载操作 (后续)

Mac mini (100.102.241.1) 需要执行类似的挂载操作：

### 6.1 macOS SMB 挂载

```bash
# 创建挂载点
mkdir -p /Volumes/nas-openclaw

# 挂载 (手动)
mount_smbfs //<用户名>:<密码>@100.65.98.22/<共享名称> /Volumes/nas-openclaw

# 或使用 Finder: Cmd+K → smb://100.65.98.22/<共享名称>
```

### 6.2 macOS 开机自动挂载

**方法 1: 使用自动挂载**
```bash
# 创建 /etc/auto_master 条目 (需要配置 autofs)
```

**方法 2: 使用登录脚本**
```bash
# 创建 ~/Library/LaunchAgents/com.nas.mount.plist
```

**方法 3: 使用 Finder 连接 (最简单)**
1. Finder → 前往 → 连接服务器 (Cmd+K)
2. 输入：`smb://100.65.98.22/<共享名称>`
3. 勾选"记住此密码"
4. 拖拽到侧边栏

---

## 7. 测试验证

挂载完成后执行以下测试：

```bash
# 1. 验证挂载
df -h | grep /mnt/nas

# 2. 测试写入
echo "test $(date)" > /mnt/nas/openclaw/test-aliyun.txt

# 3. 测试读取
cat /mnt/nas/openclaw/test-aliyun.txt

# 4. 测试权限
ls -la /mnt/nas/openclaw/

# 5. 清理测试文件
rm /mnt/nas/openclaw/test-aliyun.txt
```

---

## 8. 下一步操作

1. **请提供 NAS 配置信息** (第 2 节)
2. 更新挂载命令并执行
3. 配置开机自动挂载
4. 验证读写权限
5. 在 Mac mini 上执行类似配置

---

## 9. 故障排查

### 常见问题

**SMB 挂载失败**:
```bash
# 检查凭证
cat /root/.smbcredentials

# 检查 SMB 版本 (尝试不同版本)
mount.cifs //100.65.98.22/share /mnt/nas -o username=xxx,password=yyy,vers=2.0
mount.cifs //100.65.98.22/share /mnt/nas -o username=xxx,password=yyy,vers=3.0

# 查看内核日志
dmesg | grep -i cifs
```

**NFS 挂载失败**:
```bash
# 检查 NFS 服务
rpcinfo -p 100.65.98.22

# 检查共享导出
showmount -e 100.65.98.22

# 查看内核日志
dmesg | grep -i nfs
```

**权限问题**:
```bash
# 检查挂载选项
mount | grep /mnt/nas

# 检查文件权限
ls -la /mnt/nas/

# 重新挂载 (调整权限)
mount -o remount,file_mode=0777,dir_mode=0777 /mnt/nas
```

---

*文档结束*
