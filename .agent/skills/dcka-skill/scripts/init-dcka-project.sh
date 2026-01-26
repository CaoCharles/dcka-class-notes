#!/bin/bash
# DCKA 課程 MkDocs 專案初始化腳本
# 恆逸 Docker Containers 與 Kubernetes 系統管理課程

set -e

PROJECT_NAME=${1:-"dcka-course"}

echo "🐳 建立 DCKA 課程專案：$PROJECT_NAME"
echo "   課程：Docker Containers 與 Kubernetes 系統管理"
echo ""

# 建立專案目錄
mkdir -p "$PROJECT_NAME"
cd "$PROJECT_NAME"

# 使用 uv 初始化 Python 3.12 環境
echo "📦 初始化 Python 3.12 環境..."
uv init --python 3.12

# 安裝 MkDocs 及相關套件
echo "📚 安裝 MkDocs Material..."
uv add mkdocs mkdocs-material pymdown-extensions

# 建立目錄結構（對應 DCKA 課程大綱）
echo "📁 建立目錄結構..."
mkdir -p docs/appendix
mkdir -p docs/assets/{images,stylesheets}
mkdir -p .agent/skills/dcka-course-writer

# 建立章節檔案佔位符
echo "📝 建立章節檔案..."

# Ch1: Docker 介紹
cat > docs/01_docker_intro.md << 'EOF'
# Ch1 - Docker Container & Micro Service Introduction

## 學習目標

完成本章節後，你將能夠：

- [ ] 了解容器化技術的優勢
- [ ] 理解 Docker 架構與核心元件
- [ ] 比較 Docker 與 Podman 的差異

---

## 1.1 容器化的好處

（待撰寫）

## 1.2 Docker 架構

（待撰寫）

## 1.3 Docker 基本架構

（待撰寫）

## 1.4 Docker 與 Podman

（待撰寫）

---

## 小結

（待撰寫）
EOF

# Ch2: Docker 容器化管理
cat > docs/02_docker_management.md << 'EOF'
# Ch2 - Docker 容器化管理

## 學習目標

完成本章節後，你將能夠：

- [ ] 管理 public 與 private registry
- [ ] 執行 Docker 基本操作
- [ ] 配置 Persistent Storage 與 Network
- [ ] 使用 Docker 架設 WordPress + MySQL

---

## 2.1 Publics Registry 與 Private Registry

（待撰寫）

## 2.2 Docker 基本操作

（待撰寫）

## 2.3 Persistent Storage

（待撰寫）

## 2.4 Docker Network

（待撰寫）

## 2.5 ~ 2.7 Docker Search / Pull / Push

（待撰寫）

## 2.8 Lab：使用 Docker 架設 WordPress + MySQL

（待撰寫）

---

## 小結

（待撰寫）
EOF

# Ch3: 客製化 Docker Images
cat > docs/03_docker_images.md << 'EOF'
# Ch3 - 客製化 Docker Images

## 學習目標

完成本章節後，你將能夠：

- [ ] 使用 docker commit 建立映像檔
- [ ] 撰寫 Dockerfile
- [ ] 了解 Source-to-image 概念

---

## 3.1 Docker Commit

（待撰寫）

## 3.2 Dockerfile

（待撰寫）

## 3.3 Source-to-image 簡介

（待撰寫）

---

## 小結

（待撰寫）
EOF

# Ch4: Kubernetes Management
cat > docs/04_kubernetes.md << 'EOF'
# Ch4 - Kubernetes Management

## 學習目標

完成本章節後，你將能夠：

- [ ] 了解 Kubernetes 架構與核心元件
- [ ] 安裝與管理 Kubernetes 叢集
- [ ] 部署與管理工作負載
- [ ] 配置網路、儲存與權限控制

---

## 4.1 Kubernetes 與 OpenShift/OKD

（待撰寫）

## 4.2 Minikube vs Minishift

（待撰寫）

## 4.3 Kubernetes 架構

（待撰寫）

## 4.4 安裝 Kubernetes

（待撰寫）

## 4.5 YAML 與 JSON 檔

（待撰寫）

## 4.6 Kubernetes Resource Type

（待撰寫）

## 4.7 Kubernetes 管理

### 4.7.1 Deployment

（待撰寫）

### 4.7.2 Service

（待撰寫）

### 4.7.3 RollingUpdate 與 Recreate

（待撰寫）

### 4.7.4 Canary 與 Blue/Green

（待撰寫）

### 4.7.5 可用資源管理

（待撰寫）

## 4.8 Kubernetes 網路

（待撰寫）

## 4.9 Persistent Volumes

（待撰寫）

## 4.10 ConfigMaps 與 Secret

（待撰寫）

## 4.11 RBAC (Role Base Access Control)

（待撰寫）

## 4.12 Lab：使用 Kubernetes 架設 WordPress + MySQL

（待撰寫）

## 4.13 Logging、Monitoring 與疑難排除

（待撰寫）

---

## 小結

（待撰寫）
EOF

# 附錄：Docker 指令速查
cat > docs/appendix/docker_cheatsheet.md << 'EOF'
# Docker 指令速查表

## 容器管理

| 指令 | 說明 | 範例 |
|------|------|------|
| `docker run` | 建立並執行容器 | `docker run -d nginx` |
| `docker ps` | 列出執行中的容器 | `docker ps -a` |
| `docker stop` | 停止容器 | `docker stop <container>` |
| `docker start` | 啟動容器 | `docker start <container>` |
| `docker rm` | 刪除容器 | `docker rm <container>` |
| `docker exec` | 在容器內執行指令 | `docker exec -it <container> bash` |
| `docker logs` | 查看容器日誌 | `docker logs -f <container>` |

## 映像檔管理

| 指令 | 說明 | 範例 |
|------|------|------|
| `docker images` | 列出映像檔 | `docker images` |
| `docker pull` | 下載映像檔 | `docker pull nginx:latest` |
| `docker push` | 上傳映像檔 | `docker push myrepo/myimage` |
| `docker build` | 建置映像檔 | `docker build -t myimage .` |
| `docker rmi` | 刪除映像檔 | `docker rmi <image>` |

## 網路管理

| 指令 | 說明 | 範例 |
|------|------|------|
| `docker network ls` | 列出網路 | `docker network ls` |
| `docker network create` | 建立網路 | `docker network create mynet` |
| `docker network connect` | 連接網路 | `docker network connect mynet <container>` |

## Volume 管理

| 指令 | 說明 | 範例 |
|------|------|------|
| `docker volume ls` | 列出 volume | `docker volume ls` |
| `docker volume create` | 建立 volume | `docker volume create myvol` |
| `docker volume rm` | 刪除 volume | `docker volume rm myvol` |
EOF

# 附錄：K8S 指令速查
cat > docs/appendix/k8s_cheatsheet.md << 'EOF'
# Kubernetes 指令速查表

## 基本操作

| 指令 | 說明 | 範例 |
|------|------|------|
| `kubectl get` | 取得資源列表 | `kubectl get pods` |
| `kubectl describe` | 查看資源詳情 | `kubectl describe pod <pod>` |
| `kubectl create` | 建立資源 | `kubectl create -f file.yaml` |
| `kubectl apply` | 套用設定 | `kubectl apply -f file.yaml` |
| `kubectl delete` | 刪除資源 | `kubectl delete pod <pod>` |

## Pod 管理

| 指令 | 說明 | 範例 |
|------|------|------|
| `kubectl get pods` | 列出 Pod | `kubectl get pods -o wide` |
| `kubectl logs` | 查看 Pod 日誌 | `kubectl logs -f <pod>` |
| `kubectl exec` | 在 Pod 內執行指令 | `kubectl exec -it <pod> -- bash` |

## Deployment 管理

| 指令 | 說明 | 範例 |
|------|------|------|
| `kubectl get deployments` | 列出 Deployment | `kubectl get deploy` |
| `kubectl scale` | 調整副本數 | `kubectl scale deploy <name> --replicas=3` |
| `kubectl rollout` | 管理更新 | `kubectl rollout status deploy <name>` |

## Service 管理

| 指令 | 說明 | 範例 |
|------|------|------|
| `kubectl get services` | 列出 Service | `kubectl get svc` |
| `kubectl expose` | 建立 Service | `kubectl expose deploy <name> --port=80` |

## 設定管理

| 指令 | 說明 | 範例 |
|------|------|------|
| `kubectl get configmaps` | 列出 ConfigMap | `kubectl get cm` |
| `kubectl get secrets` | 列出 Secret | `kubectl get secrets` |
EOF

# 附錄：疑難排解
cat > docs/appendix/troubleshooting.md << 'EOF'
# 疑難排解指南

## Docker 常見問題

??? question "docker: command not found"
    確認 Docker 已正確安裝：
    ```bash
    which docker
    ```

??? question "Cannot connect to the Docker daemon"
    Docker Daemon 可能尚未啟動：
    ```bash
    # Linux
    sudo systemctl start docker
    
    # macOS / Windows
    # 啟動 Docker Desktop
    ```

??? question "Permission denied"
    Linux 使用者需要加入 docker 群組：
    ```bash
    sudo usermod -aG docker $USER
    # 然後重新登入
    ```

## Kubernetes 常見問題

??? question "kubectl: command not found"
    確認 kubectl 已正確安裝：
    ```bash
    which kubectl
    ```

??? question "The connection to the server was refused"
    確認 Kubernetes 叢集正在執行：
    ```bash
    # minikube
    minikube status
    minikube start
    ```

??? question "Pod 一直處於 Pending 狀態"
    檢查 Pod 事件：
    ```bash
    kubectl describe pod <pod-name>
    ```
    常見原因：資源不足、PVC 未綁定、映像檔拉取失敗
EOF

# 建立 CSS
cat > docs/assets/stylesheets/extra.css << 'EOF'
/* DCKA 課程自訂樣式 */
.md-typeset h1 {
    font-weight: 700;
}

.md-typeset code {
    font-family: 'JetBrains Mono', 'Consolas', monospace;
}
EOF

# 建立 .gitignore
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
.venv/

# uv
.python-version

# MkDocs
site/

# IDE
.idea/
.vscode/
*.swp

# OS
.DS_Store
Thumbs.db
EOF

echo ""
echo "✅ 專案初始化完成！"
echo ""
echo "📂 專案結構："
echo "   $PROJECT_NAME/"
echo "   ├── docs/"
echo "   │   ├── index.md"
echo "   │   ├── 01_docker_intro.md"
echo "   │   ├── 02_docker_management.md"
echo "   │   ├── 03_docker_images.md"
echo "   │   ├── 04_kubernetes.md"
echo "   │   └── appendix/"
echo "   ├── .agent/skills/"
echo "   ├── mkdocs.yml"
echo "   └── pyproject.toml"
echo ""
echo "📋 下一步："
echo "   cd $PROJECT_NAME"
echo "   # 複製 SKILL.md 到 .agent/skills/dcka-course-writer/"
echo "   # 複製 mkdocs.yml 到專案根目錄"
echo "   uv run mkdocs serve    # 本地預覽 http://127.0.0.1:8000"
echo "   uv run mkdocs build    # 建置靜態網站"
echo ""
echo "🚀 在 Antigravity 中使用："
echo "   「撰寫 Docker 介紹章節」"
echo "   「生成 Kubernetes Lab 練習」"
echo "   「新增 Dockerfile 範例」"
