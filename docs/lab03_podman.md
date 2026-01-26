# LAB 03 安裝 Podman

## 學習目標

完成本 Lab 後，你將能夠：

- [ ] 理解 Podman 的核心架構 (Daemonless & Rootless)
- [ ] 在 Linux 上安裝 Podman
- [ ] 驗證 Podman 無需守護行程 (Daemon) 即可運作
- [ ] 處理 Image Registry 搜尋順序與驗證問題

---

## 1.1 Podman 簡介

**Podman** (Pod Manager) 是一個由 Red Hat 開發的開源容器引擎，用於在 Linux 系統上開發、管理和執行 OCI (Open Container Initiative) 容器。

- **官方網站**：[https://podman.io/](https://podman.io/)
- **最新文件**：[Podman Documentation](https://docs.podman.io/en/latest/)

### Podman 與 Docker 的關鍵差異

| 特性 | Docker | Podman |
|------|--------|--------|
| **架構** | **Client-Server** (依賴 dockerd 守護行程) | **Daemonless** (直接 Fork/Exec 程序) |
| **執行權限** | 預設需要 **Root** | 原生支援 **Rootless** (一般使用者可執行) |
| **Pod 支援** | 需透過 Docker Compose 或 K8S | **原生支援 Pod** (可在一個 Pod 跑多個容器) |
| **服務相依** | 若 Daemon 掛掉，所有容器都受影響 | 容器是獨立程序，互不影響 |
| **Systemd** | 整合較弱 | 原生整合，容易將容器作成系統服務 |

!!! quote "Podman 的設計理念"
    "Alias docker=podman" —— Podman 的 CLI 指令與 Docker 高度相容，絕大多數情況下，你可以直接把 `docker` 指令換成 `podman` 執行。

---

## 實作步驟

### 步驟 1：安裝 Podman 套件

在 RHEL 9 / Rocky Linux 9 中，Podman 通常已經預裝。如果沒有，可以使用 `dnf` 安裝。

1.  **安裝 Podman**
    ```bash
    dnf install podman -y
    ```
    > **指令說明**：
    > - 套件名稱就是 `podman`，不需要像 Docker 還要去找 `docker-ce`。
    > - 如果系統顯示 `Nothing to do`，表示已經安裝過了。

    ![安裝 podman](images/lab03/podman_install.png)

2.  **檢查版本與環境資訊**
    ```bash
    podman version
    podman info
    ```
    > - `podman version`: 顯示 Client/Server 版本（注意：Podman 的 Client 和 Server 通常是同一個 binary，除非是遠端操作）。
    > - `podman info`: 顯示詳細的系統設定，包括 Storage Driver (通常是 overlay)、cgroup version (v2) 以及預設的 Registry。

---

### 步驟 2：驗證 Daemonless 架構（無需啟動服務）

這是 Podman 最特別的地方：**你不需要啟動任何服務**。

1.  **嘗試尋找 podman 服務**
    在你安裝完 Docker 時，通常下一步是 `systemctl start docker`。但在 Podman：
    
    > 你**不需要**執行 `systemctl start podman`。
    
    Podman 是一個單純的 binary執行檔。當你執行 `podman run` 時，它會直接在當前使用者的權限下產生容器程序。

2.  **為什麼會有 `podman.socket`？**
    如果你檢查 systemd，可能會看到 `podman.socket` 或 `podman.service`。這主要是為了提供 API 給遠端工具（如 Docker Compose 或 IDE）連線使用，對於本地 CLI 操作並非必要。

---

### 步驟 3：使用 Podman 下載 Container Image

Podman 預設會搜尋多個 Registry。

1.  **查看目前的 Image**
    ```bash
    podman images
    ```

2.  **嘗試下載 MySQL Image**
    執行以下指令：
    ```bash
    podman pull mysql
    ```

    **觀察輸出結果：**
    
    Podman 會依序嘗試設定檔 (`/etc/containers/registries.conf`) 中定義的 Registry：

    1.  ❌ **`registry.access.redhat.com/mysql:latest`**
        > `name unknown: Repo not found` (Red Hat 官方庫沒有這個 Image)
    
    2.  ❌ **`registry.redhat.io/mysql:latest`**
        > `unauthorized: Please login` (需要 Red Hat 訂閱帳號才能存取)
    
    3.  ✅ **`docker.io/library/mysql:latest`**
        > 成功從 Docker Hub 下載。

3.  **驗證下載結果**
    ```bash
    podman images
    ```
    > 應該會看到來自 `docker.io/library/mysql` 的 Image。

!!! tip "Registry 搜尋順序並非隨機"
    RHEL/CentOS 預設的 `/etc/containers/registries.conf` 檔案定義了搜尋順序 (Search Registries)。這就是為什麼 Podman 會先去問 Red Hat，最後才問 Docker Hub。
    而 Docker CE 預設只會找 Docker Hub (`docker.io`)。
