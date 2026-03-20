# NFS Squash 配置分析与挂载测试报告

**测试时间**: 2026-03-19 21:20 CST  
**测试服务器**: 阿里云 VPS (100.82.219.91)  
**NAS 设备**: Synology DSM (100.65.98.22, Tailscale)  
**执行**: 承道 (OpenClaw Subagent)

---

## 1. 📚 Squash 选项详解

NFS 的 Squash 选项用于控制客户端用户权限在服务器端的映射方式：

### 1.1 no_root_squash
- **含义**: 客户端的 root 用户在 NFS 服务器上保持 root 权限
- **适用场景**: 
  - 完全信任的客户端
  - 需要远程 root 访问的管理场景
  - 备份服务器需要完整权限
- **安全风险**: ⚠️ **高** - 如果客户端被攻破，攻击者可获得服务器 root 权限
- **建议**: 仅在内部可信网络使用

### 1.2 root_squash (默认)
- **含义**: 客户端的 root 用户被映射为匿名用户 (通常是 nobody:nogroup)
- **适用场景**: 
  - 大多数生产环境
  - 不信任的客户端
  - 标准文件共享
- **安全风险**: ✅ **低** - 即使客户端 root 被攻破，在服务器端也只有普通用户权限
- **建议**: **推荐默认使用**

### 1.3 all_squash
- **含义**: 所有客户端用户 (包括 root 和普通用户) 都被映射为匿名用户
- **适用场景**: 
  - 公共文件共享
  - 只读发布目录
  - 需要统一权限的场景
- **配合选项**: 通常与 `anonuid` 和 `anongid` 一起使用，指定映射的具体用户 ID
- **示例**: `all_squash,anonuid=1000,anongid=1000`
- **建议**: 用于公共只读共享或特定权限场景

---

## 2. 🔍 当前配置分析

### 2.1 网络连通性测试

| 测试项 | 状态 | 结果 |
|--------|------|------|
| Ping NAS | ✅ 通过 | 延迟 ~23ms |
| NFS 端口 2049 | ✅ 开放 | TCP 可达 |
| RPC 端口 111 | ✅ 开放 | TCP 可达 |
| showmount -e | ⚠️ 超时 | mountd 无响应 |
| rpcinfo -p | ⚠️ 超时 | RPC 服务无响应 |

### 2.2 客户端信息

- **客户端 IP**: `100.82.219.91` (阿里云 VPS 的 Tailscale IP)
- **挂载点**: `/mnt/nas` (已存在，包含 openclaw 目录)
- **NFS 工具**: nfs-utils 已安装

### 2.3 问题说明

⚠️ **未找到潘总的配置截图**。以下分析基于实际测试结果。

---

## 3. 🧪 NFS 挂载测试结果

### 3.1 测试的路径 (全部失败)

```bash
# 尝试的路径均返回 "access denied by server"
mount -t nfs 100.65.98.22:/volume1/openclawAIteam /mnt/nas
mount -t nfs 100.65.98.22:/游可玩/openclawAIteam /mnt/nas
mount -t nfs 100.65.98.22:/volume1/游可玩/openclawAIteam /mnt/nas
mount -t nfs 100.65.98.22:/volume1 /mnt/nas
mount -t nfs 100.65.98.22:/ /mnt/nas
```

### 3.2 测试的选项 (全部失败)

```bash
# NFS v4 (默认)
mount -t nfs 100.65.98.22:/volume1/openclawAIteam /mnt/nas

# NFS v3
mount -t nfs -o vers=3 100.65.98.22:/volume1/openclawAIteam /mnt/nas

# NFS v3 + nolock
mount -t nfs -o vers=3,nolock 100.65.98.22:/volume1/openclawAIteam /mnt/nas
```

### 3.3 错误详情

```
mount.nfs: mount(2): Permission denied
mount.nfs: trying 100.65.98.22 prog 100003 vers 3 prot TCP port 2049
mount.nfs: trying 100.65.98.22 prog 100005 vers 3 prot UDP port 892
mount.nfs: access denied by server while mounting 100.65.98.22:/volume1/openclawAIteam
```

**关键信息**:
- 客户端地址：`100.82.219.91`
- 错误类型：`Permission denied` (服务器拒绝访问)
- 不是网络问题，是**权限配置问题**

---

## 4. 📋 诊断分析

### 4.1 根本原因

**NFS 服务端未授权客户端 IP 访问**

虽然 NFS 端口 (2049) 已开放，但 Synology NAS 的 NFS 服务配置中**没有将客户端 IP `100.82.219.91` 加入白名单**。

### 4.2 可能的问题

1. ❌ NFS 服务未启用
2. ❌ 共享文件夹未配置 NFS 权限
3. ❌ 客户端 IP 不在允许列表中
4. ❌ Squash 配置不当 (可能性较低)

---

## 5. ✅ 建议与操作步骤

### 5.1 Squash 配置建议

| 使用场景 | 推荐配置 | 说明 |
|----------|----------|------|
| OpenClaw 工作区 | `root_squash` (默认) | 安全，普通用户权限 |
| 需要 root 操作 | `no_root_squash` | 仅限可信内部网络 |
| 公共只读共享 | `all_squash,anonuid=1000,anongid=1000` | 统一匿名权限 |

**推荐**: 使用默认的 `root_squash`，除非有特殊需求。

### 5.2 NAS 端配置步骤 (潘总操作)

#### 步骤 1: 启用 NFS 服务
```
Synology DSM → 控制面板 → 文件服务 → NFS
✓ 启用 NFS 服务
→ 应用
```

#### 步骤 2: 配置共享文件夹 NFS 权限
```
Synology DSM → 控制面板 → 共享文件夹
→ 选择目标共享 (如：openclawAIteam)
→ 编辑 → NFS 权限 → 新增
```

**配置参数**:
| 字段 | 值 |
|------|-----|
| 主机名或 IP | `100.82.219.91` |
| 权限 | 读写 (Read/Write) |
| 异步 | ✓ 启用 |
| 安全 | sys (默认) |
| Squash | root_squash (推荐) 或 no_root_squash |

#### 步骤 3: 确认共享路径
```
在共享文件夹列表中查看完整路径
格式：/volume1/<共享文件夹名称>
示例：/volume1/openclawAIteam
```

#### 步骤 4: 检查防火墙 (如启用)
```
控制面板 → 安全性 → 防火墙 → 编辑规则
确保允许来自 100.82.219.91 的 NFS 流量 (端口 2049)
```

### 5.3 客户端挂载命令 (配置完成后执行)

```bash
# 1. 卸载之前的尝试 (如有)
umount /mnt/nas 2>/dev/null

# 2. 确保挂载点存在
mkdir -p /mnt/nas

# 3. NFS 挂载 (推荐 NFS v4)
mount -t nfs 100.65.98.22:/volume1/openclawAIteam /mnt/nas

# 如果共享文件夹在中文目录下
mount -t nfs 100.65.98.22:/volume1/游可玩/openclawAIteam /mnt/nas

# 4. 验证挂载
df -h | grep /mnt/nas

# 5. 测试读写
echo "test $(date)" > /mnt/nas/test-write.txt && cat /mnt/nas/test-write.txt && rm /mnt/nas/test-write.txt

# 6. 查看目录结构
ls -la /mnt/nas/
```

### 5.4 配置开机自动挂载

```bash
# 1. 备份 fstab
cp /etc/fstab /etc/fstab.bak

# 2. 添加 NFS 挂载条目
echo "100.65.98.22:/volume1/openclawAIteam  /mnt/nas  nfs  defaults,_netdev  0  0" >> /etc/fstab

# 3. 测试配置 (不实际挂载)
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

---

## 6. 🍎 Mac mini 挂载指引

**Mac mini IP**: `100.102.241.1` (Tailscale)

### 6.1 macOS NFS 手动挂载

```bash
# 创建挂载点
mkdir -p /Volumes/nas-openclaw

# NFS 挂载
mount_nfs 100.65.98.22:/volume1/openclawAIteam /Volumes/nas-openclaw

# 验证
df -h | grep nas-openclaw
```

### 6.2 macOS Finder 挂载 (最简单)

1. 打开 Finder
2. 按 `Cmd + K` 或选择"前往" → "连接服务器"
3. 输入：`nfs://100.65.98.22/volume1/openclawAIteam`
4. 点击"连接"

### 6.3 macOS 开机自动挂载

**方法 1: 使用 autofs**
```bash
# 编辑 /etc/auto_master，添加:
# /-              auto_nfs

# 创建 /etc/auto_nfs:
# /Volumes/nas-openclaw  -fstype=nfs,rw  100.65.98.22:/volume1/openclawAIteam

# 重启 autofs
sudo automount -vc
```

**方法 2: 使用 Finder (推荐)**
1. Finder 连接 NAS
2. 拖拽到侧边栏
3. 系统设置 → 通用 → 登录时打开 → 添加挂载的卷

---

## 7. 🔧 故障排查命令

```bash
# 查看 NFS 挂载详情
mount | grep nfs

# 查看内核日志
dmesg | grep -i nfs

# 测试 RPC 连接
rpcinfo -p 100.65.98.22

# 查看导出列表
/usr/sbin/showmount -e 100.65.98.22

# 强制卸载 (如卡住)
umount -l /mnt/nas

# 重新挂载
mount -o remount /mnt/nas

# 查看系统日志
journalctl -u nfs-client.target
```

---

## 8. 📝 待确认信息

请潘总确认并提供:

- [ ] NFS 共享文件夹的准确名称 (在 DSM 控制面板 → 共享文件夹中查看)
- [ ] 是否已启用 NFS 服务
- [ ] 是否已将 `100.82.219.91` 添加到 NFS 权限白名单
- [ ] Squash 配置偏好 (推荐：root_squash)

---

## 9. ✅ 验证清单

配置完成后执行:

- [ ] NFS 服务已启用
- [ ] 共享文件夹 NFS 权限已配置
- [ ] 客户端 IP 已加入白名单
- [ ] 执行挂载命令成功
- [ ] 读写测试通过
- [ ] /etc/fstab 配置完成
- [ ] 重启后自动挂载验证通过
- [ ] Mac mini 挂载配置完成

---

**报告生成**: 2026-03-19 21:20 CST  
**测试执行**: 承道 (OpenClaw Subagent)
