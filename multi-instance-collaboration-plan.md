# 多实例协同方案规划与实施路径

**文档版本**: v1.0  
**创建时间**: 2026-03-19  
**目标**: 实现阿里云主实例 (超梦) 与本地 Mac mini 副实例的高效协同

---

## 1. 网络方案评估

### 1.1 Tailscale vs ZeroTier 对比分析

| 维度 | Tailscale | ZeroTier | 推荐 |
|------|-----------|----------|------|
| **部署复杂度** | 低 (一键安装) | 中 (需配置 Network) | Tailscale |
| **NAT 穿透能力** | 优秀 (基于 WireGuard) | 良好 | Tailscale |
| **阿里云兼容性** | 完全兼容 | 完全兼容 | 平手 |
| **免费额度** | 100 设备/3 用户 | 25 设备/1 网络 | Tailscale |
| **延迟表现** | ~20-50ms (直连) | ~30-60ms (直连) | Tailscale |
| **自托管选项** | Headscale (开源) | ZeroTier Controller | 平手 |
| **配置管理** | Web Dashboard + CLI | Web Dashboard + CLI | 平手 |
| **稳定性** | 极高 | 高 | Tailscale |

### 1.2 推荐方案：Tailscale

**选择理由**:
1. 更简单的初始配置
2. 更好的 NAT 穿透成功率
3. 更活跃的社区和文档
4. 免费额度更适合当前场景
5. 与 WireGuard 兼容，性能更优

### 1.3 具体配置步骤

#### 步骤 1: 阿里云 VPS 安装 Tailscale

```bash
# 安装 Tailscale
curl -fsSL https://tailscale.com/install.sh | sh

# 启动服务
sudo systemctl enable --now tailscaled

# 认证 (会输出认证 URL)
sudo tailscale up

# 记录 IP 地址 (格式: 100.x.y.z)
tailscale ip
```

#### 步骤 2: Mac mini 安装 Tailscale

```bash
# 下载安装 macOS 客户端
# 访问 https://tailscale.com/download

# 或通过 Homebrew 安装
brew install --cask tailscale

# 认证
tailscale up

# 记录 IP 地址
tailscale ip
```

#### 步骤 3: 配置 Tailscale 网络

```bash
# 在 Tailscale Admin Console (https://login.tailscale.com/admin) 中:
# 1. 确认两台设备都在线
# 2. 启用 "Use Tailscale" 作为默认路由 (可选)
# 3. 配置 ACL 允许互访 (默认已允许)
```

#### 步骤 4: 防火墙配置

**阿里云安全组**:
```
放行规则:
- 协议: UDP
- 端口: 41641 (Tailscale 默认)
- 源: 0.0.0.0/0 (Tailscale 流量加密，安全)
```

**Mac mini 防火墙**:
```bash
# macOS 系统偏好设置 → 安全性与隐私 → 防火墙
# 允许 Tailscale 应用通过防火墙
```

#### 步骤 5: 连通性测试

```bash
# 在阿里云 ping Mac mini
ping <mac-mini-tailscale-ip>

# 在 Mac mini ping 阿里云
ping <aliyun-tailscale-ip>

# 测试端口连通性
nc -zv <target-ip> <port>
```

### 1.4 备用方案：ZeroTier

如 Tailscale 不可用，ZeroTier 配置:

```bash
# 安装 ZeroTier
curl -s https://install.zerotier.com | sudo bash

# 加入网络 (需先在 zerotier.com 创建 Network)
sudo zerotier-cli join <network-id>

# 在 Web Console 授权设备
# https://my.zerotier.com/network/<network-id>
```

---

## 2. 工作流程梳理

### 2.1 完整业务流程图

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           超梦 (阿里云 VPS - 总控)                        │
│  角色：流程编排、任务分发、质量把控、进度追踪                              │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
        ┌───────────────────────────┼───────────────────────────┐
        │                           │                           │
        ▼                           ▼                           ▼
┌───────────────┐         ┌───────────────┐         ┌───────────────┐
│    承道       │         │    译文       │         │    棱镜       │
│  内容策划     │         │  文案翻译     │         │  视觉设计     │
│  脚本撰写     │         │  本地化处理   │         │  分镜制作     │
└───────┬───────┘         └───────┬───────┘         └───────┬───────┘
        │                         │                         │
        └─────────────────────────┼─────────────────────────┘
                                  │
                                  ▼
                    ┌─────────────────────────┐
                    │      画语               │
                    │    图片/素材生成         │
                    │    (SD/MJ 等)           │
                    └───────────┬─────────────┘
                                │
                                │ [产出物打包]
                                │ - 脚本文件
                                │ - 翻译文案
                                │ - 分镜图片
                                │ - 素材资源
                                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    Tailscale 安全隧道 (100.x.x.x)                        │
│                        加密传输 + 自动重连                                │
└─────────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                  Mac mini (本地 - 视频团队 Leader)                        │
│  角色：视频生产调度、资源协调、质量审核、发布管理                          │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
        ┌───────────────────────────┼───────────────────────────┐
        │                           │                           │
        ▼                           ▼                           ▼
┌───────────────┐         ┌───────────────┐         ┌───────────────┐
│  视频生成     │         │   视频剪辑     │         │   发布管理    │
│  (Runway/    │         │  (CapCut/     │         │  (多平台      │
│   Pika/      │         │   Premiere)   │         │   分发)       │
│   Stable     │         │               │         │               │
│   Video)     │         │               │         │               │
└───────────────┘         └───────────────┘         └───────────────┘
```

### 2.2 节点责任定义

| 节点 | 位置 | 主要职责 | 关键能力 |
|------|------|----------|----------|
| **超梦** | 阿里云 VPS | 总控编排、任务分发、进度追踪、质量审核 | 流程管理、API 调用、状态监控 |
| **承道** | 阿里云 VPS | 内容策划、脚本撰写、选题分析 | 文本生成、创意策划 |
| **译文** | 阿里云 VPS | 文案翻译、本地化适配、多语言支持 | 多语言翻译、文化适配 |
| **棱镜** | 阿里云 VPS | 视觉设计、分镜制作、风格定义 | 图像理解、设计规划 |
| **画语** | 阿里云 VPS | 图片生成、素材创作、视觉产出 | SD/MJ 等图像生成 |
| **Mac mini** | 本地 | 视频生产调度、资源协调、发布管理 | 网页调用、工具集成、API 对接 |
| **视频生成** | Mac mini | AI 视频生成、动态效果制作 | Runway/Pika/本地模型 |
| **视频剪辑** | Mac mini | 素材剪辑、配音配乐、特效合成 | CapCut/Premiere/FFmpeg |
| **发布管理** | Mac mini | 多平台分发、数据追踪、反馈收集 | 各平台 API、数据分析 |

### 2.3 消息/数据传递机制

#### 机制 1: 飞书机器人消息队列 (推荐)

```
超梦 → 飞书群机器人 → Mac mini
     (任务通知 + 附件)

Mac mini → 飞书群机器人 → 超梦
     (完成通知 + 成果链接)
```

**优势**:
- 已有飞书机器人基础设施
- 支持富文本和文件附件
- 消息可靠投递
- 便于人工监督和介入

**实现**:
```python
# 超梦侧发送任务
POST https://open.feishu.cn/open-apis/bot/v2/hook/<webhook_id>
{
    "msg_type": "interactive",
    "card": {
        "config": {"wide_screen_mode": true},
        "elements": [
            {"tag": "div", "text": {"content": "新视频任务待处理", "tag": "lark_md"}},
            {"tag": "action", "actions": [...]}
        ],
        "header": {"template": "blue", "title": {"content": "🎬 视频生产任务", "tag": "plain_text"}}
    }
}
```

#### 机制 2: 共享存储同步

```
阿里云 NAS/OSS ←→ Mac mini (本地存储)
       │
       └── Tailscale 加密通道
```

**目录结构**:
```
/shared-workspace/
├── incoming/          # 待处理任务
│   ├── task-001/
│   │   ├── script.md
│   │   ├── storyboard/
│   │   └── assets/
│   └── task-002/
├── processing/        # 处理中
├── completed/         # 已完成
│   └── task-001/
│       ├── final_video.mp4
│       └── publish_report.json
└── archive/           # 归档
```

#### 机制 3: HTTP API 直接调用

```
超梦 API Server (阿里云) ←→ Mac mini API Server (本地)
       │                            │
       └────── Tailscale IP ────────┘
```

---

## 3. 技术实施路径

### 3.1 跨实例通信方案

#### 方案对比

| 方案 | 延迟 | 可靠性 | 复杂度 | 推荐场景 |
|------|------|--------|--------|----------|
| 飞书机器人 | 中 (~1-3s) | 高 | 低 | 任务通知、状态同步 |
| 共享存储 | 低 (取决于同步) | 高 | 中 | 大文件传输 |
| HTTP API | 低 (~50-200ms) | 中 | 高 | 实时交互、状态查询 |
| WebSocket | 低 (~20-100ms) | 中 | 高 | 实时推送、长连接 |

#### 推荐架构：混合方案

```
┌─────────────────────────────────────────────────────────────┐
│                      通信架构总览                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  任务下发：飞书机器人 (可靠、可追踪、有人工监督)               │
│  文件传输：共享存储 + Tailscale (大文件、断点续传)            │
│  状态同步：HTTP API (实时查询、进度更新)                      │
│  紧急通知：飞书机器人 @提及 (高优先级)                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 身份认证和授权

#### 方案 1: API Key + IP 白名单

```yaml
# 超梦侧配置
auth:
  mac_mini_api_key: "sk_xxxxxxxxxxxxx"
  allowed_ips:
    - "100.x.x.x"  # Mac mini Tailscale IP

# Mac mini 侧配置
auth:
  chaomeng_api_key: "sk_yyyyyyyyyyyyy"
  allowed_ips:
    - "100.a.b.c"  # 超梦 Tailscale IP
```

**请求头**:
```http
Authorization: Bearer sk_xxxxxxxxxxxxx
X-Instance-ID: mac-mini-001
```

#### 方案 2: JWT Token (推荐)

```python
# Token 生成 (超梦)
import jwt
import datetime

def generate_token(instance_id, secret):
    payload = {
        'instance_id': instance_id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24),
        'iat': datetime.datetime.utcnow()
    }
    return jwt.encode(payload, secret, algorithm='HS256')

# Token 验证 (Mac mini)
def verify_token(token, secret):
    try:
        payload = jwt.decode(token, secret, algorithms=['HS256'])
        return payload['instance_id']
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
```

#### 方案 3: 飞书应用授权 (最安全)

利用飞书应用的企业授权机制，所有通信通过飞书开放平台中转，无需暴露直接 API。

### 3.3 数据同步策略

#### 策略 1: 任务状态机

```
┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐
│ CREATED │ →  │ ASSIGNED│ →  │PROCESSING│ →  │ REVIEW  │ →  │PUBLISHED│
└─────────┘    └─────────┘    └─────────┘    └─────────┘    └─────────┘
     │              │              │              │              │
     ▼              ▼              ▼              ▼              ▼
  超梦创建      超梦分发      Mac mini 处理   超梦审核      发布完成
```

**状态同步 API**:
```python
# 更新任务状态
PUT /api/v1/tasks/{task_id}/status
{
    "status": "PROCESSING",
    "progress": 45,
    "message": "视频生成中，预计剩余 15 分钟",
    "updated_by": "mac-mini-001",
    "timestamp": 1710852000000
}
```

#### 策略 2: 文件版本控制

```bash
# 使用 rsync 进行增量同步
rsync -avz --delete \
    --exclude '*.tmp' \
    --exclude '.git' \
    /shared-workspace/incoming/ \
    user@<mac-mini-tailscale-ip>:/shared-workspace/incoming/
```

#### 策略 3: 数据库同步 (可选)

如需要复杂查询，使用 SQLite + 定期同步:
```python
# 使用 litestream 进行 SQLite 实时复制到 S3/OSS
# 两端从对象存储同步最新数据
```

---

## 4. 实施步骤清单

### 阶段 1: 网络基础搭建 (Day 1)

- [ ] **1.1** 在 Tailscale 官网注册账号
- [ ] **1.2** 阿里云 VPS 安装 Tailscale
- [ ] **1.3** Mac mini 安装 Tailscale
- [ ] **1.4** 配置阿里云安全组 (UDP 41641)
- [ ] **1.5** 验证双向连通性 (ping + nc 测试)
- [ ] **1.6** 记录双方 Tailscale IP 地址
- [ ] **1.7** 配置开机自启动

### 阶段 2: 通信基础设施 (Day 2-3)

- [ ] **2.1** 创建飞书协作群 (超梦 + Mac mini 运营人员)
- [ ] **2.2** 配置飞书机器人 Webhook
- [ ] **2.3** 开发飞书消息发送模块 (超梦侧)
- [ ] **2.4** 开发飞书消息接收模块 (Mac mini 侧)
- [ ] **2.5** 测试消息收发流程
- [ ] **2.6** 设计消息模板 (任务通知、完成通知、异常告警)

### 阶段 3: 共享存储配置 (Day 3-4)

- [ ] **3.1** 在阿里云创建 NAS 或 OSS Bucket
- [ ] **3.2** 配置 Mac mini 挂载 NAS (或 OSS 同步脚本)
- [ ] **3.3** 设计目录结构 (incoming/processing/completed/archive)
- [ ] **3.4** 配置文件同步脚本 (rsync 或 ossutil)
- [ ] **3.5** 测试文件传输 (大文件测试 >1GB)
- [ ] **3.6** 配置定时同步任务 (cron)

### 阶段 4: API 服务开发 (Day 4-7)

- [ ] **4.1** 设计 API 接口文档 (OpenAPI/Swagger)
- [ ] **4.2** 超梦侧实现任务下发 API
- [ ] **4.3** Mac mini 侧实现任务接收 API
- [ ] **4.4** 实现状态查询 API
- [ ] **4.5** 实现 JWT 认证模块
- [ ] **4.6** 配置 HTTPS (自签名证书或 Let's Encrypt)
- [ ] **4.7** API 联调测试

### 阶段 5: 工作流集成 (Day 7-10)

- [ ] **5.1** 超梦集成承道/译文/棱镜/画语输出
- [ ] **5.2** 实现产出物自动打包逻辑
- [ ] **5.3** Mac mini 集成视频生成工具 (Runway/Pika API)
- [ ] **5.4** Mac mini 集成剪辑工具 (CapCut CLI 或 FFmpeg)
- [ ] **5.5** Mac mini 集成发布工具 (各平台 API)
- [ ] **5.6** 端到端流程测试 (完整视频生产链路)

### 阶段 6: 监控与优化 (Day 10-14)

- [ ] **6.1** 配置日志收集 (超梦 + Mac mini)
- [ ] **6.2** 配置健康检查端点
- [ ] **6.3** 配置异常告警 (飞书机器人通知)
- [ ] **6.4** 性能基准测试
- [ ] **6.5** 网络延迟监控
- [ ] **6.6** 编写运维文档
- [ ] **6.7** 制定应急预案

---

## 5. 风险评估和应对

### 5.1 网络风险

| 风险 | 概率 | 影响 | 应对措施 |
|------|------|------|----------|
| Tailscale 连接中断 | 中 | 高 | 配置自动重连 + 备用 ZeroTier |
| 阿里云防火墙拦截 | 低 | 高 | 提前配置安全组 + 测试验证 |
| NAT 穿透失败 | 低 | 中 | 配置 Tailscale DERP 中继 |
| 带宽不足 | 中 | 中 | 大文件走 OSS 直传 + 压缩传输 |

**应对方案**:
```bash
# 配置 Tailscale 连接监控脚本
#!/bin/bash
while true; do
    if ! tailscale status | grep -q "100\."; then
        # 发送告警到飞书
        curl -X POST "https://open.feishu.cn/open-apis/bot/v2/hook/xxx" \
            -d '{"msg_type":"text","content":{"text":"⚠️ Tailscale 连接中断"}}'
        # 尝试重启服务
        sudo systemctl restart tailscaled
    fi
    sleep 60
done
```

### 5.2 数据风险

| 风险 | 概率 | 影响 | 应对措施 |
|------|------|------|----------|
| 文件传输丢失 | 低 | 高 | 校验和验证 + 断点续传 |
| 数据不一致 | 中 | 中 | 版本控制 + 冲突检测 |
| 敏感数据泄露 | 低 | 极高 | Tailscale 加密 + API 认证 |
| 存储溢出 | 中 | 中 | 定期归档 + 容量告警 |

**应对方案**:
```python
# 文件传输校验
import hashlib

def calculate_md5(filepath):
    hash_md5 = hashlib.md5()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

# 传输前后对比 MD5，不一致则重传
```

### 5.3 业务风险

| 风险 | 概率 | 影响 | 应对措施 |
|------|------|------|----------|
| 任务堆积 | 中 | 中 | 队列管理 + 优先级调度 |
| Mac mini 宕机 | 低 | 高 | 健康检查 + 自动告警 |
| 视频生成失败 | 中 | 中 | 重试机制 + 降级方案 |
| 发布失败 | 低 | 高 | 多平台独立发布 + 失败回滚 |

**应对方案**:
```python
# 任务队列管理
class TaskQueue:
    def __init__(self, max_concurrent=3):
        self.max_concurrent = max_concurrent
        self.queue = []
        self.processing = []
    
    def add_task(self, task):
        if len(self.processing) < self.max_concurrent:
            self.processing.append(task)
            return True
        else:
            self.queue.append(task)
            return False
    
    def on_task_complete(self, task):
        self.processing.remove(task)
        if self.queue:
            next_task = self.queue.pop(0)
            self.processing.append(next_task)
```

### 5.4 安全风险

| 风险 | 概率 | 影响 | 应对措施 |
|------|------|------|----------|
| API Key 泄露 | 低 | 高 | 定期轮换 + 环境变量存储 |
| 未授权访问 | 低 | 高 | JWT 认证 + IP 白名单 |
| 中间人攻击 | 极低 | 高 | TLS 加密 + 证书验证 |
| 飞书 Webhook 泄露 | 低 | 中 | Webhook 保密 + 签名验证 |

---

## 6. 架构图

### 6.1 整体架构

```
┌────────────────────────────────────────────────────────────────────────┐
│                            阿里云 VPS (超梦)                            │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                      OpenClaw 主实例                              │  │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐                │  │
│  │  │  承道   │ │  译文   │ │  棱镜   │ │  画语   │                │  │
│  │  └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘                │  │
│  │       └───────────┴───────────┴───────────┘                      │  │
│  │                            │                                     │  │
│  │                    ┌───────▼───────┐                             │  │
│  │                    │   任务编排器   │                             │  │
│  │                    └───────┬───────┘                             │  │
│  └────────────────────────────┼──────────────────────────────────────┘  │
│                               │                                         │
│         ┌─────────────────────┼─────────────────────┐                   │
│         │                     │                     │                   │
│         ▼                     ▼                     ▼                   │
│  ┌─────────────┐      ┌─────────────┐      ┌─────────────┐             │
│  │ 飞书机器人  │      │  共享存储   │      │  HTTP API   │             │
│  │  (消息)    │      │  (OSS/NAS)  │      │  (状态同步)  │             │
│  └──────┬──────┘      └──────┬──────┘      └──────┬──────┘             │
└─────────┼────────────────────┼────────────────────┼────────────────────┘
          │                    │                    │
          │     Tailscale 加密隧道 (100.x.x.x)       │
          │                    │                    │
┌─────────┼────────────────────┼────────────────────┼────────────────────┐
│         ▼                    ▼                    ▼                    │
│  ┌─────────────┐      ┌─────────────┐      ┌─────────────┐             │
│  │ 消息接收器  │      │  存储同步   │      │  API Server │             │
│  └──────┬──────┘      └──────┬──────┘      └──────┬──────┘             │
│         │                    │                    │                    │
│         └────────────────────┼────────────────────┘                    │
│                              │                                         │
│  ┌───────────────────────────▼──────────────────────────────────────┐  │
│  │                    Mac mini OpenClaw 副实例                       │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐               │  │
│  │  │  视频生成   │  │  视频剪辑   │  │  发布管理   │               │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘               │  │
│  └──────────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────────┘
```

### 6.2 数据流

```
1. 任务创建流:
   用户 → 超梦 → 承道/译文/棱镜/画语 → 产出物打包 → 飞书通知 → Mac mini

2. 文件传输流:
   超梦共享存储 → rsync/OSS 同步 → Mac mini 本地存储 → 视频处理

3. 状态同步流:
   Mac mini → HTTP API → 超梦任务状态机 → 飞书通知 → 用户

4. 发布结果流:
   Mac mini 发布 → 收集各平台数据 → 生成报告 → 飞书通知 → 超梦归档
```

---

## 7. 运维监控

### 7.1 健康检查端点

```yaml
# 超梦侧
GET /health
{
    "status": "healthy",
    "components": {
        "tailscale": "connected",
        "feishu_bot": "ok",
        "storage": "ok",
        "sub_agents": ["chengdao:ok", "yiwen:ok", "lengjing:ok", "huayu:ok"]
    }
}

# Mac mini 侧
GET /health
{
    "status": "healthy",
    "components": {
        "tailscale": "connected",
        "feishu_bot": "ok",
        "storage_sync": "ok",
        "video_tools": ["runway:ok", "capcut:ok", "ffmpeg:ok"]
    }
}
```

### 7.2 监控指标

```prometheus
# 网络指标
tailscale_connection_status{instance="mac-mini"}  # 1=connected, 0=disconnected
tailscale_latency_seconds{instance="mac-mini"}    # 延迟

# 任务指标
tasks_total{status="pending"}                     # 待处理任务数
tasks_total{status="processing"}                  # 处理中任务数
tasks_total{status="completed"}                   # 已完成任务数
task_duration_seconds{task_type="video"}          # 任务耗时

# 资源指标
storage_used_bytes                                # 存储使用量
cpu_usage_percent                                 # CPU 使用率
memory_usage_percent                              # 内存使用率
```

### 7.3 告警规则

```yaml
# Prometheus Alertmanager 配置
groups:
  - name: multi-instance-alerts
    rules:
      - alert: TailscaleDisconnected
        expr: tailscale_connection_status == 0
        for: 5m
        annotations:
          summary: "Tailscale 连接中断"
      
      - alert: TaskQueueBacklog
        expr: tasks_total{status="pending"} > 10
        for: 30m
        annotations:
          summary: "任务队列积压"
      
      - alert: StorageNearFull
        expr: storage_used_bytes / storage_total_bytes > 0.9
        for: 1h
        annotations:
          summary: "存储空间不足"
```

---

## 8. 附录

### 8.1 配置文件模板

#### Tailscale 配置 (/etc/default/tailscale)
```bash
TAILSCALE_STATE_DIR="/var/lib/tailscale"
TAILSCALE_LOG_DIR="/var/log/tailscale"
```

#### 超梦侧应用配置 (config.yaml)
```yaml
instance:
  id: "chaomeng-aliyun"
  role: "controller"

network:
  tailscale:
    enabled: true
    expected_ip: "100.x.x.x"

communication:
  feishu:
    webhook_url: "https://open.feishu.cn/open-apis/bot/v2/hook/xxx"
    app_id: "cli_xxxxx"
    app_secret: "xxxxx"
  
  api:
    port: 8443
    tls_cert: "/etc/ssl/certs/chaomeng.crt"
    tls_key: "/etc/ssl/private/chaomeng.key"
    jwt_secret: "${JWT_SECRET}"

storage:
  type: "oss"
  bucket: "chaomeng-workspace"
  endpoint: "oss-cn-hangzhou.aliyuncs.com"
  sync_path: "/shared-workspace"
```

#### Mac mini 侧应用配置 (config.yaml)
```yaml
instance:
  id: "macmini-local"
  role: "video-producer"

network:
  tailscale:
    enabled: true
    expected_ip: "100.y.y.y"

communication:
  feishu:
    webhook_url: "https://open.feishu.cn/open-apis/bot/v2/hook/yyy"
  
  api:
    port: 8443
    jwt_secret: "${JWT_SECRET}"
    chaomeng_ip: "100.x.x.x"

storage:
  type: "local"
  sync_path: "/Volumes/Workspace/shared-workspace"
  oss_sync:
    enabled: true
    bucket: "chaomeng-workspace"

video_tools:
  runway:
    api_key: "${RUNWAY_API_KEY}"
  pika:
    api_key: "${PIKA_API_KEY}"
  capcut:
    enabled: true
```

### 8.2 常用命令速查

```bash
# Tailscale 状态检查
tailscale status
tailscale ip
tailscale ping <target-ip>

# 服务管理
sudo systemctl status tailscaled
sudo systemctl restart tailscaled

# 存储同步
rsync -avz /source/ user@<tailscale-ip>:/dest/
ossutil sync oss://bucket/path /local/path

# API 测试
curl -H "Authorization: Bearer <token>" https://<tailscale-ip>:8443/api/v1/health

# 日志查看
journalctl -u tailscaled -f
tail -f /var/log/chaomeng/app.log
```

### 8.3 故障排查流程

```
1. 网络连通性问题
   → 检查 Tailscale 状态 (tailscale status)
   → 检查防火墙规则
   → 测试 ping/nc 连通性
   → 检查 DERP 中继状态

2. 消息投递失败
   → 检查飞书机器人 Webhook 状态
   → 验证消息格式
   → 查看应用日志

3. 文件同步异常
   → 检查存储空间
   → 验证权限配置
   → 手动执行同步测试

4. API 调用失败
   → 验证 JWT Token
   → 检查证书有效性
   → 查看 API 日志
```

---

## 9. 总结

本方案采用 **Tailscale 组网 + 飞书机器人消息 + 共享存储 + HTTP API** 的混合架构，实现阿里云超梦与本地 Mac mini 的高效协同。

**核心优势**:
1. ✅ 网络层：Tailscale 提供稳定加密连接，NAT 穿透成功率高
2. ✅ 消息层：飞书机器人提供可靠通知和人工监督能力
3. ✅ 存储层：共享存储支持大文件传输和断点续传
4. ✅ API 层：HTTP API 支持实时状态同步和精细控制
5. ✅ 安全层：多重认证 (JWT + IP 白名单 + TLS 加密)

**实施周期**: 10-14 天  
**风险等级**: 中 (主要风险为网络稳定性，已有充分应对措施)  
**推荐优先级**: 高 (可显著提升视频生产效率和质量)

---

*文档结束*
