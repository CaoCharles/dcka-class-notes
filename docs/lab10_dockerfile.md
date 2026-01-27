---
authors:
  - name: 課程作者
    email: author@example.com
date: 2026-01-27
updated: 2026-01-27
tags:
  - Docker
  - Dockerfile
  - Docker Hub
---

# LAB 10 客製化 Container Images - Dockerfile

## 學習目標

完成本章節後，你將能夠：

- [ ] 撰寫 Dockerfile 建立客製化 Image
- [ ] 使用 `docker build` 建置 Image
- [ ] 使用 `docker login` 登入 Docker Hub
- [ ] 使用 `docker tag` 標記 Image
- [ ] 使用 `docker push` 上傳 Image 到 Docker Hub
- [ ] 從 Docker Hub 下載自己上傳的 Image

## 前置知識

開始之前，請確保你已經：

- 完成 LAB 09 的內容
- 了解 Docker Image 的基本概念
- 已註冊 Docker Hub 帳號（https://hub.docker.com）

---

## 10.1 環境準備

### 切換到 docker2 虛擬機

本 Lab 在 docker2 虛擬機上執行。

### 確認環境已清理

```bash title="檢視現有的 Container Images"
docker images
```

**預期結果**：

```
IMAGE   ID             DISK USAGE   CONTENT SIZE   EXTRA
```

```bash title="檢視現有的 Container"
docker ps -a
```

**預期結果**：

```
CONTAINER ID   IMAGE     COMMAND   CREATED   STATUS    PORTS     NAMES
```

### 執行清理腳本（如有需要）

```bash title="執行清理腳本"
./docker_clean_all.sh
```

!!! info "腳本說明"
    如果沒有 Container 或 Image，指令會顯示錯誤訊息，這是正常的，不影響後續操作。

---

## 10.2 建立專用目錄與 Dockerfile

### 建立工作目錄

```bash title="建立 Dockerfile 專用目錄"
mkdir /root/dockerfile-1
cd /root/dockerfile-1
```

### 建立 Dockerfile

```bash title="編輯 Dockerfile"
vi dockerfile
```

Dockerfile 內容：

```dockerfile title="dockerfile"
FROM docker1.training.lab:5000/alpine
#FROM 192.168.66.51:5000/alpine
RUN apk add --no-cache --update-cache bash
CMD ["/bin/bash"]
```

!!! note "Dockerfile 指令說明"
    | 指令 | 說明 |
    |------|------|
    | `FROM` | 指定基礎映像，這裡使用 Private Registry 的 Alpine |
    | `RUN` | 在建置過程中執行指令，這裡安裝 bash |
    | `CMD` | 指定容器啟動時預設執行的指令 |

```bash title="確認 Dockerfile 內容"
cat dockerfile
```

**預期結果**：

```
FROM docker1.training.lab:5000/alpine
#FROM 192.168.66.51:5000/alpine
RUN apk add --no-cache --update-cache bash
CMD ["/bin/bash"]
```

---

## 10.3 測試基礎 Alpine Image

在建置自訂 Image 之前，先確認基礎 Alpine 沒有 Bash：

```bash title="啟動 Alpine Container 測試"
docker run -it --name alpine-1 docker1.training.lab:5000/alpine /bin/sh
```

**預期結果**：

```
Unable to find image 'docker1.training.lab:5000/alpine:latest' locally
latest: Pulling from alpine
77cae8ab23bf: Pull complete 
Digest: sha256:d0a0f8e7bf9a6287c7dab568b947b6c3dd6b84e9c67ab9f1e95f79751d808641
Status: Downloaded newer image for docker1.training.lab:5000/alpine:latest
```

在容器內測試 Bash：

```bash title="測試 bash（在 Container 內執行）"
bash
```

**預期結果**：

```
/bin/sh: bash: not found
```

```bash title="退出容器"
exit
```

---

## 10.4 使用 Dockerfile 建置新的 Docker Image

### 執行 docker build

```bash title="建置 Docker Image"
docker build -t alpine-bash-2 .
```

**預期結果**：

```
[+] Building 2.9s (6/6) FINISHED                                                docker:default
 => [internal] load build definition from dockerfile                                      0.0s
 => => transferring dockerfile: 171B                                                      0.0s
 => [internal] load metadata for docker1.training.lab:5000/alpine:latest                  0.0s
 => [internal] load .dockerignore                                                         0.0s
 => => transferring context: 2B                                                           0.0s
 => [1/2] FROM docker1.training.lab:5000/alpine:latest                                    0.0s
 => [2/2] RUN apk add --no-cache --update-cache bash                                      2.7s
 => exporting to image                                                                    0.2s
 => => exporting layers                                                                   0.1s
 => => naming to docker.io/library/alpine-bash-2:latest                                   0.0s
 => => unpacking to docker.io/library/alpine-bash-2:latest                                0.0s
```

!!! note "docker build 語法"
    ```
    docker build -t <image_name>:<tag> <path>
    ```
    
    | 參數 | 說明 |
    |------|------|
    | `-t` | 指定 Image 名稱和標籤 |
    | `.` | 指定 Dockerfile 所在目錄（當前目錄） |

!!! info "建置過程說明"
    - `[1/2] FROM`：載入基礎映像
    - `[2/2] RUN`：執行 Dockerfile 中的 RUN 指令（安裝 bash）
    - `exporting to image`：匯出為新的 Image

---

## 10.5 測試新的 Container Image

### 使用新 Image 啟動容器

```bash title="使用新 Image 啟動 Container"
docker run -it --name alpine-3 alpine-bash-2 /bin/bash
```

進入容器後會看到 `bash-5.0#` 提示符號，表示 Bash 已成功安裝。

### 確認 Bash 已安裝

```bash title="確認 bash（在 Container 內執行）"
ls -l /bin/bash
```

**預期結果**：

```
-rwxr-xr-x    1 root     root        735488 May  3  2019 /bin/bash
```

```bash title="退出容器"
exit
```

!!! success "建置成功"
    使用 Dockerfile 建置的 Image 已包含 Bash，與 LAB 09 使用 `docker commit` 的結果相同，但 Dockerfile 方式更具可重現性。

---

## 10.6 清理環境

```bash title="切換到家目錄並清理"
cd
./docker_clean_all.sh
```

**預期結果**：

```
254f09eaadac
9ae97d52cd65
254f09eaadac
9ae97d52cd65
Untagged: alpine-bash-2:latest
Deleted: sha256:fe1c0340426860bdd7792a7e560d3dfbb1c6a4d0bf4caadd5e987a4b71fbd169
Untagged: docker1.training.lab:5000/alpine:latest
Deleted: sha256:d0a0f8e7bf9a6287c7dab568b947b6c3dd6b84e9c67ab9f1e95f79751d808641
```

---

## 10.7 上傳 Docker Image 到 Docker Hub

### 註冊 Docker Hub 帳號

!!! tip "事前準備"
    請先到 [https://hub.docker.com](https://hub.docker.com) 註冊帳號。

### 使用 docker login 登入

```bash title="登入 Docker Hub"
docker login -u <你的帳號>
```

**範例**：

```bash
docker login -u caocharles
```

**預期結果**：

```
Password: 
WARNING! Your credentials are stored unencrypted in '/root/.docker/config.json'.
Configure a credential helper to remove this warning. See
https://docs.docker.com/go/credential-store/

Login Succeeded
```

!!! warning "密碼儲存警告"
    登入後，Docker 會將認證資訊儲存在 `/root/.docker/config.json`，這是 Base64 編碼（非加密），請注意安全。

### 重新建置 Docker Image

```bash title="切換到 Dockerfile 目錄"
cd /root/dockerfile-1
```

```bash title="建置要上傳的 Image"
docker build -t alpine-bash-charles .
```

**預期結果**：

```
[+] Building 0.1s (6/6) FINISHED                                                docker:default
 => [internal] load build definition from dockerfile                                      0.0s
 => CACHED [2/2] RUN apk add --no-cache --update-cache bash                               0.0s
 => exporting to image                                                                    0.0s
 => => naming to docker.io/library/alpine-bash-charles:latest                             0.0s
```

!!! info "CACHED 說明"
    如果之前已建置過相同的層，Docker 會使用快取，加快建置速度。

### 為 Image 加上 Tag

要上傳到 Docker Hub，Image 名稱必須包含你的 Docker Hub 帳號名稱：

```bash title="為 Image 加上 Tag"
docker tag alpine-bash-charles:latest <你的帳號>/alpine-bash-charles:latest
```

**範例**：

```bash
docker tag alpine-bash-charles:latest caocharles/alpine-bash-charles:latest
```

!!! note "docker tag 語法"
    ```
    docker tag <source_image>:<tag> <target_image>:<tag>
    ```
    
    - Target image 格式：`<Docker Hub 帳號>/<Image 名稱>:<tag>`

```bash title="確認 Tag 已建立"
docker images
```

**預期結果**：

```
IMAGE                                   ID             DISK USAGE   CONTENT SIZE   EXTRA
alpine-bash-charles:latest              28024b3ae76e       14.5MB          6.6MB        
caocharles/alpine-bash-charles:latest   28024b3ae76e       14.5MB          6.6MB        
```

!!! info "兩個 Image 使用相同 ID"
    `docker tag` 只是建立一個新的標籤指向同一個 Image，不會佔用額外空間。

---

## 10.8 上傳 Docker Image

### 執行 docker push

```bash title="上傳 Image 到 Docker Hub"
docker push <你的帳號>/alpine-bash-charles:latest
```

**範例**：

```bash
docker push caocharles/alpine-bash-charles:latest
```

**預期結果**：

```
The push refers to repository [docker.io/caocharles/alpine-bash-charles]
77cae8ab23bf: Pushed 
34b2f2a4fe94: Pushed 
01bc7f934740: Pushed 
latest: digest: sha256:28024b3ae76eb1a9400407051085821a6f0a76b1b96cb2f4a92cec35f350d29f size: 855
```

!!! warning "常見錯誤：push access denied"
    如果出現以下錯誤：
    ```
    push access denied, repository does not exist or may require authorization
    ```
    
    **可能原因**：
    
    1. Image 標籤的帳號名稱與登入帳號不符
    2. 尚未登入或登入憑證過期
    
    **解決方案**：
    ```bash
    # 確認使用正確的帳號名稱
    docker tag alpine-bash-charles:latest <正確帳號>/alpine-bash-charles:latest
    
    # 重新登入
    docker logout
    docker login -u <你的帳號>
    ```

---

## 10.9 驗證上傳結果

### 在 Docker Hub 網站確認

1. 開啟 [https://hub.docker.com](https://hub.docker.com)
2. 登入你的帳號
3. 進入 Repositories
4. 確認可以看到剛上傳的 Image

### 清理本地環境並從 Docker Hub 下載

```bash title="清理本地環境"
cd
./docker_clean_all.sh
```

```bash title="確認已清理"
docker images
```

**預期結果**：

```
IMAGE   ID             DISK USAGE   CONTENT SIZE   EXTRA
```

```bash title="從 Docker Hub 下載 Image"
docker pull <你的帳號>/alpine-bash-charles
```

**範例**：

```bash
docker pull caocharles/alpine-bash-charles
```

**預期結果**：

```
Using default tag: latest
latest: Pulling from caocharles/alpine-bash-charles
01bc7f934740: Pull complete 
34b2f2a4fe94: Download complete 
Digest: sha256:28024b3ae76eb1a9400407051085821a6f0a76b1b96cb2f4a92cec35f350d29f
Status: Downloaded newer image for caocharles/alpine-bash-charles:latest
docker.io/caocharles/alpine-bash-charles:latest
```

```bash title="確認下載成功"
docker images
```

**預期結果**：

```
IMAGE                                   ID             DISK USAGE   CONTENT SIZE   EXTRA
caocharles/alpine-bash-charles:latest   28024b3ae76e       14.5MB          6.6MB    
```

!!! success "完成確認"
    成功從 Docker Hub 下載剛才上傳的 Image！

---

## 指令參考

### Dockerfile 基本指令

| 指令 | 說明 | 範例 |
|------|------|------|
| `FROM` | 指定基礎映像 | `FROM alpine:latest` |
| `RUN` | 建置時執行指令 | `RUN apk add bash` |
| `CMD` | 容器啟動時預設指令 | `CMD ["/bin/bash"]` |
| `COPY` | 複製檔案到 Image | `COPY ./src /app` |
| `WORKDIR` | 設定工作目錄 | `WORKDIR /app` |
| `EXPOSE` | 宣告開放的 Port | `EXPOSE 80` |
| `ENV` | 設定環境變數 | `ENV APP_HOME=/app` |

### Docker Hub 相關指令

| 指令 | 說明 | 範例 |
|------|------|------|
| `docker login` | 登入 Docker Registry | `docker login -u username` |
| `docker logout` | 登出 Docker Registry | `docker logout` |
| `docker tag` | 為 Image 加上標籤 | `docker tag image:tag user/image:tag` |
| `docker push` | 上傳 Image | `docker push user/image:tag` |
| `docker pull` | 下載 Image | `docker pull user/image:tag` |

---

## 常見問題

??? question "Q1：docker build 時出現 'no such file or directory' 錯誤？"
    **可能原因**：
    
    1. Dockerfile 檔名不正確（注意大小寫）
    2. 不在正確的目錄
    
    **解決方案**：
    ```bash
    # 確認檔案存在
    ls -la dockerfile
    
    # 使用 -f 指定 Dockerfile 路徑
    docker build -f ./dockerfile -t my-image .
    ```

??? question "Q2：docker push 失敗，顯示 'access denied'？"
    **解決方案**：
    
    1. 確認已登入：`docker login`
    2. 確認 Image 標籤包含正確的帳號名稱
    3. 標籤格式必須是：`<帳號>/<image名稱>:<tag>`

??? question "Q3：Dockerfile 與 docker commit 有什麼差別？"
    | 比較 | docker commit | Dockerfile |
    |------|---------------|------------|
    | 可追蹤性 | 無法追蹤變更 | 可版本控制 |
    | 可重現性 | 難以重現 | 可重複建置 |
    | 自動化 | 手動操作 | 可自動化 |
    | 建議用途 | 測試/除錯 | 生產環境 |

---

## 小結

本章節重點回顧：

- ✅ **Dockerfile**：使用 FROM、RUN、CMD 指令建立客製化 Image
- ✅ **docker build**：根據 Dockerfile 建置 Image
- ✅ **docker login**：登入 Docker Hub
- ✅ **docker tag**：為 Image 加上符合 Docker Hub 格式的標籤
- ✅ **docker push**：上傳 Image 到 Docker Hub
- ✅ **docker pull**：從 Docker Hub 下載 Image
