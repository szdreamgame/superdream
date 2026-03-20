# 飞书应用配置

## ✅ 应用信息

**应用名称**: feishubot  
**App ID**: `cli_a92e8b3399b85cd6`  
**App Secret**: `tMiX2hL0wTf7ujPSK2pqnf3d3aeg8AGa`  
**状态**: ✅ 已配置

---

## 🔧 配置位置

配置文件：`/root/.openclaw/openclaw.json`

```json
{
  "channels": {
    "feishu": {
      "accounts": {
        "feishubot": {
          "appId": "cli_a92e8b3399b85cd6",
          "appSecret": "tMiX2hL0wTf7ujPSK2pqnf3d3aeg8AGa",
          "enabled": true,
          "domain": "feishu"
        }
      }
    }
  }
}
```

---

## 🚀 环境变量配置

```bash
export FEISHU_APP_ID="cli_a92e8b3399b85cd6"
export FEISHU_APP_SECRET="tMiX2hL0wTf7ujPSK2pqnf3d3aeg8AGa"
```

---

## 📋 已授予权限

总共 251 个权限，包括：

### 关键权限
- ✅ `drive:file:upload` - 上传文件
- ✅ `drive:file:download` - 下载文件
- ✅ `base:record:update` - 更新记录
- ✅ `base:record:retrieve` - 读取记录
- ✅ `base:record:create` - 创建记录
- ✅ `base:table:read` - 读取表格
- ✅ `base:app:read` - 读取应用

完整权限列表见：`memory/grsai-app-scopes.md`

---

## 🎯 使用场景

### Nano Banana 2 图片生成

1. 轮询表格获取"待生成图片"记录
2. 调用 GRS AI API 生成图片
3. 下载图片并上传到飞书云文档
4. 更新表格记录

### API 调用示例

```python
# 获取 Tenant Access Token
def get_feishu_token():
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    payload = {
        "app_id": "cli_a92e8b3399b85cd6",
        "app_secret": "tMiX2hL0wTf7ujPSK2pqnf3d3aeg8AGa"
    }
    response = requests.post(url, json=payload)
    return response.json()['tenant_access_token']
```

---

## ⚠️ 安全提示

1. **不要泄露 App Secret**
2. **定期更换密钥**
3. **监控 API 使用量**

---

*配置时间：2026-03-16 15:42*
