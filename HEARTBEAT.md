# HEARTBEAT.md

# 定期检查任务（每 4-6 小时执行一次）

## Gateway 健康检查
- [ ] Gateway 进程数量 = 1（`ps aux | grep openclaw-gateway`）
- [ ] 无异常进程占用 CPU

## 智能体配置检查
- [ ] 承道模型：foxcode-ultra/claude-opus-4-6
- [ ] 棱镜路由：oc_ac0b758330a732a46d8a6ca9f3985260
- [ ] 译文路由：oc_95a9882e1aca9546c1930b2d27660a6a
- [ ] 画语路由：oc_f22ffe36d557729c0d77f8b11c74e0bd

## 发现异常时
1. 立即清理异常进程
2. 记录到 memory/YYYY-MM-DD.md
3. 向潘总汇报
