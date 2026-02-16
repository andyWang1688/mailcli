# EmailCLI 标准说明文档（中文）

本页是 EmailCLI 的中文标准入口文档，适合从 0 开始安装、配置与测试。

## 1. 环境要求

- Python `>= 3.10`（建议 `3.13`）
- macOS / Linux

## 2. 安装

推荐安装方式：使用 `pip` 直接安装。

### 方式 A：从 PyPI 安装（发布后推荐）

```bash
pip install exmail-cli
```

说明：安装后命令名仍然是 `mailcli`。

发布策略：合并到 `main` 不会自动发布；仅在推送版本 tag（如 `v0.1.0`）后自动发布到 PyPI。

### 方式 B：从本地源码安装（当前开发阶段）

在项目根目录执行：

```bash
cd ~/Downloads/mailcli
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
pip install .
```

验证安装：

```bash
mailcli --help
```

## 3. 配置账号（配置文件方式）

初始化配置文件：

```bash
mkdir -p ~/.config/mailcli
cp config/config.example.toml ~/.config/mailcli/config.toml
```

编辑 `~/.config/mailcli/config.toml`，填写真实邮箱地址和授权码。

## 4. 快速测试顺序

```bash
mailcli account list
mailcli account diagnose exmail-main
mailcli --output json folder list -a exmail-main
mailcli --output json envelope list -a exmail-main -f INBOX -l 10
mailcli --output json envelope search -a exmail-main -f INBOX "ALL"
mailcli --output json message read -a exmail-main -f INBOX <msg_id>
mailcli --output json message send -a exmail-main -t you@example.com -s "mailcli test" -b "hello"
mailcli --output json attachment list -a exmail-main -f INBOX <msg_id>
mailcli --output json attachment download -a exmail-main -f INBOX -o ./downloads <msg_id> <filename>
```

说明：`<msg_id>`、`<filename>` 需要替换成真实值。

## 5. 功能说明

- 详细命令说明：`docs/COMMANDS.zh-CN.md`
- 发布流程：`docs/RELEASING.zh-CN.md`
- 更新记录：`CHANGELOG.md`
- 测试报告：`docs/TESTING.md`
- 需求管理（Issues）：`https://github.com/andyWang1688/mailcli/issues?q=is%3Aissue+is%3Aopen+label%3Arequirement`
- BUG 管理（Issues）：`https://github.com/andyWang1688/mailcli/issues?q=is%3Aissue+label%3Abug`
