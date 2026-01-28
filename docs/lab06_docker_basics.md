# LAB 06 Docker 基本操作

## 學習目標

完成本章節後，你將能夠：

- [ ] 使用 `docker run` 啟動容器
- [ ] 使用 `docker ps` 查看容器狀態
- [ ] 使用 `docker logs` 查看容器日誌
- [ ] 使用 `docker inspect` 查看容器詳細資訊
- [ ] 使用 `docker exec` 進入運行中的容器
- [ ] 理解環境變數 `-e` 的使用

## 前置知識

開始之前，請確保你已經：

- 完成 LAB 05 Private Registry 建置
- Docker 已安裝並正常運行
- 已設定 Private Registry（insecure-registries）

---

## 核心概念說明

### Docker 容器生命週期

```mermaid
graph LR
    Image["映像檔"] --> Create["建立"]
    Create --> Running["運行中"]
    Running --> Stopped["停止"]
    Stopped --> Running
    Stopped --> Removed["刪除"]
    Running --> Removed
```

### 常用 Docker 指令

| 指令 | 說明 |
|------|------|
| `docker run` | 建立並啟動容器 |
| `docker ps` | 列出運行中的容器 |
| `docker ps -a` | 列出所有容器（包含停止的） |
| `docker logs` | 查看容器日誌 |
| `docker inspect` | 查看容器詳細資訊 |
| `docker exec` | 在運行中的容器執行指令 |
| `docker stop` | 停止容器 |
| `docker rm` | 刪除容器 |

---

## Lab 實作練習

!!! note "操作環境"
    本 Lab 在 **docker2** 虛擬機上執行。

---

### 步驟 1：啟動 MySQL 容器（背景執行）

使用 `-itd` 參數在背景啟動 MySQL 容器：

```bash title="啟動 MySQL 容器"
docker run -itd -e MYSQL_ROOT_PASSWORD=container docker1.training.lab:5000/mysql:5.6
```

**參數說明**：

| 參數 | 說明 |
|------|------|
| `-i` | 保持標準輸入開啟（interactive） |
| `-t` | 分配偽終端（tty） |
| `-d` | 背景執行（detached） |
| `-e` | 設定環境變數 |

!!! info "MYSQL_ROOT_PASSWORD"
    MySQL 容器**必須**指定 `MYSQL_ROOT_PASSWORD` 環境變數，否則容器會啟動失敗。

驗證：

```bash title="檢查運行中的容器"
docker ps
```

**預期結果**：

```
CONTAINER ID   IMAGE                                    COMMAND                  STATUS         PORTS      NAMES
a28f39cbe620   docker1.training.lab:5000/mysql:5.6     "docker-entrypoint.s…"   Up 10 seconds  3306/tcp   pensive_einstein
```

---

### 步驟 2：使用 --name 指定容器名稱

啟動第二個 MySQL 容器，並指定名稱：

```bash title="啟動並命名容器"
docker run -itd --name mysql-2 -e MYSQL_ROOT_PASSWORD=container docker1.training.lab:5000/mysql:5.5
```

驗證：

```bash title="檢查容器"
docker ps
```

**預期結果**：

```
CONTAINER ID   IMAGE                                    COMMAND                  STATUS         NAMES
4ba163c72270   docker1.training.lab:5000/mysql:5.5     "docker-entrypoint.s…"   Up 5 seconds   mysql-2
a28f39cbe620   docker1.training.lab:5000/mysql:5.6     "docker-entrypoint.s…"   Up 2 minutes   pensive_einstein
```

---

### 步驟 3：查看容器日誌

使用 `docker logs` 查看容器的輸出日誌：

```bash title="查看 mysql-2 日誌"
docker logs mysql-2
```

**預期結果**（部分）：

```
Initializing database
...
MySQL init process done. Ready for start up.
...
mysqld: ready for connections.
Version: '5.5.62'  socket: '/tmp/mysql.sock'  port: 3306  MySQL Community Server (GPL)
```

!!! tip "即時追蹤日誌"
    使用 `-f` 參數可以即時追蹤日誌輸出：
    ```bash
    docker logs -f mysql-2
    ```
    按 `Ctrl+C` 停止追蹤。

---

### 步驟 4：使用 docker inspect 查看容器詳細資訊

`docker inspect` 會輸出容器的完整 JSON 資訊：

```bash title="查看完整資訊"
docker inspect mysql-2
```

輸出內容非常長，包含：

- **State**：容器狀態（運行中、停止等）
- **Config**：容器設定（環境變數、指令等）
- **NetworkSettings**：網路設定（IP 位址等）
- **Mounts**：掛載的 Volume

---

### 步驟 5：使用 -f 格式化輸出

使用 `-f` 參數搭配 Go Template 語法，可以只取出需要的資訊：

```bash title="取得容器 IP 位址"
docker inspect -f '{{ .NetworkSettings.IPAddress }}' mysql-2
```

**預期結果**：

```
172.17.0.3
```

也可以使用 `grep` 過濾：

```bash title="使用 grep 過濾"
docker inspect mysql-2 | grep -i ipadd
```

**預期結果**：

```
            "SecondaryIPAddresses": null,
            "IPAddress": "172.17.0.3",
                    "IPAddress": "172.17.0.3",
```

---

### 步驟 6：使用 docker exec 進入容器

使用 `docker exec` 可以在運行中的容器內執行指令：

```bash title="進入容器執行 bash"
docker exec -it mysql-2 /bin/bash
```

進入容器後，可以執行各種指令：

```bash title="在容器內操作"
# 查看主機名稱
hostname

# 查看 MySQL 版本
mysql --version

# 連線到 MySQL
mysql -u root -pcontainer

# 退出 MySQL
exit

# 退出容器
exit
```

!!! info "exec vs run"
    - `docker run`：建立**新容器**並執行指令
    - `docker exec`：在**已運行**的容器中執行指令

---

### 步驟 7：啟動容器時執行自訂指令

可以在 `docker run` 後面指定要執行的指令（覆蓋預設 CMD）：

```bash title="啟動容器並進入 bash"
docker run -it --name mysql-3 -e MYSQL_ROOT_PASSWORD=container docker1.training.lab:5000/mysql:5.5 /bin/bash
```

這樣容器啟動後會直接進入 bash，而不是啟動 MySQL 服務：

```
root@6502526623f3:/# hostname
6502526623f3
root@6502526623f3:/# exit
```

!!! warning "注意"
    使用自訂指令啟動時，MySQL 服務不會自動啟動！

---

### 步驟 8：停止與刪除容器

```bash title="停止容器"
docker stop mysql-2 mysql-3
```

```bash title="刪除容器"
docker rm mysql-2 mysql-3
```

一次刪除所有停止的容器：

```bash title="刪除所有停止的容器"
docker rm $(docker ps -aq -f status=exited)
```

---

## 清理腳本

建立一個清理所有容器和映像檔的腳本：

```bash title="docker_clean_all.sh"
#!/bin/bash
# 停止所有容器
docker stop $(docker ps -aq)
# 刪除所有容器
docker rm $(docker ps -aq)
# 刪除所有映像檔
docker rmi -f $(docker images -aq)
```

```bash title="設定執行權限"
chmod +x docker_clean_all.sh
```

---

## 常見問題

??? question "Q1：啟動 MySQL 容器失敗"
    **原因**：沒有設定 `MYSQL_ROOT_PASSWORD` 環境變數
    
    **解決方案**：
    ```bash
    docker run -itd -e MYSQL_ROOT_PASSWORD=yourpassword mysql:5.6
    ```

??? question "Q2：docker exec 無法進入容器"
    **原因**：容器已停止或 bash 不存在
    
    **解決方案**：
    1. 確認容器運行中：`docker ps`
    2. 如果沒有 bash，嘗試 `/bin/sh`

??? question "Q3：容器名稱衝突"
    **錯誤訊息**：`Conflict. The container name "xxx" is already in use`
    
    **解決方案**：
    ```bash
    # 刪除舊容器
    docker rm xxx
    # 或使用不同名稱
    docker run --name xxx-new ...
    ```

---

## 小結

本章節重點回顧：

- ✅ **docker run**：使用 `-itd` 背景執行，`--name` 命名，`-e` 設定環境變數
- ✅ **docker logs**：查看容器日誌，`-f` 即時追蹤
- ✅ **docker inspect**：查看容器詳細資訊，`-f` 格式化輸出
- ✅ **docker exec**：進入運行中的容器執行指令

## 延伸閱讀

- [Docker run 官方文件](https://docs.docker.com/engine/reference/run/)
- [Docker exec 官方文件](https://docs.docker.com/engine/reference/commandline/exec/)
- [Docker logs 官方文件](https://docs.docker.com/engine/reference/commandline/logs/)
