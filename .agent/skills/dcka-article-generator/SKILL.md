---
name: DCKA 課程文章生成
description: 用於生成 Docker 與 Kubernetes 課程文章的標準格式規範
---

# DCKA 課程文章生成 Skill

## 概述

本 Skill 定義了 DCKA（Docker Containers 與 Kubernetes 系統管理）課程文章的標準撰寫格式，確保 AI 生成的課程內容具有一致的結構與風格。

## 觸發條件

當使用者提到以下關鍵字時啟用：
- 撰寫課程、新增章節、寫課程內容
- 新增小節、補充內容
- Docker、Kubernetes 教學內容

---

## 文章元資料格式

每篇文章開頭必須包含 YAML Front Matter：

```yaml
---
authors:
  - name: 作者名稱
    email: author@example.com
date: 2024-01-26
updated: 2024-01-26
tags:
  - Docker
  - Container
---
```

---

## 標準文章結構

### 1. 標題與學習目標

```markdown
# 第 X 章：章節標題

## 學習目標

完成本章節後，你將能夠：

- [ ] 學習目標 1
- [ ] 學習目標 2
- [ ] 學習目標 3

## 前置知識

開始之前，請確保你已經：

- 完成前一章節內容
- 具備 XXX 基礎知識
- 準備好 XXX 環境

---
```

### 2. 主要內容區塊

每個小節使用以下格式：

```markdown
## X.Y 小節標題

### 概念說明

（2-3 段概念介紹文字）

!!! info "背景知識"
    補充說明的背景資訊

### 架構圖

使用 Mermaid 繪製架構圖：

\`\`\`mermaid
graph LR
    A[元件 A] --> B[元件 B]
    B --> C[元件 C]
\`\`\`

### 比較表格

| 比較項目 | 選項 A | 選項 B |
|----------|--------|--------|
| 特性 1 | 說明 | 說明 |
| 特性 2 | 說明 | 說明 |

### 實作步驟

\`\`\`bash title="步驟說明"
# 指令說明
command --option value
\`\`\`

**預期結果**：

\`\`\`
輸出結果
\`\`\`

!!! tip "實用技巧"
    操作小技巧或注意事項

---
```

### 3. Lab 實作練習

```markdown
## Lab 實作練習

### Lab X-1：練習標題

**目標**：說明練習目的

**情境**：模擬的實務情境描述

**環境需求**：
- 需求 1
- 需求 2

#### 步驟 1：步驟標題

\`\`\`bash title="步驟 1 說明"
# 指令說明
command
\`\`\`

#### 步驟 2：步驟標題

\`\`\`bash title="步驟 2 說明"
command
\`\`\`

#### 驗證結果

\`\`\`bash title="驗證指令"
verification_command
\`\`\`

**預期結果**：

\`\`\`
預期輸出
\`\`\`

!!! success "完成確認"
    如果看到上述輸出，表示 Lab 完成成功

---
```

### 4. 常見問題（FAQ）

```markdown
## 常見問題

??? question "Q1：問題描述"
    **原因**：說明問題原因
    
    **解決方案**：
    \`\`\`bash
    solution_command
    \`\`\`

??? question "Q2：問題描述"
    **解答**：詳細解答內容
    
    **補充說明**：
    - 重點 1
    - 重點 2

---
```

### 5. 小結與延伸閱讀

```markdown
## 小結

本章節重點回顧：

- ✅ **重點 1**：簡短說明
- ✅ **重點 2**：簡短說明
- ✅ **重點 3**：簡短說明
- ✅ **重點 4**：簡短說明

## 延伸閱讀

- [資源標題 1](URL)
- [資源標題 2](URL)
- [資源標題 3](URL)
```

---

## Admonition 使用規範

| 類型 | 用途 | 語法 |
|------|------|------|
| `note` | 補充說明、背景知識 | `!!! note "標題"` |
| `tip` | 實用技巧、最佳實踐 | `!!! tip "標題"` |
| `warning` | 警告、注意事項 | `!!! warning "標題"` |
| `danger` | 危險操作、不可逆動作 | `!!! danger "標題"` |
| `example` | 範例說明 | `!!! example "標題"` |
| `info` | 一般資訊補充 | `!!! info "標題"` |
| `success` | 成功提示 | `!!! success "標題"` |
| `question` | FAQ（可摺疊） | `??? question "標題"` |

---

## 程式碼區塊規範

### 必須標註語言類型和用途

```markdown
\`\`\`bash title="建立 nginx 容器"
docker run -d --name my-nginx -p 8080:80 nginx:latest
\`\`\`

\`\`\`yaml title="docker-compose.yml"
version: '3.8'
services:
  web:
    image: nginx
\`\`\`

\`\`\`dockerfile title="Dockerfile"
FROM nginx:alpine
COPY . /usr/share/nginx/html
\`\`\`
```

### 支援的語言標籤

- `bash` - Shell 指令
- `yaml` - YAML 設定檔
- `json` - JSON 資料
- `dockerfile` - Dockerfile
- `python` - Python 程式碼
- `go` - Go 程式碼
- `javascript` - JavaScript
- `html` - HTML
- `css` - CSS

---

## Mermaid 圖表規範

### 支援的圖表類型

1. **流程圖 (flowchart/graph)**
```markdown
\`\`\`mermaid
graph LR
    A[開始] --> B{條件}
    B -->|是| C[結果 A]
    B -->|否| D[結果 B]
\`\`\`
```

2. **時序圖 (sequenceDiagram)**
```markdown
\`\`\`mermaid
sequenceDiagram
    participant Client
    participant Server
    Client->>Server: 請求
    Server-->>Client: 回應
\`\`\`
```

3. **狀態圖 (stateDiagram-v2)**
```markdown
\`\`\`mermaid
stateDiagram-v2
    [*] --> 狀態A
    狀態A --> 狀態B
    狀態B --> [*]
\`\`\`
```

---

## 語言規範

1. **使用繁體中文**：所有說明文字使用繁體中文
2. **技術名詞保留英文**：首次出現時附中文說明
   - 例如：Container（容器）、Pod（最小部署單位）
3. **指令與程式碼**：保持英文原文
4. **標點符號**：使用全形標點（，。：；！？）

---

## 專有名詞對照表

| 英文 | 中文 | 首次出現寫法 |
|------|------|--------------|
| Container | 容器 | Container（容器） |
| Image | 映像檔 | Image（映像檔） |
| Registry | 倉庫 | Registry（倉庫） |
| Volume | 儲存卷 | Volume（儲存卷） |
| Pod | Pod | Pod（最小部署單位） |
| Deployment | 部署 | Deployment（部署） |
| Service | 服務 | Service（服務） |
| ConfigMap | 設定對應 | ConfigMap（設定對應） |
| Secret | 密鑰 | Secret（密鑰） |
| Namespace | 命名空間 | Namespace（命名空間） |
| Node | 節點 | Node（節點） |
| Cluster | 叢集 | Cluster（叢集） |

---

## 檔案命名規則

- 章節檔案：`XX_chapter_name.md`（XX 為兩位數字）
- 附錄檔案：`appendix/topic_name.md`
- 範例：
  - `01_docker_intro.md`
  - `02_docker_management.md`
  - `appendix/docker_cheatsheet.md`

---

## 範例：完整章節模板

```markdown
---
authors:
  - name: 課程作者
    email: author@example.com
date: 2024-01-26
tags:
  - Docker
  - Container
---

# 第 X 章：章節標題

## 學習目標

完成本章節後，你將能夠：

- [ ] 目標 1
- [ ] 目標 2
- [ ] 目標 3

## 前置知識

開始之前，請確保你已經：

- 完成前一章節內容
- 具備 Linux 基礎知識

---

## X.1 小節標題

### 概念說明

概念介紹文字...

!!! info "背景知識"
    補充說明

### 架構圖

\`\`\`mermaid
graph LR
    A --> B --> C
\`\`\`

### 實作範例

\`\`\`bash title="範例指令"
command --option
\`\`\`

---

## Lab 實作練習

### Lab X-1：練習標題

**目標**：練習目的

**步驟**：

1. 步驟說明
   \`\`\`bash
   command
   \`\`\`

**驗證**：

\`\`\`bash
verify_command
\`\`\`

---

## 常見問題

??? question "Q1：問題"
    解答內容

---

## 小結

- ✅ **重點 1**：說明
- ✅ **重點 2**：說明

## 延伸閱讀

- [資源](URL)
```
