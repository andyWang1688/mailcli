# Mail CLI 路线图（规划版）

## 总体策略

- 先交付 `v0.1` 可用能力，再补齐 Himalaya 风格完整体验。
- 先做高频主链路（list/read/search/send/attachment），再做广覆盖命令。
- 所有阶段都要求 `--output json` 可自动化调用。

## 阶段拆分

### Phase A：项目基线（当前）

- 项目骨架、目录规范、文档基线。
- 需求归档与实施计划拆解。

### Phase B：v0.1 主链路（P0 子集）

- `account`（add/list/use/diagnose）。
- `envelope`（list/search，含分页与基础排序）。
- `message`（read/send）。
- `attachment`（download）。
- 全局输出与调试（`--output`、`--debug`、`--trace`）。

### Phase C：P0 补齐

- `folder`（list/create/delete + expunge/purge 语义）。
- `message`（reply/forward/copy/move/delete）。
- `flag`（seen/flagged 增删）。
- 线程视图与更完善排序过滤。

### Phase D：P1 工程化

- `~/.config/mailcli/config.toml` 标准化。
- 认证扩展：`auth.cmd`。
- Exmail quirks 可配置。
- 错误模型、日志模型、测试覆盖提升。

### Phase E：P2 发布

- PyPI 发布链路（tag -> release）。
- README 完整化（安装、快速上手、故障排查）。
- Homebrew tap。

### Phase F：P3 增强

- `template` 子命令。
- agent skill（`SKILL.md`）。
- 多服务商支持与重构评估。
