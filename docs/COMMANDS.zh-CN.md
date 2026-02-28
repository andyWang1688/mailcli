# Mail CLI 命令参考（中文版）

可执行命令：`mailcli`

## 全局用法

```bash
mailcli [OPTIONS] COMMAND [ARGS]...
```

全局选项：

- `--output [plain|json]`：输出格式，默认 `plain`
- `--debug`：调试模式
- `--trace`：异常时输出完整 traceback

## 命令组总览

- `account`：账号信息与连通诊断
- `folder`：邮箱文件夹管理
- `envelope`：邮件摘要列表与搜索
- `message`：读信、写信、发信与邮件迁移
- `attachment`：附件列表与下载
- `flag`：邮件标记增删（seen/flagged）
- `template`：服务商模板与配置片段生成

## account

### `mailcli account list`

列出配置文件中的所有账号。

### `mailcli account default <account>`

设置默认账号（会写回 `~/.config/mailcli/config.toml`）。

### `mailcli account diagnose <account>`

检查 IMAP/SMTP 网络与认证可用性。

## folder

### `mailcli folder list`

列出服务器真实文件夹名。

```bash
mailcli folder list -a exmail-main
mailcli --output json folder list -a exmail-main
```

### `mailcli folder create <name>`

创建文件夹。

### `mailcli folder delete <name>`

删除文件夹。

### `mailcli folder expunge`

仅清理已标记删除的邮件。

### `mailcli folder purge`

将整个文件夹邮件标记删除后执行 expunge（危险操作）。

## envelope

### `mailcli envelope list`

列出邮件摘要。

常用参数：

- `-a, --account <account>`
- `-f, --folder <folder>`，默认 `INBOX`
- `-l, --limit <number>`，默认 `50`
- `--sort-by [date|size|subject|from]`
- `--order [asc|desc]`
- `--page <number>`、`--page-size <number>`
- `--threaded`：按主题粗粒度聚合线程

```bash
mailcli envelope list -a exmail-main -f INBOX --sort-by date --order desc --page 1 --page-size 20
```

### `mailcli envelope search <query>`

按 IMAP 查询语法搜索邮件，支持和 `list` 相同的排序/分页/线程参数。

```bash
mailcli envelope search -a exmail-main -f INBOX "UNSEEN"
mailcli envelope search -a exmail-main -f INBOX "FROM \"alice@example.com\""
```

## message

### `mailcli message read <msg_id>`

读取指定邮件。

### `mailcli message write`

写本地草稿并导出为 `.eml`：

```bash
mailcli message write -t you@example.com -s "draft" -b "hello" -o ./drafts/hello.eml
```

### `mailcli message export <msg_id>`

将远程邮件导出到本地 `.eml` 文件。

### `mailcli message send`

发送纯文本邮件。

### `mailcli message reply <msg_id>`

回复邮件，支持 `--reply-all`。

### `mailcli message forward <msg_id>`

转发邮件到指定收件人。

### `mailcli message copy <msg_id>` / `mailcli message move <msg_id>`

在文件夹间复制或移动邮件。

### `mailcli message delete <msg_id>`

删除邮件；默认会 expunge，可用 `--no-expunge` 仅标记删除。

## attachment

### `mailcli attachment list <msg_id>`

列出邮件附件。

### `mailcli attachment download <msg_id> <filename>`

下载附件到本地目录。

```bash
mailcli attachment download -a exmail-main -f INBOX -o ./downloads 12345 report.pdf
```

## flag

### `mailcli flag add <msg_id> --flag <seen|flagged>`

为邮件增加标记。

### `mailcli flag remove <msg_id> --flag <seen|flagged>`

移除邮件标记。

## template

### `mailcli template list-providers`

列出内置服务商模板：`exmail`、`gmail`、`m365`。

### `mailcli template render`

生成配置片段（TOML）：

```bash
mailcli template render --provider gmail --account gmail-main --email your.name@gmail.com
```
