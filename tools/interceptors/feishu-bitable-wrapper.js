/**
 * 飞书表格 API 包装器
 * 
 * 为拦截器提供飞书表格操作功能
 */

const FEISHU_APP_ID = "cli_a92e8b3399b85cd6";
const FEISHU_APP_SECRET = "tMiX2hL0wTf7ujPSK2pqnf3d3aeg8AGa";

let tenantTokenCache = null;
let tokenExpireAt = 0;

/**
 * 获取飞书 tenant_access_token
 */
async function getFeishuTenantToken() {
  const now = Date.now();
  if (tenantTokenCache && now < tokenExpireAt) {
    return tenantTokenCache;
  }
  
  try {
    const response = await fetch("https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        app_id: FEISHU_APP_ID,
        app_secret: FEISHU_APP_SECRET
      })
    });
    
    const result = await response.json();
    if (result.code === 0) {
      tenantTokenCache = result.tenant_access_token;
      tokenExpireAt = now + (7200 * 1000); // 2 小时有效期
      return tenantTokenCache;
    }
    throw new Error(`获取 Token 失败：${result.msg}`);
  } catch (error) {
    console.error("[飞书表格] 获取 Token 失败:", error);
    throw error;
  }
}

/**
 * 创建表格记录
 */
export async function createBitableRecord({ app_token, table_id, fields }) {
  try {
    const token = await getFeishuTenantToken();
    const url = `https://open.feishu.cn/open-apis/bitable/v1/apps/${app_token}/tables/${table_id}/records`;
    
    const response = await fetch(url, {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${token}`,
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ fields })
    });
    
    const result = await response.json();
    if (result.code === 0) {
      return result.data?.record_id;
    }
    console.error("[飞书表格] 创建记录失败:", result);
    return null;
  } catch (error) {
    console.error("[飞书表格] 创建记录错误:", error);
    return null;
  }
}

/**
 * 更新表格记录
 */
export async function updateBitableRecord({ app_token, table_id, record_id, fields }) {
  try {
    const token = await getFeishuTenantToken();
    const url = `https://open.feishu.cn/open-apis/bitable/v1/apps/${app_token}/tables/${table_id}/records/${record_id}`;
    
    const response = await fetch(url, {
      method: "PUT",
      headers: {
        "Authorization": `Bearer ${token}`,
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ fields })
    });
    
    const result = await response.json();
    if (result.code === 0) {
      return true;
    }
    console.error("[飞书表格] 更新记录失败:", result);
    return false;
  } catch (error) {
    console.error("[飞书表格] 更新记录错误:", error);
    return false;
  }
}

/**
 * 查询表格记录
 */
export async function getBitableRecords({ app_token, table_id, filter }) {
  try {
    const token = await getFeishuTenantToken();
    let url = `https://open.feishu.cn/open-apis/bitable/v1/apps/${app_token}/tables/${table_id}/records`;
    
    if (filter) {
      url += `?filter=${encodeURIComponent(JSON.stringify(filter))}`;
    }
    
    const response = await fetch(url, {
      headers: { "Authorization": `Bearer ${token}` }
    });
    
    const result = await response.json();
    if (result.code === 0) {
      return result.data?.items || [];
    }
    console.error("[飞书表格] 查询记录失败:", result);
    return [];
  } catch (error) {
    console.error("[飞书表格] 查询记录错误:", error);
    return [];
  }
}

/**
 * 兼容性导出（CommonJS）
 */
if (typeof module !== "undefined" && module.exports) {
  module.exports = {
    createBitableRecord,
    updateBitableRecord,
    getBitableRecords,
    getFeishuTenantToken
  };
}
