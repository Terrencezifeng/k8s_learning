# VMware K8s 自动校时：实施与维护

日期：2026-10-29（Asia/Shanghai）。用户明确授权助手远程配置三台虚拟机。本次为环境维护与问答，不计作用户独立操作证据。

## 1 小范围需求与验收

- 目标：master、node1、node2 开机自动校时，VMware 挂起恢复后继续自动校时。
- 使用既有 chronyd 3.4 与 NTP 时间源；新增一个开机校时脚本和 systemd oneshot 服务。
- 校时偏差超过 1 秒时允许直接跳变，小偏差继续平滑修正；适用于频繁挂起的学习环境。
- 保留 Asia/Shanghai 时区与 UTC RTC；不升级 K8s，不改变应用配置。
- 验收：三台服务 enabled/active，NTP 来源可用，剩余校正量小于 0.5 秒，脚本成功；API readyz、节点、Pod 和现有服务访问复查。
- 网络离线时启动校时有界失败，chronyd 继续重试；不承诺无网络时获得准确时间，也不保证恢复瞬间即同步。
- 完整重启/VMware 挂起恢复的真实测试须单独记录，不能用服务重启冒充。

## 2 变更前基线

- CentOS 7，systemd 219，chrony 3.4；Kubernetes 客户端/服务端实查均 v1.22.2。
- 三台 chronyd 均 enabled/active；ntpd disabled/inactive；未安装 open-vm-tools。
- 约北京时间 2026-10-29 01:10，三台系统显示 2026-10-28 02:15 左右。
- chronyc tracking 的 System time：master 慢 82533.867 秒，node1 慢 82543.000 秒，node2 慢 82542.438 秒。这些是查询时快照。
- 时间源可达，存在选中来源；原配置 makestep 1.0 3 只允许服务启动后的前三次更新跳变，后续巨大偏差仅慢慢追赶。
- master 日志显示启动时小幅校正，随后检测到约 82791 秒偏差并开始渐进调整；未追溯到最初时钟偏差的唯一来源。
- 本机 Windows 查询 w32time 服务时返回未启动；本方案使用客体直接访问 NTP，不把宿主机时间作为唯一标准。
- 变更前 3 节点 Ready，15 个 Pod 均 Running/1/1，API readyz 通过，无 CronJob。
- 工作区资料全部为既有未跟踪文件；保留交接 ZIP、清单与其他学习记录。无项目构建/前端/CI，按系统脚本与集群运维方式验证。

## 3 配置

每台 /etc/chrony.conf 保留现有 server 与其他设置：
- server/pool 添加 minpoll 6 maxpoll 6（2^6=64 秒采样间隔）。
- makestep 1.0 -1：取消只在前三次更新跳变的限制。
- 保留 iburst 与 rtcsync。

每台部署：
- /usr/local/sbin/k8s-time-sync：源码见 ../../scripts/k8s-time-sync.sh。
- /etc/systemd/system/k8s-time-sync.service：源码见 ../../scripts/k8s-time-sync.service。
- chronyd 与 k8s-time-sync.service 均开机启用。

开机 helper 在 kubelet 启动任务之前执行，最多约 40 秒等待同步，systemd 超时为 50 秒；无网络时失败不会永久阻止 kubelet 启动。挂起恢复不重跑开机服务，由仍运行的 chronyd 按上述配置重新测量和自动校正。通常需一个或数个采样周期，具体取决于 NTP、DNS、网络恢复与来源选择。rtcsync 在正常同步后周期性更新 RTC，开机 helper 成功时也写入 RTC。

## 4 检查与手动触发

以下在要检查的每一台 Linux 虚拟机执行：

```bash
# 查看当前时间、服务与同步状态
date
systemctl is-enabled chronyd k8s-time-sync
systemctl status chronyd k8s-time-sync --no-pager
chronyc tracking
chronyc sources -v
timedatectl status

# 必要时主动发起测量并等待同步
sudo systemctl restart k8s-time-sync

# 查看本次启动的校时日志
journalctl -u chronyd -u k8s-time-sync -b --no-pager

# 手工编辑配置（之后需要重启 chronyd）
sudo vim /etc/chrony.conf
```

chronyc tracking 的 Leap status=Normal 还不够，应同时看 System time 的剩余校正量和来源的新鲜程度。初始三台就是来源正常但仍有约 23 小时未校正。timedatectl 的同步标志可能稍后才更新。

## 5 安全与回滚

- root 所有的固定路径脚本，0750；service 0644；未引入远程下载执行、凭据、额外监听端口或应用接口变更。
- 保留已有公共 NTP 源。Chrony 3.4 的现有 NTP 配置不提供 NTS 认证，本次不扩大为公网授时服务。
- 大偏差可产生向前或向后跳变，会影响依赖墙上时间的任务；这是频繁挂起实验环境的明确取舍。
- 原始配置和服务启用状态存入每台 /root/k8s-time-sync-backup.*；精确路径见验收记录。
- 回滚时在对应节点先停止并禁用新增 oneshot 服务，再从该节点备份恢复 chrony.conf、重启 chronyd。恢复旧策略也会恢复其挂起后大偏差慢慢追赶的问题。
- 新服务/脚本如需要移除，仅移除上述明确新增的两个路径，执行 systemctl daemon-reload。不要删除既有 chrony 数据或 Kubernetes 配置。

## 6 官方依据

- [Chrony 3.4 配置：makestep、minpoll/maxpoll、rtcsync](https://chrony-project.org/doc/3.4/chrony.conf.html)
- [Chrony 3.4 命令：burst、waitsync、tracking](https://chrony-project.org/doc/3.4/chronyc.html)
- [VMware Linux 客体时间同步建议](https://knowledge.broadcom.com/external/article/310053/timekeeping-best-practices-for-linux-gue.html)

## 7 实际验收

验收时间：北京时间 2026-10-29 01:19–01:20。

| 节点 | 原始配置备份目录 | 同步检查 |
| --- | --- | --- |
| master | /root/k8s-time-sync-backup.QnfgT4 | waitsync < 0.5 秒通过，NTP synchronized=yes |
| node1 | /root/k8s-time-sync-backup.0dgxzg | waitsync < 0.5 秒通过，NTP synchronized=yes |
| node2 | /root/k8s-time-sync-backup.oDqvZE | waitsync < 0.5 秒通过，NTP synchronized=yes |

- 三台 chronyd 为 active/running，k8s-time-sync 为 active/exited、Result=success、ExecMainStatus=0；两服务均 enabled。oneshot 的 active/exited 表示一次任务已成功完成。
- 三台逐一通过 bash -n、systemd-analyze verify，以及 chronyd -Q 只读 NTP 测量与候选配置解析检查。
- 初版 helper 在两个 worker 上因刚启动时 DNS 尚未解析、burst 返回 503 No such source 而提前失败；已修正为允许该预热请求暂时失败，随后依靠有界 waitsync 确认真正同步。重新启动 chronyd 后三台都实际遇到该条件并成功完成，覆盖此启动时序问题。
- 配置生效后校正了约 82500 秒的巨大偏差。校时后的微秒级 System time 仅表示 Chrony 估算的剩余校正量，不是独立测出的绝对授时精度；NTP 网络路径仍有毫秒级延迟与不确定性。
- 三台部署脚本 SHA256：b2b2f140a5decc7d7ac308eae9653b75541d3d6208502acd9a9417a148b287df；service：1ee5cf5ec5be0d8124d960d24f9d62fd3839bc462d2e984bcba92d723f3d1200，与工作区源码一致。
- 最后集群检查：3 个 Ready 节点，16 个 Running/1/1 Pod，API readyz 全通过（含 etcd），Nginx NodePort HTTP 200，Dashboard HTTP 200（原有自签名证书，用 -k 只验证 HTTP 访问）。
- 检查期间出现 k8s-lab-20261029/web-5dcdf98765-d2pld，运行于 node1；这解释了前后 Pod 数从 15 变 16。本会话没有创建、修改或删除该实验对象，不据此记录用户创建过程或知识掌握情况。
- 原有 15 个 Pod 的重启计数在前后检查中保持一致。校时后 AGE 和“多久前重启”显示变化源于时钟调整，不能当作新增重启。
- master 复查 NTP 控制端口仅监听 127.0.0.1/::1:323，没有增加公网 NTP 服务。
- **未执行整机重启、实际 VMware 挂起恢复或断网测试**。启动服务的重新执行通过；恢复后的自动校时依据 chronyd 的持续运行、已验证配置及官方行为。下次实际挂起恢复后应再次检查，不宣称已经通过此场景实测。
- 完整命令输出节选：../../logs/time-sync-20261029.json。

回滚示例：在要回滚的虚拟机以 root 执行，BACKUP 必须使用上表对应节点的目录：

```bash
# 例：master；在其他节点先换成对应目录
BACKUP=/root/k8s-time-sync-backup.QnfgT4
test -f "$BACKUP/chrony.conf" || exit 1
systemctl disable --now k8s-time-sync.service
cp -a "$BACKUP/chrony.conf" /etc/chrony.conf
restorecon /etc/chrony.conf
systemctl restart chronyd.service
```

以上会停用本次开机 helper 并恢复原 Chrony 策略，保留脚本以便审阅；不把时钟拨回错误时间。

## 8 学习中的问题与解答

**用户问题一：关机开机后时间没有同步，能否代为配置开机和挂起恢复后的自动校时？**

已由助手远程配置并验证时间服务重新启动。问题原因已观察到：已有 NTP 来源可达，但默认只允许前三次更新跳变，恢复后约 23 小时的大偏差持续缓慢修正。增加 boot helper 与持续自动大偏差修正规则。VMware 真实挂起/恢复验证尚未执行。用户亲手配置能力未考核，学习时长未知。

**用户问题二：时间同步有问题会影响 K8s 哪些功能？**

- TLS 证书：当前时间用于有效期校验；时钟太慢或太快可能报证书尚未生效/已过期，影响 kubectl、API Server、kubelet 或 etcd 的 TLS 通信。若 kubelet 因认证失败不能上报，节点状态和调度会间接受影响。时差并不保证立即导致节点 NotReady，本次修复前节点仍 Ready。
- 带有效期的令牌：v1.22.2 ServiceAccount TokenRequest 令牌含签发、生效和过期时间；错误时钟可导致验证失败。不把所有旧式长期 Token 一概当作相同行为。
- CronJob：依据控制器时间计算调度、遗漏和启动截止期限；时间错误/跳变可能导致错点执行、遗漏或错过截止期限。当前集群没有 CronJob；没有为演示新增任务。
- 日志、事件、AGE 和监控：各节点时间线错位、对象年龄误导排障；依赖时间戳的指标也可能受影响。
- 业务容器：通常共享所在 Node 的系统时钟，登录有效期、业务 TTL、定时任务与签名校验也可能受影响；具体以应用实现为准。
- 时区决定显示方式，NTP 校正实际时刻。当前三台 Asia/Shanghai 已正确，问题不是 8 小时时区偏差。
- 没有依据将任意小时间差等同于 etcd 数据损坏；本次 readyz 的 etcd 检查通过。

官方核对：[Go X.509 时间校验](https://pkg.go.dev/crypto/x509#VerifyOptions)、[K8s v1.22.2 ServiceAccount 验证源码](https://github.com/kubernetes/kubernetes/blob/v1.22.2/pkg/serviceaccount/claims.go)、[K8s v1.22.2 CronJob 控制器](https://github.com/kubernetes/kubernetes/blob/v1.22.2/pkg/controller/cronjob/cronjob_controllerv2.go)、[CronJob 调度限制](https://kubernetes.io/docs/concepts/workloads/controllers/cron-jobs/)。
