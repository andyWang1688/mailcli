# EmailCLI 命令参考（中文版）

可执行命令：`mailcli`

## 全局用法

```bash
mailcli [OPTIONS] COMMAND [ARGS]...
```

全局选项：

- `--output [plain|json]`：输出格式，默认 `plain`
- `--debug`：输出调试信息

## 可用命令

- `account`：账号信息与连通诊断
- `folder`：邮箱文件夹列表
- `envelope`：邮件摘要列表与搜索
- `message`：读信与发信
- `attachment`：附件列表与下载

## account

### `mailcli account list`

显示配置中的账号。

```bash
mailcli account list
mailcli --output json account list
```

### `mailcli account diagnose <account>`

检查账号 IMAP/SMTP 连通性与认证状态。

```bash
mailcli account diagnose exmail-main
mailcli --output json account diagnose exmail-main
```

### `mailcli account default <account>`

设置默认账号。

```bash
mailcli account default exmail-main
```

## envelope

### `mailcli envelope list`

列出邮箱中的邮件摘要。

选项：

- `-a, --account <account>`：账号名
- `-f, --folder <folder>`：文件夹，默认 `INBOX`
- `-l, --limit <number>`：返回数量，默认 `50`

```bash
mailcli envelope list -a exmail-main -f INBOX -l 10
mailcli --output json envelope list -a exmail-main -f INBOX -l 10
```

### `mailcli envelope search <query>`

按 IMAP 查询语法搜索邮件。

选项：

- `-a, --account <account>`：账号名
- `-f, --folder <folder>`：文件夹，默认 `INBOX`

```bash
mailcli envelope search -a exmail-main -f INBOX "ALL"
mailcli envelope search -a exmail-main -f INBOX "UNSEEN"
mailcli envelope search -a exmail-main -f INBOX "FROM \"alice@example.com\""
mailcli --output json envelope search -a exmail-main -f INBOX "SUBJECT \"invoice\""
```

## folder

### `mailcli folder list`

列出服务器返回的可用文件夹。

选项：

- `-a, --account <account>`：账号名

```bash
mailcli folder list -a exmail-main
mailcli --output json folder list -a exmail-main
```

## message

### `mailcli message read <msg_id>`

读取指定邮件。

选项：

- `-a, --account <account>`：账号名
- `-f, --folder <folder>`：文件夹，默认 `INBOX`

```bash
mailcli message read -a exmail-main -f INBOX 12345
mailcli --output json message read -a exmail-main -f INBOX 12345
```

### `mailcli message send`

发送纯文本邮件。

选项：

- `-a, --account <account>`：账号名
- `-t, --to <email>`：收件人（必填）
- `-s, --subject <text>`：主题（必填）
- `-b, --body <text>`：正文（必填）

```bash
mailcli message send -a exmail-main -t you@example.com -s "mailcli test" -b "hello"
mailcli --output json message send -a exmail-main -t you@example.com -s "mailcli test" -b "hello"
```

## attachment

### `mailcli attachment list <msg_id>`

列出邮件附件。

选项：

- `-a, --account <account>`：账号名
- `-f, --folder <folder>`：文件夹，默认 `INBOX`

```bash
mailcli attachment list -a exmail-main -f INBOX 12345
mailcli --output json attachment list -a exmail-main -f INBOX 12345
```

### `mailcli attachment download <msg_id> <filename>`

下载指定附件到本地目录。

选项：

- `-a, --account <account>`：账号名
- `-f, --folder <folder>`：文件夹，默认 `INBOX`
- `-o, --output <dir>`：输出目录，默认当前目录

```bash
mailcli attachment download -a exmail-main -f INBOX -o ./downloads 12345 report.pdf
mailcli --output json attachment download -a exmail-main -f INBOX -o ./downloads 12345 report.pdf
```
