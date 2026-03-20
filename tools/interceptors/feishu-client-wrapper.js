/**
 * 飞书客户端包装器
 * 
 * 为拦截器提供飞书 API 客户端创建功能
 */

/**
 * 创建飞书客户端
 * @param {Object} account - 飞书账号配置
 * @returns {Object} 飞书客户端
 */
export function createFeishuClient(account) {
  // 这里需要调用 OpenClaw 内部的飞书客户端创建逻辑
  // 由于是在插件外部，我们通过 runtime API 来访问
  
  const runtime = globalThis.__openclaw_runtime__;
  
  if (!runtime) {
    throw new Error("OpenClaw runtime not available");
  }
  
  // 使用 OpenClaw 提供的飞书客户端工厂
  return runtime.createFeishuClient(account);
}

/**
 * 兼容性导出（CommonJS）
 */
if (typeof module !== "undefined" && module.exports) {
  module.exports = { createFeishuClient };
}
