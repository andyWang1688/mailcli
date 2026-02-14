# Mail CLI Bug List

这个文档只做一件事：快速记下你测出来的 bug。

## 怎么写

- 每发现一个 bug，直接新增一条。
- 用你自己的描述就行，不需要严格格式。
- 修复后把 `状态` 改成 `已修复` 或 `已验证`。

## Bug 记录

### BUG-001
- 时间：2026-02-14
- 状态：已修复
- 描述：认证失败时，`mailcli envelope list -a exmail-main` 会直接输出 traceback，不够友好。
- 备注：已添加全局错误处理，所有命令现在都会捕获异常并显示友好错误提示。支持 `--output json` 格式化错误输出。支持 `--debug` 显示完整 traceback。

---

### BUG-002
- 时间：2026-02-14
- 状态：已修复
- 描述：未定义配置时输入 `mailcli account list` 会直接出现python错误，应该给予友好提示，不要出现报错
- 备注：配置文件未找到时，现在会显示 "Configuration Error: Configuration file not found..." 的友好提示。

---

### BUG-003
- 时间：2026-02-14
- 状态：已修复
- 描述：mailcli envelope list -a exmail-main -f 收件箱 -l 10不支持中文，输入中文就报错了
- 备注：已在 IMAP 文件夹选择逻辑中增加中文文件夹名的 IMAP modified UTF-7 编码处理。复测 `mailcli --output json envelope list -a exmail-main -f "其他文件夹/穆桥" -l 2` 已返回正常结果。

---

### BUG-004
- 时间：2026-02-14
- 状态：已修复
- 描述：`mailcli envelope list -a exmail-main -f INBOX -l 10` 返回了 10 条记录，但每条 `id/subject/from/date/size` 都为空或 0。
- 备注：已修复 envelope 解析逻辑，现可正确返回 `id/subject/from/to/date/size`。同时新增 `mailcli folder list` 用于查看服务端真实文件夹名称和映射。
