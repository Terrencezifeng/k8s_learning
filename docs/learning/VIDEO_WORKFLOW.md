# 视频笔记读取与复用

验证日期：2026-10-28；2026-10-29 增补 P14–P25 字幕与关键画面流程。本文件保存已验证的方法，避免后续会话重复遇到相同问题。

跨设备说明（2026-11-03）：下述绝对路径、登录状态、`.local/` 辅助脚本和依赖为原 Windows 本地记录，不随 Git 上传。Mac 可直接使用已同步的笔记和教学图片；如需新抓取，再按 [Mac 配置说明](../MAC_SETUP.md) 独立准备工具和登录，不假定这些缓存存在。

## 1 已安装与已验证

- 用户指定的 [bilibili-obsidian-notes](https://github.com/le876/bilibili-obsidian-notes) 已安装在 `C:/Users/TERRENCE/.codex/skills/bilibili-obsidian-notes/`。使用前读取其 SKILL.md。
- 项目本地依赖在 `.local/python-deps/`，包括 qrcode 与 yt-dlp 2026.10.26；安装没有修改全局 Python 包。
- 登录已通过 B 站 nav 接口验证。有效的 Netscape 格式 Cookie 位于 `.local/bilibili/cookies.txt`，仅用于 B 站；不得打印其内容或提交版本控制。
- P13 正确字幕位于 `.local/bilibili/BV1PbeueyE8V/P013/yt-dlp-ai-zh.srt`，共 255 条；`subtitle.json` 为用 skill 解析函数转换的版本，`source.json` 保存来源与验证范围。
- 课程笔记为 [P013-什么是资源.md](video-notes/P013-什么是资源.md)。
- 2026-10-28 按用户要求补读 P1–P12：12 节共 7,211 条中文 AI 字幕，分别保存于 `.local/bilibili/BV1PbeueyE8V/P001/` 至 `P012/`。各目录包含 SRT、`subtitle.json`、带时间位置的 `transcript.txt` 及来源元数据 `source.json`；分 P/CID 目录索引为同课程目录下的 `parts-01-12.json`。
- 前十二节的标题、分 P、时长与字幕主题已核对；P5 与 P1 高度重复，已比较字幕差异。回顾文档为 [P001-P012-已学内容回顾.md](video-notes/P001-P012-已学内容回顾.md)，未逐帧查看课件或核对音频。

## 2 本次兼容问题

1. skill 原始扫码脚本仅从跳转 URL 取参数，没有保留登录响应 Cookie；虽然文件写入成功，登录校验仍返回未登录。该次生成的 `.local/bilibili/BBDown.data` **不是有效登录凭据，不要使用**。
2. 临时兼容程序 `.local/bilibili/login_with_cookiejar.py` 保留响应 Cookie，仅允许 B 站 HTTPS 请求和重定向；通过 nav 验证后才保存 `cookies.txt`。7 个 URL 边界检查通过，实际扫码登录已验证。
3. 首次直接 player 接口返回的字幕与课程不符，已排除并单独保留为 `.local/bilibili/BV1PbeueyE8V/P013/rejected-unrelated-subtitle.json`，**不得用于课程笔记**。原因尚未确定。
4. 随后使用 yt-dlp 的 B 站提取器取得与 P13 相符的字幕，并检查标题、分 P、时长和整份字幕主题。不能仅凭 HTTP 成功或字幕文件存在就认定来源正确。

## 3 后续字幕获取

优先复用已校验字幕；需要重新获取时，可在项目根目录的 PowerShell 中运行：

```powershell
python -B -X utf8 -c "import sys, runpy; sys.path.insert(0, r'.\.local\python-deps'); runpy.run_module('yt_dlp', run_name='__main__')" --cookies '.\.local\bilibili\cookies.txt' --no-playlist --skip-download --write-subs --sub-langs 'ai-zh,zh-Hans,zh' --sub-format srt -o '.local/bilibili/%(id)s/%(id)s.%(ext)s' 'https://www.bilibili.com/video/BV1PbeueyE8V/?p=13'
```

该命令读取字幕，不下载整段视频；输出路径带分 P 标识。命令的等价 Python 提取路径已实际验证。更换章节时替换 URL 的 `p` 并重新核对内容；不要覆盖已有学习问答。

登录失效时，先确认需要用户重新扫码，再运行临时登录程序生成新二维码。二维码需要用户在 B 站 App 中扫描并确认，不能把生成二维码当作已经登录。

如学习涉及板书、图表或具体命令画面，再按 skill 的关键帧流程获取并实际查看画面。2026-10-28 的 P1–P13 回顾没有提取关键帧或核对音频；2026-10-29 的 P14–P25 画面读取见下方，不混淆两次范围。

## 4 2026-10-29：P14–P25 字幕与高清画面

- 用户指定先精读 P14–P25，后续随学习进度继续。本批已完整读取 6,268 条中文 AI 字幕；12 节视频合计 17,138 秒，不能当作用户学习时长或助手完整播放时长。
- 字幕兼容流程脚本为 `.local/bilibili/review_14_25.py`，沿用现有有效 Cookie 和项目本地 yt-dlp，使用 skill 的 SRT 解析函数。官方分 P/CID/时长表存于 `.local/bilibili/BV1PbeueyE8V/parts-14-25.json`。
- 各分 P 缓存目录为同课程下 `P014/` 至 `P025/`，分别包含 `yt-dlp.ai-zh.srt`、`subtitle.json`、`transcript.txt`、`source.json`。本批元数据及字幕主题已核对，字幕文件哈希互不重复。不得复用 P13 CID 或被排除的字幕。
- 项目本地安装 imageio-ffmpeg 0.7.0，使用其 FFmpeg 7.1 二进制；未安装到全局 Python。`.local/bilibili/review_frames_14_25.py` 用 yt-dlp 取得视频流，再让 FFmpeg 在选定时间寻址并解码一帧，取得 12 张 1920×1080 图；没有保存完整视频或核对音频。
- 目标时间保存在 `.local/bilibili/frame-targets-14-25.json`；每节 `frames/frame-NNNN.png` 和同名 JSON 保存画面、CID、请求秒数、分辨率和实际核验状态。流链接仅在取帧时使用，不写入正式资料。登录信息不打印，不写入文档或日志。
- `.local/bilibili/review_contact_sheet.py` 生成总览图；先看总览，再逐张用图像查看工具阅读原帧。关键帧只证明对应时刻可见内容，不能据单帧推断全部运行结果。
- 已调用 skill 的 `touch_video_activity` 更新各分 P 的保留记录；没有额外设置后台清理或定时任务。必要教学插图复制至 `docs/learning/video-notes-images/P014-P025/`，原始缓存保留在 `.local/`。
- 正式入口：[P14–P25 预习索引](video-notes/P014-P025-预习索引.md)、[关键画面核对](video-notes/P014-P025-关键画面核对.md)。各分组笔记保留读取限制和独立问答章节；后续不能重新生成覆盖用户新增问答。
