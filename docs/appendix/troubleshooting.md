# 疑難排解指南

本章節整理 Docker 與 Kubernetes 常見問題的診斷與解決方法。

---

## Docker 疑難排解

### 1. Docker 服務無法啟動

!!! warning "症狀"
    ```
    Cannot connect to the Docker daemon at unix:///var/run/docker.sock
    ```

**診斷步驟**：

```bash title="檢查 Docker 服務"
# 檢查服務狀態
sudo systemctl status docker

# 查看服務日誌
sudo journalctl -u docker -f

# 檢查 socket 檔案
ls -la /var/run/docker.sock
```

**解決方案**：

```bash
# 啟動 Docker 服務
sudo systemctl start docker

# 設定開機自動啟動
sudo systemctl enable docker

# 如果 socket 問題，重新建立
sudo rm /var/run/docker.sock
sudo systemctl restart docker
```

---

### 2. Permission Denied

!!! warning "症狀"
    ```
    permission denied while trying to connect to the Docker daemon socket
    ```

**解決方案**：

```bash
# 將使用者加入 docker 群組
sudo usermod -aG docker $USER

# 重新登入或執行
newgrp docker

# 驗證群組
groups
```

---

### 3. 容器啟動後立即退出

**診斷步驟**：

```bash title="診斷容器退出"
# 檢視容器狀態
docker ps -a

# 查看退出碼
docker inspect <container> --format='{{.State.ExitCode}}'

# 查看日誌
docker logs <container>

# 查看最後輸出
docker logs --tail 50 <container>
```

**常見原因與解決**：

| 退出碼 | 原因 | 解決方案 |
|--------|------|----------|
| 0 | 正常結束 | 確認 CMD 指令是否為前景程序 |
| 1 | 應用程式錯誤 | 查看日誌找出錯誤 |
| 137 | OOM Killed | 增加記憶體限制 |
| 139 | Segmentation Fault | 檢查應用程式相容性 |
| 143 | SIGTERM | 正常終止信號 |

```bash title="保持容器運行（測試用）"
# 使用 sleep 保持運行
docker run -d --name test ubuntu sleep infinity

# 或使用 tail
docker run -d --name test ubuntu tail -f /dev/null
```

---

### 4. Image 拉取失敗

!!! warning "症狀"
    ```
    Error response from daemon: pull access denied
    Error response from daemon: Get https://registry-1.docker.io/v2/: net/http: request canceled
    ```

**診斷步驟**：

```bash
# 確認 Image 名稱
docker search <image-name>

# 確認網路連線
ping registry-1.docker.io

# 確認 DNS
nslookup registry-1.docker.io
```

**解決方案**：

```bash
# 如需登入
docker login

# 設定 Registry Mirror（國內加速）
# 編輯 /etc/docker/daemon.json
{
  "registry-mirrors": ["https://mirror.example.com"]
}

# 重啟 Docker
sudo systemctl restart docker
```

---

### 5. 磁碟空間不足

!!! warning "症狀"
    ```
    no space left on device
    ```

**診斷步驟**：

```bash title="檢查磁碟使用"
# 檢視 Docker 磁碟使用
docker system df

# 詳細資訊
docker system df -v

# 檢查系統磁碟
df -h
```

**解決方案**：

```bash title="清理資源"
# 清理未使用的資源
docker system prune

# 完整清理（包含未使用的 Image 和 Volume）
docker system prune -a --volumes

# 刪除 dangling Image
docker image prune

# 刪除未使用的 Volume
docker volume prune

# 刪除已停止的容器
docker container prune
```

---

### 6. Port 已被佔用

!!! warning "症狀"
    ```
    Bind for 0.0.0.0:8080 failed: port is already allocated
    ```

**診斷步驟**：

```bash
# 查看 Port 使用情況
sudo lsof -i :8080

# 或使用 netstat
sudo netstat -tlnp | grep 8080

# 查看 Docker 容器使用的 Port
docker ps --format "table {{.Names}}\t{{.Ports}}"
```

**解決方案**：

```bash
# 停止佔用 Port 的程序
sudo kill <PID>

# 或使用其他 Port
docker run -d -p 8081:80 nginx
```

---

### 7. Volume 權限問題

!!! warning "症狀"
    容器內無法寫入掛載的目錄

**解決方案**：

```bash
# 方法 1：調整主機目錄權限
sudo chown -R 1000:1000 /path/to/host/dir

# 方法 2：使用特定 UID 執行容器
docker run -u $(id -u):$(id -g) -v /host:/container image

# 方法 3：使用 SELinux 標籤（RHEL/CentOS）
docker run -v /host:/container:Z image
```

---

## Kubernetes 疑難排解

### 1. Pod 處於 Pending 狀態

**診斷步驟**：

```bash title="診斷 Pending Pod"
# 查看 Pod 事件
kubectl describe pod <pod-name>

# 查看 Events
kubectl get events --field-selector involvedObject.name=<pod-name>

# 檢查節點資源
kubectl describe nodes | grep -A 5 "Allocated resources"
```

**常見原因與解決**：

| 原因 | 說明 | 解決方案 |
|------|------|----------|
| 資源不足 | CPU/Memory 不夠 | 增加節點或減少 requests |
| nodeSelector 不符 | 沒有符合的節點 | 調整 selector 或加 label |
| PVC 未綁定 | PV 不存在或不符合 | 建立符合的 PV |
| Taint/Toleration | 節點有 Taint | 加上 Toleration |

---

### 2. Pod 處於 CrashLoopBackOff

**診斷步驟**：

```bash title="診斷 CrashLoopBackOff"
# 查看日誌
kubectl logs <pod-name>

# 查看前一個容器的日誌
kubectl logs <pod-name> --previous

# 查看詳細狀態
kubectl describe pod <pod-name>

# 檢查退出碼
kubectl get pod <pod-name> -o jsonpath='{.status.containerStatuses[0].lastState.terminated.exitCode}'
```

**常見原因與解決**：

| 原因 | 解決方案 |
|------|----------|
| 應用程式錯誤 | 查看日誌，修復程式 |
| 設定錯誤 | 檢查 ConfigMap/Secret |
| 資源不足 | 增加 memory/cpu limits |
| 健康檢查失敗 | 調整 probe 參數 |
| 依賴服務未就緒 | 使用 initContainer |

---

### 3. Pod 處於 ImagePullBackOff

**診斷步驟**：

```bash
# 查看錯誤訊息
kubectl describe pod <pod-name> | grep -A 10 Events

# 驗證 Image 存在
docker pull <image-name>
```

**解決方案**：

```bash
# 確認 Image 名稱正確
# 確認 Registry 存取權限

# 如果是私有 Registry，建立 Secret
kubectl create secret docker-registry regcred \
  --docker-server=<registry> \
  --docker-username=<username> \
  --docker-password=<password>

# 在 Pod spec 加入 imagePullSecrets
spec:
  imagePullSecrets:
    - name: regcred
```

---

### 4. Service 無法連接

**診斷步驟**：

```bash title="診斷 Service 連線"
# 確認 Service 存在
kubectl get svc <service-name>

# 確認 Endpoints
kubectl get endpoints <service-name>

# 確認 Pod 運行中
kubectl get pods -l <selector>

# 從 Pod 內測試連線
kubectl exec -it <pod> -- curl <service-name>:<port>

# 檢查 DNS
kubectl exec -it <pod> -- nslookup <service-name>
```

**常見原因與解決**：

| 原因 | 解決方案 |
|------|----------|
| Selector 不符 | 確認 Service selector 與 Pod label 一致 |
| Pod 未就緒 | 等待 Pod Ready 或檢查 readinessProbe |
| Port 錯誤 | 確認 port 和 targetPort |
| NetworkPolicy 阻擋 | 檢查 NetworkPolicy 規則 |

---

### 5. ConfigMap/Secret 更新後 Pod 沒有變化

**原因**：Pod 不會自動重新載入 ConfigMap/Secret

**解決方案**：

```bash
# 方法 1：重啟 Deployment
kubectl rollout restart deployment/<name>

# 方法 2：使用 annotation 觸發更新
kubectl patch deployment <name> -p \
  '{"spec":{"template":{"metadata":{"annotations":{"date":"'$(date +%s)'"}}}}}'

# 方法 3：使用 Reloader 工具
# https://github.com/stakater/Reloader
```

---

### 6. PVC 處於 Pending 狀態

**診斷步驟**：

```bash
# 查看 PVC 狀態
kubectl get pvc <pvc-name>

# 查看詳細資訊
kubectl describe pvc <pvc-name>

# 查看可用的 PV
kubectl get pv
```

**常見原因與解決**：

| 原因 | 解決方案 |
|------|----------|
| 無符合的 PV | 建立符合規格的 PV |
| StorageClass 不存在 | 建立 StorageClass 或指定正確名稱 |
| 容量不足 | 減少 PVC 請求或增加 PV 容量 |
| accessModes 不符 | 確認 PV/PVC accessModes 一致 |

---

### 7. Node 處於 NotReady

**診斷步驟**：

```bash
# 查看節點狀態
kubectl describe node <node-name>

# 檢查 kubelet 狀態
ssh <node> "sudo systemctl status kubelet"

# 查看 kubelet 日誌
ssh <node> "sudo journalctl -u kubelet -f"
```

**常見原因與解決**：

| 原因 | 解決方案 |
|------|----------|
| kubelet 停止 | 重啟 kubelet |
| 網路問題 | 檢查節點網路連線 |
| 磁碟壓力 | 清理磁碟空間 |
| 記憶體壓力 | 增加記憶體或減少 Pod |

---

### 8. RBAC 權限問題

!!! warning "症狀"
    ```
    Error from server (Forbidden): pods is forbidden: User "xxx" cannot list resource "pods"
    ```

**診斷步驟**：

```bash
# 檢查權限
kubectl auth can-i list pods --as=<user>

# 檢查角色綁定
kubectl get rolebindings,clusterrolebindings -A | grep <user>

# 詳細檢查
kubectl describe rolebinding <name> -n <namespace>
```

**解決方案**：

```bash
# 建立適當的 Role 和 RoleBinding
kubectl create role pod-reader --verb=get,list,watch --resource=pods
kubectl create rolebinding pod-reader-binding --role=pod-reader --user=<user>
```

---

## 診斷工具

### kubectl debug

```bash
# 建立除錯 Pod
kubectl debug node/<node-name> -it --image=busybox

# 為 Pod 建立除錯容器
kubectl debug <pod-name> -it --image=busybox --target=<container>
```

### 常用診斷指令

```bash title="綜合診斷"
# 快速檢查叢集狀態
kubectl get nodes
kubectl get pods --all-namespaces | grep -v Running

# 檢查系統 Pod
kubectl get pods -n kube-system

# 檢查最近事件
kubectl get events --sort-by='.lastTimestamp' | tail -20

# 檢查資源使用
kubectl top nodes
kubectl top pods --all-namespaces
```

---

## 日誌收集

### 收集診斷資訊

```bash title="收集診斷資訊腳本"
#!/bin/bash
OUTPUT_DIR="k8s-debug-$(date +%Y%m%d-%H%M%S)"
mkdir -p $OUTPUT_DIR

# 節點資訊
kubectl get nodes -o wide > $OUTPUT_DIR/nodes.txt
kubectl describe nodes > $OUTPUT_DIR/nodes-describe.txt

# Pod 資訊
kubectl get pods --all-namespaces -o wide > $OUTPUT_DIR/pods.txt

# Service 資訊
kubectl get svc --all-namespaces > $OUTPUT_DIR/services.txt

# Events
kubectl get events --all-namespaces --sort-by='.lastTimestamp' > $OUTPUT_DIR/events.txt

# 壓縮
tar -czvf $OUTPUT_DIR.tar.gz $OUTPUT_DIR
echo "診斷資訊已儲存至 $OUTPUT_DIR.tar.gz"
```
