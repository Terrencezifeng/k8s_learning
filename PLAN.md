# K8s 当前计划

当前已经完成集群修复及其网络、DNS、应用访问验收。学习进度更新于 2026-11-04：用户已报告学习至 P18，原六道生命周期题、R1–R3 复盘与 C1–C2 收尾均完整作答；init 重试范围与 Never 下 Pod Failed、startup 门控、readiness 失败／恢复、describe／上一实例日志命令及 UID 读取比较均有书面通过证据。综合复习 B1、B2 已提交，B1 主线正确、职责细节待巩固，B2a 的 NotFound／Namespace 查询通过，B2b 的 exec 定位参数正确、命令工具依赖已补充；B3–B5 待答，既有通过结论保留。此前四轮基础实验及清理完成，本轮无新实操。下方区分历史修复成果与学习证据，详细情况见 [学习进度](docs/learning/PROGRESS.md)。

## 1 已完成的工作

- [x] 建立 vm01、node1、node2 三个 SSH MCP 连接别名。
- [x] 检查 Kubernetes、kubelet、containerd、证书和网络状态。
- [x] 续签过期控制平面证书，恢复 API Server 和 etcd 之间的 TLS 通信。
- [x] 恢复 node1、node2 的 kubelet 客户端凭据和证书自动轮换。
- [x] 修正 containerd 默认 bridge CNI 与 Flannel 的配置冲突。
- [x] 补齐 Flannel CNI 初始化步骤，将 /run 挂载收窄到 /run/flannel。
- [x] 清除失效的 containerd 代理配置，调整启动等待时间。
- [x] 修复 Nginx 和 Dashboard 的镜像启动问题。
- [x] 完成验收并清理临时测试 Pod。
- [x] 生成中文 Debug 日志和原始修复记录。

## 2 修复验收标准与结果

| 验收项 | 结果 |
| --- | --- |
| 1 Master + 2 Worker | 全部 Ready |
| etcd 与 API Server | endpoint health 和 readyz 通过 |
| Flannel、kube-proxy | 分别 3/3 Ready |
| CoreDNS | 2/2 Ready |
| 跨节点 Pod 网络 | 6 个通信方向均通过，测试包无丢失 |
| 集群 DNS | 三个节点上的测试 Pod 均能解析集群服务 |
| Service HTTP | 三处测试均获得 Nginx 页面 |
| NodePort | 三个节点的 30255 端口均返回 HTTP 200 |
| Dashboard | 页面探测返回 HTTP 200 |
| 测试资源清理 | 临时命名空间已删除 |

完整证据见 [Debug 日志](logs/k8s-debug-20261028.log)。

## 3 后续学习建议

以下保留修复交接时的阶段目标，并补入截至 2026-10-30 的学习证据。P1–P12 按用户确认记为已学；用户随后已报告学习 P14、P15。课程位置与逐项掌握情况以 [学习进度](docs/learning/PROGRESS.md) 为准，不能把助手的环境修复或预习计入用户独立能力。后续仍在独立实验命名空间内操作，并清理当次创建的资源。

| 阶段 | 学习内容 | 当前证据 | 完成标志 |
| --- | --- | --- | --- |
| 1 基础对象 | Node、Namespace、Pod、Deployment、标签与选择器；查看现有 Nginx | 基础查询、归属与运行位置有实操证据；清单、标签查询、logs／describe／explain 有书面证据；Service 与完整排障待验证 | 能解释 Deployment、Pod、Service 之间的关系，并用 get、describe、logs 排查状态 |
| 2 部署与扩缩容 | 创建实验 Deployment，调整副本，观察调度、自愈和滚动更新 | 已按指导创建、扩为 2 副本、删除单个 Pod 后观察补建并清理；缩容、滚动更新、回滚及脱离提示独立复现待验证 | 能完成一次部署、扩缩容和更新，并说明 Pod 的变化 |
| 3 网络访问 | Pod IP、ClusterIP、NodePort、DNS；观察两个 Worker 之间的通信 | 端口声明不改变真实监听已书面通过；Service 端口关系已讲解未验证，暂无本阶段用户独立访问实验记录 | 能验证 Pod、Service、NodePort 三种访问路径，并解释差别 |
| 4 配置与维护 | ConfigMap、Secret 基本使用、资源请求与限制、事件、日志和证书检查 | 有相关概念补充和历史助手维护，未计作用户独立完成配置或排障 | 能定位一次实验故障，并写出故障现象、证据、原因和处理结果 |

当前依据用户 P16–P18 的学习报告开展 Pod 生命周期场景考核，完整组件协同和按证据定位故障继续按既有状态保留。具体拓展顺序与验证目标见 [学习进度](docs/learning/PROGRESS.md)；本轮仅书面考核，未连接或修改集群。

部署、观察、暴露服务、扩缩容和更新也是 Kubernetes 官方入门教程的主要练习顺序，可参考 [Learn Kubernetes Basics](https://kubernetes.io/docs/tutorials/kubernetes-basics/)。当前集群为 v1.22.2，使用文档示例前需要核对对应版本支持的 API 和字段。

## 4 维护事项

- [ ] 下次使用前重新检查节点、Pod、运行时和网络状态。
- [ ] 在需要升级时单独制定版本迁移计划，不在基础练习中顺带升级整个集群。
- [ ] 控制平面证书到期前检查并续签；本次新证书到期约为北京时间 2027-10-28。
- [ ] 如需长期运行，再规划备份、整机重启验收和资源扩容。

kubelet 自动轮换已恢复，控制平面证书的维护仍需单独安排。相关机制见 [kubeadm 证书管理](https://kubernetes.io/docs/tasks/administer-cluster/kubeadm/kubeadm-certs/)。本项目没有配置新的定时任务。

## 5 本次范围

本次修复依据用户要求跳过了 etcd 和配置备份，没有重建集群或升级 Kubernetes。该选择属于本次测试环境修复记录；后续实验和维护按当次需求确定范围。
