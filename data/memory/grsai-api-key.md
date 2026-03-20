# GRS AI API Key 配置

## ✅ API Key 已验证

**Key**: `sk-10eee66de80245e78277514e88a67401`  
**状态**: ✅ 有效  
**测试时间**: 2026-03-16 15:36  
**测试结果**: 成功提交任务，API 响应正常

---

## 🔧 配置方式

### 方式 1: 环境变量（推荐）

```bash
# 添加到 ~/.bashrc 或 ~/.zshrc
export GRS_API_KEY="sk-10eee66de80245e78277514e88a67401"

# 立即生效
source ~/.bashrc
```

### 方式 2: 脚本内配置

已配置在 `/root/.openclaw/workspace/scripts/nano-banana-generator.py`:

```python
GRS_API_KEY = "sk-10eee66de80245e78277514e88a67401"
```

### 方式 3: 配置文件

创建 `.env` 文件：

```bash
# /root/.openclaw/workspace/.env
GRS_API_KEY=sk-10eee66de80245e78277514e88a67401
GRS_API_HOST=https://grsai.dakka.com.cn
```

---

## 🧪 测试结果

### 测试 1: 提交任务

```bash
curl -X POST "https://grsai.dakka.com.cn/v1/draw/nano-banana" \
  -H "Authorization: Bearer sk-10eee66de80245e78277514e88a67401" \
  -d '{
    "model": "nano-banana-2",
    "prompt": "一只可爱的猫咪，卡通风格，高质量",
    "aspectRatio": "1:1",
    "imageSize": "1K",
    "webHook": "-1"
  }'
```

**响应**:
```json
{
  "code": 0,
  "data": {
    "id": "2-6efa0278-eed8-4ed9-b3a3-3b375281dece"
  },
  "msg": "success"
}
```

### 测试 2: 查询进度

```bash
curl -X POST "https://grsai.dakka.com.cn/v1/draw/result" \
  -H "Authorization: Bearer sk-10eee66de80245e78277514e88a67401" \
  -d '{"id": "2-6efa0278-eed8-4ed9-b3a3-3b375281dece"}'
```

**响应**:
```json
{
  "code": 0,
  "data": {
    "id": "2-6efa0278-eed8-4ed9-b3a3-3b375281dece",
    "status": "running",
    "progress": 10,
    "results": null
  },
  "msg": "success"
}
```

---

## 🚀 立即使用

### 测试脚本

```bash
cd /root/.openclaw/workspace
python3 scripts/nano-banana-generator.py test
```

### 启动服务

```bash
# 后台运行
nohup python3 scripts/nano-banana-generator.py > /tmp/nano-banana.log 2>&1 &

# 查看状态
ps aux | grep nano-banana

# 查看日志
tail -f /tmp/nano-banana.log
```

### 停止服务

```bash
# 查找进程
ps aux | grep nano-banana

# 停止
kill <PID>
```

---

## 📊 API 配额查询

登录控制台查看积分余额：
https://grsai.ai/zh/dashboard/user-info

---

## ⚠️ 安全提示

1. **不要公开 API Key**: 不要提交到 Git 仓库或公开场合
2. **定期更换**: 建议定期更换 API Key
3. **监控使用**: 定期查看消耗日志
4. **权限最小化**: 仅授予必要的权限

---

## 🔗 相关文档

- [Nano Banana API 文档](./grsai-docs/nano-banana-api.md)
- [生成工具脚本](../scripts/nano-banana-generator.py)
- [知识库索引](./grsai-docs/README.md)

---

*配置时间：2026-03-16 15:36*
