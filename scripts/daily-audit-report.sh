#!/bin/bash
# 每日审计报告生成脚本
# 用法：./daily-audit-report.sh [日期]

AUDIT_FILE="$HOME/.openclaw/workspace/audit.md"
REPORT_DIR="$HOME/.openclaw/workspace/reports"
DATE="${1:-$(date +%Y-%m-%d)}"
YESTERDAY=$(date -d "$DATE -1 day" +%Y-%m-%d 2>/dev/null || date -v-1d -jf "%Y-%m-%d" "$DATE" +%Y-%m-%d 2>/dev/null)

# 创建报告目录
mkdir -p "$REPORT_DIR"

REPORT_FILE="$REPORT_DIR/daily-audit-$YESTERDAY.md"

echo "# 每日审计报告" > "$REPORT_FILE"
echo "" >> "$REPORT_FILE"
echo "**报告日期**: $(date +%Y-%m-%d %H:%M)" >> "$REPORT_FILE"
echo "**审计日期**: $YESTERDAY" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"
echo "---" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

# 提取指定日期的日志
echo "## 操作摘要" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

# 统计操作数量
TOTAL_OPS=$(grep -c "### $YESTERDAY" "$AUDIT_FILE" 2>/dev/null || echo "0")
echo "- **总操作数**: $TOTAL_OPS" >> "$REPORT_FILE"

# 按操作者统计
echo "" >> "$REPORT_FILE"
echo "### 按操作者统计" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"
grep -A2 "### $YESTERDAY" "$AUDIT_FILE" | grep "操作者" | sort | uniq -c | sort -rn >> "$REPORT_FILE" 2>/dev/null || echo "- 无操作记录" >> "$REPORT_FILE"

# 按操作类型统计
echo "" >> "$REPORT_FILE"
echo "### 按操作类型统计" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"
grep -A2 "### $YESTERDAY" "$AUDIT_FILE" | grep "操作类型" | sort | uniq -c | sort -rn >> "$REPORT_FILE" 2>/dev/null || echo "- 无操作记录" >> "$REPORT_FILE"

# 按结果统计
echo "" >> "$REPORT_FILE"
echo "### 按结果统计" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"
grep -A2 "### $YESTERDAY" "$AUDIT_FILE" | grep "结果" | sort | uniq -c | sort -rn >> "$REPORT_FILE" 2>/dev/null || echo "- 无操作记录" >> "$REPORT_FILE"

# 详细操作列表
echo "" >> "$REPORT_FILE"
echo "## 详细操作列表" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"
grep -A15 "### $YESTERDAY" "$AUDIT_FILE" >> "$REPORT_FILE" 2>/dev/null || echo "- 无操作记录" >> "$REPORT_FILE"

# 告警检查
echo "" >> "$REPORT_FILE"
echo "## 告警检查" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

DANGER_OPS=$(grep -c "危险操作" "$AUDIT_FILE" 2>/dev/null || echo "0")
FAILED_OPS=$(grep -c "结果：❌ 失败" "$AUDIT_FILE" 2>/dev/null || echo "0")

if [ "$DANGER_OPS" -gt 0 ]; then
    echo "- ⚠️ **发现危险操作**: $DANGER_OPS 次" >> "$REPORT_FILE"
else
    echo "- ✅ 无危险操作" >> "$REPORT_FILE"
fi

if [ "$FAILED_OPS" -gt 0 ]; then
    echo "- ⚠️ **失败操作**: $FAILED_OPS 次" >> "$REPORT_FILE"
else
    echo "- ✅ 无失败操作" >> "$REPORT_FILE"
fi

echo "" >> "$REPORT_FILE"
echo "---" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"
echo "**报告生成时间**: $(date +%Y-%m-%d %H:%M:%S)" >> "$REPORT_FILE"

echo "每日审计报告已生成：$REPORT_FILE"
