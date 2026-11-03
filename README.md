# K8s 入门项目

这套 VMware 测试集群已于 2026 年 10 月 28 日完成修复，形成 1 个 Master 和 2 个 Worker。这个目录保存当前计划、集群交接资料和完整排障记录，供后续学习和运维继续使用。

| 节点 | IP | 角色 | 修复验收状态 |
| --- | --- | --- | --- |
| master | 192.168.169.3 | Master | Ready |
| node1 | 192.168.169.4 | Worker | Ready |
| node2 | 192.168.169.5 | Worker | Ready |

版本为 Kubernetes v1.22.2、containerd 1.5.5、Flannel v0.15.0。表中的状态是修复验收快照；每次实验开始时可按检查命令重新确认。

## 1 从这里开始

在公司 Mac 接续学习，先读 [Mac 配置与上下文](docs/MAC_SETUP.md) 和 [学习会话自动同步](docs/SYNC_WORKFLOW.md)。Mac 只进行阅读、讲解和书面考核，集群实操留在 Windows。

1. 阅读 [当前计划](PLAN.md)，区分已完成的修复与后续学习建议。
2. 阅读 [集群交接说明](docs/CLUSTER_CONTEXT.md)，了解连接方式、网络和已知限制。
3. 使用 [日常检查命令](docs/CHECK_COMMANDS.md) 查看集群状态。
4. 遇到问题时查阅 [中文 Debug 日志](logs/k8s-debug-20261028.log) 和 [原始修复记录](logs/k8s-repair-20261028.log)。

## 2 项目文件

| 文件 | 用途 |
| --- | --- |
| PLAN.md | 当前目标、完成项、验收标准和后续学习顺序 |
| docs/CLUSTER_CONTEXT.md | 节点、SSH MCP、网络、修复变更与交接上下文 |
| docs/CHECK_COMMANDS.md | 按执行位置划分的检查命令 |
| inventory/cluster.json | 可由程序读取的集群信息，不含登录凭据 |
| logs/k8s-debug-20261028.log | 中文根因分析、失败与重试、原始命令附录 |
| logs/k8s-repair-20261028.log | 修复阶段保存的原始执行记录 |
| PACKAGE-MANIFEST.json | 文件清单、大小和 SHA-256 校验值 |

## 3 已验证的访问入口

- [Nginx 测试服务](http://192.168.169.3:30255)
- [Kubernetes Dashboard](https://192.168.169.3:32320)

修复验收时，从 master 访问这两个入口均返回 HTTP 200。Dashboard 探测使用了自签名证书兼容方式；登录 Token 不包含在项目中。

## 4 在新的 Codex 对话中继续

日常打开本项目的学习会话后，直接说 **“今天继续，我接下来应该学什么、复习什么？”** 即可。助手会先同步并读取最新记录，简要提示当前位置、已有掌握证据、优先复习点和建议下一步；规则适用于 Mac 与 Windows。仅打开文件夹不会自动发送消息。

可以直接发送：

> 请先按 AGENTS.md 执行学习同步 pull，成功后重新读取项目规则、README.md、PLAN.md、docs/learning/PROGRESS.md 和 PENDING.md，从最新记录继续。若当前在 Mac，只做阅读、讲解和书面考核，不连接集群或布置真实集群实操。每次保存学习记录后自动同步 push，Linux 编辑器默认使用 vim。

项目使用本机已有 SSH MCP。密钥仍位于原来的 Windows .ssh 目录，压缩包不携带私钥，也不会在另一台电脑上自动获得服务器访问权限。

## 5 学习规则与记录

项目内学习会话遵循 [AGENTS.md](AGENTS.md)：以亲手实验为主，用 Linux、Docker、脚本和 infra 运维经验辅助理解，Linux 编辑默认使用 vim。

- [学习者画像](docs/learning/PROFILE.md)：学习目标、讲解方式和记录约定。
- [当前进度](docs/learning/PROGRESS.md)：课程位置、实践证据、卡点和下次起点。
- [P1–P12 已学内容回顾](docs/learning/video-notes/P001-P012-已学内容回顾.md)：用户确认前十二节学习完成，已补读字幕并整理与当前环境的对应关系。
- [短时学习暂存](docs/learning/PENDING.md)：不足半小时先保留，下次续接合并。
- [学习记录模板](docs/learning/SESSION_TEMPLATE.md)：包含独立的“学习中的问题与解答”章节；正式记录保存到 `docs/learning/records/`。
- [P13 课程笔记初稿](docs/learning/video-notes/P013-什么是资源.md)：基于已校验字幕整理，待学习时补充问答与实践结果。
- [P14–P25 预习索引](docs/learning/video-notes/P014-P025-预习索引.md)：助手已精读本批字幕并逐张检查 12 张关键画面，附分组笔记、时间戳和版本差异；不改变用户学习进度。
- [视频读取方法](docs/learning/VIDEO_WORKFLOW.md)：已验证的登录、字幕读取路径与当前限制。

新学习会话可以发送：

> 请先按项目 AGENTS.md 同步并读取学习进度和短时暂存，提示我目前学到哪里、该复习什么以及建议的下一步。按当前设备安排学习：Mac 只做阅读和书面练习，Windows 在我明确要求时再进入集群实操。

视频字幕、下载媒体、临时依赖与登录状态放在忽略版本控制的 `.local/` 中。`PACKAGE-MANIFEST.json` 和交接 ZIP 保留原交接包快照，未包含后来新增的学习规则和记录。
