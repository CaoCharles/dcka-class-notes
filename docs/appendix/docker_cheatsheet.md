# Docker 指令速查表

快速參考 Docker 常用指令，適合日常操作與考試複習。

---

## 容器管理

### 執行容器

| 指令 | 說明 |
|------|------|
| `docker run <image>` | 執行容器 |
| `docker run -d <image>` | 背景執行 |
| `docker run -it <image> /bin/bash` | 互動模式 |
| `docker run --name <name> <image>` | 指定名稱 |
| `docker run -p 8080:80 <image>` | Port 對應 |
| `docker run -v /host:/container <image>` | 掛載目錄 |
| `docker run -e VAR=value <image>` | 設定環境變數 |
| `docker run --rm <image>` | 結束後自動刪除 |
| `docker run --restart=always <image>` | 自動重啟 |
| `docker run --network <network> <image>` | 指定網路 |

### 容器操作

| 指令 | 說明 |
|------|------|
| `docker ps` | 列出運行中的容器 |
| `docker ps -a` | 列出所有容器 |
| `docker start <container>` | 啟動容器 |
| `docker stop <container>` | 停止容器 |
| `docker restart <container>` | 重啟容器 |
| `docker pause <container>` | 暫停容器 |
| `docker unpause <container>` | 繼續容器 |
| `docker rm <container>` | 刪除容器 |
| `docker rm -f <container>` | 強制刪除運行中的容器 |
| `docker container prune` | 刪除所有已停止的容器 |

### 容器操作與除錯

| 指令 | 說明 |
|------|------|
| `docker exec -it <container> /bin/bash` | 進入容器 |
| `docker exec <container> <command>` | 執行指令 |
| `docker logs <container>` | 查看日誌 |
| `docker logs -f <container>` | 追蹤日誌 |
| `docker logs --tail 100 <container>` | 最後 100 行 |
| `docker inspect <container>` | 詳細資訊 |
| `docker stats` | 資源使用統計 |
| `docker top <container>` | 容器內程序 |
| `docker cp <src> <container>:<dest>` | 複製檔案到容器 |
| `docker cp <container>:<src> <dest>` | 從容器複製檔案 |

---

## Image 管理

### 基本操作

| 指令 | 說明 |
|------|------|
| `docker images` | 列出本地 Image |
| `docker pull <image>` | 拉取 Image |
| `docker push <image>` | 推送 Image |
| `docker rmi <image>` | 刪除 Image |
| `docker image prune` | 刪除未使用的 Image |
| `docker image prune -a` | 刪除所有未使用的 Image |

### 建置與標籤

| 指令 | 說明 |
|------|------|
| `docker build -t <name>:<tag> .` | 建置 Image |
| `docker build -f Dockerfile.prod .` | 指定 Dockerfile |
| `docker build --no-cache .` | 不使用快取 |
| `docker tag <image> <new-tag>` | 加上標籤 |
| `docker history <image>` | 查看 Image 歷史 |
| `docker save -o image.tar <image>` | 匯出 Image |
| `docker load -i image.tar` | 匯入 Image |

### 搜尋

| 指令 | 說明 |
|------|------|
| `docker search <keyword>` | 搜尋 Docker Hub |
| `docker search --filter is-official=true <keyword>` | 只搜尋官方 Image |
| `docker search --limit 5 <keyword>` | 限制結果數量 |

---

## Volume 管理

| 指令 | 說明 |
|------|------|
| `docker volume ls` | 列出所有 Volume |
| `docker volume create <name>` | 建立 Volume |
| `docker volume inspect <name>` | 查看詳細資訊 |
| `docker volume rm <name>` | 刪除 Volume |
| `docker volume prune` | 刪除未使用的 Volume |

### 掛載方式

```bash
# Volume 掛載
docker run -v my-volume:/app/data nginx

# Bind Mount
docker run -v /host/path:/container/path nginx

# 唯讀掛載
docker run -v /host/path:/container/path:ro nginx

# --mount 語法（推薦）
docker run --mount type=volume,source=my-volume,target=/app/data nginx
docker run --mount type=bind,source=/host/path,target=/container/path nginx
```

---

## 網路管理

| 指令 | 說明 |
|------|------|
| `docker network ls` | 列出所有網路 |
| `docker network create <name>` | 建立網路 |
| `docker network connect <network> <container>` | 連接網路 |
| `docker network disconnect <network> <container>` | 斷開網路 |
| `docker network rm <name>` | 刪除網路 |
| `docker network prune` | 刪除未使用的網路 |
| `docker network inspect <name>` | 查看詳細資訊 |

### 網路類型

| 類型 | 說明 |
|------|------|
| `bridge` | 預設，容器透過虛擬橋接器連接 |
| `host` | 直接使用主機網路 |
| `none` | 無網路 |
| `overlay` | 跨主機通訊（Swarm） |

---

## 系統管理

| 指令 | 說明 |
|------|------|
| `docker info` | 系統資訊 |
| `docker version` | 版本資訊 |
| `docker system df` | 磁碟使用量 |
| `docker system prune` | 清理未使用資源 |
| `docker system prune -a --volumes` | 完整清理 |
| `docker events` | 即時事件 |

---

## Docker Compose

| 指令 | 說明 |
|------|------|
| `docker compose up` | 啟動服務 |
| `docker compose up -d` | 背景啟動 |
| `docker compose down` | 停止並移除 |
| `docker compose down -v` | 同時移除 Volume |
| `docker compose ps` | 列出服務 |
| `docker compose logs` | 查看日誌 |
| `docker compose logs -f` | 追蹤日誌 |
| `docker compose exec <service> <command>` | 執行指令 |
| `docker compose build` | 建置服務 |
| `docker compose pull` | 拉取 Image |

---

## Registry 登入

| 指令 | 說明 |
|------|------|
| `docker login` | 登入 Docker Hub |
| `docker login <registry>` | 登入私有 Registry |
| `docker logout` | 登出 |

---

## 常用組合指令

```bash title="常用操作"
# 停止所有容器
docker stop $(docker ps -q)

# 刪除所有容器
docker rm $(docker ps -aq)

# 刪除所有 Image
docker rmi $(docker images -q)

# 刪除 dangling Image
docker rmi $(docker images -f "dangling=true" -q)

# 取得容器 IP
docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' <container>

# 進入運行中的容器
docker exec -it $(docker ps -q -f name=nginx) /bin/sh
```

---

## Dockerfile 指令

| 指令 | 說明 |
|------|------|
| `FROM` | 基礎 Image |
| `RUN` | 執行指令 |
| `COPY` | 複製檔案 |
| `ADD` | 複製檔案（支援 URL、解壓縮） |
| `WORKDIR` | 工作目錄 |
| `ENV` | 環境變數 |
| `EXPOSE` | 暴露 Port |
| `CMD` | 預設執行指令 |
| `ENTRYPOINT` | 入口點 |
| `VOLUME` | 掛載點 |
| `USER` | 執行身份 |
| `ARG` | 建置參數 |
| `LABEL` | 標籤 |
| `HEALTHCHECK` | 健康檢查 |

---

## 環境變數

| 變數 | 說明 |
|------|------|
| `DOCKER_HOST` | Docker 主機位址 |
| `DOCKER_TLS_VERIFY` | 啟用 TLS 驗證 |
| `DOCKER_CERT_PATH` | TLS 憑證路徑 |
| `DOCKER_CONFIG` | 設定檔目錄 |
