## Factory Assembly Line Workflow

```mermaid
flowchart TD
    A([User Input: product description])
    A --> B

    B["🔍 inspect_station<br/>(AgentExecutor — AI quality control inspector)"]

    B -- defective --> C["🗑️ scrap_station<br/>(executor — terminal)"]
    B -- good --> D["🔀 to_paint_request<br/>(bridge 1: AgentExecutorResponse → str)"]

    D --> E["🎨 paint_station<br/>(Executor — applies paint & finish)"]
    E --> F["🔀 to_package_request<br/>(bridge 2: str → AgentExecutorRequest)"]
    F --> G["📦 package_station<br/>(AgentExecutor — AI packaging specialist)"]
    G --> H["✅ package_result<br/>(executor — terminal)"]

    C --> OUT1([Output: SCRAPPED: reason])
    H --> OUT2([Output: METHOD: method. REASON: reason])

    style B fill:#dbeafe,stroke:#3b82f6
    style G fill:#dbeafe,stroke:#3b82f6
    style D fill:#fef9c3,stroke:#eab308
    style F fill:#fef9c3,stroke:#eab308
    style C fill:#fee2e2,stroke:#ef4444
    style H fill:#dcfce7,stroke:#22c55e
```

**Node types:**
- 🔵 Blue — `AgentExecutor` (AI agent nodes)
- 🟡 Yellow — Bridge nodes (type adapters between agent and plain executors)
- 🔴 Red — Scrap terminal (defective path)
- 🟢 Green — Package terminal (good path)
