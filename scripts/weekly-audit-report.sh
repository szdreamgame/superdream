#!/bin/bash
# 每周审计报告生成脚本
# 用法：./weekly-audit-report.sh [日期]

AUDIT_FILE="$HOME/.openclaw/workspace/audit.md"
REPORT_DIR="$HOME/.openclaw/workspace/reports"
REPORT_DATE="${1:-$(date +%Y-%m-%d)}"

# 计算上周一和上周日的日期
TODAY=$(date +%Y-%m-%d)
LAST_MONDAY=$(date -d "last monday" +%Y-%m-%d 2>/dev/null || date -v-mon -jf "%Y-%m-%d" "$TODAY" +%Y-%m-%d 2>/dev/null)
LAST_SUNDAY=$(date -d "last sunday" +%Y-%m-%d 2>/dev/null || date -v-sun -jf "%Y-%m-%d" "$TODAY" +%Y-%m-%d 2>/dev/null)

# 创建报告目录
mkdir -p "$REPORT_DIR"

REPORT_FILE="$REPORT_DIR/weekly-audit-$LAST_MONDAY.md"

echo "# 每周审计报告" > "$REPORT_FILE"
echo "" >> "$REPORT_FILE"
echo "**报告生成日期**: $(date +%Y-%m-%d %H:%M)" >> "$REPORT_FILE"
echo "**审计周期**: $LAST_MONDAY 至 $LAST_SUNDAY" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"
echo "---" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

# 周统计摘要
echo "## 周统计摘要" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

# 总操作数
TOTAL_OPS=$(grep -c "### 2026-" "$AUDIT_FILE" 2>/dev/null || echo "0")
echo "- **总操作数**: $TOTAL_OPS" >> "$REPORT_FILE"

# 按操作者统计
echo "" >> "$REPORT_FILE"
echo "### 按操作者统计" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"
grep "操作者：" "$AUDIT_FILE" | sort | uniq -c | sort -rn >> "$REPORT_FILE" 2>/dev/null || echo "- 无操作记录" >> "$REPORT_FILE"

# 按操作类型统计
echo "" >> "$REPORT_FILE"
echo "### 按操作类型统计" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"
grep "操作类型：" "$AUDIT_FILE" | sort | uniq -c | sort -rn >> "$REPORT_FILE" 2>/dev/null || echo "- 无操作记录" >> "$REPORT_FILE"

# 按结果统计
echo "" >> "$REPORT_FILE"
echo "### 按结果统计" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"
grep "结果：" "$AUDIT_FILE" | sort | uniq -c | sort -rn >> "$REPORT_FILE" 2>/dev/null || echo "- 无操作记录" >> "$REPORT_FILE"

# 趋势分析
echo "" >> "$REPORT_FILE"
echo "## 趋势分析" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

# 成功率计算
SUCCESS_OPS=$(grep -c "结果：✅ 成功" "$AUDIT_FILE" 2>/dev/null || echo "0")
if [ "$TOTAL_OPS" -gt 0 ]; then
    SUCCESS_RATE=$(echo "scale=2; $SUCCESS_OPS * 100 / $TOTAL_OPS" | bc 2>/dev/null || echo "N/A")
    echo "- **成功率**: ${SUCCESS_RATE}%" >> "$REPORT_FILE"
else
    echo "- **成功率**: N/A (无操作)" >> "$REPORT_FILE"
fi

# 告警检查
echo "" >> "$REPORT_FILE"
echo "## 告警检查" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

DANGER_OPS=$(grep -c "危险操作" "$AUDIT_FILE" 2>/dev/null || echo "0")
FAILED_OPS=$(grep -c "结果：❌ 失败" "$AUDIT_FILE" 2>/dev/null || echo "0")

if [ "$DANGER_OPS" -gt 0 ]; then
    echo "- ⚠️ **危险操作**: $DANGER_OPS 次" >> "$REPORT_FILE"
    echo "  建议：审查危险操作日志，确认是否有异常行为" >> "$REPORT_FILE"
else
    echo "- ✅ 无危险操作" >> "$REPORT_FILE"
fi

if [ "$FAILED_OPS" -gt 0 ]; then
    echo "- ⚠️ **失败操作**: $FAILED_OPS 次" >> "$REPORT_FILE"
    echo "  建议：检查失败原因，修复潜在问题" >> "$REPORT_FILE"
else
    echo "- ✅ 无失败操作" >> "$REPORT_FILE"
fi

# 改进建议
echo "" >> "$REPORT_FILE"
echo "## 改进建议" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

if [ "$TOTAL_OPS" -eq 0 ]; then
    echo "- 本周无操作记录，建议检查系统是否正常运行" >> "$REPORT_FILE"
elif [ "$TOTAL_OPS" -lt 5 ]; then
    echo "- 本周操作较少 ($TOTAL_OPS 次)，系统运行平稳" >> "$REPORT_FILE"
else
    echo "- 本周操作活跃 ($TOTAL_OPS 次)，系统运行正常" >> "$REPORT_FILE"
fi

echo "" >> "$REPORT_FILE"
echo "---" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"
echo "**报告生成时间**: $(date +%Y-%m-%d %H:%M:%S)" >> "$REPORT_FILE"
echo "**下周审计**: $(date -d "+7 days" +%Y-%m-%d 2>/dev/null || date -v+7d -jf "%Y-%m-%d" "$TODAY" +%Y-%m-%d 2>/dev/null)" >> "$REPORT_FILE"

echo "每周审计报告已生成：$REPORT_FILE"
