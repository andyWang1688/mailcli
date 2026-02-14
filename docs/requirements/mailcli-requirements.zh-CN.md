# Mail CLI 需求清单

## 项目目标

- 开源一个邮件 CLI 工具，优先支持腾讯企业邮箱（Exmail，IMAP/SMTP）。
- 提供简单安装方式：先支持 `pipx`/`pip`，后续支持 `brew`。
- 定位为 Himalaya 风格替代方案，重点提升 Exmail 场景稳定性。

## 范围定义

- 第一阶段仅支持 IMAP + SMTP（不支持 POP3）。
- 命令风格尽量贴近 Himalaya，降低迁移成本。
- 以社区可复用、可维护为目标，不做一次性脚本。

## P0：核心功能复刻（Himalaya Core）

- `account`：账号配置、账号列表、默认账号切换、基础诊断。
- `folder`：文件夹列表/创建/删除，支持 expunge/purge 语义。
- `folder list`：必须优先提供，用于列出邮箱服务端真实文件夹名称（便于排查 `INBOX`/中文名映射问题）。
- `envelope`：列表、搜索、排序、线程视图、分页。
- `message`：读信、导出、写信、发信、回复、转发。
- `message`：复制、移动、删除。
- `flag`：标记增删（至少支持 `seen`、`flagged`）。
- `attachment`：附件下载。
- 统一输出格式：`--output plain|json`。
- 调试能力：`--debug`、`--trace`。

## P1：MVP 工程化（可对外使用）

- 配置文件路径：`~/.config/<tool>/config.toml`。
- 认证方式：先支持 `auth.raw`，再支持 `auth.cmd`。
- Exmail 兼容策略（quirks）可配置。
- 错误处理清晰（认证失败、超时、文件夹不存在等）。
- 核心流程具备基础测试覆盖（list/read/search/send）。

## P2：发布与安装

- 使用 `pyproject.toml` 打包并提供 console script 入口。
- 发布到 PyPI（支持 `pipx install` / `pip install`）。
- GitHub Actions：基于 tag 自动发布 PyPI。
- 提供 Homebrew tap formula。
- 后续评估提交 `homebrew/core`。
- 完整 README：安装与快速上手文档。

## P3：增强项（后续）

- 增加 `template` 子命令（先轻量版，后续再做高级能力）。
- 提供配套 agent skill（`SKILL.md`）以支持自动化调用。
- 扩展更多邮箱服务商支持（Gmail、M365 等）。
- 在验证产品可行后评估 Go/Rust 重构。

## 验收标准（v0.1）

- Exmail 账号可稳定完成列信、读信、搜索、发信、下载附件。
- 核心命令均支持 `--output json`，可用于自动化。
- 新用户可在 5 分钟内安装并完成首次连通性测试。
