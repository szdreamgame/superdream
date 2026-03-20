# 多实例协同方案 - 执行摘要

## 📌 方案概述

实现**阿里云超梦 (总控)**与**本地 Mac mini(视频生产)**的安全高效协同，通过 Tailscale 组网建立加密通道，结合飞书机器人、共享存储和 API 服务实现任务流转。

---

## 🏗️ 核心架构

```
超梦 (阿里云 VPS)
├── 承道/译文/棱镜/画语 (内容生产)
├── 任务编排器
└── 通信层
    ├── 飞书机器人 (消息通知)
    ├── OSS 共享存储 (文件传输)
    └── HTTP API (状态同步)
        │
        ═══════ Tailscale 加密隧道 ═══════
        │
Mac mini (本地)
├── 视频生成 (Runway/Pika)
├── 视频剪辑 (CapCut/FFmpeg)
└── 发布管理 (多平台分发)
```

---

## ✅ 推荐方案

| 组件 | 选择 | 理由 |
|------|------|------|
| **组网** | Tailscale | 配置简单、NAT 穿透优秀、免费额度充足 |
| **消息** | 飞书机器人 | 已有基础设施、可靠投递、可人工监督 |
| **存储** | 阿里云 OSS + ossutil | 大文件支持、断点续传、成本低 |
| **API** | HTTPS + JWT | 实时同步、细粒度控制、安全可靠 |
| **认证** | JWT Token + IP 白名单 | 双重验证、定期轮换 |

---

## 📅 实施计划 (10-14 天)

| 阶段 | 时间 | 关键任务 | 交付物 |
|------|------|----------|--------|
| **1. 网络搭建** | Day 1 | Tailscale 安装配置、连通性测试 | 加密隧道建立 |
| **2. 通信基建** | Day 2-3 | 飞书机器人配置、消息模块开发 | 消息可收发 |
| **3. 存储配置** | Day 3-4 | OSS 创建、同步脚本、大文件测试 | 文件可同步 |
| **4. API 开发** | Day 4-7 | 接口实现、JWT 认证、HTTPS 配置 | API 可调用 |
| **5. 工作流集成** | Day 7-10 | 子智能体集成、视频工具对接 | 端到端流程 |
| **6. 监控优化** | Day 10-14 | 日志、告警、性能测试、文档 | 可稳定运行 |

---

## ⚠️ 关键风险与应对

| 风险 | 影响 | 应对措施 |
|------|------|----------|
| Tailscale 中断 | 高 | 自动重连 + 备用 ZeroTier |
| 文件传输丢失 | 高 | MD5 校验 + 断点续传 |
| Mac mini 宕机 | 高 | 健康检查 + 飞书告警 |
| API 认证泄露 | 高 | JWT 定期轮换 + 环境变量 |
| 任务堆积 | 中 | 队列管理 + 优先级调度 |

---

## 📊 验收标准

**功能**: 任务下发 ✓ 文件传输 ✓ 状态同步 ✓ 视频发布 ✓  
**性能**: 延迟<100ms ✓ 传输>10MB/s ✓ API<500ms ✓ 成功率>99% ✓  
**稳定**: 7 天无故障 ✓ 自动重连 ✓ 自动恢复 ✓  
**安全**: 通信加密 ✓ API 认证 ✓ 访问控制 ✓  

---

## 🛠️ 快速启动命令

```bash
# ===== 阿里云 VPS =====
# 安装 Tailscale
curl -fsSL https://tailscale.com/install.sh | sh
sudo systemctl enable --now tailscaled
sudo tailscale up
# 访问输出 URL 完成认证

# 配置安全组 (阿里云控制台)
# UDP 41641 允许 0.0.0.0/0

# ===== Mac mini =====
# 安装 Tailscale
brew install --cask tailscale
tailscale up
# 访问输出 URL 完成认证

# ===== 连通性测试 =====
# 互相 ping Tailscale IP
ping 100.x.x.x
```

---

## 📁 输出文档

1. **multi-instance-collaboration-plan.md** - 完整规划文档 (20KB)
   - 网络方案详细对比
   - 工作流程图
   - 技术实施路径
   - 风险评估

2. **multi-instance-workflow-diagrams.md** - 流程图集合 (5KB)
   - Mermaid 流程图
   - 状态流转图
   - 通信时序图
   - 部署架构图

3. **implementation-checklist.md** - 实施检查清单 (8KB)
   - 6 阶段详细任务
   - 验收标准
   - 命令速查

4. **EXECUTIVE-SUMMARY.md** - 本文档

---

## 🎯 下一步行动

1. **立即执行**: 阶段 1 (网络搭建) - 预计 2 小时
2. **本周完成**: 阶段 2-3 (通信 + 存储) - 预计 2 天
3. **下周完成**: 阶段 4-5 (API+ 工作流) - 预计 5 天
4. **下周末**: 阶段 6 (监控优化) - 预计 2 天

**关键决策点**:
- [ ] 确认 Tailscale 账号注册
- [ ] 确认 OSS Bucket 命名
- [ ] 确认飞书机器人配置人
- [ ] 确认 API 开发负责人

---

## 📞 支持资源

- Tailscale 文档：https://tailscale.com/kb
- 飞书开放平台：https://open.feishu.cn/document
- 阿里云 OSS: https://help.aliyun.com/product/31815.html
- 项目文档：`/root/.openclaw/workspace/multi-instance-*.md`

---

*创建时间：2026-03-19*  
*版本：v1.0*  
*状态：待实施*
