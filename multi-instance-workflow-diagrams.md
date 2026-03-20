# 多实例协同工作流程图

## 主流程图

```mermaid
flowchart TD
    subgraph AliCloud["阿里云 VPS - 超梦 (总控)"]
        A1[用户/触发器] --> A2[任务编排器]
        A2 --> A3[承道 - 内容策划]
        A2 --> A4[译文 - 文案翻译]
        A2 --> A5[棱镜 - 视觉设计]
        A2 --> A6[画语 - 图片生成]
        
        A3 --> A7[产出物汇总]
        A4 --> A7
        A5 --> A7
        A6 --> A7
        
        A7 --> A8[打包任务包]
        A8 --> A9[上传共享存储]
        A8 --> A10[发送飞书通知]
        A8 --> A11[调用 Mac mini API]
    end
    
    subgraph Network["Tailscale 加密隧道"]
        N1[100.x.x.x ←→ 100.y.y.y]
    end
    
    subgraph MacMini["Mac mini - 视频团队 Leader"]
        M1[接收任务] --> M2[解析任务包]
        M2 --> M3[视频生成]
        M2 --> M4[视频剪辑]
        M2 --> M5[配音配乐]
        
        M3 --> M6[合成输出]
        M4 --> M6
        M5 --> M6
        
        M6 --> M7[质量审核]
        M7 --> M8[多平台发布]
        M8 --> M9[收集发布数据]
        M9 --> M10[生成报告]
        
        M10 --> M11[回传超梦]
        M10 --> M12[飞书通知]
    end
    
    A9 -.共享存储同步.-> M1
    A10 -.飞书消息.-> M1
    A11 -.API 调用.-> M1
    M11 -.状态同步.-> A2
    
    style AliCloud fill:#e1f5ff,stroke:#0066cc
    style MacMini fill:#fff4e1,stroke:#cc6600
    style Network fill:#f0f0f0,stroke:#666666,stroke-dasharray: 5 5
```

## 任务状态流转图

```mermaid
stateDiagram-v2
    [*] --> CREATED: 超梦创建任务
    
    CREATED --> ASSIGNED: 分发到 Mac mini
    ASSIGNED --> PROCESSING: Mac mini 开始处理
    PROCESSING --> REVIEW: 视频生成完成
    REVIEW --> PUBLISHED: 审核通过
    REVIEW --> REVISION: 需要修改
    REVISION --> PROCESSING: 重新处理
    PUBLISHED --> [*]: 流程结束
    
    PROCESSING --> FAILED: 处理失败
    FAILED --> ASSIGNED: 重试
    FAILED --> [*]: 放弃
    
    note right of CREATED
        状态包含:
        - 任务 ID
        - 优先级
        - 截止时间
        - 产出物列表
    end note
    
    note right of PROCESSING
        进度同步:
        - 当前阶段
        - 完成百分比
        - 预计剩余时间
    end note
```

## 通信架构图

```mermaid
sequenceDiagram
    participant User as 用户
    participant CM as 超梦 (阿里云)
    participant FS as 飞书机器人
    participant SS as 共享存储
    participant MM as Mac mini
    
    User->>CM: 创建视频任务
    CM->>CM: 调用子智能体<br/>(承道/译文/棱镜/画语)
    CM->>SS: 上传产出物
    CM->>FS: 发送任务通知
    FS->>MM: 推送消息
    
    MM->>SS: 拉取任务包
    MM->>MM: 视频生成 + 剪辑
    MM->>FS: 发送进度更新
    FS->>CM: 同步状态
    
    MM->>MM: 多平台发布
    MM->>SS: 上传成品 + 报告
    MM->>FS: 发送完成通知
    FS->>CM: 最终状态同步
    CM->>User: 任务完成报告
```

## 数据同步机制

```mermaid
flowchart LR
    subgraph Sync["文件同步机制"]
        A[超梦本地] -->|rsync | B[阿里云 OSS]
        B -->|ossutil sync| C[Mac mini 本地]
        C -->|处理结果 | B
        B -->|拉取 | A
    end
    
    subgraph Check["一致性校验"]
        D[MD5 校验] --> E[版本对比]
        E --> F[冲突检测]
        F --> G[自动合并/告警]
    end
    
    Sync --> Check
    
    style Sync fill:#e8f5e9,stroke:#2e7d32
    style Check fill:#fff3e0,stroke:#ef6c00
```

## 故障处理流程

```mermaid
flowchart TD
    Start[发现异常] --> Check{异常类型}
    
    Check -->|网络中断 | Net[检查 Tailscale 状态]
    Net --> NetFix{是否恢复}
    NetFix -->|是 | Resume[恢复任务]
    NetFix -->|否 | Alert1[发送告警 + 切换 ZeroTier]
    
    Check -->|消息失败 | Msg[检查飞书 Webhook]
    Msg --> MsgFix{是否恢复}
    MsgFix -->|是 | Resume
    MsgFix -->|否 | Alert2[发送告警 + 备用通知]
    
    Check -->|文件同步失败 | File[检查存储/权限]
    File --> FileFix{是否恢复}
    FileFix -->|是 | Resume
    FileFix -->|否 | Alert3[发送告警 + 手动同步]
    
    Check -->|API 调用失败 | API[检查认证/服务]
    API --> APIFix{是否恢复}
    APIFix -->|是 | Resume
    APIFix -->|否 | Alert4[发送告警 + 降级方案]
    
    Resume --> End[继续执行]
    Alert1 --> Manual[人工介入]
    Alert2 --> Manual
    Alert3 --> Manual
    Alert4 --> Manual
    Manual --> End
    
    style Start fill:#ffebee,stroke:#c62828
    style End fill:#e8f5e9,stroke:#2e7d32
    style Manual fill:#fff3e0,stroke:#ef6c00
```

## 部署架构

```mermaid
flowchart TB
    subgraph AliCloud["阿里云 VPS"]
        direction TB
        OC1[OpenClaw 主实例]
        TS1[Tailscale 客户端]
        NG1[Nginx 反向代理]
        APP1[应用服务 :8443]
        OSS[OSS Bucket]
    end
    
    subgraph Internet["Internet"]
        TS_NET[Tailscale Network<br/>100.x.x.0/24]
    end
    
    subgraph Local["本地 Mac mini"]
        direction TB
        OC2[OpenClaw 副实例]
        TS2[Tailscale 客户端]
        APP2[应用服务 :8443]
        LOCAL[本地存储]
        VIDEO[视频工具集]
    end
    
    OC1 --> TS1
    TS1 <-->|UDP 41641<br/>加密隧道 | TS_NET
    TS_NET <-->|UDP 41641| TS2
    TS2 --> OC2
    
    OC1 --> NG1 --> APP1
    OC2 --> APP2
    
    OC1 --> OSS
    OSS -.sync.-> LOCAL
    
    style AliCloud fill:#e1f5ff,stroke:#0066cc
    style Local fill:#fff4e1,stroke:#cc6600
    style TS_NET fill:#f3e5f5,stroke:#7b1fa2
```

---

## 图例说明

| 符号 | 含义 |
|------|------|
| ──→ | 数据流/控制流 |
| - -→ | 异步通知/消息 |
| <──> | 双向通信 |
| [.sync.] | 定期同步 |
| 🔵 | 阿里云资源 |
| 🟠 | 本地资源 |
| 🟣 | 网络层 |

---

*使用 Mermaid 渲染器查看完整图表*
