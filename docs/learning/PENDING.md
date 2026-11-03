# 学习暂存

状态：2026-11-02 用户已提交 P16–P18 全部六道场景题，逐项反馈见 4.28。三类探针用途、Service 静态后端选择、退出按 Always 重启与退避等有书面正确证据；init 重试、Never、startup 门控、退出宽限期、TCP 检查、readiness 动态恢复、命令及 UID 区分已纠正／补充待验证。新增三道针对性复盘待答；无本轮实操输出。实际学习时长未知，历史记录尚未归档。

2026-10-28 进行了学习方式和笔记机制配置，未将其计作课程学习；学习时长未知。

当前起点：[查看进展总览、掌握清单和拓展顺序，再按用户后续疑问或实际课程位置继续](PROGRESS.md)。

## 1 2026-10-30 配置补充：Markdown 大纲编号

- 用户通过 Typora 大纲截图提出：已有及后续 Markdown 文档的标题都增加数字标签；随后确认总标题不编号，正文采用 1、2、3，子标题采用 2.1、2.2，更深层采用 2.1.1。
- 已统一整理项目 Markdown 的正文标题，并将后续维护规则写入项目 AGENTS.md、同步到学习者画像；学习记录模板一并采用相同编号。
- 日期、课程 P 编号、原题号、代码与学习证据保留；本次为文档格式配置，不计入学习时长，不改变学习进度或知识验证状态。

## 2 2026-10-29 配置补充：考核回答模板

- 用户要求：考核知识掌握情况时，特别是多个知识点、多道题一起考核时，在最后提供方便填写答案的模板。
- 已写入项目 `AGENTS.md` 并同步到 [学习者画像](PROFILE.md)，适用于本项目所有学习会话。模板须可复制填写，与题号和小问对应，不预填答案；实操题按需留出命令、实际输出和解释的位置。
- 后续续接已布置的第一轮考核时，同样提供对应模板。本次仅调整学习机制，不计入学习时长，不改变既有考核和学习进度的验证状态。

## 3 2026-10-28 既往进度补记

- 用户确认：P13 之前，即 **P1–P12，均按学习完成记录**。
- 已取得并阅读这些章节的字幕，保存 [已学内容回顾](video-notes/P001-P012-已学内容回顾.md)，作为后续讲解的前置背景。
- 实际学习日期、耗时及逐项实验结果未提供，不补造；本次读取资料的等待时间不计入用户学习时长。
- P13 状态不变；没有新增用户报告的卡点。

已准备 [P13 课程笔记初稿](video-notes/P013-什么是资源.md)，基于已校验字幕整理，等待后续学习时追加实际问答与实践证据；它不是已完成的学习记录。

## 4 学习中的问题与解答

### 4.1 2026-10-28：Namespace、Node 与“元数据型资源”的关系

- 来源：本项目学习会话。用户正在学习 P13，未提供精确观看时间；问题对应字幕约 05:21–11:08。课程为 [BV1PbeueyE8V，P13](https://www.bilibili.com/video/BV1PbeueyE8V/?p=13)，CID 为 `500001651183323`。
- 原始问题：希望从命名空间级别、集群级别、元数据型资源理解 K8s 架构。当前理解为集群包含 Namespace 和 Node，每个 Node 内可能有自己的 Namespace，Pod、ConfigMap 在其中运行，元数据资源依附于其他资源。
- 课程内容：复用已校验的 255 条中文 AI 字幕；课程区分命名空间级别、集群级别和“元数据型资源”，后者举到 HPA、Pod 模板、资源限制。没有重新查看课件或核对音频，不能将字幕措辞当作精确原话。
- 助手补充解释：
  - 集群是整体系统；“集群级别”表示 API 资源不属于某个 Namespace，不表示它是所有其他资源的父对象。Node、Namespace 本身都是集群作用域资源。
  - Namespace 是逻辑管理与命名范围，Node 是 Pod 的运行位置。一个 Namespace 的不同 Pod 可以运行在不同 Node；同一 Node 可以运行来自不同 Namespace 的 Pod。单个 Pod 调度到一台 Node，其中的容器运行在该 Node 上。
  - ConfigMap 是独立的配置数据对象，不是运行在 Node 上的进程。Pod 可以通过环境变量或挂载文件使用同 Namespace 的 ConfigMap。
  - API 作用域分为 namespaced 与 cluster-scoped。“元数据型资源”是课程的教学分类，不是第三种 API 作用域，也不能直接等同于 YAML 的 `metadata`。
  - `metadata` 是对象字段，包含名称、标签等，命名空间对象的归属可由 `metadata.namespace` 表示。HPA 自身是独立的命名空间级 API 对象，引用目标工作负载来调整 Pod 副本数，不负责增加 Node。Deployment 中的 Pod 模板以及容器 requests/limits 则是嵌入配置，不能一概认为都属于独立 API 对象。
  - 组件与资源对象也需区分：API Server 接收对象操作，etcd 保存对象数据，控制器协调状态，Scheduler 为 Pod 选 Node，Node 上的 kubelet 与 containerd 负责落实运行。
- 官方核对：[Namespaces](https://kubernetes.io/docs/concepts/overview/working-with-objects/namespaces/)、[ConfigMaps](https://kubernetes.io/docs/concepts/configuration/configmap/)、[集群组件](https://kubernetes.io/docs/concepts/overview/components/)、[v1.22 官方 HPA 文档源码](https://github.com/kubernetes/website/blob/release-1.22/content/en/docs/tasks/run-application/horizontal-pod-autoscale.md)。实验版本依据既有 v1.22.2 快照，未连接服务器刷新实时状态。
- 用户掌握证据：首次提问暴露了 Namespace 与 Node 的层级混淆，以及“元数据型资源”与对象字段的混淆。随后对“dev 的两个 Pod 分别在 node1、node2，共几个 dev Namespace”回答：“1个，namespace跟pod和node无关，namespace的数量需要命令创建”。数量判断正确，但“与 Pod 无关”的理由不准确。
- 复盘补充（助手解释）：Pod 属于某个 Namespace，同时可以被分配到某台 Node；Namespace 不隶属于 Node，其数量不会随 Pod 或 Node 的数量自动增加。Namespace 的数量取决于集群中实际存在的 Namespace 对象；可以通过命令、提交 YAML 或其他 API 客户端创建，集群也有预置命名空间，并非全部需要用户手动创建。
- 验证与状态：**部分口头验证，仍有待巩固点**。已验证本例数量判断；上述理由纠正尚无用户再次复述，metadata／HPA 区别仍未验证。没有执行集群命令；示意分布不代表当前集群实际状态。
- 学习时长：未知；保持草稿，不生成达到半小时的正式记录。
- 下一步：巩固“Pod 属于 Namespace、运行在 Node”的双重关系；随后可由用户在 master 执行 `kubectl get pods -A -o wide`，对照 NAMESPACE 与 NODE 列。不能预先保证现有 Pod 恰好覆盖所有示例组合。

### 4.2 2026-10-28 临时会话补充：Pod 创建、调度与配置读取

- 来源：用户在临时会话中的两次追问，并明确要求将内容补入学习笔记；完整解释、流程图、只读命令及逐问解答已追加到 [P13 笔记](video-notes/P013-什么是资源.md)。原有问答保留。
- 问题一：先创建 Pod 还是先选择 Node？Pod 未运行会怎样，调度是否依据 Deployment 配置？答：先创建 API 对象，再选择和绑定 Node，最后启动容器；Pending 既可能是未调度，也可能是已调度但尚未完成启动准备。调度依据生成后的 Pod 配置及集群情况，先筛选再评分。
- 问题二：生成后的 Pod 配置在哪里，是否是 RC 生成的配置文件？答：Deployment 使用 RS；控制器通过 API Server 创建 Pod 对象，数据由 etcd 保存。调度器经由 API Server 获取和监听对象；`kubectl get pod ... -o yaml` 是读取对象并格式化输出，不是查找生成的磁盘文件。
- 资料分类：本次为助手补充与真实用户问答，已查阅官方资料；没有新增视频字幕、关键帧或课程时间戳。
- 掌握证据：用户表示讨论有意义并要求记录；尚无独立复述和实操输出。两问均标记 **已解释未验证**。
- 实际学习时长：未知；保持暂存状态，不据此生成半小时正式记录，也不标为正式归档。
- 后续验证：由用户在 master 查看 Pod 列表及某个 Pod 的 YAML，区分对象存在、节点绑定和容器运行，并辨认 `metadata`、`spec`、`status`。本次只更新学习文档，未执行集群命令。

### 4.3 2026-10-28：P14 提到的微服务是什么？

- 来源与原始问题：用户报告正在学习第 14 集，其中提到“微服务”，希望简单解释其含义。课程沿用 [BV1PbeueyE8V，P14](https://www.bilibili.com/video/BV1PbeueyE8V/?p=14)；未提供播放时间，本次未读取 P14 字幕或关键帧，标题、CID、时长尚未核对，不复用 P13 CID。
- 资料分类：这是助手围绕真实提问补充的通用概念解释，不是 P14 课程内容摘要。定义参考 [AWS 微服务说明](https://aws.amazon.com/microservices/)。
- 助手解答：微服务是一种按业务能力将应用拆成多个职责明确、可独立部署的服务的架构；服务通过网络接口或消息协作。以电商为例，用户、商品、订单、支付可以由一个整体应用提供，也可以拆为分别运行和发布的服务。拆分后可单独更新或扩容某个服务，代价是增加网络调用、故障排查和数据一致性处理的复杂度，服务并非拆得越小越好。
- 运维与 K8s 衔接：Docker 可以打包运行这些服务，K8s 可以管理其部署、副本与故障恢复；微服务不要求必须使用 Docker 或 K8s。一个订单服务运行 3 个 Pod，通常表示同一个微服务的 3 个副本，不能仅凭 Pod 数量判断微服务数量。
- 用户掌握证据与状态：用户主动询问定义；**已解释未验证**，没有用户复述或实操结果。转入 P14 不代表 P13 的全部卡点已验证解决。
- 实际学习时长：未知，保持暂存，不生成正式记录。
- 下一步：沿 P14 继续，按需用“3 个订单服务副本与用户／订单／支付 3 个不同服务”复盘业务拆分与副本数量的区别。

### 4.4 2026-10-29：kubectl 命令入门与小测试考核

- 用户请求：准备运行虚拟机集群进行 K8s 小测试，希望提供考核；自述尚不熟悉 K8s 命令，要求先介绍命令。
- 范围与操作分工：用户亲手启动虚拟机、登录 master 并执行；助手讲解、出题和根据输出反馈，本次未连接服务器或执行集群操作。沿用 P13／P14 概念作为练习背景，不声称这些题目来自 P14 视频。
- 环境依据：历史快照为 Kubernetes v1.22.2，master、node1、node2；本次第一步读取实时版本和状态，不能把 2026-10-28 验收状态当作重启后的结果。
- 助手讲解：kubectl 经由 API Server 管理集群；资源操作常用结构为 `kubectl 动作 资源类型 [名称] [选项]`。get 查看列表／对象，describe 查看详情与相关事件，logs 查看容器日志，create／apply／scale／delete 用于后续对象变更。强调 `-n` 指定 Namespace，`-A` 查询所有 Namespace，`-o wide` 增加表格列，`-o yaml` 以 YAML 显示；不指定 Namespace 时使用当前上下文的命名空间，未配置则通常为 default。
- 四轮安排：①只读观察并解释 Node／Namespace／Pod 的关系；②确认环境后，在新建专用命名空间 `k8s-lab-20261029` 创建一个 Nginx Deployment；③扩为 2 个副本并比较 Deployment、ReplicaSet、Pod，不要求副本一定分散到两台 Node；④只删除实验中受控的单个 Pod，验证控制器补建，并在核对归属后清理当次实验资源。命名空间若已存在需先核对，不直接覆盖或删除。后面三轮暂未下发具体变更命令，待第一轮结果后逐轮教学。
- 第一轮执行位置：master（历史 IP `192.168.169.3`）的 Linux 终端。命令：`kubectl version -o yaml`、`kubectl get nodes -o wide`、`kubectl get namespaces`、`kubectl get pods -A -o wide`。讲解示例另用 `kubectl get pods -n default -o wide`。
- 预期观察：version 输出 clientVersion／serverVersion 的 gitVersion；节点表观察名称、STATUS、INTERNAL-IP，历史预期为三台 Ready；Namespace 表列出实际命名空间；Pod 表观察 NAMESPACE、NAME、READY、STATUS、NODE，未调度 Pod 的 NODE 可为 `<none>`。这些是观察目标，不是运行结果，也不是完整集群健康验收。
- 第一轮考题（助手布置，不冒充用户提问）：有几个 Node、是否 Ready；找出一个 Pod 的名称、Namespace 与 Node；解释 READY 的 `1/1`；自行写出只看 kube-system 中 Pod 并显示运行节点的命令。允许查询帮助，按命令、输出与解释评估。
- 官方核对：[kubectl 命令结构](https://kubernetes.io/docs/reference/kubectl/)、[查询速查表](https://kubernetes.io/docs/reference/kubectl/quick-reference/)、[v1.22.2 对应 kubectl version 实现](https://github.com/kubernetes/kubectl/blob/v0.22.2/pkg/cmd/version/version.go)。version 的 YAML 输出已核对旧版支持；实际客户端／服务端版本仍待用户输出。
- 证据与状态：**已讲解、已布置，未执行／未验证**。没有虚构输出，没有据此记为用户掌握；学习时长未知，保持暂存。
- 下一步：接收四条基础查询输出与四个考题的回答。若出现连接失败、NotReady 或异常 Pod，保留原始错误并收集证据后排障，再决定后续创建实验。

### 4.5 2026-10-29：第一轮提交与 READY 纠正

- 来源：用户提交第一轮 4 道考题的命令、输出与解读；这是实际操作证据，不是助手代操作或模拟输出。记录时保留核心事实，不用 AGE、RESTARTS 的时间推算学习时长。
- 第 1 题：用户执行 `kubectl get nodes`，输出 master、node1、node2 均 Ready，VERSION 均为 v1.22.2；回答“3 个 node，都 ready”。**正确**。VERSION 列代表节点 kubelet 版本，尚未收到此前布置的客户端／API Server 版本查询。
- 第 2 题：用户从全局 Pod 表识别 `etcd-master` 属于 `kube-system`、运行在 `master`。**正确**，提供了 Namespace 归属与 Node 运行位置的读表证据。所贴全局表共 15 个 Pod，均 Running、READY 1/1；其中 default/nginx-5d54fb6d7f-bfdwt 在 node2、IP 10.244.2.2。全局查询粘贴命令是 `kubectl get pods -A`，但输出含 IP／NODE 等 wide 列，存在记录不一致，原因未确认；不擅自补成用户已输入 `-o wide`。
- 第 3 题原回答：认为 READY 前一个 1 是 ready 的 Pod 个数，后一个 1 是这个 Node、Namespace 中同名 etcd-master Pod 的总数。**错误，待纠正后复盘**。
- 助手补充：在当前 v1.22 的 `kubectl get pods` 表中，一行表示一个 Pod；READY 的分子是该 Pod 内已就绪的普通容器数，分母是该 Pod 配置的普通容器总数。etcd-master 的 1/1 表示这个 Pod 中 1 个普通容器、该容器已就绪。0/1、1/2、2/2 同理；不要与应用副本数或 Node 上的 Pod 数量混淆。容器 Running 与 Ready 不是同一个判断。
- 第 4 题：用户独立组合并执行 `kubectl get pods -n kube-system -o wide`，所贴输出共 12 个 kube-system Pod，含 NODE 列。**正确**。表中同一个 kube-system Namespace 的 Pod 分布在 master、node1、node2，能用于复盘命名空间与运行节点的交叉关系。
- 状态汇总：**4 题中 3 题正确；第 3 题已解释未验证**。已验证查询与读表的具体能力，不据此认定掌握所有 kubectl 命令，也不将列表正常记为完整网络验收。version 和 namespaces 两条原定查询的输出尚未提供，执行情况未知。
- 只读补充练习：在 master 执行 `kubectl describe pod etcd-master -n kube-system`，用途是查看该 Pod 内的容器详情；预期可在 `Containers:` 中看到容器名、State、Ready 等字段。命令尚未执行，不预填实际输出。依据 [官方 Pod 排查说明](https://kubernetes.io/docs/tasks/debug/debug-application/debug-running-pod/)。
- 助手补充考题：①假设有 3 个 Pod，每个含 2 个普通容器且全部就绪，列表有多少行（不含表头）、每行 READY 是什么；②其中一个 Pod 有一个容器未就绪，它的 READY 是什么；③执行上述 describe，提供 Containers 中容器名称与 Ready 的相关原文。按项目新约定在消息末尾附空白作答模板，不替用户填写。
- 下一步：接收这次 READY 复盘与容器详情，随后继续第二轮创建实验。实际学习时长仍未知，不形成正式归档。

### 4.6 2026-10-29：READY 复盘通过，多容器 describe 问答与第二轮布置

- 用户真实问题：一个 Pod 里有多个容器时，`kubectl describe pods` 的 Containers 下是否分别有多个容器的描述？助手解答：指定 Pod 名称后，Containers 下按普通容器名称分别列出 Image、State、Ready 等信息；`pod` 和 `pods` 均可用。不指定 Pod 名称时会描述查询范围内的多个 Pod，应区分 Pod 之间的分段与单个 Pod 内的容器分段。
- 复盘证据：用户解释 3 个 Pod 各有 2 个容器且全部就绪时，输出 3 行、每行 READY 为 2/2；其中一个 Pod 只有一个容器就绪时为 1/2。两题均正确，原先把 READY 当 Pod 数量的误解已通过这次复述纠正。
- 实操证据：用户实际贴出 `kubectl describe pods etcd-master -n kube-system | grep -Ei 'namespace|Ready'`，输出为 Namespace kube-system、缩进的 `Ready: True`、条件行 `Ready True` 与 `ContainersReady True`。填写的“执行命令”一栏写成 `-n kubesystem`，实际终端命令为正确的 `-n kube-system`；不把未展示的错误命令推定为已运行失败。
- 助手解释：缩进的 `Ready:` 是 Containers 中的单个容器状态；Conditions 中 ContainersReady 汇总容器就绪情况，Ready 表示 Pod 整体的就绪条件（还可能受 readiness gates 等因素影响）。过滤结果丢失 Containers／Conditions 标题及容器名称，所以不能把三个 True 当作三个容器。当前证据验证了 describe 查询成功，但未保留容器名称，不能替用户补造。
- 第一轮状态：核心考点已通过；容器名原文未提供，容器与 Pod 条件的区分属于本次新补充、未独立验证。学习时长未知，保留草稿。
- 第二轮目标与边界：由用户在 master 新建专用 Namespace `k8s-lab-20261029`，创建名为 `web` 的 Nginx Deployment，期望 1 个副本；观察 Deployment → ReplicaSet → Pod。沿用交接中验证过的镜像 `registry.aliyuncs.com/k8sxio/nginx@sha256:f49a843c290594dcf4d193535d1f4ba8af7d56cea2cf79d1e9554f077f1e7aaa`；不能保证目标调度节点已有缓存或此刻镜像仓库可达。第二轮不做扩缩容、对外暴露或清理，保留对象用于后续练习。
- 本轮命令（已布置、未执行）：先补 `kubectl version -o yaml`、`kubectl get namespaces`；新命名空间不存在时执行 `kubectl create namespace k8s-lab-20261029`，再执行 `kubectl create deployment web --image=registry.aliyuncs.com/k8sxio/nginx@sha256:f49a843c290594dcf4d193535d1f4ba8af7d56cea2cf79d1e9554f077f1e7aaa --replicas=1 -n k8s-lab-20261029`；查询 `kubectl get deployments,replicasets,pods -n k8s-lab-20261029 -o wide`。若 Namespace 已存在，先提供输出核对来源，不直接复用、覆盖或删除。前置查询失败或版本与记录不符时先贴输出核对。
- 预期结果：新 Namespace 与 Deployment 创建成功；正常情况下控制器建立 1 个 ReplicaSet、1 个 Pod，Pod 最终 Running、READY 1/1。创建成功仅表示 API 接受对象，不保证容器已运行。Deployment 表的 READY 表示就绪 Pod 副本数／期望副本数，Pod 表的 READY 表示就绪容器数／容器总数。若未就绪，查看对应实验 Pod 的 describe 与 Events 后分析，不根据状态名称直接断定根因。
- 第二轮考题：①贴前置版本、Namespace 查询及两条创建命令的输出；②贴组合查询的完整输出，记录三类对象的数量及 Pod 的名称、Namespace、Node、READY；③说明自己直接创建的工作负载对象，以及其余对象由谁创建。消息末尾按顺序提供空白作答模板。
- 官方参考：[describe 排查说明](https://kubernetes.io/docs/tasks/debug/debug-application/debug-running-pod/)、[create deployment 参数](https://kubernetes.io/docs/reference/kubectl/generated/kubectl_create/kubectl_create_deployment/)。只使用旧版已有的基础命令；实时客户端／API Server 版本仍待前置查询提供。
- 后续起点：评阅第二轮真实输出和用户解释，再推进扩容测试；本次助手没有连接服务器或代执行任何实验。

### 4.7 2026-10-29：三台虚拟机自动校时与 K8s 时间依赖

- 用户真实请求：发现虚拟机关机/开机后时间不对，明确要求助手连接三台机器配置开机和挂起恢复自动校时，并解释对 K8s 的影响。
- 分类：助手代操作的环境维护与补充问答，不是视频课程摘要，也不是用户独立实操证据；实际学习时长未知，保留暂存。
- 变更前：三台 chronyd 已启用、NTP 来源可达，但 System time 仍慢约 82534–82543 秒；原 makestep 1.0 3 限制了后续大偏差的直接修正；三台没有 open-vm-tools。时区本来已是 Asia/Shanghai。
- 已实施：保留现有 NTP 来源，将轮询设为约 64 秒、makestep 1.0 -1；新增 root 管理的 /usr/local/sbin/k8s-time-sync 和开机启用的 k8s-time-sync.service。开机脚本等待实际同步后写 UTC RTC；挂起恢复由持续运行的 Chrony 自动校正。网络离线时不能保证立即同步。
- 验证：三台时间已恢复，NTP synchronized=yes，helper 成功、两服务 enabled；重新启动时间服务时出现的 DNS 初始化 503 已修复并在三台重测通过。三个节点 Ready，最终 16 个 Pod Running/1/1，API readyz、Nginx 和 Dashboard 检查通过。助手实查客户端/API Server 均 v1.22.2，这不替代用户自己的版本查询证据。
- 边界：未实际重启整机、挂起恢复或断网演练。检查时观察到 k8s-lab-20261029 的 web Pod，非本会话创建，未修改该实验资源。第二轮学习评阅继续依据用户提交的输出。
- 问答解答：大时间偏差可影响 TLS 证书有效期、带期限 Token、CronJob 调度、日志/事件/AGE、监控与业务容器内的时间逻辑；认证中断可能间接造成节点状态异常。不能认为有时差就必定 NotReady 或 etcd 数据损坏。容器通常共享 Node 时钟；NTP 同步和时区显示是不同问题。
- 状态：服务层面修复已验证；真实挂起恢复待下次操作后验证；概念已解释、用户理解未考核。
- 细节、脚本、真实输出、备份与回滚：[自动校时维护说明](../operations/TIME_SYNC.md)、[原始验收输出](../../logs/time-sync-20261029.json)。
- 本问题下次起点：实际恢复三台虚拟机后分别查 date、chronyc tracking、timedatectl status，再查集群；原 P14/第二轮学习起点保留。

### 4.8 2026-10-29：第二轮提交——查询范围与对象类型纠正

- 用户实操证据：`kubectl version -o yaml` 中 clientVersion.gitVersion 与 serverVersion.gitVersion 均为 v1.22.2。Namespace 列表为 default、kube-flannel、kube-node-lease、kube-public、kube-system、kubernetes-dashboard，6 个均 Active；未显示实验 Namespace。该列表可能来自创建前，不能据此推断当前实验 Namespace 不存在。
- 用户组合查询：`kubectl get pod,deployment,rs -o wide`，未指定 `-n`。显示 Pod nginx-5d54fb6d7f-bfdwt（Running，1/1，node2，IP 10.244.2.2）、Deployment nginx（READY 1/1）及两个 RS：nginx-5d54fb6d7f 为 DESIRED/CURRENT/READY=1/1/1，nginx-847bc9794 为 0/0/0。用户计数 1 Deployment、2 RS、1 Pod，及对 Pod READY 的解释均正确。
- 关键范围问题：本次表格是已有 nginx，没有显示本轮目标 web。没有 `-n` 时使用当前上下文的 Namespace，未配置时通常为 default；前一条 create 命令的 `-n k8s-lab-20261029` 不会改变后一条查询的范围。结合此前用户全局表，同名 nginx Pod 属于 default，但本次表格本身没有 Namespace 列，应显式查询确认目标作用域。
- 资源身份问题：用户将 `pod/nginx-5d54fb6d7f-bfdwt` 填入“所属 Namespace”，Pod 名称栏留空。助手纠正：`pod/` 是混合资源查询中的类型前缀，名称是 nginx-5d54fb6d7f-bfdwt，整段不是 Namespace。
- 用户创建命令：贴出了 `kubectl create deployment web --image=registry.aliyuncs.com/k8sxio/nginx@sha256:f49a843c290594dcf4d193535d1f4ba8af7d56cea2cf79d1e9554f077f1e7aaa --replicas=1 -n k8s-lab-20261029`，但未贴 Namespace／Deployment 创建回显。用户认为直接创建的对象是“web 的 pod”；助手纠正为名称为 web 的 Deployment。create 后的 deployment 指定对象类型，web 指定该对象的名称。
- 创建关系回答：用户回答控制器创建 RS、RS 控制创建 Pod 并保证 replicas 数量，方向基本正确。精确表述为 Deployment 控制器根据 Deployment 创建／管理 RS，ReplicaSet 控制器根据 RS 创建／维护 Pod，操作通过 API Server 完成；RS 对象本身不是执行代码的进程。
- 两个 RS 的补充解释：对象数量与副本数不同；输出中一个 RS 期望并拥有 1 个 Pod，另一个期望与当前均为 0，因此不要求有两个 Pod。两个 RS 使用不同镜像，这与更新后保留旧 RS 的现象一致；Deployment 可保留旧 RS 供回滚，不把“新实验预期 1 个 RS”推广成任何 Deployment 永远只有 1 个 RS。具体归属和更新历史需 ownerReferences／describe／rollout history 进一步证实，不仅凭名称断言。
- 跨记录证据边界：上方自动校时维护记录曾观察到 k8s-lab-20261029 中的 web Pod，这是另一会话的历史代操作检查证据；不替代本轮用户查询，也不据此断定此刻状态。优先只读核查，不重复创建或删除现有对象。
- 本次反馈状态：版本、既有资源计数、Pod READY 已验证；第二轮 web 创建与运行的本轮证据待补充；Namespace／对象类型纠正已解释未验证。学习时长未知，不依据 AGE 或时间校正推算。
- 后续命令：由用户在 master 执行 `kubectl get namespace k8s-lab-20261029` 与 `kubectl get deployment,rs,pods -n k8s-lab-20261029 -o wide`。用途为确认实验 Namespace 是否存在及其中真实对象；有 NotFound 或 No resources found 也保留原始输出，先判断状态再决定创建或修复。
- 补充考核：①贴上述两条查询原始输出；②根据实验结果填写 Deployment 名称、Pod 名称、Namespace、Node（没有则写未找到）；③复述 create deployment web 直接创建的对象类型，以及 -n 是否会自动影响下一条查询。末尾提供与题目对应的空白作答模板。
- 官方参考：[Deployment 的更新与旧 ReplicaSet 保留](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)、[ReplicaSet 控制机制](https://kubernetes.io/docs/concepts/workloads/controllers/replicaset/)。属于助手补充，不冒充视频课程内容。

### 4.9 2026-10-29：第二轮通过，-A／默认 Namespace 补充与第三轮布置

- 用户实际查询：`kubectl get namespace k8s-lab-20261029` 返回 Active；`kubectl get deployment,rs,pods -n k8s-lab-20261029 -o wide` 返回 Deployment web（READY 1/1，UP-TO-DATE 1，AVAILABLE 1）、RS web-5dcdf98765（DESIRED/CURRENT/READY 均 1）和 Pod web-5dcdf98765-d2pld（Running，READY 1/1，RESTARTS 0，IP 10.244.1.4，NODE node1）。这些是用户提交的实操证据，原创建回显仍未提供，但后续查询已验证对象存在和运行。
- 用户回答：Deployment 名称 web、Pod 名称 web-5dcdf98765-d2pld、Namespace k8s-lab-20261029、Node node1，均正确；明确 create deployment web 直接创建 deployment，且 -n 不影响下一条命令，均正确。第二轮核心考点通过。
- 用户额外命令：`kubectl get pods -n k8s-lab-20261029 -A -o wide | awk 'NR == 1 || tolower($0) ~ /k8s-lab-20261029|web/'`，过滤后显示上述实验 Pod。
- 助手补充：`-A` 表示跨所有 Namespace 查询，会忽略 `-n` 指定的范围；随后 awk 只是本地筛选已返回的行。全行正则匹配 web 也会匹配其他 Namespace 中包含该词的对象，不能等同于精确指定 Namespace。本实验直接使用 `-n k8s-lab-20261029` 即可。
- 默认 Namespace 纠正：用户说“不加 -n 默认用 default”，需要补充为“使用当前上下文配置的 Namespace，未设置时才回退为 default”。这一细节和参数优先级已解释，尚未独立复述验证。
- 第三轮范围：继续由用户在 master 操作同一个实验 Deployment web，把期望副本从 1 改为 2；不修改 Pod 模板、不增加 Namespace，不操作 default 的 nginx。命令为 `kubectl scale deployment web --replicas=2 -n k8s-lab-20261029`，然后 `kubectl get deployment,rs,pods -n k8s-lab-20261029 -o wide`。
- 预期（不是实际结果）：scale 回显 deployment.apps/web scaled 仅表示期望副本数更新成功；控制器协调完成后，1 个 Deployment、原来的 1 个 RS、2 个 Pod。Deployment READY 2/2，RS DESIRED/CURRENT/READY 均为 2，每个 Pod 内仍为 1 个容器、各自 READY 1/1。扩容复制 Pod 模板，不是给原 Pod 增加容器；没有显式分散约束，不要求两个 Pod 必须位于不同 Node。
- 如需观察变化：在 master 执行 `kubectl get pods -n k8s-lab-20261029 -o wide -w`，-w 持续观察，Ctrl+C 仅退出观察；此命令为可选辅助，未执行。
- 第三轮考题：①贴 scale 回显和组合查询完整输出；②根据实际输出填写 Deployment／RS／Pod 数量，以及每个 Pod 的名称、Namespace、Node；③解释 Deployment 的 READY 与各 Pod 的 READY 分别统计什么，扩容改变的是 Pod 数量还是原 Pod 内容器数量。按顺序提供空白模板，允许写不确定或未执行。
- 官方核对：[get 的 -A 参数](https://kubernetes.io/docs/reference/kubectl/generated/kubectl_get/)、[scale 命令](https://kubernetes.io/docs/reference/kubectl/generated/kubectl_scale/)。基础命令适用于已由用户确认的 v1.22.2。
- 状态与边界：第二轮已验证；第三轮已讲解、已布置、未执行验证；实际学习时长未知，保持暂存。助手未连接服务器或代操作。

### 4.10 2026-10-29：kubectl 的 Tab 自动补全

- 用户真实问题：在三台虚拟机使用 kubectl 时，输入 Namespace 名称的唯一前缀仍无法按 Tab 补全，希望了解可用工具。
- 助手解释：使用 bash-completion 与 kubectl 自带的 Bash 补全脚本；Shell 通过脚本理解子命令、参数，资源名称补全还依赖当前用户的 kubeconfig、API 可达性和查询权限。唯一前缀也需要先加载补全功能。
- 环境依据：本会话此前实际核对 CentOS 7、kubectl/服务端 v1.22.2。此次没有重新连接服务器，未检查三台当前交互式 Shell、bash-completion 安装情况或用户 kubeconfig，不将缺少软件包直接断言为已证实根因。
- 提供的亲手操作步骤：先在 master 的 Bash/root 会话执行 yum install -y bash-completion；用 vim ~/.bashrc，在保留原内容的前提下追加 source /usr/share/bash-completion/bash_completion 和 source <(kubectl completion bash)；执行 source ~/.bashrc 后试按 Tab。其他机器/登录用户需分别配置，使用本机 kubectl 生成匹配版本的脚本。
- 示例：kubectl get namespace k8s- 后按 Tab；若只有 k8s-lab-20261029 匹配且查询正常，预期补全该名称。-n 后的 Namespace 和指定 Namespace 中的 Pod 名也可补全；多个候选通常连按两次 Tab 查看。示例是预期行为，未实际验证。
- 排查入口：type _init_completion、complete -p kubectl、kubectl get namespaces；区分补全框架未加载、kubectl 规则未注册和集群资源查询失败。worker 节点角色不等于当前用户已配置 kubectl 管理访问。
- 官方参考：[Linux kubectl 自动补全说明](https://kubernetes.io/docs/tasks/tools/install-kubectl-linux/#enable-shell-autocompletion)。版本标签源码网页抓取失败，本机 HTTP 获取也受网络限制；不声称已读取该版本实现。采用已有 Bash completion 方法并让目标机的已安装 kubectl 生成脚本，不下载新版补全文件或升级 kubectl。
- 状态：已说明配置方法，用户未提交执行结果，未代安装或修改虚拟机；学习时长未知，保留草稿，原第三轮扩容学习起点不变。

### 4.11 2026-10-29：逐段理解当前 .bashrc

- 用户真实问题：贴出 .bashrc，包含 rm/cp/mv 的 -i 别名、条件加载 /etc/bashrc、M2_HOME 与 PATH、bash-completion 与 kubectl completion 两行，希望解释各项含义。
- 证据边界：用户提供的是文件内容；未标明来自哪一台机器，也未提交加载结果或 Tab 成功演示。确认所贴文本包含补全配置，但不推定三台均已配置或安装、加载成功。
- 助手解释：# 开头是注释；alias 在交互式 Bash 中为命令提供替代写法，rm -i 删除前确认，cp -i/mv -i 覆盖目标前确认；别名不会修改这些程序本身，非交互脚本默认不展开别名。
- 条件加载：if [ -f /etc/bashrc ] 检查是否存在该普通文件，then 分支用 . /etc/bashrc 在当前 Shell 读取执行，fi 结束判断；点命令与 source 同义。CentOS 的 /etc/bashrc 提供系统公共 Bash 配置，~/.bashrc 属于当前用户。
- 环境变量：M2_HOME 记录 Maven 安装目录；export 让之后启动的子进程继承变量，不代表立即影响其他用户/已运行进程。PATH 是冒号分隔的外部命令搜索目录列表；原 PATH 后追加 $M2_HOME/bin，使 mvn 可通过名称找到，原有目录优先。赋值本身不安装 Maven，也未验证该目录实际存在。
- 补全：第一条 source 加载 Bash 补全框架；kubectl completion bash 生成补全代码，<(...) 是进程替换，将命令输出暴露为可读取的文件路径，外层 source 在当前 Shell 执行这些定义以注册补全。与直接 bash 执行配置的子进程作用域不同。
- 生效方式：交互式非登录 Bash 读取 ~/.bashrc，登录会话通常通过 ~/.bash_profile 间接加载；不能理解成所有 Shell 脚本或 systemd 服务都自动加载。保存文件后可在对应 Bash 终端 source ~/.bashrc 让当前会话生效；编辑沿用 vim。
- 资料：[Bash 启动文件](https://www.gnu.org/software/bash/manual/html_node/Bash-Startup-Files)、[Bash 进程替换](https://www.gnu.org/s/bash/manual/html_node/Process-Substitution.html)、[Bash 手册](https://www.gnu.org/s/bash/manual/bash.html)、前条 Kubernetes 官方补全说明。
- 状态：助手补充讲解，未执行虚拟机命令、未修改其 .bashrc；用户理解未考核，学习时长未知，保留暂存，原学习起点不变。

### 4.12 2026-10-29：第三轮扩容成功，Deployment READY 待巩固

- 用户实际执行：`kubectl scale deployment web --replicas=2 -n k8s-lab-20261029`，回显 `deployment.apps/web scaled`；随后组合查询确认 Deployment web 的 READY 2/2、UP-TO-DATE 2、AVAILABLE 2，原 RS web-5dcdf98765 的 DESIRED/CURRENT/READY 均为 2。
- Pod 证据：web-5dcdf98765-d2pld（10.244.1.4）与新增的 web-5dcdf98765-dpxbr（10.244.1.5）均位于 node1，Namespace 为 k8s-lab-20261029，均 Running、READY 1/1、RESTARTS 0。同一 Node 承载两个副本符合本轮要求，不据此判为调度失败。
- 用户回答与评价：Deployment 数量 1、Pod 数量 2 正确；主动区分“RS 自己的数量 1”和“RS 维护的 Pod 数量 2”，正确。两个 Pod 的名称、Namespace、Node 均正确。各 Pod READY 表示一个容器、一个就绪，以及扩容增加 Pod 数量的回答均正确。
- 用户明确卡点：对“Deployment 的 READY 及其含义”填写“不会”。助手补充：Deployment READY = 已就绪的 Pod 副本数／期望的 Pod 副本数。当前 2/2 中，后一个 2 对应 scale 设置的期望数量，前一个 2 是就绪副本数；Pod 表的 1/1 统计单个 Pod 内容器，两个表的统计单位不同。
- 期望数边界：Deployment READY 的分母不是当前已存在 Pod 的总数；例如 1/3 说明期望 3 个、就绪 1 个，仅凭这一列不能判断另外两个 Pod 是否已创建。当前实际 Pod 数量应结合 Pod 列表或其他状态字段判断。
- 官方核对：[Deployment 列表字段说明](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)。属于助手针对真实卡点的补充，不是视频内容摘要。
- 状态：**第三轮实操成功；Deployment READY 概念已解释未验证**。不因命令成功把用户明确不会的部分记为已掌握。实际学习时长未知，不根据对象 AGE=44m 认定学习满半小时。
- 本次仅补一道口头题：假设某个 Deployment 的 READY 为 1/3，前一个 1 和后一个 3 各表示什么；末尾提供空白模板。本轮不新增集群变更命令，第四轮自愈及清理尚未开始，用户准备继续时再推进。

### 4.13 2026-10-29：第三轮复盘通过与第四轮自愈练习布置

- 用户真实回答：Deployment READY 为 1/3 时，前一个 1 表示目前已有一个副本 ready，后一个 3 表示 Deployment 期望三个副本就绪。评价：正确；这里的副本单位是 Pod。第三轮实操和核心概念均通过。
- 第四轮目标：由用户删除专用实验 Namespace 中一个由 RS 管理的 Pod，观察期望副本数保持 2 时，ReplicaSet 控制器创建新的 Pod 来补足数量。本轮仍保留 Deployment、RS 和 Namespace，收集结果后再指导收尾清理。
- 操作位置：两个终端都登录 master。终端 A 执行 `kubectl get pods -n k8s-lab-20261029 -o wide -w`，初始应能看到上次已验证的两个 Pod。指定删除目标为用户此前实际输出中的 web-5dcdf98765-dpxbr；若当前找不到该目标，先贴最新列表，不猜新名称或扩大删除范围。
- 终端 B 的实验命令（已布置、未执行）：`kubectl delete pod web-5dcdf98765-dpxbr -n k8s-lab-20261029`，仅删除这个实验 Pod；随后用 `kubectl get deployment,rs,pods -n k8s-lab-20261029 -o wide` 取得最终快照。所有操作由用户亲手完成，助手未代操作。
- 观察与预期：旧 Pod 终止，新 Pod 按同一模板被创建，最终通常为 Deployment READY 2/2、原 RS 维持 2 副本、两个 Pod 各 1/1；这是预期而非实际结果。新对象有新身份，不能解释成原 Pod 复活；IP／Node 不要求与旧 Pod 相同。删除与补建可以重叠，不要求一定观察到仅剩一行的瞬间。
- watch 使用边界：-w 会随变化重复打印状态，不能按累计输出行数统计当前 Pod 数量；最终数量以不带 -w 的查询快照为准。Ctrl+C 退出观察，不停止 Pod。该补建能力来自 RS 的管理关系，不适用于所有独立 Pod。
- 第四轮考题：①提供删除回显与最终组合查询输出；②记录新 Pod 名称、Node、最终 Pod 数量和 Deployment READY；③说明删除单个 Pod 是否改变期望副本数、哪个控制器负责补建。末尾提供一一对应的空白模板。
- 官方依据：[ReplicaSet 的工作机制](https://kubernetes.io/docs/concepts/workloads/controllers/replicaset/)。使用已确认 v1.22.2 支持的基础行为；不引入新版专属功能。
- 状态：第三轮已验证通过；第四轮已说明／已布置、未执行／未验证。学习时长仍未知，不形成正式记录。

### 4.14 2026-10-29：第四轮补建验证通过，布置实验清理

- 用户实际执行：`kubectl delete pod web-5dcdf98765-dpxbr -n k8s-lab-20261029`，回显 `pod "web-5dcdf98765-dpxbr" deleted`；随后提交不带 -w 的组合查询最终快照。
- 实际结果：Deployment web 为 READY 2/2、UP-TO-DATE 2、AVAILABLE 2；同一 RS web-5dcdf98765 的 DESIRED/CURRENT/READY 均为 2。原 Pod web-5dcdf98765-d2pld（10.244.1.4）保留，补建 Pod 为 web-5dcdf98765-p5sgv（10.244.1.6）；两者均在 node1，Running、READY 1/1、RESTARTS 0。新 Pod 名称与 IP 不同，表明创建了新 Pod；未提供 watch 过程，不能声称用户实际观察到了特定中间状态。
- 用户回答与评价：新 Pod 名称、Node、最终数量 2、Deployment READY 2/2 均正确；“删除单个 Pod 不改变期望副本数”正确。关于控制器，用户描述 controller 根据 Deployment 定义的副本数通过 RS 维护 Pod，整体方向正确。
- 助手补充：Deployment 控制器管理 RS，ReplicaSet 控制器根据 RS 的期望副本数直接补建 Pod。第四轮实操和基本原理通过；精确控制器名称为本次补充，不冒充用户已自行准确命名。
- 清理步骤（仅布置、未执行）：在 master 执行 `kubectl delete deployment web -n k8s-lab-20261029`，随后 `kubectl get deployment,rs,pods -n k8s-lab-20261029`；预期所属 RS 和 Pod 经默认级联删除后不再列出。若短暂出现 Terminating，等待后再查询。此查询只核对指定的三类资源，不表示 Namespace 已不存在。
- 再执行 `kubectl delete namespace k8s-lab-20261029` 清理本次专用 Namespace 及其中剩余资源，用 `kubectl get namespace k8s-lab-20261029` 验证；预期返回 NotFound。所有输出均为预期，待用户回传实际证据；本次助手未连接集群或代操作。
- 原理补充：删除单个受控 Pod 时，RS 的期望数仍为 2，因此会补建；默认删除 Deployment 会连带删除它拥有的 RS 和 Pod，最终不再维持这组副本。依据：[ReplicaSet 工作机制](https://kubernetes.io/docs/concepts/workloads/controllers/replicaset/)、[官方级联删除说明](https://kubernetes.io/docs/tasks/administer-cluster/use-cascading-deletion/)。沿用已确认 v1.22.2 支持的基础命令。
- 本次收尾提交项：Deployment 删除回显与后续组合查询输出；Namespace 删除回显与后续查询输出。末尾提供对应空白模板，不新增未经提问的用户问题。
- 状态：第四轮通过，清理待验证；实际学习时长仍未知，不将 Pod AGE=66m 或新 Pod AGE=87s 作为学习时长，不形成正式记录。

### 4.15 2026-10-29：实验资源清理验证完成

- 用户实际执行：`kubectl delete deployment web -n k8s-lab-20261029`，回显 `deployment.apps "web" deleted`；随后执行 `kubectl get deployment,rs,pods -n k8s-lab-20261029`，实际输出 `No resources found in k8s-lab-20261029 namespace.`。据此确认该 Namespace 中这三类实验资源已不再列出，不将这个查询单独解释为 Namespace 已删除。
- 用户随后执行：`kubectl delete namespace k8s-lab-20261029`，回显 `namespace "k8s-lab-20261029" deleted`；再执行 `kubectl get namespace k8s-lab-20261029`，实际输出 `Error from server (NotFound): namespaces "k8s-lab-20261029" not found`。这是删除后按名称查询的预期结果，确认专用 Namespace 已不存在。
- 评价：收尾清理通过，本次四轮基础实验完成。用户亲手按指导完成了查询、创建、扩容、删除受控 Pod 后观察补建及清理；不能据此推定已能脱离指导完成全部操作，或把此前未验证概念改记为已掌握。
- 助手本次仅核对用户输出并更新本地记录，没有连接集群、执行清理或额外检查全局健康。下一步回到用户当前 P14 视频学习主线，不自动开始新一轮集群变更。
- 状态：本次实验没有待执行的收尾命令；学习时长仍未知，用户尚未表达本次学习结束，继续保留暂存，不形成正式记录。此前“清理待验证”等条目为历史状态，以本条和顶部状态为准。

### 4.16 2026-10-29：Pod 的定义与“对象已存在、容器未启动”的区别

- 用户真实问题：选中 P13 笔记的对象创建与调度流程后，指出 Pod 先经过 RS 创建、Scheduler 调度到 Node，之后 kubelet 还需配合运行时落实容器，因此询问“Pod 实际上不是正在运行的容器，对吧，那 Pod 应该怎么定义”。
- 用户已有理解证据：正确区分对象创建与应用容器启动，并复述本例的创建、调度、运行顺序；没有提交额外的集群状态或容器运行证据。
- 助手解答：Pod 是 Kubernetes 中最小的可部署、可调度单位，将一个或多个紧密关联的容器作为整体管理，定义运行要求与共享环境。同一 Pod 的容器安排到同一 Node，共享网络环境，也可以按配置共享存储卷；并非自动共享整个根文件系统。
- 两个层面：API 对象记录 metadata、spec、status；Node 上的 kubelet 配合容器运行时落实环境并启动容器。对象在启动前后都可存在，启动后继续记录状态；不是对象消失后转换成容器。任务单类比仅帮助理解需求记录、执行与回报，不替代 Pod 的完整定义。
- 官方依据：[Pod 定义](https://kubernetes.io/docs/concepts/workloads/pods/)、[Pod 生命周期](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/)。本次核对官方基础概念，沿用已确认 v1.22.2 环境，不涉及新版专属字段。
- 笔记同步：已在 [P13 笔记](video-notes/P013-什么是资源.md) 的对象创建流程前增加定义，并追加独立问答条目，保留原流程和问答。属于助手补充，不冒充视频内容；未读取新字幕或画面，观看位置仍为 P14。
- 状态：部分理解已有用户主动推导证据；完整定义和共享资源边界已解释未验证。本次无考题、无新增实验、无服务器连接；学习时长未知，继续暂存。

### 4.17 2026-10-29：已分配节点后的启动失败与 Ready 含义

- 用户真实问题：Pod 分配到 Node 后，实际容器是否可能运行不起来；Ready 表示已经分配节点，还是容器已经正常运行。
- 助手解答：可能启动失败，镜像拉取、存储／网络准备、应用启动配置均可能出问题。PodScheduled 表示已调度，Running 是运行阶段且不保证全部容器就绪，Pod Ready 表示按规则判断可接收请求。READY 列统计就绪容器数／配置容器数；Pod Ready 条件另外考虑已配置的 readinessGates。
- 就绪判定：readinessProbe 用于检查是否准备好接收请求；未配置时通常启动完成即可判定容器就绪，不能推定 K8s 自动验证所有业务。假设的单容器 Pod 可以已在 node1 上运行，却显示 Running、READY 0/1；具体不就绪原因需进一步收集证据，不能根据例子认定用户集群故障。
- 来源与版本：已阅读 [v1.22 官方文档源码](https://github.com/kubernetes/website/blob/release-1.22/content/en/docs/concepts/workloads/pods/pod-lifecycle.md) 并核对 [就绪探针说明](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/#define-readiness-probes)，不引入新版本专属字段。定义与问答已同步到 [P13 笔记](video-notes/P013-什么是资源.md)。
- 状态：已解释未验证；本次没有实验、服务器操作或新考题，故障及状态示例均为助手补充。此前 READY 数字计数的正确作答证据仍有效；实际学习时长未知，暂存未归档。

### 4.18 2026-10-29：严格核对用户对部署全过程的复述

- 用户真实复述：controller 根据 Deployment 要求指挥 RS 创建 Pod，Pod 信息写入 etcd 完成创建，再将信息分配给 Scheduler，Scheduler 调度至合适 Node，Node 使用 kubelet 和节点上的“容器”创建实际容器；要求严格检查理解。
- 评价与已有证据：主流程顺序正确，已经区分对象创建和容器进程运行；知道 etcd 存储对象、Scheduler 选择节点、kubelet 参与节点执行。但尚不能将组件分工与通信机制整体记为已掌握。
- 四处校正：①Deployment 控制器管理 RS 对象，RS 控制器创建 Pod 对象，RS 对象不是执行程序；②控制器经 API Server 创建对象，由 API Server 持久化到 etcd，控制器不直接写 etcd；③Scheduler 通过 API Server 获取／监听已存在但尚未绑定 Node 的 Pod，完成选节点并经 API Server 提交绑定，不是被派发“待创建 Pod 的数据”；④kubelet 获取本节点 Pod 后调用容器运行时 containerd 创建和启动容器，不是用现有应用容器创建新容器。
- 助手补全：kubelet 回报 Pod／容器状态到 API Server；对象与状态保存在 etcd，各组件持续观察并协调。完整流程称部署或创建到运行流程；调度只指其中的选择节点与绑定环节。本次仅讨论 Deployment 管理的普通 Pod。
- 来源与同步：已核对 [RS](https://kubernetes.io/docs/concepts/workloads/controllers/replicaset/)、[API](https://kubernetes.io/docs/concepts/overview/kubernetes-api/)、[Scheduler](https://kubernetes.io/docs/concepts/scheduling-eviction/kube-scheduler/)、[kubelet](https://kubernetes.io/docs/reference/node/kubelet-sync-loop/) 的官方基础职责说明，沿用已确认的 v1.22.2／containerd 环境；完整问答追加到 [P13 笔记](video-notes/P013-什么是资源.md)，不标为视频原文。
- 状态：本次为对用户主动复述的反馈，没有额外出题或新增实验；四处校正与状态回报未获用户修正后复述，Ready 的此前待验证状态保留。本次没有服务器操作，学习时长未知，继续暂存。

### 4.19 2026-10-29：提前精读 P14–P25，准备后续答疑

- 用户真实请求：希望助手先 review 后续章节，便于用户学习后马上提问；在范围确认中选择“先精读 P14–P25，跟随我的学习进度再继续”。
- 已完成：通过已验证的 B 站登录与 yt-dlp 流程取得并完整阅读 12 节共 6,268 条中文 AI 字幕，逐 P 核对官方标题、CID、时长与主题；实际逐张查看每节一张、共 12 张 1920×1080 关键画面。视频合计 4:45:38 为源材料长度，不是用户实际学习时长。
- 资料入口：[统一索引](video-notes/P014-P025-预习索引.md)、[P14–P17](video-notes/P014-P017-预习精读.md)、[P18–P21](video-notes/P018-P021-预习精读.md)、[P22–P25](video-notes/P022-P025-预习精读.md)、[关键画面](video-notes/P014-P025-关键画面核对.md)。各组记录时间戳、课程主线、助手补充、与 Linux/Docker 经验的联系、v1.22.2 适配和独立问答章节。
- 助手核对重点：PID 共享配置、普通 init 的失败重试、readiness 持续检查、startup 成功/失败阈值、RS 的选择器及归属、apply 的历史声明与省略字段、普通 replace 和 force 重建的区别。部分课件处于错误演示或编辑中，已注明不可直接照抄；具体官方来源和读取限制保留在笔记。
- 状态：**助手资料准备完成，用户掌握状态不变**。这是字幕精读和关键画面抽查，未完整听看全部视频，未逐字符核验全部 YAML，未复现课程实验或连接三台服务器。预备的易问点不是已发生的用户提问。
- 续接：当前课程仍为 P14；根据真实提问或实验输出继续。后续章节在后续学习会话中随进度准备，本次未读取 P26 以后。实际学习时长未知，继续暂存，不生成正式学习记录。

### 4.20 2026-10-29：P14–P15 学习进度更新与场景考核

- 用户真实请求：已学习 P14、P15，主要内容是资源清单编写；希望通过实际工作场景或面试问题检验掌握，因命令不熟悉希望有适量提示。
- 资料核对：读取 bilibili-obsidian-notes 技能和 VIDEO_WORKFLOW.md，复用既有精读笔记与经校验字幕缓存／来源元数据。P14 CID `500001651184251`，P15 CID `500001651187296`；原链接与读取限制见 [精读笔记](video-notes/P014-P017-预习精读.md)。本轮未重新下载视频或查看新画面，不声称完整听看视频。
- 考核为助手根据课程范围编制的模拟场景，并非用户真实故障或视频原题。按已确认的 v1.22.2／containerd 环境，结合官方对象说明、kubectl 参考和 v1.22 Pod 生命周期说明校对；本轮不连接服务器、不创建资源。
- 第 1 题：同事拟给 Pod 写 `apiVersion: v1.29` 并通过 `status.phase: Running` 保证启动，分别解释 API 版本及 spec/status。
- 第 2 题：在假设已存在的独立 Namespace `k8s-lab-manifest-20261029` 中编写 `lab-web` Pod；标签 `app: web`、`env: study`，容器 web 使用 `nginx:1.22`，helper 使用 `busybox:1.36` 执行 `/bin/sh -c 'sleep 3600'`；给出 YAML、提交命令并解释 created 的边界。镜像仅用于模拟，不声称当前网络可拉取。
- 第 3 题：指定 Namespace 按 `app=web` 查询 Pod 并显示 IP／Node；判断 `kubectl get nodes -n ...` 是否只查该 Namespace 的节点。
- 第 4 题：分别查 containers 字段说明与实际 Pod 详情／事件；读取 web 日志；进入 helper 的 `/bin/sh`，要求定位 Namespace、Pod 和容器。
- 第 5 题：假设同 Pod 两个 Nginx 都监听 TCP `0.0.0.0:80`，模拟 READY 1/2、CrashLoopBackOff 及 bind 地址占用日志；解释 READY、冲突原因，并判断只改 containerPort 能否解决及实际修复方向。
- 第 6 题：无控制器管理的普通 Pod，restartPolicy=Always；分别判断 sleep 正常结束与直接删除 Pod 后的行为，关联此前 RS 补建实验。
- 教学安排：允许查帮助，先书写作答，可分批先答 1–3；每题附适量提示，末尾模板逐项覆盖小问、不预填答案。状态为已布置／未作答，不把观看完成记为掌握。用户实际学习时长未知，不生成正式记录。

### 4.21 2026-10-29：P14–P15 首轮六题提交与逐题反馈

- 用户提交全部六题答案；实际终端证据为在 master 上执行未带 `-n` 的 `kubectl describe pod lab-web` 返回 `Error from server (NotFound): pods "lab-web" not found`。用户认为与没有可拉取镜像有关，但没有提供创建回显、目标 Namespace 查询或镜像拉取事件，因此该归因未获支持。
- 第 1 题：将 apiVersion 理解成定义在 Deployment 中的 Pod 运行版本，概念错误；第 2 题 YAML 中实际写对了 `v1`。已解释 Pod 使用核心组 v1，Deployment 使用 apps/v1，接口组／版本用于解释 API 对象结构，与 Kubernetes 软件版本、容器镜像标签分开。微服务只是课程类比，API 分组不等于每组独立部署微服务。spec/status 的期望／实际方向正确，但适用于所描述的对象，不专属于 Deployment；status 记录观测状态，填写 Running 不能启动进程。
- 第 2 题：按消息所呈现的 YAML 内容，名称、Namespace、标签、双容器列表和 command 数组均符合要求；create -f 与同值 -n 正确，-n 在此重复但不冲突。用户正确解释 created 只证明对象创建成功，容器运行还需调度与 kubelet／运行时落实；补充经 API Server 持久化到 etcd。不把作答命令视为真实执行或创建成功，消息里的转义字符不据此认定为实际文件错误。
- 第 3 题：`kubectl get pod -n k8s-lab-manifest-20261029 -l app=web -o wide` 正确；Node 不隶属 Namespace 的结论正确。精确补充 Node 与 Namespace 对象本身是集群作用域，Pod 是命名空间作用域。
- 第 4 题：explain 查询资源字段格式，不依赖某个 Pod 实例或镜像已启动，但需访问 API 说明；describe 查看实际对象。未给 -n 时使用当前 context 的 Namespace，未配置时才是 default。NotFound 仅说明该请求范围中未找到对象，不能推定镜像故障；拉取失败通常保留 Pod 对象，可查看 ErrImagePull／ImagePullBackOff 与事件。给出只读定位命令 `kubectl get pods -A --field-selector metadata.name=lab-web`，预期查到同名 Pod 及 Namespace 或空列表，实际输出待提供。
- 第 4 题容器操作：用户将 web/helper 容器名放到 Pod 参数位置；正确形式为 `kubectl logs lab-web -n k8s-lab-manifest-20261029 -c web` 与 `kubectl exec -it lab-web -n k8s-lab-manifest-20261029 -c helper -- /bin/sh`。当前对象是否存在仍未知，不承诺运行成功。
- 第 5 题：将 READY 解释为运行／期望运行不够准确，已纠正为 1 个应用容器就绪／共配置 2 个应用容器；运行不保证就绪。共享网络造成本例同地址 TCP 80 冲突的原因正确。用户明确猜测仅改 containerPort 不能解决、但不知原因，未提供修复方案；已解释声明不会改变 Nginx 的真实监听，可将第二个 Nginx 配置改为 listen 8080，并相应更新声明；或按应用设计拆为独立 Pod。本轮为解释，未实际修改配置。
- 第 6 题：Always 下正常退出仍重启、无控制器普通 Pod 删除后不补建，两个结论正确。需要修正“此前额外配置了 RS”：此前由 Deployment 控制器自动创建／管理 RS，再由 RS 控制器维护 Pod 数量。restartPolicy 是 kubelet 对现有 Pod 内容器退出的处理规则，不是独立运行的 Pod 重建控制器。
- 官方依据：[API 组与版本](https://kubernetes.io/docs/reference/using-api/)、[explain](https://kubernetes.io/docs/reference/kubectl/generated/kubectl_explain/)、[logs](https://kubernetes.io/docs/reference/kubectl/generated/kubectl_logs/)、[exec](https://kubernetes.io/docs/reference/kubectl/generated/kubectl_exec/)、[v1.22 生命周期](https://raw.githubusercontent.com/kubernetes/website/release-1.22/content/en/docs/concepts/workloads/pods/pod-lifecycle.md)、[v1.22.2 ContainerPort 定义](https://raw.githubusercontent.com/kubernetes/api/v0.22.2/core/v1/types.go)、[Deployment](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)。基础语义按已确认 v1.22.2 环境解释。
- 下一轮只复盘三题：①仅将 nginx:1.22 改为 nginx:1.23 是否需要改 Pod apiVersion，解释原因；②假设 Namespace 为 training、Pod 为 api-demo、容器为 worker，写查看该容器日志的命令；③两个应用进程都运行但只有一个就绪时的 READY，以及应用仍监听 80 而 containerPort 写 8080 时实际端口。附一一对应空白模板；均待作答。
- 状态：本轮已有书面回答与一次 NotFound 查询证据；纠正内容尚未复述验证。学习时长未知，继续暂存。助手未连接服务器或修改集群，未将用户猜测记成真实镜像故障。

### 4.22 2026-10-29：Deployment 端口声明、RS 创建与维护范围

- 用户真实问题：选中“containerPort 不会修改 Nginx listen”和“Deployment 控制器自动创建 RS”两段，要求详细解释 Deployment YAML 中端口声明与真实容器端口的关系；确认能否通过 Deployment 创建 RS、RS 如何创建、如何维护 Pod 数量及数量之外的能力。
- 端口说明：准确字段路径是 `spec.template.spec.containers[].ports[].containerPort`。该信息随 Deployment 的 Pod 模板进入 RS／Pod；它声明端口，不代替应用配置或启动参数设置监听，不等同 Docker 的 `-p`。真实监听由应用进程根据配置、参数或其支持的环境变量建立。示例假设 Nginx 监听 80，声明改 8080 不会使其改听 8080；省略声明也不自动关闭真实端口，能否访问另受地址、网络与策略影响。
- 声明用途与补充：端口可命名，例如 http→80；Service 的数字 targetPort 直接选择 Pod 目标端口，命名 targetPort 按 Pod 的端口名解析；Service port 是客户端入口端口。用 Service port 8080、targetPort http 与 Pod http:80 演示入口与后端端口不同。若仅把声明 http 改为 8080 而应用仍听 80，依赖此命名的 Service 将指向错误端口。Service 是助手为解释关联补充，不计作用户已学完整 Service 章节。
- 变更边界：正常未暂停的 Deployment 更新 Pod 模板中的 containerPort 会触发发布，通常对应新的 RS／替换 Pod；即使新容器重建，应用仍按未改变的 listen 配置监听。要改变应用端口需修改实际配置／受支持参数等，并同步声明与引用。
- 创建链路：用户提交 Deployment 对象，Deployment 控制器经 API Server 创建／管理 RS，RS 控制器经 API Server 按模板创建 Pod，Scheduler 绑定节点，kubelet／运行时落实容器；对象与状态经 API Server 持久化，控制器不直接操作 etcd。Deployment、RS 是资源对象，执行协调的是控制器。可以直接编写 kind: ReplicaSet 清单，但已有 Deployment 时通常由它管理 RS。
- 副本数：replicas=3 表示 3 个 Pod；若模板有两个应用容器，每个 Pod 都有这两个容器。选择器与模板标签确定匹配范围，ownerReferences 记录归属；RS 不靠名称前缀识别归属。正常稳定场景下缺少则按模板补建，多出则缩减；仅改 replicas 不改变 Pod 模板，不因此触发新的发布。Pending／不就绪 Pod 可能已计入副本，不能把目标 3 推定为 3 个健康实例；滚动更新／终止期间实际数量可能暂时不同。
- 网络关联：普通 Pod 各有网络环境，多个副本可在各自 Pod IP 上监听 80；同一 Pod 的两个容器则共享端口空间，若争用同地址同协议端口会冲突。此处不讨论 hostNetwork／hostPort。
- 数量之外的分工：RS 保存用于新建 Pod 的模板并报告状态，不逐项把现存 Pod 改回模板、不提供滚动升级；Deployment 维护模板版本、协调新旧 RS 的滚动更新、扩缩容及保留历史供回滚，默认不因失败自动回滚。kubelet 依据 restartPolicy／探针重启容器和判定就绪，Scheduler 负责选节点，Service 提供访问入口与流量分配，HPA 需另配才会按指标调整 replicas。副本重建不复制原容器内存或临时文件，也不自动修正错误应用配置。
- 来源：已核对 [v1.22.2 API 类型](https://raw.githubusercontent.com/kubernetes/api/v0.22.2/core/v1/types.go)、[Nginx listen](https://nginx.org/en/docs/http/ngx_http_core_module.html#listen)、[v1.22 Deployment](https://raw.githubusercontent.com/kubernetes/website/release-1.22/content/en/docs/concepts/workloads/controllers/deployment.md)、[ReplicaSet](https://kubernetes.io/docs/concepts/workloads/controllers/replicaset/)、[v1.22 Service](https://raw.githubusercontent.com/kubernetes/website/release-1.22/content/en/docs/concepts/services-networking/service.md) 与 [Pod 生命周期](https://raw.githubusercontent.com/kubernetes/website/release-1.22/content/en/docs/concepts/workloads/pods/pod-lifecycle.md)。
- 状态：本轮为概念解答及示意 YAML／关系图，无新实验、服务器操作或新考题；尚未验证理解，原 3 个复盘问题保持待答。实际学习时长未知，继续暂存。

### 4.23 2026-10-30：三个针对性复盘提交与反馈

- 用户实际作答：①仅更新镜像标签不需修改 apiVersion，认为其指 Pod 所属 API 分组、与镜像版本无关；②`kubectl logs api-demo -n training -c worker`；③两个进程运行但只有一个就绪时 READY 为 1/2，声明 containerPort 8080 不会改变 Nginx 按配置监听 80。
- 第 1 题：不需要修改的结论和接口／镜像区分方向正确。精确补充 apiVersion 标识 API 组及版本，核心组省略组名，Pod 的 v1 是核心组 v1 版本；Deployment 的 apps/v1 中 apps 为组、v1 为版本。镜像写在具体容器的 image 字段，并非必须通过 Deployment：独立 Pod 路径为 spec.containers[].image，Deployment 模板路径为 spec.template.spec.containers[].image。字段拼写为 apiVersion。
- 第 2 题：命令完全正确，Namespace／Pod／容器三层定位的书面迁移验证通过。没有实际执行输出，不记为已验证日志获取成功；exec 不因 logs 正确而自动记为通过。
- 第 3 题：READY 1/2 判断和 Running 不保证 Ready 的解释正确；提醒分母是配置的应用容器总数。真实端口 80 以及应用自己建立监听的原因解释正确，containerPort 与 Nginx listen 区别取得复述证据。本例没有真实监听检查，不扩展为完整网络或 Service 验证。
- 反馈安排：不重做已答的三题；新增最后两个短题核实此前未验证点。第 1 题 a 查询 pod.spec.containers 字段说明，b 假设 training/api-demo 存在，查询其详情与事件；第 2 题 a Deployment replicas=2 且每个 Pod 两个应用容器，在稳定运行时分别有多少 Pod／应用容器，b 删除其中一个 Pod 后负责补建的控制器及理由。均为书面模拟，无需运行命令，附逐项空白模板。
- 来源：复用本会话已核对的 v1.22 基础行为和官方命令说明；再次核对 [API 组与版本](https://kubernetes.io/docs/reference/using-api/#api-groups) 及 [镜像说明](https://kubernetes.io/docs/concepts/containers/images/)。没有读取新视频或连接服务器。
- 状态：核心结论正确且有书面证据；apiVersion 的组加版本精确措辞为本轮补充，字段查询与 RS 补建机制仍待作答。实际学习时长未知，跨日期不自动计时或归档，保留此前全部来源与状态。

### 4.24 2026-10-30：字段查询与副本数量补题反馈

- 用户实际作答：查询字段写 `kubectl explain spec.containers`，查询实例写 `kubectl describe pod api-demo -n training`；对于 replicas=2 且模板中两个应用容器，回答 1 个 Pod／2 个容器，附“在 deployment 中目前只看到一个 pod”；补建回答 RS，依据 Deployment 配置 replicas:2。
- 第 1 题：选 explain 的方向正确，缺少资源类型前缀，准确命令为 `kubectl explain pod.spec.containers`，先定位 Pod 资源再沿字段路径查说明。describe 命令完全正确，取得指定 Namespace 查询实际对象的书面证据；未提供运行输出。
- 第 2 题数量：原题明确稳定运行、无发布更新，答案应为 2 个 Pod、4 个应用容器。一份 spec.template 是每个 Pod 的模板，replicas=2 决定生成两份 Pod 实例，每个都有两个应用容器。用两个 Pod 各含 web/helper 的示意说明；不把模板条目数作为实际 Pod 个数。
- 对“目前只看到一个 Pod”的处理：可能指清单中的一份模板，也可能指真实查询，但用户未提供命令／输出，不能判断实际数量或认定集群异常；明确原题为假定稳定场景，实际问题需按输出核实。
- 第 2 题补建：RS 方向正确，准确执行主体为 ReplicaSet 控制器。Deployment 的 replicas 是上层目标，稳定无更新场景下由 Deployment 控制器将对应数量设置到 RS.spec.replicas；RS 控制器直接比较这个目标与其管理的 Pod 数量，发现缺少后按 RS 模板补建。控制器经 API Server 创建对象。
- 官方依据：[explain 语法](https://kubernetes.io/docs/reference/kubectl/generated/kubectl_explain/)、[RS 的模板与副本数](https://kubernetes.io/docs/concepts/workloads/controllers/replicaset/)，沿用已核对 v1.22.2 基础语义，无集群变更。
- 后续两个微复盘：①写查询 Deployment.spec.replicas 字段说明的命令；②仍是一份包含两个应用容器的模板，仅将 replicas 改为 3，稳定运行时的 Pod／应用容器总数，并解释一份模板为何可以创建多份 Pod。末尾附完整空白模板；不要求实操。
- 状态：describe 书面验证通过；explain 完整路径、模板／实例数量区分及 RS 直接依据为已纠正待复述。本轮未收到新的实际输出，学习时长未知，继续暂存，不连接或修改集群。

### 4.25 2026-10-30：explain 完整路径与模板／副本数量复盘通过

- 用户真实答案：`kubectl explain deployment.spec.replicas`；一份双容器模板、replicas=3 时有 3 个 Pod、6 个应用容器；解释 spec.template 定义 Pod 模板，在 RS 控制器按副本要求维护下可以创建多个 Pod。
- 评价：两题均正确。explain 已明确资源类型和字段路径，并迁移到 Deployment；模板份数与实例数量已正确区分，应用容器总数计算正确，明确提到执行维护的是 RS 控制器。此处记录为书面验证通过。
- 解释重点：spec.template 定义每个 Pod 的结构，replicas 定义期望 Pod 数量，RS 控制器按模板创建／维护实例；不把“使用副本”解释为另一个独立执行组件。无需重做这两题或新增考题。
- 边界：没有新的命令实际输出、运行状态、服务器连接或集群变更。完整 Deployment／RS 通信机制、exec、NotFound 归因及 Service 关联等此前未验证项不自动视为已掌握。
- 状态：本轮已布置题目均已有作答，没有待答题。学习时长仍未知，用户未表达结束，不形成正式记录、不归档；前日及本日历史作答与修正链保留。

### 4.26 2026-10-30：按用户要求更新学习进展总览

- 用户真实请求：将当前学习进展、可以拓展的知识、掌握情况等更新到文档。
- 汇总来源：本项目 2026-10-28 至 2026-10-30 的暂存、当前进度、P13 问答和 P14–P17 真实作答记录。保留原日期和原问题，不把本次整理日期改成全部知识的实际学习日期。
- 当前进度：P1–P12 按用户确认记为已学，用户已报告学习 P14、P15；P13 精确观看终点仍未单独确认；P16 及后续章节没有新的用户观看报告。助手已准备 P14–P25，不计作用户进度。
- 已验证证据：四轮基础实验及清理有用户亲手操作输出；截至本日，explain 完整路径、模板与副本／应用容器数量、logs／describe 定位、Running 与 Ready 区别、containerPort 与真实监听等已有正确书面回答。不把这些最新通过项恢复成历史的“待答”。
- 边界与卡点：完整组件协同、Pod 完整定义、探针判定机制、exec、NotFound 归因、默认查询范围、Service 端口关系等仍按各自证据保留；镜像故障和“只看到一个 Pod”均未获实际定位证据。书面正确、指导下亲手完成、脱离提示独立完成三者分别记录。
- 文档变更：重整 [PROGRESS.md](PROGRESS.md) 的概览与掌握清单，新增分优先级拓展方向、资料入口和后续验证目标，并整理下次起点；同步 [项目计划](../../PLAN.md) 的当前学习位置与各阶段实际完成范围。既有课程来源、实验历史、问答、维护资料继续保留。
- 后续方向：优先巩固对象与控制器／API Server 协同及按证据定位问题；随后随课程衔接 Pod 生命周期与探针、Service、更新回滚和声明式管理，配置与资源调度再按需要展开。这些是规划，没有新增考题或待执行命令。
- 状态：本次只更新学习文档，没有连接服务器、读取新视频或宣称完成新实验。实际学习时长仍未知，未推算时长，也未将暂存标成已归档；未来整理正式记录时继续保留原始来源和纠正链。

### 4.27 2026-11-02：P16–P18 学习报告与 Pod 生命周期场景考核

- 用户真实请求：已学习 P16、P17、P18，内容主要是 Pod 生命周期；很多地方尚不理解实际工作与面试会用到哪些点，希望通过出题、自己解释来验证掌握情况。
- 课程来源：复用已验证 AI 字幕与精读笔记。[P16：Pod的生命周期1](https://www.bilibili.com/video/BV1PbeueyE8V/?p=16)，CID `500001651190464`，27:28；[P17：Pod的生命周期2](https://www.bilibili.com/video/BV1PbeueyE8V/?p=17)，CID `500001651192877`，23:10；[P18：Pod的生命周期3](https://www.bilibili.com/video/BV1PbeueyE8V/?p=18)，CID `500001651195252`，27:25。各标题前缀为“第四章.k8s资源清单-”。
- 读取限制：本轮读取既有精读笔记、分 P/CID 索引并抽查缓存字幕，未重新下载、完整播放或听写课程，未查看新关键帧。详见 [视频流程](VIDEO_WORKFLOW.md)、[P14–P17 精读](video-notes/P014-P017-预习精读.md)、[P18–P21 精读](video-notes/P018-P021-预习精读.md)。
- 课程定位：P16 03:23–11:08 普通 init、11:08–21:23 钩子、21:24–27:27 就绪与存活；P17 00:00–04:48 startup、05:01–16:24 init/DNS 等待、16:24–23:03 退出码；P18 00:27–06:58 探测方式与用途、07:03–14:49 Service/就绪与参数。
- 助手核对：以最近确认的 v1.22.2 为基线，查阅 [v1.22 生命周期](https://raw.githubusercontent.com/kubernetes/website/release-1.22/content/en/docs/concepts/workloads/pods/pod-lifecycle.md)、[v1.22 探针](https://raw.githubusercontent.com/kubernetes/website/release-1.22/content/en/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes.md)、[普通 init](https://kubernetes.io/docs/concepts/workloads/pods/init-containers/)、[容器钩子](https://kubernetes.io/docs/concepts/containers/container-lifecycle-hooks/) 和 [v1.22 Service](https://raw.githubusercontent.com/kubernetes/website/release-1.22/content/en/docs/concepts/services-networking/service.md)。后续按官方行为判题，不沿用课程中 init 失败必全体重跑、没有 liveness 就不管进程退出等不准确表述。
- 六道题目（全部为假设场景，不是真实运行结果）：
  1. 普通 init 按 init-config、init-db 顺序，1 个 app，restartPolicy=Always；第一个成功，第二个 exit 1。a）app 能否启动；b）通常重试哪个 init、第一个是否必重跑；c）改为 Never 时第二个失败的结果。排除节点／sandbox 重建。
  2. a）应用启动必需配置写到 postStart 是否可靠，应放哪里；b）单应用容器正常删除，宽限期 30 秒、preStop 用 20 秒，收到 SIGTERM 后是否还有完整 30 秒，超时如何处理。忽略额外调度耗时。
  3. 应用需约 90 秒启动，liveness 在启动完成前反复终止它。a）三类探针如何分别处理慢启动、临时不能服务、进程活着但卡死；b）谁执行探针，startup 成功前另外两种是否检查，成功是否保证 Ready。
  4. a）init 中 nslookup mydb 成功能否证明数据库可登录查询，还需什么证据；b）TCP 8080 连通但业务接口持续 500，TCP 探针会怎样，如何改进检查内容。
  5. 同 Namespace 的普通 Service selector=app:web；A 标签 app=web,version=v1 且 Ready；B 标签 app=web 且 NotReady；C 标签 app=api 且 Ready。a）稳定后哪些接该 Service 新流量；b）仅 A 的 readiness 连续失败达阈值、主进程与 liveness 正常时，会否因此重启、后端如何变化、恢复后能否重新接流量。publishNotReadyAddresses=false，网络与端口正常，不讨论既有长连接。
  6. k8s-lab-lifecycle/api-demo 的应用容器 api，restartPolicy=Always，无 liveness；主进程反复 exit 1，显示 CrashLoopBackOff。a）为何还能重启、退避是否永久停止；b）写查看事件/退出原因、上一次实例日志的命令及希望取得的证据；c）用什么字段区分同 Pod 容器重启与 Pod 对象被替换。命令只书面作答；若执行应在配好 kubeconfig 的 master 上，题目对象未创建。
- 作答与状态：题末附覆盖全部小问的空白模板，允许先答 1–3 题或填写不确定／不会。只新增用户学习报告，尚无本轮答案或实验输出，六题均待答；不计为已掌握或答错。后续逐题解释工作用途、面试表达和待实验验证项。没有连接服务器或修改集群，学习时长未知，不正式归档。

### 4.28 2026-11-02：生命周期六题提交、逐题反馈与三题复盘

- 来源：用户在本会话提交 4.27 全部六题及各小问，部分明确写不确定；下表区分原答案、助手解释和验证状态。不确定不伪装成已验证，也不将本次讲解计为用户已掌握。

| 原题 | 用户实际作答与疑问 | 助手反馈与工作联系 | 当前状态 |
| --- | --- | --- | --- |
| 1a–c 普通 init | a：全部 init 按顺序成功后 app 才能启动；b：认为有上下游依赖，失败后 init-config 到 init-db 整条链重跑；c：不确定策略范围，猜 Never 只管 app、init 一直重试 | a 正确；本题通常只重试失败的 init-db，已成功的 init-config 不必重跑。Kubernetes 不分析业务依赖后决定从头执行。普通 init 受 Pod 重启策略影响，Never 下失败使 Pod Failed，app 不启动；Always 下成功的普通 init 不反复运行。排查应定位当前失败 init 的日志、状态和条件 | 顺序阻塞书面通过；重试范围和 Never 已纠正待复述 |
| 2a–b 钩子 | a：不可靠，无钩子先完成的保证，建议 init，但不确定工作实践；b：退出时间不确定 | a 核心正确。现成非敏感配置可挂载 ConfigMap；启动前动态生成可用 init 并经共享卷交给 app，不能假定文件系统自动共享；也可在同容器入口脚本先准备成功再 exec 应用。preStop 与收到 SIGTERM 后的退出共享宽限期，本题约剩 10 秒，到期仍未退出被强制结束；通常由运行时发送 SIGKILL。正常单容器例子不展开特殊延期 | postStart 无先后保证及 init 方向书面通过；配置交接和宽限期已讲解未验证 |
| 3a–b 探针 | 三种用途分别答 startup、readiness、liveness；执行组件首答 kubelet，解释时误写 kubenet，并提出节点分摊工作与低延迟；不确定 startup 成功前是否执行另外两种；认为 startup 成功不保证 Ready | 用途、kubelet、startup 不保证 Ready 的核心判断正确；统一拼写为 kubelet，不能写成 kubenet。startup 成功前 liveness/readiness 不执行，成功后放行；不是固定等够时间自动成功，需检查通过且失败容忍时间覆盖慢启动。readiness 改就绪和接流量资格，liveness 达阈值后终止目标容器，再依 restartPolicy 处理。上述分工由配置定义，不是 kubelet推断故障是否能靠重启解决 | 核心用途和组件书面通过；门控、阈值和动作边界已讲解待复述 |
| 4a–b 检查深度 | a：解析证明 mydb DNS 映射，建议简单 SELECT 或 mysql ping 验证；b：TCP 结果与改进不确定 | DNS 与业务可用边界及 SELECT 思路正确。若指 mysqladmin ping，它仅检测服务存活，Access denied 也可退出 0，不能证明应用账户能查询。TCP 连接可建立则本题 TCP 检查成功，不检查 HTTP 500；可用有实际意义的 HTTP 健康端点／exec 校验，分别设计就绪与存活条件。不要把外部数据库短暂异常无差别用于 liveness 重启所有应用 | DNS 与查询验证思路通过；ping 限制、TCP 与 HTTP 边界已讲解未验证 |
| 5a–b Service | A 可以，B 不 Ready，C 标签不匹配；认为 A 不重启，因为 liveness 通过，可能依赖延迟重启无用；不知道后端变化与恢复后是否接流量 | A/B/C 静态判断正确，额外 version 标签不影响匹配。A 不因 readiness 失败重启的结论正确，但根本原因是 readiness 不直接触发重启，不是系统推断重启无益。状态同步后 A 不再是就绪后端，B/C 仍不合格，所以本题可用后端为 0；Pod 与 Service 对象仍存在。持续探测达到恢复条件、Pod Ready 后，A 可重新接新流量，不需重建；不保证所有连接当刻中断或固定 HTTP 错误码 | 静态选择与不重启结论通过；准确因果和动态恢复已讲解待复述 |
| 6a–c 重启排障 | a：退出由 Always 触发恢复，CrashLoopBackOff 为间隔延长；b-1：`kubectl get pod api-demo -n k8s-lab-lifecycle -o wide`、`kubectl describe pod api -n k8s-lab-lifecycle`；b-2：`kubectl logs pod api-demo -n k8s-lab-lifecycle -c api --previous --timestamps`，想查上一次终止实例日志；c：字段不确定 | a 核心正确，是主进程退出，非永久停试；v1.22 默认退避有上限。get wide 正确但不包含完整事件/退出原因；describe 的对象应为 Pod api-demo，api 是容器名。logs 参数应为 POD 或 TYPE/NAME，删除独立的 pod 参数或用 pod/api-demo；--previous/--timestamps 意图正确。退出码主要查 Last State/Reason/Exit Code，不保证日志内打印；日志用于关联应用错误。以 metadata.uid 区分 Pod 身份，同 UID 下结合 api 的 containerID 变化及 restartCount 判断容器重启；新 UID 是新 Pod，同名也可能不同对象 | 重启/退避与 previous 概念通过；命令定位、语法与身份字段已纠正待验证 |

- 正确命令示例（只讲解，未执行）：在配好 kubeconfig 的 master 上，`kubectl describe pod api-demo -n k8s-lab-lifecycle` 查看容器 State/Last State、Reason、Exit Code、Restart Count 及 Events；`kubectl logs api-demo -n k8s-lab-lifecycle -c api --previous --timestamps` 获取尚可用的上一次实例日志；`kubectl get pod api-demo -n k8s-lab-lifecycle -o yaml` 查看 metadata.uid 与 status.containerStatuses 中 api 的 containerID/restartCount。题目对象未确认存在，不伪造输出。
- 官方核对：沿用 4.27 的 init、钩子和 v1.22 生命周期／探针来源，新增 [kubectl logs 参数](https://kubernetes.io/docs/reference/kubectl/generated/kubectl_logs/)、[ConfigMap 文件挂载](https://kubernetes.io/docs/concepts/configuration/configmap/)、[MySQL mysqladmin ping 的边界](https://dev.mysql.com/doc/refman/8.4/en/mysqladmin.html)。本轮为作答反馈与助手补充，不冒充新的课程原话或视频实验。
- 针对性复盘（R1–R3，均待答；末尾附空白模板）：R1：普通 init-a 成功、init-b exit 1；a）Always 下重试谁、app 能否启动；b）Never 下结果。R2：a）startup 未成功时另外两类是否探测；b）启动后 readiness 失败、liveness 正常，是否因此重启及是否继续接普通 Service 新流量；c）就绪恢复后能否重新接流量。R3：假设 Namespace=training-life、Pod=order-api-0、容器=server；a）写 describe 事件/退出状态命令；b）写上一次 server 实例日志命令；c）说出识别 Pod 是否被替换的关键字段。命令只书面作答，不要求实操。
- 后续边界：退出宽限期、TCP 检查、配置共享及 MySQL ping 等本轮补充仍标已讲解未验证，不因未纳入三题复盘而自动通过。保留既往命令正确证据，同时记录本轮新场景迁移错误。无集群连接或新实验，学习时长未知，未正式归档。

## 5 下次续接

先读 [PROGRESS.md](PROGRESS.md) 和 4.28 的逐题反馈；原六题已全部提交，从新复盘 R1–R3 接收回答。保留历史正确证据和本轮迁移错误，按最新回答更新，不把原题重新记成未答。退出宽限期、TCP 等补充尚未验证。题目对象均为假设；此前 lab-web 是否存在及镜像故障仍未确认，实操先取证据，不自动创建或清理资源。实际学习时长未知。

对应 P14–P25 的问题可直接查阅 [预习索引](video-notes/P014-P025-预习索引.md)；助手预习完成不覆盖上述未验证概念和历史实验状态。

## 6 归档记录

暂无。合并后记录原日期与正式笔记链接，避免重复计时或遗失未解决问题。

## 7 2026-11-03 配置补充：Mac 迁移与会话自动同步

- 用户要求：将项目上传到指定 GitHub 仓库，在公司 Mac 接续使用；已确认采用会话开始自动拉取、每次保存学习记录后自动提交推送。会话之外不运行后台定时同步。
- 平台约束：实际集群仅安装在 Windows VMware；Mac 不连接、探测或操作集群，也不向用户布置或追问需要集群实时输出的实操。可进行概念解释、命令书面推演和考核，未执行内容继续标为未验证。
- 新增 [Mac 配置与上下文](../MAC_SETUP.md)、[同步说明](../SYNC_WORKFLOW.md) 和跨平台脚本，并同步项目规则及学习画像。GitHub 登录、全局 skills、MCP、Cookie、私钥和 `.local/` 缓存不由 Git 迁移。
- 当前学习位置仍为已报告学习 P18；2026-11-02 原六题已提交，新复盘 R1–R3 待答。本次修正进度文档中残留的“六题待答”旧句，没有新增掌握证据、实验或学习时长。
