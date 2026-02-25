# Mail CLI 用户文档（中文）

本页面向终端用户，包含安装、配置和常用命令。

## 1. 环境要求

- Python `>= 3.10`（建议 `3.13`）
- macOS / Linux

## 2. 安装

### 方式 A：从 PyPI 安装（推荐）

```bash
pip install exmail-cli
```

安装后命令名是 `mailcli`。

### 方式 B：从源码安装

```bash
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
pip install .
```

验证安装：

```bash
mailcli --help
```

## 3. 配置账号

```bash
mkdir -p ~/.config/mailcli
cp config/config.example.toml ~/.config/mailcli/config.toml
```

编辑 `~/.config/mailcli/config.toml`，填写邮箱地址和授权码。

## 4. 常用命令

```bash
mailcli account list
mailcli account diagnose exmail-main
mailcli folder list -a exmail-main
mailcli envelope list -a exmail-main -f INBOX -l 10
mailcli envelope search -a exmail-main -f INBOX "UNSEEN"
mailcli message read -a exmail-main -f INBOX <msg_id>
mailcli message send -a exmail-main -t you@example.com -s "mailcli test" -b "hello"
mailcli attachment list -a exmail-main -f INBOX <msg_id>
mailcli attachment download -a exmail-main -f INBOX -o ./downloads <msg_id> <filename>
```

说明：`<msg_id>`、`<filename>` 需要替换为真实值。

需要机器可读输出时，添加 `--output json`。

## 5. 相关文档

- 命令详解：`docs/user/COMMANDS.zh-CN.md`
- 更新记录：`CHANGELOG.md`
- 开发文档：`docs/development/README.zh-CN.md`
