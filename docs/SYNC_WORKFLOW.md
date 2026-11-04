# 学习会话自动同步

确认日期：2026-11-03。用户选择“会话开始拉取、学习记录保存后提交并推送”；目标固定为 `Terrencezifeng/k8s_learning` 的 `main`。自动同步由项目规则驱动 Codex 调用脚本，不是常驻服务。

## 1 时机与范围

| 时机 | 动作 | 完成依据 |
| --- | --- | --- |
| Mac／Windows 开始学习会话 | 先运行 `pull`，成功后再读取最新项目规则和学习进度 | 脚本退出码为 0、显示 Pull complete |
| 每个实质问答、复盘或实验记录保存后 | 运行 `push`，自动提交本次 Markdown 记录并推送 | 退出码为 0、显示 Push complete 和提交短 SHA |
| 用户表达学习结束 | 按既有规则整理草稿／正式记录，再执行 `push` | 最终报告本地保存与推送状态 |
| 会话外使用 Typora | 先保存文件；下次由 Codex 检查本地修改，或手动运行 `push` | 未保存到磁盘的编辑无法同步 |

自动提交范围为根目录 `AGENTS.md`、`README.md`、`PLAN.md` 和 `docs/` 下的普通 UTF-8 Markdown 文件，支持中文路径及删除记录。代码、图片、清单和日志同样可以通过 Git 迁移，但修改这些文件时需在相应任务中检查后显式提交，不由学习记录同步脚本自动发布。目录白名单和凭据模式检测只是防误传措施，不能保证识别所有秘密；笔记中仍不得填写凭据。

不会上传 `.local/`、IDE 设置、登录状态、私钥、kubeconfig 或虚拟环境。同步不使用 `git add .`，也不会把已有手动暂存内容混入学习提交。历史 ZIP 与清单继续保持原快照。

## 2 执行方法

在 **Mac 项目根目录**执行：

```bash
python3 scripts/learning_sync.py pull
python3 scripts/learning_sync.py push
```

在 **Windows 项目根目录的 PowerShell**执行：

```powershell
python -B -X utf8 scripts/learning_sync.py pull
python -B -X utf8 scripts/learning_sync.py push
```

`pull` 获取远端并仅允许快进更新；`push` 先检查远端，再扫描、提交合规的本地 Markdown 变化并推送。首次准备依赖和 GitHub 登录见 [Mac 说明](MAC_SETUP.md)。两端均需 Git、Python 3.9+、提交身份和可用的 Git 推送凭据；脚本不会将凭据写进命令参数或项目。

## 3 异常与恢复

| 情况 | 脚本处理 | 下一步 |
| --- | --- | --- |
| 开始时存在本地修改 | 停止 pull，保留文件 | Codex 先检查是否为上次未同步学习记录；若是则运行 push，成功后重新 pull |
| 远端已更新且本地有未提交修改 | 停止，不覆盖本地 | 保留双方内容，结合 diff 在单独修复步骤中合并；不要反复重试或自动选一边 |
| 两端分别产生了提交 | 停止，不自动 merge/rebase | 查看提交差异，人工决定合并方式；禁止 force push、reset --hard |
| 已有暂存文件或进行中的 Git 操作 | 停止，保留暂存／冲突状态 | 先完成或处理原操作，再重试 |
| 网络或登录失败 | 非零退出；已生成的本地提交仍保留 | 修复网络／登录后再 push，不能报告上传成功 |
| 疑似凭据、非 Markdown 变化、符号链接或大文件 | 停止并只报文件名，不打印可疑内容 | 检查文件及尚未推送的历史；删除当前文本不代表旧提交中的秘密消失 |
| 同步锁存在 | 停止 | 确认没有同步进程后，才能处理 `.git/learning-sync.lock`；不要自动删除活动锁 |
| 远端在推送前又发生变化 | 普通 push 拒绝 | 本地提交保留，拉取检查后处理分叉；不强制覆盖远端 |

扫描或提交在暂存后失败时，相关文件可能保留在暂存区供检查；脚本不会擅自重置它。日常建议一台电脑结束并推送成功后，再从另一台继续编辑。

若工具环境限制网络，Codex 可以在用户已授权同步的范围内申请该次网络权限；失败需明确报告，不能将“准备提交”或“本地已保存”等同于 GitHub 已更新。

## 4 实现约束与验收

- 使用现有 Git 凭据；只允许预设 GitHub origin 和单一推送目标；只在 main 执行。
- 工作树有未提交修改时不拉取覆盖，不自动 stash，不自动合并分叉，不强推。
- 自动提交前检查 Markdown 路径、UTF-8、文件大小、符号链接和常见凭据模式；推送前还检查全部未发布提交，避免只删除最新版本中的凭据却泄露历史版本。
- 文件锁防止两个同步脚本同时运行；不代替编辑器的保存，也不能替代与其他 Git 工具的协调。
- 脚本不调用 SSH、kubectl、Docker 或任何集群组件。macOS 操作边界由项目规则明确约束。

## 5 验证命令与已知限制

在项目根目录执行（Mac 将 `python` 换为 `python3`）：

```bash
python -B -m unittest discover -s tests -v
```

集成测试在临时目录创建本地 bare 仓库和两个克隆，验证跨电脑往返、重复同步、脏工作树、分叉、已有暂存、忽略文件、凭据拦截、未推送历史与推送失败恢复；不访问真实 GitHub 或集群。GitHub Actions 对 Windows、macOS、Linux 分别运行这些测试，不配置自动部署或发布凭据。

Windows 的本地验证与实际 GitHub 推送可以在当前电脑完成。公司 Mac 的首次登录、Codex 项目打开和实际同步需在该电脑执行，不能仅凭 CI 通过认定其本地环境已配置完成。

Git 快进与合并行为参考 [Git 官方文档](https://git-scm.com/docs/git-merge)。

## 6 首次迁移验证记录

- 2026-11-03：首次提交 `5d743b9` 已推送至指定 GitHub 仓库 main，本地与远端 SHA 一致；共发布 45 个文件，排除 `.local/` 和 `.idea/`，历史 ZIP、清单及日志按原始字节保留。
- Windows 本地 13 项同步集成测试通过；真实仓库上的脚本 `pull` 与无变化 `push` 均成功，工作树干净。
- 已配置三平台 GitHub Actions；运行结果以 [Actions 页面](https://github.com/Terrencezifeng/k8s_learning/actions) 为准。公司 Mac 尚需按迁移说明配置 Git、Python 和登录，不能把 CI 或 Windows 验证等同于公司 Mac 已安装完成。
- 2026-11-04：Mac 已安装并验证 GitHub CLI 2.103.3；用户完成浏览器授权后，本机活动账户与 keyring 认证验证通过，真实脚本 push 成功，积压的 4 个学习提交已补推至 `6f5ec7d`。随后独立读取远端 main，确认与本地 HEAD、origin/main 一致，工作树干净；此前“Mac 尚需首次配置”的状态已解除。详见 [Mac 说明](MAC_SETUP.md) 2.3；此 SHA 为补推验收点，后续记录提交会推进 main。

## 7 2026-11-05 核查：同步成功，macOS 自动检查曾因 Runner 容量失败

用户发现 GitHub 上的失败标记后，已分别核对文件同步和 Actions 检查，结论如下：

| 核查项 | 实际证据 | 结论 |
| --- | --- | --- |
| 仓库与认证 | 指定 origin、main 分支；Terrencezifeng 的 keyring 授权有效 | 未出现登录或仓库目标错误 |
| 同步提交 | 核查时本地 HEAD、origin/main、GitHub refs/heads/main 均为 efbcaf171e53dee63f0e3b2039f3ba613453984f，工作树干净 | 最新学习记录已推送；此 SHA 为诊断起点，后续诊断记录提交会推进 main |
| 学习文件 | 远端 PROGRESS.md、PENDING.md 的 Git blob SHA 与本地提交一致；远端记录包含 F1a 补填通过与短复盘收尾 | 最近的学习进度和问答内容没有遗漏 |
| 同步脚本 | 本机实际执行 pull 退出码为 0，返回 Pull complete | 拉取流程正常 |
| 本机测试 | python3 -B -m unittest discover -s tests -v，13 项全部通过 | 同步脚本离线回归通过 |
| 最新 Actions 初次运行 | run 41863078249 的 Windows、Ubuntu 均通过；macos-latest 无 Runner、无执行步骤，约 15 分钟后 cancelled | macOS 检查未开始执行，不是测试断言失败 |
| macOS 平台注释 | GitHub 报告托管 Runner 多次分配未成功，并提示 macOS arm64 容量不足 | 根因为该次 GitHub 托管 Runner 资源分配失败 |
| 重跑验证 | 仅重跑 macOS job，run 41863078249 的 attempt 2 整体 success，三个平台均为 success | 本次检查恢复通过，保留现有工作流与同步脚本 |

前一次 run 41861645703 也表现为 Windows／Ubuntu 成功、macOS 在执行任何步骤前被取消。旧运行历史保留失败记录，不据此认定最新文件未上传。

以后排查时先区分两类结果：文件同步用脚本退出码、本地与远端提交 SHA 和工作树状态核对；自动检查用 Actions 的具体 job、步骤、注释和重跑结果核对。红色检查标记本身不能证明提交未推送。若属于 Runner 分配失败，可在授权范围内仅重跑受影响 job；若测试步骤实际执行并失败，再按日志定位脚本或环境问题，不直接强推、重置或改动学习记录。

本项目工作流由 push／pull_request 触发，使用只读 contents 权限，在 Windows、macOS、Ubuntu 运行离线同步集成测试。它不承担学习文件的上传，也没有生产部署或发布步骤。参考：[本次运行](https://github.com/Terrencezifeng/k8s_learning/actions/runs/41863078249)、[GitHub 重跑失败任务说明](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/re-run-workflows-and-jobs/re-run-failed-jobs-in-a-workflow)。
