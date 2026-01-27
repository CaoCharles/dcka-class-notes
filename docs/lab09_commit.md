---
authors:
  - name: 課程作者
    email: author@example.com
date: 2026-01-27
updated: 2026-01-27
tags:
  - Docker
  - Container
  - Image
---

# LAB 09 客製化 Container Images - docker commit

## 學習目標

完成本章節後，你將能夠：

- [ ] 使用 `docker commit` 從容器建立新的 Image
- [ ] 使用 `docker save` 將 Image 匯出為 tar 檔
- [ ] 使用 `docker load` 從 tar 檔載入 Image
- [ ] 建立清理 Docker 環境的腳本

## 前置知識

開始之前，請確保你已經：

- 完成 LAB 06 的內容
- 熟悉 Docker 基本操作
- 已設定 Private Registry（docker1.training.lab:5000）

---

## 9.1 環境準備

### 切換到 docker2 虛擬機

本 Lab 在 docker2 虛擬機上執行。

### 確認現有環境

```bash title="檢視現有的 Container Images"
docker images
```

**預期結果**：

```
IMAGE                                   ID             DISK USAGE   CONTENT SIZE   EXTRA
192.168.66.51:5000/nginx:1.9.1          667cfe3b0942        289MB          139MB        
docker1.training.lab:5000/nginx:1.7.1   b1590b02702d       1.06GB          515MB        
```

```bash title="檢視現有的 Container"
docker ps -a
```

**預期結果**：

```
CONTAINER ID   IMAGE     COMMAND   CREATED   STATUS    PORTS     NAMES
```

### 建立清理腳本

建立一個腳本來清理所有 Container 與 Image：

```bash title="建立 docker_clean_all.sh"
vi docker_clean_all.sh
```

腳本內容：

```bash title="docker_clean_all.sh"
#!/bin/bash
# 停止並刪除所有 Container
docker stop $(docker ps -aq)
docker rm $(docker ps -aq)
# 刪除所有 Image
docker rmi $(docker images -q)
```

!!! note "腳本說明"
    - `docker ps -aq`：列出所有 Container 的 ID（`-a` 包含已停止的，`-q` 只顯示 ID）
    - `docker images -q`：列出所有 Image 的 ID
    - 如果沒有 Container 或 Image，指令會顯示錯誤訊息，但不影響後續操作

```bash title="設定執行權限"
chmod 755 ./docker_clean_all.sh
```

```bash title="執行清理腳本"
./docker_clean_all.sh
```

**預期結果**：

```
docker: 'docker stop' requires at least 1 argument
docker: 'docker rm' requires at least 1 argument
Untagged: 192.168.66.51:5000/nginx:1.9.1
Deleted: sha256:667cfe3b094262dcd2323f28a800d8376221b017a9dd14b6fff78e4ec96a6177
Untagged: docker1.training.lab:5000/nginx:1.7.1
Deleted: sha256:b1590b02702d926755e02ca8f01baa42c9789758a3fb6d40aa87bdcfe871965d
```

!!! info "錯誤訊息說明"
    當沒有 Container 時，`docker stop` 和 `docker rm` 會顯示錯誤訊息，這是正常的，不影響後續操作。

---

## 9.2 下載 Docker Image

### 從 Private Registry 下載 Alpine

```bash title="下載 Alpine Image"
docker pull docker1.training.lab:5000/alpine
```

**預期結果**：

```
Using default tag: latest
latest: Pulling from alpine
77cae8ab23bf: Pull complete 
Digest: sha256:d0a0f8e7bf9a6287c7dab568b947b6c3dd6b84e9c67ab9f1e95f79751d808641
Status: Downloaded newer image for docker1.training.lab:5000/alpine:latest
docker1.training.lab:5000/alpine:latest
```

!!! note "docker pull 說明"
    - 如果沒有指定 tag，預設會使用 `latest`
    - 從 Private Registry 下載需要指定完整的 Registry 位址

```bash title="確認 Image 已下載"
docker images
```

**預期結果**：

```
IMAGE                                     ID             DISK USAGE   CONTENT SIZE   EXTRA
docker1.training.lab:5000/alpine:latest   d0a0f8e7bf9a       11.6MB         5.82MB        
```

---

## 9.3 進入 Alpine 執行 sh

### 啟動互動式 Container

```bash title="啟動 Alpine Container"
docker run -it --name alpine-1 docker1.training.lab:5000/alpine:latest
```

!!! note "docker run 參數說明"
    | 參數 | 說明 |
    |------|------|
    | `-i` | 保持 STDIN 開啟（interactive） |
    | `-t` | 分配虛擬終端機（tty） |
    | `--name alpine-1` | 指定 Container 名稱 |

進入容器後會看到提示符號 `/ #`，表示已在 Container 內部。

---

## 9.4 在 Alpine 中安裝 Bash

### 測試 Bash 是否存在

```bash title="測試 bash（在 Container 內執行）"
bash
```

**預期結果**：

```
/bin/sh: bash: not found
```

!!! info "為什麼 Alpine 沒有 Bash？"
    Alpine Linux 是一個極輕量的 Linux 發行版，使用 BusyBox 作為核心工具集，預設只提供 `/bin/sh`（ash shell）以維持極小的映像大小（約 5MB）。

### 使用 apk 安裝 Bash

```bash title="安裝 bash（在 Container 內執行）"
apk add --no-cache --update-cache bash
```

**預期結果**：

```
fetch http://dl-cdn.alpinelinux.org/alpine/v3.10/main/x86_64/APKINDEX.tar.gz
fetch http://dl-cdn.alpinelinux.org/alpine/v3.10/community/x86_64/APKINDEX.tar.gz
(1/4) Installing ncurses-terminfo-base (6.1_p20190518-r2)
(2/4) Installing ncurses-libs (6.1_p20190518-r2)
(3/4) Installing readline (8.0.0-r0)
(4/4) Installing bash (5.0.0-r0)
Executing bash-5.0.0-r0.post-install
Executing busybox-1.30.1-r2.trigger
OK: 8 MiB in 18 packages
```

!!! tip "apk 參數說明"
    | 參數 | 說明 |
    |------|------|
    | `add` | 安裝套件 |
    | `--no-cache` | 不使用本地快取，減少 Image 大小 |
    | `--update-cache` | 更新套件索引 |

### 驗證安裝成功

```bash title="切換到 bash（在 Container 內執行）"
bash
```

**預期結果**：

成功進入 bash，提示符號變成 `bash-5.0#`

```bash title="退出 Container"
exit  # 退出 bash
exit  # 退出 Container
```

---

## 9.5 Commit 新的 Container Image

### 使用 docker commit 建立新 Image

```bash title="建立新 Image"
docker commit -m "alpine + bash" alpine-1 alpine-bash
```

**預期結果**：

```
sha256:4326afd8916bbf220fcb95d27fd5cac5096b74fa6ccba7c8929d5a70820875ec
```

!!! note "docker commit 語法"
    ```
    docker commit [OPTIONS] CONTAINER [REPOSITORY[:TAG]]
    ```
    
    | 參數 | 說明 |
    |------|------|
    | `-m` | 提交訊息（描述變更內容） |
    | `-a` | 指定作者（可選） |
    | `alpine-1` | 來源 Container 名稱 |
    | `alpine-bash` | 新 Image 名稱（預設 tag 為 latest） |

```bash title="確認新 Image 已建立"
docker images
```

**預期結果**：

```
IMAGE                                     ID             DISK USAGE   CONTENT SIZE   EXTRA
alpine-bash:latest                        4326afd8916b       14.5MB          6.6MB        
docker1.training.lab:5000/alpine:latest   d0a0f8e7bf9a       11.6MB         5.82MB    U   
```

!!! info "Image 大小變化"
    安裝 Bash 後，Image 從 5.82MB 增加到 6.6MB，增加約 0.78MB（主要是 Bash 及其相依套件）。

---

## 9.6 匯出並壓縮為 Tar Ball 檔案

### 使用 docker save 匯出 Image

```bash title="匯出 Image 為 tar 檔"
docker save --output=alpine-bash.tar alpine-bash
```

!!! note "docker save 語法"
    ```
    docker save [OPTIONS] IMAGE [IMAGE...]
    ```
    
    | 參數 | 說明 |
    |------|------|
    | `--output` 或 `-o` | 指定輸出檔案名稱 |
    | 可一次匯出多個 Image | |

```bash title="確認 tar 檔案大小"
ls -lh alpine-bash.tar
```

**預期結果**：

```
-rw------- 1 root root 6.3M Jan 27 11:05 alpine-bash.tar
```

### 使用 gzip 壓縮

```bash title="壓縮 tar 檔案"
gzip -9 alpine-bash.tar
```

!!! tip "gzip 參數說明"
    - `-9`：最高壓縮比（1-9，9 為最高）
    - 壓縮後檔案會自動加上 `.gz` 副檔名

```bash title="確認壓縮後大小"
ls -lh alpine-bash.tar.gz
```

**預期結果**：

```
-rw------- 1 root root 3.4M Jan 27 11:05 alpine-bash.tar.gz
```

!!! success "壓縮效果"
    檔案從 6.3MB 壓縮到 3.4MB，減少約 46% 的空間。

---

## 9.7 測試 - 清除全部的 Container 及 Images

```bash title="清除所有 Container 與 Image"
./docker_clean_all.sh
```

**預期結果**：

```
20fb31307e87
20fb31307e87
Untagged: alpine-bash:latest
Deleted: sha256:4326afd8916bbf220fcb95d27fd5cac5096b74fa6ccba7c8929d5a70820875ec
Untagged: docker1.training.lab:5000/alpine:latest
Deleted: sha256:d0a0f8e7bf9a6287c7dab568b947b6c3dd6b84e9c67ab9f1e95f79751d808641
```

```bash title="確認環境已清理"
docker images
```

**預期結果**：

```
IMAGE   ID             DISK USAGE   CONTENT SIZE   EXTRA
```

---

## 9.8 載入 Container Image

### 使用 docker load 載入壓縮檔

```bash title="從壓縮檔載入 Image"
docker load -i alpine-bash.tar.gz
```

**預期結果**：

```
Loaded image: alpine-bash:latest
```

!!! note "docker load 語法"
    ```
    docker load [OPTIONS]
    ```
    
    | 參數 | 說明 |
    |------|------|
    | `-i` 或 `--input` | 指定輸入檔案 |
    | 支援 `.tar` 和 `.tar.gz` 格式 | |

```bash title="確認 Image 已載入"
docker images
```

**預期結果**：

```
IMAGE                ID             DISK USAGE   CONTENT SIZE   EXTRA
alpine-bash:latest   4326afd8916b       14.5MB          6.6MB        
```

---

## 9.9 確認是否有 Bash

```bash title="使用載入的 Image 啟動 Container"
docker run -it --name alpine-2 alpine-bash /bin/bash
```

進入容器後會看到提示符號 `bash-5.0#`，表示 Bash 已成功安裝。

```bash title="確認 bash 已安裝（在 Container 內執行）"
ls -l /bin/bash
```

**預期結果**：

```
-rwxr-xr-x    1 root     root        735488 May  3  2019 /bin/bash
```

```bash title="退出 Container"
exit
```

---

## 9.10 清除全部的 Container 及 Images

```bash title="最終清理"
./docker_clean_all.sh
```

**預期結果**：

```
db10817df336
db10817df336
Untagged: alpine-bash:latest
Deleted: sha256:4326afd8916bbf220fcb95d27fd5cac5096b74fa6ccba7c8929d5a70820875ec
```

!!! success "Lab 完成"
    恭喜你已成功完成本 Lab！

---

## 指令參考

### docker commit

| 選項 | 說明 | 範例 |
|------|------|------|
| `-m` | 提交訊息 | `-m "alpine + bash"` |
| `-a` | 指定作者 | `-a "John Doe"` |
| `-c` | 套用 Dockerfile 指令 | `-c 'CMD ["bash"]'` |
| `-p` | 提交前暫停容器 | `-p` |

### docker save 與 docker load

| 指令 | 說明 | 範例 |
|------|------|------|
| `docker save` | 將 Image 匯出為 tar 檔 | `docker save -o image.tar my-image` |
| `docker load` | 從 tar 檔載入 Image | `docker load -i image.tar` |

!!! warning "docker save vs docker export"
    | 比較 | docker save | docker export |
    |------|-------------|---------------|
    | 對象 | Image | Container |
    | 保留 | 完整 Layer 與 metadata | 單一檔案系統 |
    | 載入指令 | docker load | docker import |
    | 用途 | Image 備份/傳輸 | Container 檔案系統備份 |

---

## 小結

本章節重點回顧：

- ✅ **docker commit**：將執行中的 Container 狀態儲存為新 Image
- ✅ **docker save**：將 Image 匯出為 tar 檔案
- ✅ **docker load**：從 tar 檔載入 Image
- ✅ **gzip 壓縮**：減少匯出檔案的大小
- ✅ **清理腳本**：使用腳本批次清理 Container 與 Image
