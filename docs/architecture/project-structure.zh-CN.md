# 项目目录说明

```text
mailcli/
  config/
    config.example.toml
  docs/
    architecture/
      project-structure.zh-CN.md
    plan/
      roadmap.zh-CN.md
      v0.1-execution-plan.zh-CN.md
    requirements/
      mailcli-requirements.zh-CN.md
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

- `docs/requirements/`：需求原文与版本化需求文档。
- `docs/plan/`：阶段计划、里程碑和风险管理。
- `docs/architecture/`：架构约定、模块边界、目录规范。
- `src/mailcli/`：可执行代码入口和业务实现目录。
- `tests/`：单元测试与集成测试。
- `config/`：示例配置与本地开发模板。

## 后续建议补充（由实现模型完成）

- `src/mailcli/core/`：命令业务逻辑。
- `src/mailcli/providers/exmail/`：Exmail 兼容策略。
- `src/mailcli/infra/`：IMAP/SMTP 客户端、配置加载、日志。
- `tests/integration/`：对接真实或模拟邮箱服务的测试。
