# Kubernetes 指令速查表

快速參考 kubectl 常用指令，適合日常操作與考試複習。

---

## 基本操作

### 叢集資訊

| 指令 | 說明 |
|------|------|
| `kubectl cluster-info` | 叢集資訊 |
| `kubectl version` | 版本資訊 |
| `kubectl config view` | 查看設定 |
| `kubectl config get-contexts` | 列出 Context |
| `kubectl config use-context <name>` | 切換 Context |
| `kubectl api-resources` | 列出 API 資源 |
| `kubectl api-versions` | 列出 API 版本 |

### 資源查詢

| 指令 | 說明 |
|------|------|
| `kubectl get <resource>` | 列出資源 |
| `kubectl get pods` | 列出 Pod |
| `kubectl get pods -o wide` | 詳細資訊（含 IP、Node） |
| `kubectl get pods -o yaml` | YAML 格式輸出 |
| `kubectl get pods -o json` | JSON 格式輸出 |
| `kubectl get pods -w` | 持續監看 |
| `kubectl get pods -l app=nginx` | 依標籤過濾 |
| `kubectl get pods -n <namespace>` | 指定 Namespace |
| `kubectl get pods --all-namespaces` | 所有 Namespace |
| `kubectl get all` | 列出常見資源 |

---

## 資源管理

### 建立與套用

| 指令 | 說明 |
|------|------|
| `kubectl apply -f <file.yaml>` | 套用設定 |
| `kubectl apply -f <directory>/` | 套用目錄下所有設定 |
| `kubectl create -f <file.yaml>` | 建立資源 |
| `kubectl create deployment <name> --image=<image>` | 建立 Deployment |
| `kubectl create service clusterip <name> --tcp=80:80` | 建立 Service |
| `kubectl create configmap <name> --from-literal=key=value` | 建立 ConfigMap |
| `kubectl create secret generic <name> --from-literal=key=value` | 建立 Secret |

### 編輯與刪除

| 指令 | 說明 |
|------|------|
| `kubectl edit <resource> <name>` | 編輯資源 |
| `kubectl delete <resource> <name>` | 刪除資源 |
| `kubectl delete -f <file.yaml>` | 依設定檔刪除 |
| `kubectl delete pods --all` | 刪除所有 Pod |
| `kubectl delete pods -l app=nginx` | 依標籤刪除 |

### 詳細資訊

| 指令 | 說明 |
|------|------|
| `kubectl describe <resource> <name>` | 詳細描述 |
| `kubectl describe pod <pod-name>` | 描述 Pod |
| `kubectl describe node <node-name>` | 描述 Node |

---

## Pod 操作

### 執行與存取

| 指令 | 說明 |
|------|------|
| `kubectl run <name> --image=<image>` | 建立 Pod |
| `kubectl exec -it <pod> -- /bin/sh` | 進入 Pod |
| `kubectl exec <pod> -- <command>` | 執行指令 |
| `kubectl logs <pod>` | 查看日誌 |
| `kubectl logs -f <pod>` | 追蹤日誌 |
| `kubectl logs <pod> -c <container>` | 多容器指定 |
| `kubectl logs <pod> --previous` | 前一個容器的日誌 |
| `kubectl logs <pod> --tail=100` | 最後 100 行 |
| `kubectl port-forward <pod> 8080:80` | Port 轉發 |
| `kubectl cp <pod>:<path> <local-path>` | 複製檔案 |

---

## Deployment 管理

### 基本操作

| 指令 | 說明 |
|------|------|
| `kubectl get deployments` | 列出 Deployment |
| `kubectl describe deployment <name>` | 詳細描述 |
| `kubectl scale deployment <name> --replicas=3` | 調整副本 |
| `kubectl set image deployment/<name> <container>=<image>` | 更新 Image |

### 滾動更新

| 指令 | 說明 |
|------|------|
| `kubectl rollout status deployment/<name>` | 查看更新狀態 |
| `kubectl rollout history deployment/<name>` | 查看歷史 |
| `kubectl rollout undo deployment/<name>` | 回滾 |
| `kubectl rollout undo deployment/<name> --to-revision=2` | 回滾到特定版本 |
| `kubectl rollout restart deployment/<name>` | 重啟 |
| `kubectl rollout pause deployment/<name>` | 暫停更新 |
| `kubectl rollout resume deployment/<name>` | 繼續更新 |

---

## Service 管理

| 指令 | 說明 |
|------|------|
| `kubectl get services` | 列出 Service |
| `kubectl get endpoints` | 列出 Endpoints |
| `kubectl expose deployment <name> --port=80` | 建立 Service |
| `kubectl expose deployment <name> --type=NodePort --port=80` | NodePort |
| `kubectl expose deployment <name> --type=LoadBalancer --port=80` | LoadBalancer |

---

## Namespace 管理

| 指令 | 說明 |
|------|------|
| `kubectl get namespaces` | 列出 Namespace |
| `kubectl create namespace <name>` | 建立 Namespace |
| `kubectl delete namespace <name>` | 刪除 Namespace |
| `kubectl config set-context --current --namespace=<name>` | 切換預設 Namespace |

---

## ConfigMap & Secret

### ConfigMap

| 指令 | 說明 |
|------|------|
| `kubectl get configmaps` | 列出 ConfigMap |
| `kubectl create configmap <name> --from-literal=key=value` | 從字面值建立 |
| `kubectl create configmap <name> --from-file=<file>` | 從檔案建立 |
| `kubectl describe configmap <name>` | 檢視內容 |

### Secret

| 指令 | 說明 |
|------|------|
| `kubectl get secrets` | 列出 Secret |
| `kubectl create secret generic <name> --from-literal=key=value` | 建立 Secret |
| `kubectl get secret <name> -o jsonpath='{.data.key}' \| base64 -d` | 解碼 Secret |

---

## PV & PVC

| 指令 | 說明 |
|------|------|
| `kubectl get pv` | 列出 PersistentVolume |
| `kubectl get pvc` | 列出 PersistentVolumeClaim |
| `kubectl describe pv <name>` | 描述 PV |
| `kubectl describe pvc <name>` | 描述 PVC |

---

## Node 管理

| 指令 | 說明 |
|------|------|
| `kubectl get nodes` | 列出節點 |
| `kubectl describe node <name>` | 描述節點 |
| `kubectl top nodes` | 節點資源使用 |
| `kubectl cordon <node>` | 標記節點不可調度 |
| `kubectl uncordon <node>` | 取消標記 |
| `kubectl drain <node>` | 排空節點 |
| `kubectl taint nodes <node> key=value:NoSchedule` | 加上 Taint |

---

## RBAC

| 指令 | 說明 |
|------|------|
| `kubectl get roles` | 列出 Role |
| `kubectl get clusterroles` | 列出 ClusterRole |
| `kubectl get rolebindings` | 列出 RoleBinding |
| `kubectl get clusterrolebindings` | 列出 ClusterRoleBinding |
| `kubectl auth can-i <verb> <resource>` | 檢查權限 |
| `kubectl auth can-i <verb> <resource> --as=<user>` | 模擬使用者檢查 |

---

## 疑難排解

| 指令 | 說明 |
|------|------|
| `kubectl get events` | 查看事件 |
| `kubectl get events --sort-by='.lastTimestamp'` | 依時間排序 |
| `kubectl top pods` | Pod 資源使用 |
| `kubectl top nodes` | Node 資源使用 |
| `kubectl describe pod <name>` | 詳細描述 |
| `kubectl logs <pod> --previous` | 前一個容器日誌 |

---

## 輸出格式

| 格式 | 說明 |
|------|------|
| `-o wide` | 額外欄位 |
| `-o yaml` | YAML 格式 |
| `-o json` | JSON 格式 |
| `-o name` | 只顯示名稱 |
| `-o jsonpath='{...}'` | JSONPath 查詢 |
| `-o custom-columns=...` | 自訂欄位 |

### JSONPath 範例

```bash
# 取得 Pod IP
kubectl get pod <name> -o jsonpath='{.status.podIP}'

# 取得所有 Pod 名稱
kubectl get pods -o jsonpath='{.items[*].metadata.name}'

# 取得所有 Container Image
kubectl get pods -o jsonpath='{.items[*].spec.containers[*].image}'
```

---

## 常用組合指令

```bash title="實用指令"
# 刪除所有 Evicted Pod
kubectl delete pods --field-selector=status.phase=Failed --all-namespaces

# 取得所有 Pod 的 Image
kubectl get pods -o jsonpath="{.items[*].spec.containers[*].image}" | tr -s '[[:space:]]' '\n' | sort | uniq

# 依記憶體使用量排序 Pod
kubectl top pods --sort-by=memory

# 快速建立測試 Pod
kubectl run test --image=busybox --rm -it -- /bin/sh

# 產生 YAML 但不執行
kubectl create deployment nginx --image=nginx --dry-run=client -o yaml

# 匯出現有資源
kubectl get deployment nginx -o yaml > nginx-deployment.yaml
```

---

## minikube 指令

| 指令 | 說明 |
|------|------|
| `minikube start` | 啟動 |
| `minikube stop` | 停止 |
| `minikube delete` | 刪除 |
| `minikube status` | 狀態 |
| `minikube dashboard` | 開啟 Dashboard |
| `minikube ip` | 取得 IP |
| `minikube ssh` | SSH 連線 |
| `minikube service <name>` | 開啟 Service |
| `minikube addons list` | 列出插件 |
| `minikube addons enable <name>` | 啟用插件 |

---

## 快捷別名

```bash title="建議加入 ~/.bashrc 或 ~/.zshrc"
alias k='kubectl'
alias kgp='kubectl get pods'
alias kgs='kubectl get services'
alias kgd='kubectl get deployments'
alias kgn='kubectl get nodes'
alias kd='kubectl describe'
alias kl='kubectl logs'
alias ke='kubectl exec -it'
alias ka='kubectl apply -f'
alias kd='kubectl delete -f'

# 自動補全
source <(kubectl completion bash)
source <(kubectl completion zsh)
```
