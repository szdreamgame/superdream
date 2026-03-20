#!/bin/bash
# NAS 挂载脚本 - 阿里云服务器
# 使用前请配置下方的 NAS_CONFIG 部分

set -e

NAS_CONFIG() {
    # ===== 请配置以下信息 =====
    NAS_IP="100.65.98.22"
    SHARE_NAME="<请替换为实际共享名称>"
    MOUNT_POINT="/mnt/nas"
    
    # SMB 认证 (如使用 NFS 请注释掉)
    SMB_USERNAME="<请替换为用户名>"
    SMB_PASSWORD="<请替换为密码>"
    
    # 协议选择：smb 或 nfs
    PROTOCOL="smb"
    # ===== 配置结束 =====
}

load_config() {
    NAS_CONFIG
}

mount_nas() {
    load_config
    
    echo "准备挂载 NAS..."
    echo "NAS IP: $NAS_IP"
    echo "共享名称：$SHARE_NAME"
    echo "挂载点：$MOUNT_POINT"
    echo "协议：$PROTOCOL"
    
    # 创建挂载点
    mkdir -p "$MOUNT_POINT"
    
    # 创建 openclaw 目录结构
    mkdir -p "$MOUNT_POINT/openclaw"/{workspace,logs/{aliyun,macmini},backups,config,media}
    
    if [ "$PROTOCOL" = "smb" ]; then
        echo "使用 SMB 协议挂载..."
        # 创建凭证文件
        CRED_FILE="/root/.smbcredentials"
        cat > "$CRED_FILE" <<EOF
username=$SMB_USERNAME
password=$SMB_PASSWORD
EOF
        chmod 600 "$CRED_FILE"
        
        # 挂载
        mount.cifs "//$NAS_IP/$SHARE_NAME" "$MOUNT_POINT" \
            -o credentials=$CRED_FILE,vers=3.0,iocharset=utf8,file_mode=0777,dir_mode=0777,_netdev
        
    elif [ "$PROTOCOL" = "nfs" ]; then
        echo "使用 NFS 协议挂载..."
        mount -t nfs "$NAS_IP:/volume1/$SHARE_NAME" "$MOUNT_POINT"
    else
        echo "错误：未知协议 $PROTOCOL"
        exit 1
    fi
    
    # 验证挂载
    if mountpoint -q "$MOUNT_POINT"; then
        echo "✅ NAS 挂载成功!"
        df -h "$MOUNT_POINT"
        
        # 测试读写
        TEST_FILE="$MOUNT_POINT/openclaw/test-$(date +%Y%m%d-%H%M%S).txt"
        echo "挂载测试 - $(date)" > "$TEST_FILE"
        cat "$TEST_FILE"
        rm "$TEST_FILE"
        echo "✅ 读写测试通过!"
    else
        echo "❌ 挂载失败!"
        exit 1
    fi
}

configure_autostart() {
    load_config
    
    echo "配置开机自动挂载..."
    
    # 备份 fstab
    cp /etc/fstab /etc/fstab.bak.$(date +%Y%m%d-%H%M%S)
    
    # 检查是否已存在
    if grep -q "$MOUNT_POINT" /etc/fstab; then
        echo "警告：$MOUNT_POINT 已存在于 fstab 中"
        return
    fi
    
    if [ "$PROTOCOL" = "smb" ]; then
        CRED_FILE="/root/.smbcredentials"
        echo "//$NAS_IP/$SHARE_NAME  $MOUNT_POINT  cifs  credentials=$CRED_FILE,vers=3.0,iocharset=utf8,file_mode=0777,dir_mode=0777,_netdev  0  0" >> /etc/fstab
    elif [ "$PROTOCOL" = "nfs" ]; then
        echo "$NAS_IP:/volume1/$SHARE_NAME  $MOUNT_POINT  nfs  defaults,_netdev  0  0" >> /etc/fstab
    fi
    
    echo "✅ 已添加到 /etc/fstab"
    
    # 测试 fstab
    if mount -a --dry-run 2>/dev/null; then
        echo "✅ fstab 配置验证通过"
    else
        echo "⚠️  fstab 配置可能有问题，请检查"
    fi
}

unmount_nas() {
    load_config
    echo "卸载 NAS..."
    umount "$MOUNT_POINT"
    echo "✅ 卸载完成"
}

show_status() {
    load_config
    echo "=== NAS 挂载状态 ==="
    echo "挂载点：$MOUNT_POINT"
    echo ""
    
    if mountpoint -q "$MOUNT_POINT"; then
        echo "状态：✅ 已挂载"
        df -h "$MOUNT_POINT"
        echo ""
        echo "目录结构:"
        ls -la "$MOUNT_POINT/openclaw/" 2>/dev/null || echo "(目录不存在)"
    else
        echo "状态：❌ 未挂载"
    fi
}

usage() {
    echo "用法：$0 {mount|unmount|autostart|status}"
    echo ""
    echo "命令:"
    echo "  mount      - 挂载 NAS"
    echo "  unmount    - 卸载 NAS"
    echo "  autostart  - 配置开机自动挂载"
    echo "  status     - 显示挂载状态"
}

case "${1:-status}" in
    mount)
        mount_nas
        ;;
    unmount)
        unmount_nas
        ;;
    autostart)
        configure_autostart
        ;;
    status)
        show_status
        ;;
    *)
        usage
        ;;
esac
