# Mail CLI

Mail CLI is an open-source terminal email tool.

## Install

Use `pip`:

```bash
pip install exmail-cli
```

Or install from source:

```bash
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
pip install .
```

Verify:

```bash
mailcli --help
```

## Configure

```bash
mkdir -p ~/.config/mailcli
cp config/config.example.toml ~/.config/mailcli/config.toml
```

Then edit `~/.config/mailcli/config.toml` with your account info.

## Quick Usage

```bash
mailcli account list
mailcli account diagnose exmail-main
mailcli folder list -a exmail-main
mailcli envelope list -a exmail-main -f INBOX -l 10
mailcli message read -a exmail-main -f INBOX <msg_id>
mailcli message send -a exmail-main -t you@example.com -s "hello" -b "hi"
mailcli attachment download -a exmail-main -f INBOX -o ./downloads <msg_id> <filename>
```

Use JSON output for automation:

```bash
mailcli --output json envelope search -a exmail-main -f INBOX "UNSEEN"
```

## Documentation

- User guide (Chinese): `docs/user/README.zh-CN.md`
- Command reference (Chinese): `docs/user/COMMANDS.zh-CN.md`
- Changelog: `CHANGELOG.md`
- Development docs: `docs/development/README.zh-CN.md`
