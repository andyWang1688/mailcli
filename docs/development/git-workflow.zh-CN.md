# Mail CLI Git 使用规范

## 1. 目标

统一分支管理和提交流程，保证发布可追溯、代码可审查、问题可回滚。

## 2. 分支模型

- `main`：生产分支，只存放可发布代码。
- `develop`：开发集成分支（可视为 dev 主线）。
- `feature/<name>`：功能分支，从 `develop` 拉取，完成后回合并到 `develop`。
- `release/<version>`：发布准备分支，从 `develop` 拉取，用于发布前修复。
- `hotfix/<name>`：线上紧急修复分支，从 `main` 拉取，修复后合并回 `main` 和 `develop`。

## 3. 保护规则（必须）

- `main`、`develop` 禁止直接推送和直接提交。
- 所有变更必须通过 Pull Request 合并。
- PR 至少需要 1 个 Approve。
- 禁止 force push 到受保护分支。

## 4. 日常开发流程

1. 从 `develop` 创建功能分支：

```bash
git checkout develop
git pull
git checkout -b feature/xxx
```

2. 在功能分支提交并推送：

```bash
git add .
git commit -m "feat: add xxx"
git push -u origin feature/xxx
```

3. 发起 PR：`feature/xxx -> develop`，通过评审后合并。

## 5. 发布流程（简化）

1. 从 `develop` 创建 `release/<version>`。
2. 在 `release/<version>` 完成发布前验证和修复。
3. 发起 PR 合并到 `main`。
4. 合并后打 tag（例如 `v0.1.0`）并推送触发发布。
5. 将 `release/<version>` 变更再合并回 `develop`。

详细发布说明见 `docs/development/RELEASING.zh-CN.md`。

## 6. 提交信息建议

建议使用 Conventional Commits：

- `feat:` 新功能
- `fix:` 缺陷修复
- `docs:` 文档变更
- `refactor:` 重构
- `test:` 测试相关
- `chore:` 工具或杂项维护
