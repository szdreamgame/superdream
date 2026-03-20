# Nano Banana 2 图片生成服务 - 完整部署指南

> 🎨 基于 GRS AI API + 飞书多维表格的自动化图片生成服务

---

## 📋 功能概述

**自动化流程**：
1. 监听飞书表格状态变化
2. 当记录状态为"待生成图片"时自动触发
3. 读取"修改后角色"和"修改后场景"字段
4. 调用 Nano Banana 2 API 生成图片
5. 下载图片并上传到飞书云文档
6. 回写图片链接到表格
7. 更新状态为"图片已完成"

---

## 🔧 配置信息

### 1. GRS AI API 配置

| 项目 | 值 | 状态 |
|------|-----|------|
| API Host | `https://grsai.dakka.com.cn` | ✅ |
| API Key | `sk-10eee66de80245e78277514e88a67401` | ✅ 已验证 |
| 模型 | `nano-banana-2` | ✅ |

### 2. 飞书应用配置

| 项目 | 值 | 状态 |
|------|-----|------|
| App ID | `cli_a92e8b3399b85cd6` | ✅ |
| App Secret | `tMiX2hL0wTf7ujPSK2pqnf3d3aeg8AGa` | ✅ |
| 表格 Token | `GHrubiTjnayG4fsWP2IcJIotnfc` | ✅ |
| 表格 ID | `tbl8ik4qLltAlXvp` | ✅ |

### 3. 已授予权限

✅ 所有必需权限已授予（251 个权限）：
- `drive:file:upload` - 上传文件
- `drive:file:download` - 下载文件
- `base:record:update` - 更新记录
- `base:record:retrieve` - 读取记录
- `base:record:create` - 创建记录

---

## 📂 文件结构

```
/root/.openclaw/workspace/
├── scripts/
│   ├── nano-banana-generator-full.py    # 完整版生成脚本
│   ├── nano-banana-generator.py         # 简化版生成脚本
│   └── grsai-doc-crawler.py             # 文档爬虫
│
└── memory/
    ├── grsai-docs/                      # GRS AI 文档库
    │   ├── README.md
    │   ├── nano-banana-api.md
    │   └── ...
    ├── grsai-api-key.md                 # API Key 配置
    └── feishu-app-config.md             # 飞书应用配置
```

---

## 🚀 启动服务

### 方式 1: 直接运行

```bash
cd /root/.openclaw/workspace

# 测试模式（生成一张测试图片）
python3 scripts/nano-banana-generator-full.py test

# 正式运行（后台服务）
nohup python3 scripts/nano-banana-generator-full.py > /tmp/nano-banana.log 2>&1 &
```

### 方式 2: Systemd 服务（推荐生产环境）

创建服务文件：

```bash
sudo tee /etc/systemd/system/nano-banana-generator.service > /dev/null <<'EOF'
[Unit]
Description=Nano Banana 2 Image Generator
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/.openclaw/workspace
ExecStart=/usr/bin/python3 /root/.openclaw/workspace/scripts/nano-banana-generator-full.py
Restart=always
RestartSec=10
StandardOutput=append:/var/log/nano-banana.log
StandardError=append:/var/log/nano-banana.error.log

[Install]
WantedBy=multi-user.target
EOF

# 启动服务
sudo systemctl daemon-reload
sudo systemctl enable nano-banana-generator
sudo systemctl start nano-banana-generator

# 查看状态
sudo systemctl status nano-banana-generator

# 查看日志
sudo journalctl -u nano-banana-generator -f
```

---

## 📊 监控和维护

### 查看运行状态

```bash
# 检查进程
ps aux | grep nano-banana

# 查看日志
tail -f /tmp/nano-banana.log

# 或者使用 systemd
sudo journalctl -u nano-banana-generator -n 50 -f
```

### 停止服务

```bash
# 找到进程 ID
ps aux | grep nano-banana

# 停止
kill <PID>

# 或者使用 systemd
sudo systemctl stop nano-banana-generator
```

### 重启服务

```bash
# systemd
sudo systemctl restart nano-banana-generator

# 或者直接运行
pkill -f nano-banana-generator-full.py
nohup python3 scripts/nano-banana-generator-full.py > /tmp/nano-banana.log 2>&1 &
```

---

## 📋 表格字段说明

### 输入字段（需要填写）

| 字段名 | 类型 | 说明 | 示例 |
|--------|------|------|------|
| 修改后角色 | 长文本 | 角色描述 | "车主：女，25 岁，长发，现代休闲装" |
| 修改后场景 | 长文本 | 场景描述 | "城市街头路边，停放着私家车，周围有行人" |
| 状态 | 单选 | 触发状态 | "待生成图片" |

### 输出字段（自动生成）

| 字段名 | 类型 | 说明 |
|--------|------|------|
| 角色设定图 | 附件/URL | 生成的角色图片链接 |
| 场景设定图 | 附件/URL | 生成的场景图片链接 |
| 图片生成状态 | 单选 | 生成状态（生成中/已完成/失败） |
| 图片生成时间 | 日期 | 完成时间 |

---

## 🧪 测试流程

### 1. 创建测试记录

打开表格：https://szdreamgame.feishu.cn/base/GHrubiTjnayG4fsWP2IcJIotnfc

添加新记录：
- **译文评审管理**: "测试记录"
- **修改后角色**: "一位 25 岁的女性，长发，穿着现代休闲装"
- **修改后场景**: "城市街头，路边停放着私家车，阳光明媚"
- **状态**: "待生成图片"

### 2. 等待服务处理

服务每 60 秒轮询一次，通常 1-2 分钟内完成。

### 3. 查看结果

刷新表格，检查：
- ✅ 图片链接已生成
- ✅ 状态变为"图片已完成"
- ✅ 图片生成时间已填写

---

## ⚠️ 注意事项

### 1. 图片 URL 有效期

GRS AI 生成的图片 URL 有效期为 **2 小时**，服务会自动下载并上传到飞书云文档，确保永久保存。

### 2. API 配额

查看积分余额：https://grsai.ai/zh/dashboard/user-info

每次生成约消耗 7-15 积分（取决于尺寸和模型）。

### 3. 错误处理

服务会自动重试：
- API 调用失败：重试 30 次，间隔 5 秒
- 上传失败：记录为"失败"状态，可手动重试

### 4. 并发处理

服务按顺序处理记录，避免同时提交过多任务导致 API 限流。

---

## 🔧 故障排查

### 问题 1: 服务未启动

```bash
# 检查进程
ps aux | grep nano-banana

# 手动启动
python3 scripts/nano-banana-generator-full.py
```

### 问题 2: API Key 无效

检查日志：
```bash
tail -f /tmp/nano-banana.log | grep "API"
```

如果看到 "401 Unauthorized"，检查 API Key 是否正确。

### 问题 3: 飞书 Token 获取失败

检查 App ID 和 Secret：
```bash
cat /root/.openclaw/openclaw.json | grep -A2 "feishubot"
```

### 问题 4: 图片上传失败

检查飞书权限：
```bash
# 查看权限列表
feishu_app_scopes | grep "drive:file"
```

---

## 📈 性能优化

### 调整轮询间隔

编辑脚本：
```python
POLL_INTERVAL = 60  # 秒，默认 60 秒
```

- 缩短间隔：更快响应，更多 API 调用
- 延长间隔：减少 API 调用，响应较慢

### 批量处理

修改 `fetch_pending_records()` 函数，增加 `page_size` 参数。

---

## 📝 更新日志

- **2026-03-16**: 初始版本，完整飞书集成
- **2026-03-16**: API Key 验证通过
- **2026-03-16**: 飞书权限确认（251 个权限）

---

## 🔗 相关文档

- [GRS AI 知识库](./grsai-docs/README.md)
- [Nano Banana API 文档](./grsai-docs/nano-banana-api.md)
- [飞书应用配置](./feishu-app-config.md)
- [API Key 配置](./grsai-api-key.md)

---

*文档创建时间：2026-03-16 15:42*
