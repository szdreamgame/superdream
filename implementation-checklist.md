# 多实例协同实施检查清单

**项目**: 超梦 (阿里云) ↔ Mac mini 协同  
**版本**: v1.0  
**预计周期**: 10-14 天  

---

## 📋 阶段 1: 网络基础搭建 (Day 1)

### 1.1 Tailscale 账号注册
- [ ] 访问 https://login.tailscale.com
- [ ] 使用 GitHub/Google/邮箱注册
- [ ] 记录账号信息
- [ ] 确认免费额度 (100 设备/3 用户)

### 1.2 阿里云 VPS 安装
```bash
# 执行以下命令并记录输出
curl -fsSL https://tailscale.com/install.sh | sh
sudo systemctl enable --now tailscaled
sudo tailscale up
# 复制认证 URL 到浏览器完成认证
tailscale ip -4
# 记录 IP: ____________________
```
- [ ] 安装完成
- [ ] 服务已启动
- [ ] 认证成功
- [ ] IP 地址已记录

### 1.3 Mac mini 安装
```bash
# 方式 1: Homebrew
brew install --cask tailscale

# 方式 2: 官网下载
# https://tailscale.com/download

# 认证
tailscale up
tailscale ip -4
# 记录 IP: ____________________
```
- [ ] 安装完成
- [ ] 认证成功
- [ ] IP 地址已记录
- [ ] 菜单栏显示 Tailscale 图标

### 1.4 阿里云安全组配置
- [ ] 登录阿里云控制台
- [ ] 进入 ECS → 安全组
- [ ] 添加入站规则:
  - 协议：UDP
  - 端口：41641
  - 授权对象：0.0.0.0/0
  - 优先级：1
  - 策略：允许
- [ ] 保存配置

### 1.5 连通性测试
```bash
# 在阿里云执行
ping <mac-mini-tailscale-ip>
nc -zv <mac-mini-tailscale-ip> 8443

# 在 Mac mini 执行
ping <aliyun-tailscale-ip>
nc -zv <aliyun-tailscale-ip> 8443
```
- [ ] 双向 ping 通
- [ ] 端口测试通过
- [ ] 延迟 < 100ms
- [ ] 无丢包

### 1.6 开机自启动配置
```bash
# 阿里云 (systemd 已自动配置)
sudo systemctl is-enabled tailscaled

# Mac mini (图形界面自动配置)
# 系统设置 → 通用 → 登录项 → 确认 Tailscale 在列
```
- [ ] 阿里云自启动确认
- [ ] Mac mini 自启动确认
- [ ] 重启测试通过

**阶段 1 完成标志**: ✅ 两台设备可通过 Tailscale IP 互访

---

## 📋 阶段 2: 通信基础设施 (Day 2-3)

### 2.1 飞书协作群创建
- [ ] 创建飞书群 "超梦-Mac mini 协同"
- [ ] 添加相关人员
- [ ] 设置群公告 (用途说明)

### 2.2 飞书机器人配置
- [ ] 进入群设置 → 机器人 → 添加机器人
- [ ] 选择 "自定义机器人"
- [ ] 设置机器人名称 (如 "协同助手")
- [ ] 复制 Webhook 地址
- [ ] 配置安全设置 (推荐：签名验证)
- [ ] 记录 Webhook URL: ____________________

### 2.3 超梦侧消息模块开发
- [ ] 创建飞书 API 客户端
- [ ] 实现消息发送函数
- [ ] 设计消息模板 (任务通知/完成通知/告警)
- [ ] 测试发送

**测试代码**:
```python
import requests
import hashlib
import hmac
import time

def send_feishu_message(webhook, secret, message):
    timestamp = str(int(time.time()))
    sign = hmac.new(
        secret.encode(),
        f"{timestamp}\n{secret}".encode(),
        hashlib.sha256
    ).hexdigest()
    
    data = {
        "msg_type": "text",
        "content": {"text": message},
        "timestamp": timestamp,
        "sign": sign
    }
    response = requests.post(webhook, json=data)
    return response.status_code == 200

# 测试
send_feishu_message("WEBHOOK_URL", "SECRET", "🧪 协同系统测试消息")
```
- [ ] 测试消息发送成功

### 2.4 Mac mini 侧消息接收
- [ ] 配置飞书事件订阅 (如需双向)
- [ ] 或实现轮询逻辑
- [ ] 测试消息接收

### 2.5 消息模板设计
- [ ] 任务通知模板
- [ ] 进度更新模板
- [ ] 完成通知模板
- [ ] 异常告警模板

**阶段 2 完成标志**: ✅ 飞书消息可双向发送

---

## 📋 阶段 3: 共享存储配置 (Day 3-4)

### 3.1 阿里云 OSS 创建
- [ ] 登录 OSS 控制台
- [ ] 创建 Bucket (如：chaomeng-workspace)
- [ ] 选择区域 (建议：华东 1-杭州)
- [ ] 权限设置：私有
- [ ] 记录 Bucket 名称：____________________
- [ ] 记录 Endpoint: ____________________

### 3.2 访问凭证配置
- [ ] 创建 RAM 用户
- [ ] 授予 OSS 读写权限
- [ ] 创建 AccessKey
- [ ] 记录 AccessKey ID: ____________________
- [ ] 记录 AccessKey Secret: ____________________

### 3.3 Mac mini 存储挂载方案选择

**方案 A: ossutil 同步 (推荐)**
```bash
# 安装 ossutil
curl https://gosspublic.alicdn.com/ossutil/install.sh | bash

# 配置
./ossutil64 config
# 输入 Endpoint、AccessKeyID、AccessKeySecret

# 测试
./ossutil64 ls oss://chaomeng-workspace
```
- [ ] ossutil 安装完成
- [ ] 配置完成
- [ ] 可列出 Bucket 内容

**方案 B: Mount 挂载**
```bash
# 使用 ossfs
brew install ossfs
echo "bucket-name:access-key-id:access-key-secret" > ~/.passwd-ossfs
chmod 600 ~/.passwd-ossfs
ossfs bucket-name ~/mnt/oss -ourl=http://oss-cn-hangzhou.aliyuncs.com
```
- [ ] ossfs 安装完成
- [ ] 挂载成功
- [ ] 读写测试通过

### 3.4 目录结构创建
```bash
# 在 OSS 创建目录结构
ossutil64 cp -r ./workspace-structure oss://chaomeng-workspace/

# 结构:
# incoming/       # 待处理任务
# processing/     # 处理中
# completed/      # 已完成
# archive/        # 归档
```
- [ ] 目录结构创建完成
- [ ] 权限验证通过

### 3.5 同步脚本开发
```bash
#!/bin/bash
# sync-from-oss.sh
ossutil64 sync oss://chaomeng-workspace/incoming /local/workspace/incoming
ossutil64 sync /local/workspace/completed oss://chaomeng-workspace/completed
```
- [ ] 同步脚本编写完成
- [ ] 测试同步成功
- [ ] 配置 cron 定时任务

### 3.6 大文件测试
- [ ] 上传 >1GB 测试文件
- [ ] 验证传输速度
- [ ] 验证 MD5 一致性
- [ ] 测试断点续传

**阶段 3 完成标志**: ✅ 文件可双向同步，大文件传输稳定

---

## 📋 阶段 4: API 服务开发 (Day 4-7)

### 4.1 API 接口设计
- [ ] 编写 OpenAPI/Swagger 文档
- [ ] 定义接口清单:
  - POST /api/v1/tasks - 创建任务
  - GET /api/v1/tasks/:id - 查询任务
  - PUT /api/v1/tasks/:id/status - 更新状态
  - GET /api/v1/health - 健康检查
- [ ] 评审接口设计

### 4.2 超梦侧 API 实现
- [ ] 选择框架 (FastAPI/Express 等)
- [ ] 实现任务下发接口
- [ ] 实现状态查询接口
- [ ] 添加 JWT 认证中间件
- [ ] 配置 HTTPS

### 4.3 Mac mini 侧 API 实现
- [ ] 实现任务接收接口
- [ ] 实现状态上报接口
- [ ] 实现进度推送接口
- [ ] 添加 JWT 认证中间件
- [ ] 配置 HTTPS

### 4.4 JWT 认证模块
```python
import jwt
from datetime import datetime, timedelta

SECRET = "your-secret-key"  # 从环境变量读取

def generate_token(instance_id):
    payload = {
        'instance_id': instance_id,
        'exp': datetime.utcnow() + timedelta(hours=24),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, SECRET, algorithm='HS256')

def verify_token(token):
    try:
        payload = jwt.decode(token, SECRET, algorithms=['HS256'])
        return payload['instance_id']
    except:
        return None
```
- [ ] JWT 模块实现完成
- [ ] Token 生成测试通过
- [ ] Token 验证测试通过

### 4.5 HTTPS 配置
```bash
# 自签名证书 (内网可用)
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes

# 或使用 Let's Encrypt (需域名)
certbot certonly --standalone -d your-domain.com
```
- [ ] 证书生成
- [ ] 服务配置 HTTPS
- [ ] 客户端信任证书

### 4.6 API 联调测试
```bash
# 测试健康检查
curl -k https://<tailscale-ip>:8443/api/v1/health

# 测试任务创建
curl -k -X POST https://<tailscale-ip>:8443/api/v1/tasks \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"name": "test-task", "priority": 1}'
```
- [ ] 健康检查通过
- [ ] 任务创建通过
- [ ] 状态更新通过
- [ ] 认证失败正确处理

**阶段 4 完成标志**: ✅ API 服务可正常通信，认证有效

---

## 📋 阶段 5: 工作流集成 (Day 7-10)

### 5.1 超梦侧子智能体集成
- [ ] 承道输出格式标准化
- [ ] 译文输出格式标准化
- [ ] 棱镜输出格式标准化
- [ ] 画语输出格式标准化
- [ ] 实现产出物自动汇总

### 5.2 任务打包逻辑
```python
def pack_task(task_id, outputs):
    # 创建任务目录
    task_dir = f"/workspace/incoming/{task_id}"
    os.makedirs(task_dir, exist_ok=True)
    
    # 写入元数据
    with open(f"{task_dir}/manifest.json", 'w') as f:
        json.dump({
            'task_id': task_id,
            'created_at': datetime.now().isoformat(),
            'outputs': list(outputs.keys()),
            'requirements': {...}
        }, f, indent=2)
    
    # 复制产出物
    for name, path in outputs.items():
        shutil.copy(path, f"{task_dir}/{name}")
    
    return task_dir
```
- [ ] 打包逻辑实现
- [ ] 测试打包成功

### 5.3 Mac mini 视频工具集成
- [ ] Runway API 配置
- [ ] Pika API 配置
- [ ] CapCut 配置 (或 FFmpeg)
- [ ] 测试各工具可用性

### 5.4 剪辑流程自动化
- [ ] 编写剪辑脚本
- [ ] 配置配音流程
- [ ] 配置配乐流程
- [ ] 测试完整剪辑流程

### 5.5 发布工具集成
- [ ] 抖音 API 配置
- [ ] B 站 API 配置
- [ ] 视频号 API 配置
- [ ] 测试发布流程

### 5.6 端到端测试
- [ ] 创建测试任务
- [ ] 验证完整流程
- [ ] 记录各环节耗时
- [ ] 优化瓶颈

**阶段 5 完成标志**: ✅ 完整视频生产链路可自动化运行

---

## 📋 阶段 6: 监控与优化 (Day 10-14)

### 6.1 日志配置
- [ ] 超梦日志配置
- [ ] Mac mini 日志配置
- [ ] 日志级别设置
- [ ] 日志轮转配置

### 6.2 健康检查端点
- [ ] 实现 /health 端点
- [ ] 包含所有组件状态
- [ ] 配置定时检查

### 6.3 告警配置
- [ ] 飞书告警机器人
- [ ] 告警规则配置
- [ ] 告警分级 (P0/P1/P2)
- [ ] 测试告警触发

### 6.4 性能测试
- [ ] 网络延迟基准测试
- [ ] 文件传输速度测试
- [ ] API 响应时间测试
- [ ] 并发任务测试

### 6.5 文档编写
- [ ] 运维手册
- [ ] 故障排查指南
- [ ] API 文档
- [ ] 用户手册

### 6.6 应急预案
- [ ] 网络中断预案
- [ ] 服务宕机预案
- [ ] 数据丢失预案
- [ ] 人工接管流程

**阶段 6 完成标志**: ✅ 系统可稳定运行，有完善的监控和应急机制

---

## 🎯 验收标准

### 功能验收
- [ ] 任务可从超梦成功下发到 Mac mini
- [ ] 文件可可靠传输 (无丢失、无损坏)
- [ ] 状态可实时同步
- [ ] 视频可成功生成并发布
- [ ] 结果可回传到超梦

### 性能验收
- [ ] 网络延迟 < 100ms
- [ ] 文件传输速度 > 10MB/s
- [ ] API 响应时间 < 500ms
- [ ] 任务处理成功率 > 99%

### 稳定性验收
- [ ] 连续运行 7 天无故障
- [ ] 断网自动重连
- [ ] 服务异常自动恢复
- [ ] 数据一致性保证

### 安全验收
- [ ] 所有通信加密
- [ ] API 认证有效
- [ ] 访问控制正常
- [ ] 无敏感信息泄露

---

## 📝 备注

**关键依赖**:
- Tailscale 账号
- 阿里云 OSS
- 飞书开放平台应用
- 视频生成工具 API

**风险点**:
- 网络稳定性 (已配置备用方案)
- 大文件传输 (已配置断点续传)
- API 限流 (已配置重试机制)

**联系人**:
- 技术负责人：____________________
- 运维负责人：____________________
- 业务负责人：____________________

---

*最后更新：2026-03-19*
