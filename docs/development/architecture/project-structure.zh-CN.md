# 项目目录说明

```text
mailcli/
  config/
    config.example.toml
  docs/
    user/
      README.zh-CN.md
      COMMANDS.zh-CN.md
    development/
      README.zh-CN.md
      git-workflow.zh-CN.md
      RELEASING.zh-CN.md
      architecture/
        project-structure.zh-CN.md
  src/
    mailcli/
      __init__.py
      __main__.py
      cli.py
  tests/
    __init__.py
  .gitignore
  pyproject.toml
  README.md
```

## 目录职责

- `GitHub Issues`：需求与 BUG 的唯一维护入口。
- `docs/user/`：面向终端用户的安装、配置与命令说明。
- `docs/development/`：面向开发者的流程与架构文档（Git 规范、发布、架构）。
- `src/mailcli/`：可执行代码入口和业务实现目录。
- `tests/`：单元测试与集成测试。
- `config/`：示例配置与本地开发模板。

## 后续建议补充（由实现模型完成）

- `src/mailcli/core/`：命令业务逻辑。
- `src/mailcli/providers/exmail/`：Exmail 兼容策略。
- `src/mailcli/infra/`：IMAP/SMTP 客户端、配置加载、日志。
- `tests/integration/`：对接真实或模拟邮箱服务的测试。
