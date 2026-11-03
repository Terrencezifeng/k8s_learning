# Mac 接续学习与项目同步

整理日期：2026-11-03。仓库：[Terrencezifeng/k8s_learning](https://github.com/Terrencezifeng/k8s_learning)。用户已确认公司 Mac 用于阅读、讲解、笔记和书面考核；集群仅在 Windows 电脑的 VMware 中运行。

## 1 第一次在 Mac 打开

需要 Git、Python 3.9 或以上（运行同步脚本）、Markdown 阅读器，以及用于学习的 Codex。阅读已有资料不需要 Docker、kubectl、B 站登录或视频工具。

在 **Mac 终端**执行，检查工具是否可用：

```bash
git --version
python3 --version
```

预期分别显示 Git 版本和 Python 3.9+。若未安装，通过公司的软件安装方式补齐；Git 可来自 Apple Command Line Tools，Python 可从 [Python 官方 macOS 下载页](https://www.python.org/downloads/macos/)安装。本项目同步脚本只使用标准库，不需要 pip 安装依赖。

在 **Mac 终端**克隆项目：

```bash
mkdir -p ~/Projects
cd ~/Projects
git clone https://github.com/Terrencezifeng/k8s_learning.git
cd k8s_learning
git status -sb
```

预期得到 `~/Projects/k8s_learning`，当前分支为 `main`，跟踪 `origin/main`。目录已存在时进入原目录并按同步说明更新，不要在其中再次克隆。

用 Codex 打开整个 `k8s_learning` 文件夹，使根目录的 `AGENTS.md` 成为项目规则入口；Typora 可打开 `README.md` 或 `docs/learning/PROGRESS.md`。规则和学习上下文以仓库文件为准，不依赖原电脑中的聊天记录。项目规则的加载方式参考 [OpenAI 官方说明](https://learn.chatgpt.com/docs/customization/overview)。

## 2 配置一次 GitHub 推送登录

公开仓库允许匿名克隆，但自动推送需要在 Mac 单独登录有写入权限的 GitHub 账户。本机现有 GitHub 认证不会随仓库复制。

若已经安装 GitHub CLI，在 **Mac 终端**执行：

```bash
gh auth login --hostname github.com --git-protocol https --web
gh auth setup-git --hostname github.com
```

按浏览器提示登录 `Terrencezifeng` 或已获仓库写权限的账户。没有 `gh` 时可按 [GitHub CLI 官方安装说明](https://cli.github.com/)安装，或沿用公司允许的 Git 凭据管理工具。同步脚本不接收 Token 参数，也不自动打开登录页面。命令依据：[登录说明](https://cli.github.com/manual/gh_auth_login)、[Git 凭据配置](https://cli.github.com/manual/gh_auth_setup-git)。

为此仓库设置提交身份（只影响当前仓库）：

```bash
git config user.name "Terrencezifeng"
git config user.email "89788335+Terrencezifeng@users.noreply.github.com"
python3 scripts/learning_sync.py pull
python3 scripts/learning_sync.py push
```

预期显示 `Pull complete` 和 `Push complete`。没有文件变化时不会创建空提交；第二条同步命令可检查推送权限。若出现 `SYNC STOPPED`，按 [同步说明](SYNC_WORKFLOW.md) 处理，不能据此认为已经同步成功。

### 2.1 2026-11-04 本机推送认证诊断

诊断时 Mac 检查结果：Apple Git 2.50.1 可用，origin 为本项目 HTTPS 仓库，Git 已配置 `osxkeychain` 凭据助手；当时终端找不到 `gh` 或 `brew`，常见 Homebrew 路径也未检测到 brew。GitHub CLI 后续安装结果见 2.2。已配置的 Git 姓名和邮箱用于提交署名，不代表已经完成 GitHub 登录。

本次执行 `git push --dry-run`，未写入远端，返回：

```text
fatal: could not read Username for 'https://github.com': terminal prompts disabled
```

这说明当前命令行 Git 没有取得可用 GitHub 身份。公开仓库可匿名下载／拉取，但推送需要有写权限的登录认证。钥匙串助手已配置，只代表 Git 知道从哪里查找凭据，不代表已经存入可用凭据；其他应用的登录状态也不能据此判断。

同步脚本主动设置 `GIT_TERMINAL_PROMPT=0`、`GCM_INTERACTIVE=never`，避免自动同步挂起等待输入。应先独立完成一次认证，再重试同步。推荐安装 GitHub CLI 后，在 Mac 终端执行：

```bash
gh auth login --hostname github.com --git-protocol https --web
gh auth setup-git --hostname github.com
gh auth status --hostname github.com
```

浏览器授权由用户本人完成，使用 `Terrencezifeng` 或有该仓库写权限的账户，并允许 Git 使用认证。之后在项目根目录执行 `python3 scripts/learning_sync.py push`；只有显示 `Push complete` 才能认为本地学习提交已经上传。本轮诊断没有安装新工具或更改 Git／钥匙串认证配置，本地提交继续保留。

依据：[GitHub 凭据缓存](https://docs.github.com/en/get-started/git-basics/caching-your-github-credentials-in-git)、[Git 提交署名](https://docs.github.com/en/get-started/git-basics/setting-your-username-in-git)、[gh 登录](https://cli.github.com/manual/gh_auth_login) 和 [Git 凭据助手配置](https://cli.github.com/manual/gh_auth_setup-git)。

### 2.2 2026-11-04 GitHub CLI 安装验证

用户明确要求安装 GitHub CLI。已从 [官方稳定版 v2.103.3](https://github.com/cli/cli/releases/tag/v2.103.3) 下载 macOS arm64 ZIP；GitHub 发布接口确认为非预发布版本，发布日期为 2026-10-26。安装包通过官方 SHA-256 清单校验，清单本身的 SHA-256 也与官方发布接口的 digest 一致。

- 可执行文件：`/Users/zifeng.deng/.local/bin/gh`，该目录原已位于 PATH，无需修改 shell 配置。
- 许可证：`/Users/zifeng.deng/.local/share/licenses/gh/LICENSE`。
- 实际验证：`command -v gh` 返回上述路径；`gh --version` 返回 `gh version 2.103.3 (2026-10-26)`；安装前后可执行文件 SHA-256 一致，架构为 Mach-O arm64。
- 登录状态：`gh auth status --hostname github.com` 返回尚未登录任何 GitHub 主机；安装成功不等于认证已完成。

本次使用官方独立安装包，未安装 Homebrew。下一步由用户在 Mac 终端执行 2.1 的浏览器登录与 Git 凭据配置命令；授权成功后重新运行学习同步 push，补传保留的本地提交。此处仅记录工具安装，不新增 K8s 学习完成度或实操证据。

## 3 给新学习会话的上下文

可直接将下面内容发给 Mac 上此项目中的 Codex：

```text
这是我从 Windows 同步来的 K8s 入门项目，目前在公司 Mac 上。
请遵守 AGENTS.md，先用 python3 scripts/learning_sync.py pull 更新，
成功后重新读取 AGENTS.md、README.md、PLAN.md、docs/MAC_SETUP.md，
以及 docs/learning/PROFILE.md、PROGRESS.md、PENDING.md。
Mac 只用于讲解、阅读和书面考核，不连接集群，不布置需要实际集群的操作，
也不要求我启动虚拟机或提供集群实时输出。命令可以作为书面推演，但标明未执行。
依据文件中的最新证据接续，不把已经提交的六道生命周期题当成未答。
每次更新学习记录后自动运行 python3 scripts/learning_sync.py push，
失败时保留本地内容并说明原因。考题最后附可填写的空白模板。
```

Git 同步的是文件和提交；Windows 的聊天会话、GitHub 登录、全局 skills 和 MCP 注册不由此迁移。

### 3.1 是否会出现 Windows 上相同的五个会话

**仅将项目推送到 GitHub 再在 Mac 克隆，不会自动复制 Codex 侧边栏的五个会话。** 本方案同步的是版本库文件，未导出或迁移 Codex 会话历史。

| 内容 | 此次 Git 同步是否包含 |
| --- | --- |
| 项目规则、进度、问答笔记、教学图片 | 包含 |
| 已写入 Markdown 的学习结论与待答题 | 包含，新会话可以读取并接续 |
| 五个会话的列表、消息历史、附件与原会话身份 | 不包含，不会因为 clone 自动重建 |
| 尚未记录到项目文件中的聊天内容 | 不包含，不能假定 Mac 的新会话知道 |

因此，Mac 的接续方式是在克隆目录中新建学习会话，并使用上面的上下文提示。也可以按主题新建多个会话，但它们是新会话，不能称为 Windows 原会话的完整复制。[OpenAI 项目与会话说明](https://learn.chatgpt.com/docs/projects?surface=app) 区分了共享文件上下文与各自的聊天记录。

若要移动原始会话，需要单独考虑 Codex 的会话交接功能及其主机连接条件；那是另一项配置，见 [官方远程连接与 Handoff 说明](https://learn.chatgpt.com/docs/remote-connections)。本次没有启用远程主机或迁移会话，Mac 禁止集群实操的约定继续适用。

### 3.2 日常自动提示学习进度与方向

完成首次配置后，在本项目的学习会话中直接发送：

```text
今天继续。我目前学到哪里了？接下来建议学什么、复习什么？
```

助手会读取同步后的最新记录，简短列出当前位置、已有掌握证据、优先复习点和一个建议下一步。建议随实际学习记录变化，不固定停留在本文的迁移快照；Mac 只给阅读和书面练习方向。用户只问安排时，不直接追加整套考题。仅打开文件夹不会主动发消息，具体规则见根目录 AGENTS.md 第 9 节。

## 4 当前接续点与证据入口

这是截至 **2026-11-02** 的迁移快照，之后始终以拉取后的 [PROGRESS.md](learning/PROGRESS.md) 为准。

| 项目 | 接续信息 |
| --- | --- |
| 用户基础 | 一年运维经验，熟悉 Linux、Docker 和部分脚本；类比以 infra 运维为主 |
| 已学位置 | 用户已报告学到 P18；P19 以后尚未报告已学 |
| 当前待答 | PENDING.md 的 4.28：R1 普通 init 重试与 Never；R2 startup 门控和 readiness 失败恢复；R3 describe/logs 对象定位与 Pod UID |
| 已有实践 | 四轮基础实验及清理已按指导亲手完成；本轮生命周期考核仅有书面证据 |
| 视频准备 | 助手预习已覆盖至 P25，已有笔记和 12 张教学图片；预习不等于用户掌握 |
| 学习时长 | 未知；不要把迁移、下载和同步耗时记作学习时间 |

重点阅读 [学习画像](learning/PROFILE.md)、[进度与掌握证据](learning/PROGRESS.md)、[原始问答暂存](learning/PENDING.md)、[P14–P25 资料索引](learning/video-notes/P014-P025-预习索引.md)。后续仍采用原理、运维类比、书面推演与复盘，保留未验证项。

## 5 Mac 的操作边界

- Mac 不安装或重建本项目集群，不调用 SSH/MCP/kubectl 去访问 VMware，不探测节点和 Dashboard，不要求用户进行实时集群实操。
- 可讲解命令、审阅 YAML、模拟输出和书面排障；示例必须注明假设，不能记录成真实运行结果。需要真实环境验证的点先记入待验证事项，回到 Windows 且用户明确进入实操时再开展。
- [集群交接说明](CLUSTER_CONTEXT.md) 内的 Windows 路径、私网 IP 和历史验收状态仅作背景。Mac 克隆后不会得到 VMware、SSH 密钥、kubeconfig 或原 SSH MCP。
- `scripts/k8s-time-sync.sh` 和 `.service` 属于 CentOS 7 虚拟机的历史维护脚本，不在 Mac 执行。`scripts/learning_sync.py` 才是本机跨设备同步入口。

## 6 视频工具与未同步的资料

已有 Markdown 笔记、问答和必要教学图片随仓库同步，可以直接阅读。`.local/` 中的 B 站 Cookie、二维码、字幕、下载视频、Python 依赖和临时兼容脚本不上传；Windows 的登录状态和 Python 二进制包不能作为 Mac 安装包。

如以后在 Mac 获取新视频资料，先读取 [VIDEO_WORKFLOW.md](learning/VIDEO_WORKFLOW.md)。需要独立安装用户指定的 [bilibili-obsidian-notes](https://github.com/le876/bilibili-obsidian-notes) skill，并按当时环境建立依赖和扫码登录。已知原始扫码脚本存在 Cookie 保留兼容问题；文中 `.local/` 辅助脚本属于原 Windows 本地文件，不应在 Mac 假定其存在。当前范围无需重新拉字幕或安装这些工具。

项目规则已在 `AGENTS.md` 中。未安装 `grill-me` 或视频 skill 不影响阅读现有笔记；需使用某技能时先查本机可用列表，再按 [OpenAI 技能安装说明](https://learn.chatgpt.com/docs/build-skills)配置，不照抄 Windows 的绝对路径。

## 7 日常切换电脑

同步的完整时机、范围、冲突处理和验证方法见 [SYNC_WORKFLOW.md](SYNC_WORKFLOW.md)。每次换电脑前，确认上一台会话已经提示推送成功；下一台会话开始自动拉取。Typora 在会话外的修改需先保存，再进入 Codex 会话处理，或手动执行同步脚本。没有后台定时任务。
