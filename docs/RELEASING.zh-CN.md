# EmailCLI 发布流程（PyPI）

本项目采用 **tag 触发发布**：

- 合并到 `main`：不会自动发布 PyPI
- 推送 `vX.Y.Z` tag：自动发布到 PyPI，并自动创建 GitHub Release

## 1. 一次性配置

1) 在 PyPI 创建 API Token（作用域建议限制到项目）

2) 在 GitHub 仓库配置 Secret：

- 名称：`PYPI_API_TOKEN`
- 值：你的 PyPI token（形如 `pypi-...`）

3) 确认工作流文件存在：

- `.github/workflows/publish-pypi.yml`

## 2. 版本规则

使用语义化版本（SemVer）：

- `MAJOR.MINOR.PATCH`
- 修复兼容性 bug：`PATCH` +1
- 新增兼容功能：`MINOR` +1
- 不兼容变更：`MAJOR` +1

示例：

- `0.1.0` -> `0.1.1`（bugfix）
- `0.1.1` -> `0.2.0`（新功能）

## 3. 正式发布步骤

1) 修改版本号（`pyproject.toml`）

2) 提交并合并到 `main`

3) 在本地打 tag 并推送：

```bash
git checkout main
git pull
git tag v0.1.0
git push origin v0.1.0
```

4) GitHub Actions 自动执行：

- 校验 tag 与 `pyproject.toml` 版本一致
- 构建包（sdist + wheel）
- 执行 `twine check`
- 发布到 PyPI
- 创建 GitHub Release（自动生成发布说明，并上传 `dist/*` 产物）

## 4. 自动创建 GitHub Release 的底层逻辑

触发条件：

- 你执行 `git push origin vX.Y.Z` 后，GitHub 触发 `push tags` 事件。

工作流按顺序执行：

1. 从 tag 对应的提交检出代码。
2. 读取 `pyproject.toml` 并校验版本与 tag 一致（例如 `v0.1.0` 对应 `0.1.0`）。
3. 构建 `dist/*.whl` 和 `dist/*.tar.gz`。
4. 用 `PYPI_API_TOKEN` 上传到 PyPI。
5. 调用 GitHub Release API 创建 Release，绑定当前 tag，并附加 `dist/*` 文件。

关键点：

- 不会在每次合并 `main` 时触发发布。
- 只有 tag 发布才会触发“发布到 PyPI + 创建 GitHub Release”。
- `dist/` 是 CI 运行时目录，不会自动保存到仓库代码树，但会作为 Release 附件长期保存。

## 5. 常见问题

- tag 和 `pyproject.toml` 版本不一致：工作流会失败
- 未配置 `PYPI_API_TOKEN`：发布步骤会失败
- 包名冲突：PyPI 会拒绝上传（当前包名为 `exmail-cli`）
