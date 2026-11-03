# 三节点集群交接说明

集群状态快照来自 2026 年 10 月 28 日的修复验收。三台机器是用户的本地 VMware 测试虚拟机，后续操作通过本机已配置的 SSH MCP 进行。

## 1 节点与连接

| 主机名 | MCP 别名 | IP | SSH 端口 | 用户名 | 本机密钥文件名 |
| --- | --- | --- | --- | --- | --- |
| master | vm01 | 192.168.169.3 | 22 | root | codex_mcp_vm01 |
| node1 | node1 | 192.168.169.4 | 22 | root | codex_mcp_node1 |
| node2 | node2 | 192.168.169.5 | 22 | root | codex_mcp_node2 |

密钥目录是 `C:\Users\TERRENCE\.ssh\codex-mcp`，密钥未设置口令。项目只记录位置与名称，不复制密钥内容。

已有 SSH MCP 的本机位置：

- 实现目录：`C:\Users\TERRENCE\Documents\windows自动化\ssh-mcp`
- 服务器清单：该目录中的 `servers.json`
- Codex 注册：`C:\Users\TERRENCE\.codex\config.toml` 中的 SSH MCP 配置
- 工具：`mcp__ssh__list_servers`、`mcp__ssh__execute_command`

`vm01` 是连接别名，登录后的 Linux 主机名是 `master`。本次项目打包没有迁移 MCP 实现、Python 虚拟环境或全局注册路径。

## 2 集群配置

| 项目 | 值 |
| --- | --- |
| Kubernetes | v1.22.2 |
| containerd | 1.5.5 |
| Flannel | v0.15.0，VXLAN |
| 系统 | CentOS Linux 7 |
| 内核 | 3.10.0-1160.el7.x86_64 |
| API Server | https://192.168.169.3:6443 |
| Pod 网段 | 10.244.0.0/16 |
| Service 网段 | 10.96.0.0/12 |
| CoreDNS Service | 10.96.0.10 |
| 集群域 | cluster.local |
| CRI 接口 | unix:///run/containerd/containerd.sock |

节点 PodCIDR 分别为 master 的 `10.244.0.0/24`、node1 的 `10.244.1.0/24`、node2 的 `10.244.2.0/24`。

Master 约有 2 GiB 内存，两个 Worker 各约 1 GiB。三台机器均关闭 swap，修复验收时没有内存、磁盘或 PID 压力告警。

## 3 本次修复后的关键状态

- 控制平面证书已续签，约在北京时间 2027-10-28 到期，原 CA 保留。
- 三个节点均启用 kubelet 证书自动轮换，客户端配置引用 `kubelet-client-current.pem`。
- `/etc/cni/net.d` 只保留 `10-flannel.conflist`，移除了冲突的 `10-containerd-net.conflist`。
- Flannel DaemonSet 包含 `install-cni` 初始化容器，宿主机挂载范围为 `/run/flannel`。
- containerd 的失效代理 `192.168.169.1:7890` 已清空。
- `containerd.service.d/startup-timeout.conf` 设置 `TimeoutStartSec=300`。
- 三个节点的 kubelet 和 containerd 均为 active、enabled。

## 4 应用状态

| 应用 | 命名空间 | 验收结果 | 入口 |
| --- | --- | --- | --- |
| Nginx | default | 1/1 Ready | http://192.168.169.3:30255 |
| Dashboard | kubernetes-dashboard | 1/1 Ready | https://192.168.169.3:32320 |
| Dashboard metrics scraper | kubernetes-dashboard | 1/1 Ready | 集群内部 Service |

Nginx 使用的固定镜像摘要：

```text
registry.aliyuncs.com/k8sxio/nginx@sha256:f49a843c290594dcf4d193535d1f4ba8af7d56cea2cf79d1e9554f077f1e7aaa
```

Dashboard 使用 `docker.io/kubernetesui/dashboard:v2.3.1`，拉取策略为 `IfNotPresent`，本次依靠已有缓存恢复。新增空白节点时需要单独解决镜像可达性。

## 5 调试经验

节点 Ready 后仍需要测试跨节点通信和 DNS；本次曾出现 Ready 但 Pod 使用错误 `10.88.0.0/16` 网段的情况。

SSH/MCP 超时后先检查远程进程和 systemd 任务。超时关闭 SSH 不保证远程操作已终止，本次有运行时重启继续在服务器执行的情况。

此环境的 systemctl 不支持 `--value`；可通过 `systemctl show -p MainPID containerd | cut -d= -f2` 取得 PID。etcd 镜像中没有 `env` 命令，健康检查直接执行 `etcdctl`。

## 6 后续对话衔接

先阅读 `PLAN.md` 和学习进度。公司 Mac 只用于阅读、讲解和书面考核，不尝试集群连接或要求实时输出；Windows 上仅在用户明确进入集群实操后，才通过已有 SSH MCP 确认实时状态。集群检查命令通常在 master 执行，工作节点主要检查 kubelet、containerd 和本机网络。Linux 配置编辑默认使用 vim。

两份日志记录的是已完成修复，里面包含会修改状态的历史命令，不能整份当成脚本重复执行。本次临时验收命名空间 `codex-check-20261028-0027` 已清理。

## 7 2026-10-29 自动校时维护

三台原有 chronyd 虽运行但仍慢约 23 小时，已配置持续校正大偏差（makestep 1.0 -1，约 64 秒轮询），并新增开机启用的 k8s-time-sync.service。三台同步与服务重新启动验证通过；整机重启和真实 VMware 挂起恢复尚未实测。脚本、备份路径、检查命令和回滚见 [自动校时维护说明](operations/TIME_SYNC.md)。这是后续维护，不改变原交接 ZIP 和清单。
