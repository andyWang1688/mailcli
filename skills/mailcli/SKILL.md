# Mail CLI Skill

## Purpose

Use this skill when you need to operate email accounts via `mailcli` in scripts or automation tasks.

## Quick Workflow

1. Verify config exists: `~/.config/mailcli/config.toml`
2. Check account status: `mailcli account list` and `mailcli account diagnose <account>`
3. Resolve folder names first: `mailcli folder list -a <account>`
4. Use JSON output for automation: append `--output json`

## Common Commands

- List mail: `mailcli --output json envelope list -a <account> -f INBOX -l 20`
- Search mail: `mailcli --output json envelope search -a <account> -f INBOX "UNSEEN"`
- Read message: `mailcli --output json message read -a <account> -f INBOX <msg_id>`
- Send message: `mailcli --output json message send -a <account> -t you@example.com -s "subject" -b "body"`
- Download attachment: `mailcli --output json attachment download -a <account> -f INBOX -o ./downloads <msg_id> <filename>`

## Safety Notes

- `message delete` and `folder purge` are destructive; use with explicit folder/message IDs.
- Use `--trace` when debugging production errors to capture complete stack traces.
