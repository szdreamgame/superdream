#!/bin/bash
# 审计日志查询工具
# 用法：./audit-query.sh [选项]

AUDIT_FILE="$HOME/.openclaw/workspace/audit.md"

usage() {
    echo "用法：audit-query [选项]"
    echo ""
    echo "选项:"
    echo "  -d, --date <日期>     按日期查询 (YYYY-MM-DD)"
    echo "  -o, --operator <名字> 按操作者查询"
    echo "  -t, --type <类型>     按操作类型查询"
    echo "  -r, --result <结果>   按结果查询 (成功/失败/部分成功)"
    echo "  -s, --since <日期>    查询指定日期之后的日志"
    echo "  -u, --until <日期>    查询指定日期之前的日志"
    echo "  -l, --limit <数量>    限制返回结果数量"
    echo "  -h, --help            显示帮助信息"
    echo ""
    echo "示例:"
    echo "  audit-query -d 2026-03-21"
    echo "  audit-query -o 超梦 -t 配置变更"
    echo "  audit-query --since 2026-03-20 --limit 10"
}

# 解析参数
while [[ $# -gt 0 ]]; do
    case $1 in
        -d|--date) DATE="$2"; shift 2 ;;
        -o|--operator) OPERATOR="$2"; shift 2 ;;
        -t|--type) TYPE="$2"; shift 2 ;;
        -r|--result) RESULT="$2"; shift 2 ;;
        -s|--since) SINCE="$2"; shift 2 ;;
        -u|--until) UNTIL="$2"; shift 2 ;;
        -l|--limit) LIMIT="$2"; shift 2 ;;
        -h|--help) usage; exit 0 ;;
        *) echo "未知选项：$1"; usage; exit 1 ;;
    esac
done

# 检查文件是否存在
if [ ! -f "$AUDIT_FILE" ]; then
    echo "错误：审计日志文件不存在：$AUDIT_FILE"
    exit 1
fi

# 执行查询
QUERY_RESULT=$(cat "$AUDIT_FILE")

if [ -n "$DATE" ]; then
    QUERY_RESULT=$(grep -A15 "### $DATE" "$AUDIT_FILE" | head -20)
fi

if [ -n "$OPERATOR" ]; then
    if [ -n "$DATE" ]; then
        QUERY_RESULT=$(echo "$QUERY_RESULT" | grep -B2 -A10 "操作者：$OPERATOR")
    else
        QUERY_RESULT=$(grep -B2 -A10 "操作者：$OPERATOR" "$AUDIT_FILE")
    fi
fi

if [ -n "$TYPE" ]; then
    QUERY_RESULT=$(echo "$QUERY_RESULT" | grep -B2 -A10 "操作类型：$TYPE")
fi

if [ -n "$RESULT" ]; then
    case $RESULT in
        成功) QUERY_RESULT=$(echo "$QUERY_RESULT" | grep -B2 -A10 "结果：✅ 成功") ;;
        失败) QUERY_RESULT=$(echo "$QUERY_RESULT" | grep -B2 -A10 "结果：❌ 失败") ;;
        部分成功) QUERY_RESULT=$(echo "$QUERY_RESULT" | grep -B2 -A10 "结果：⚠️ 部分成功") ;;
    esac
fi

# 输出结果
if [ -n "$LIMIT" ]; then
    echo "$QUERY_RESULT" | head -n "$LIMIT"
else
    echo "$QUERY_RESULT"
fi
