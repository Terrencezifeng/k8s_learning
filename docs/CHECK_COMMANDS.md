# 集群日常检查命令

下面的命令用于重新确认集群状态。默认集群命令在 master 执行，各节点本机命令通过对应 SSH MCP 别名执行。

## 1 Master 上检查集群

```bash
kubectl get nodes -o wide
kubectl get pods -A -o wide
kubectl get ds,deploy -A
kubectl get svc -A
kubectl get --raw='/readyz?verbose'
kubeadm certs check-expiration
kubectl get events -A --sort-by=.lastTimestamp
```

正常状态包括三个节点 Ready、CoreDNS 2/2、Flannel 和 kube-proxy 各 3/3，以及 API 返回 `readyz check passed`。历史事件可能包含已恢复故障，要结合时间与当前状态判断。

## 2 Master 上检查 etcd

```bash
kubectl -n kube-system exec etcd-master -- \
  etcdctl --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/healthcheck-client.crt \
  --key=/etc/kubernetes/pki/etcd/healthcheck-client.key \
  endpoint health
```

正常输出包含 `is healthy`。此命令使用容器内现有证书路径，不输出证书或私钥内容。

## 3 三个节点分别检查服务与资源

```bash
hostname
systemctl is-active kubelet containerd
systemctl is-enabled kubelet containerd
systemctl show containerd -p TimeoutStartUSec
journalctl -u kubelet --since '30 minutes ago' --no-pager
journalctl -u containerd --since '30 minutes ago' --no-pager
crictl --runtime-endpoint unix:///run/containerd/containerd.sock ps -a
free -m
df -h /
ls -l /etc/cni/net.d
ip -4 address show cni0
ip -4 route
```

如果节点暂时没有普通 Pod，cni0 可能尚未创建，需要结合实际 Pod 状态判断。配置目录应使用 Flannel 配置，不应重新出现抢先加载的默认 bridge 配置。

## 4 检查 kubelet 证书与轮换配置

在各节点执行：

```bash
openssl x509 -in /var/lib/kubelet/pki/kubelet-client-current.pem \
  -noout -subject -dates
grep 'rotateCertificates:' /var/lib/kubelet/config.yaml
grep -E 'client-certificate:|client-key:' /etc/kubernetes/kubelet.conf
```

最后一条只显示文件路径，不显示内嵌凭据。控制平面证书与 kubelet 客户端证书分别检查。

## 5 检查现有应用入口

在 master 执行：

```bash
for host in 192.168.169.3 192.168.169.4 192.168.169.5; do
  curl --noproxy '*' -sS --max-time 5 -o /dev/null \
    -w '%{http_code}\n' "http://$host:30255"
done

curl --noproxy '*' -k -sS --max-time 5 -o /dev/null \
  -w '%{http_code}\n' https://192.168.169.3:32320
```

修复验收时以上检查均返回 200。Dashboard 的 `-k` 用于当前测试环境的自签名证书探测，只验证 HTTP 响应。

## 6 定位一个异常 Pod

把下面的大写占位符替换为实际命名空间和 Pod 名称后执行：

```bash
kubectl -n NAMESPACE describe pod POD_NAME
kubectl -n NAMESPACE logs POD_NAME --tail=100
kubectl -n NAMESPACE logs POD_NAME --previous --tail=100
```

`--previous` 用于查看存在上一实例时的容器日志。多容器 Pod 可以增加 `-c CONTAINER_NAME` 选择容器。

需要编辑 Linux 配置时默认使用 `vim 路径`。本页只整理检查命令，修复操作应根据当次证据选择。
