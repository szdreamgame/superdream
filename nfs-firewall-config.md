# NFS 防火墙配置指南

## 1. NFS 所需端口清单

### 核心端口

| 服务 | 端口 | 协议 | 说明 |
|------|------|------|------|
| **rpcbind/portmapper** | 111 | TCP/UDP | RPC 端口映射服务（必须） |
| **nfsd** | 2049 | TCP/UDP | NFS 主服务端口（必须） |
| **mountd** | 动态/固定 | TCP/UDP | NFS 挂载服务 |
| **statd** | 动态/固定 | TCP/UDP | NFS 状态监控 |
| **lockd** | 动态/固定 | TCP/UDP | NFS 文件锁服务 |
| **rquotad** | 动态/固定 | TCP/UDP | 磁盘配额服务 |

### 当前系统 RPC 端口状态

```
rpcinfo -p 输出:
- portmapper: 111 (TCP/UDP) ✓
- status: 54579 (UDP), 57161 (TCP) - 动态端口
```

### 建议固定端口配置

为避免动态端口变化，建议在 `/etc/nfs.conf` 或 `/etc/sysconfig/nfs` 中固定端口：

```bash
# /etc/sysconfig/nfs (RHEL/CentOS/Alibaba Cloud Linux)
RQUOTAD_PORT=875
LOCKD_TCPPORT=32803
LOCKD_UDPPORT=32769
MOUNTD_PORT=892
STATD_PORT=662
STATD_OUTGOING_PORT=32765
```

## 2. 阿里云服务器防火墙检查

### 当前状态

- **firewalld**: 未运行 (inactive/disabled)
- **iptables**: 无规则或不可用
- **当前开放端口**: 111 (rpcbind)
- **NFS 服务**: 未运行 (nfs-utils 已安装但未启动)

### 需要放行的端口（阿里云安全组 + 本地防火墙）

| 端口 | 协议 | 用途 | 优先级 |
|------|------|------|--------|
| 111 | TCP | RPC 端口映射 | 必须 |
| 111 | UDP | RPC 端口映射 | 必须 |
| 2049 | TCP | NFS 服务 | 必须 |
| 2049 | UDP | NFS 服务 | 必须 |
| 892 | TCP | mountd | 推荐固定 |
| 892 | UDP | mountd | 推荐固定 |
| 662 | TCP | statd | 推荐固定 |
| 662 | UDP | statd | 推荐固定 |
| 32803 | TCP | lockd | 推荐固定 |
| 32769 | UDP | lockd | 推荐固定 |

## 3. 防火墙配置命令

### 3.1 阿里云服务器配置

#### 方案 A: 使用 firewalld（推荐）

```bash
# 启动 firewalld
systemctl enable firewalld
systemctl start firewalld

# 添加 NFS 相关服务
firewall-cmd --permanent --add-service=nfs
firewall-cmd --permanent --add-service=rpc-bind
firewall-cmd --permanent --add-service=mountd

# 或者手动添加端口
firewall-cmd --permanent --add-port=111/tcp
firewall-cmd --permanent --add-port=111/udp
firewall-cmd --permanent --add-port=2049/tcp
firewall-cmd --permanent --add-port=2049/udp
firewall-cmd --permanent --add-port=892/tcp
firewall-cmd --permanent --add-port=892/udp
firewall-cmd --permanent --add-port=662/tcp
firewall-cmd --permanent --add-port=662/udp
firewall-cmd --permanent --add-port=32803/tcp
firewall-cmd --permanent --add-port=32769/udp

# 限制源 IP（推荐，替换为实际客户端 IP）
firewall-cmd --permanent --add-rich-rule='rule family="ipv4" source address="客户端 IP/32" port port="2049" protocol="tcp" accept'

# 重载配置
firewall-cmd --reload

# 验证
firewall-cmd --list-all
```

#### 方案 B: 使用 iptables

```bash
# 添加 NFS 规则（替换 客户端IP 为实际 IP）
iptables -A INPUT -p tcp -s 客户端IP --dport 111 -j ACCEPT
iptables -A INPUT -p udp -s 客户端IP --dport 111 -j ACCEPT
iptables -A INPUT -p tcp -s 客户端IP --dport 2049 -j ACCEPT
iptables -A INPUT -p udp -s 客户端IP --dport 2049 -j ACCEPT
iptables -A INPUT -p tcp -s 客户端IP --dport 892 -j ACCEPT
iptables -A INPUT -p udp -s 客户端IP --dport 892 -j ACCEPT
iptables -A INPUT -p tcp -s 客户端IP --dport 662 -j ACCEPT
iptables -A INPUT -p udp -s 客户端IP --dport 662 -j ACCEPT
iptables -A INPUT -p tcp -s 客户端IP --dport 32803 -j ACCEPT
iptables -A INPUT -p udp -s 客户端IP --dport 32769 -j ACCEPT

# 保存规则
service iptables save  # 或 iptables-save > /etc/iptables/rules.v4
```

#### 方案 C: 阿里云安全组配置（控制台）

1. 登录阿里云控制台
2. 进入 ECS → 安全组
3. 添加入方向规则:
   - 端口范围：111/111, 2049/2049, 892/892, 662/662, 32803/32803, 32769/32769
   - 授权对象：客户端 IP/32
   - 协议：TCP 和 UDP 分别添加

### 3.2 Synology NAS 防火墙配置

#### 通过 DSM 界面配置

1. **打开 DSM 控制面板**
   - 登录 Synology DSM
   - 进入 `控制面板` → `安全性` → `防火墙`

2. **启用防火墙**
   - 勾选 `启用防火墙`
   - 点击 `规则` 按钮

3. **添加 NFS 规则**
   - 点击 `新增`
   - 端口：`111, 2049, 892, 662, 32803, 32769`
   - 协议：`TCP` 和 `UDP`（分别创建规则）
   - 来源 IP：`指定 IP` → 输入阿里云服务器 IP
   - 操作：`允许`

4. **文件服务特殊配置**
   - 进入 `控制面板` → `文件服务` → `NFS`
   - 确保 NFS 服务已启用
   - 编辑共享文件夹的 NFS 权限，添加客户端 IP

#### 通过 SSH 配置（高级）

```bash
# 登录 NAS SSH
# 编辑 iptables 规则（如果支持）
iptables -A INPUT -p tcp -s 阿里云服务器IP --dport 2049 -j ACCEPT
iptables -A INPUT -p udp -s 阿里云服务器IP --dport 2049 -j ACCEPT
iptables -A INPUT -p tcp -s 阿里云服务器IP --dport 111 -j ACCEPT
iptables -A INPUT -p udp -s 阿里云服务器IP --dport 111 -j ACCEPT

# 保存配置
/usr/syno/etc.defaults/rc.firewall.user  # 根据型号可能不同
```

## 4. NFS 服务配置与启动

### 4.1 阿里云服务器 NFS 服务端配置

```bash
# 1. 配置固定端口（如果使用动态端口则跳过）
cat >> /etc/sysconfig/nfs << EOF
RQUOTAD_PORT=875
LOCKD_TCPPORT=32803
LOCKD_UDPPORT=32769
MOUNTD_PORT=892
STATD_PORT=662
STATD_OUTGOING_PORT=32765
EOF

# 2. 配置 NFS 导出
cat >> /etc/exports << EOF
# 示例：导出 /data/nfs 给特定客户端
/data/nfs    客户端IP(rw,sync,no_root_squash,no_subtree_check)
# 或导出给整个网段
/data/nfs    192.168.1.0/24(rw,sync,no_root_squash,no_subtree_check)
EOF

# 3. 创建导出目录
mkdir -p /data/nfs
chmod 755 /data/nfs

# 4. 应用导出配置
exportfs -ra

# 5. 启动并启用 NFS 服务
systemctl enable rpcbind
systemctl start rpcbind
systemctl enable nfs-server
systemctl start nfs-server
systemctl enable nfs-lock
systemctl start nfs-lock
systemctl enable nfs-idmap
systemctl start nfs-idmap

# 6. 验证服务状态
systemctl status nfs-server
rpcinfo -p
showmount -e localhost
```

### 4.2 Synology NAS NFS 配置

1. **启用 NFS 服务**
   - DSM → 控制面板 → 文件服务 → NFS
   - 勾选 `启用 NFS 服务`
   - 点击 `应用`

2. **配置共享文件夹 NFS 权限**
   - DSM → 控制面板 → 共享文件夹
   - 选择要导出的文件夹 → 编辑
   - NFS 权限 → 新增
   - 权限：`可读/可写`
   - 主机：`阿里云服务器 IP`
   - 权限：`no_root_squash` (如需要 root 访问)
   - 安全：`sys` (默认)

## 5. 测试 NFS 挂载

### 5.1 客户端测试挂载

```bash
# 1. 安装 NFS 客户端（如未安装）
# Alibaba Cloud Linux / RHEL / CentOS
yum install -y nfs-utils

# Ubuntu / Debian
apt install -y nfs-common

# 2. 查看服务器导出
showmount -e 服务器IP

# 3. 测试挂载
mkdir -p /mnt/nfs-test
mount -t nfs 服务器IP:/导出路径 /mnt/nfs-test

# 4. 验证挂载
df -h | grep nfs
ls -la /mnt/nfs-test

# 5. 测试读写
echo "NFS test $(date)" > /mnt/nfs-test/test.txt
cat /mnt/nfs-test/test.txt

# 6. 卸载测试
umount /mnt/nfs-test
```

### 5.2 持久化挂载（/etc/fstab）

```bash
# 添加到 /etc/fstab
echo "服务器IP:/导出路径  /mnt/nfs  nfs  defaults,_netdev  0  0" >> /etc/fstab

# 测试 fstab 配置
mount -a
```

### 5.3 故障排查命令

```bash
# 检查网络连接
ping 服务器IP
telnet 服务器IP 2049
nc -zv 服务器IP 2049

# 检查 RPC 服务
rpcinfo -p 服务器IP

# 查看挂载详情
mount -t nfs
nfsstat -m

# 查看 NFS 统计
nfsstat

# 检查防火墙日志
tail -f /var/log/messages | grep -i nfs
journalctl -u firewalld -f

# 测试端口连通性
nmap -p 111,2049,892,662 服务器IP
```

## 6. 快速配置检查清单

### 阿里云服务器

- [ ] firewalld 已启动并配置 NFS 规则
- [ ] 阿里云安全组已放行 NFS 端口
- [ ] NFS 服务已启动 (rpcbind, nfs-server)
- [ ] /etc/exports 已配置导出路径
- [ ] exportfs -ra 已执行
- [ ] showmount -e 显示导出列表

### Synology NAS

- [ ] DSM 防火墙已启用并配置规则
- [ ] NFS 服务已启用
- [ ] 共享文件夹 NFS 权限已配置
- [ ] 客户端 IP 已添加到允许列表

### 客户端

- [ ] nfs-utils/nfs-common 已安装
- [ ] 可以 ping 通服务器
- [ ] showmount -e 可以看到导出
- [ ] 可以成功挂载
- [ ] 读写测试通过

## 7. 安全建议

1. **限制源 IP**: 只允许特定 IP 访问 NFS 端口
2. **使用 NFSv4**: 比 NFSv3 更安全，只需要 2049 端口
3. **避免 no_root_squash**: 除非确实需要 root 访问
4. **使用 Kerberos**: 生产环境考虑 NFS + Kerberos 认证
5. **定期审计**: 检查 /etc/exports 和防火墙规则
6. **监控日志**: 关注 /var/log/messages 中的 NFS 相关日志

---

**文档生成时间**: 2026-03-19
**适用系统**: Alibaba Cloud Linux / Synology DSM
