# Mail CLI

Mail CLI - An open-source email command-line tool for managing emails from the terminal.

## Documentation

- Chinese product standard doc: `docs/README.zh-CN.md`
- Chinese command reference: `docs/COMMANDS.zh-CN.md`
- Release guide (Chinese): `docs/RELEASING.zh-CN.md`
- Changelog: `CHANGELOG.md`
- Requirements issues: `https://github.com/andyWang1688/mailcli/issues?q=is%3Aissue+is%3Aopen+label%3Arequirement`
- Bug issues: `https://github.com/andyWang1688/mailcli/issues?q=is%3Aissue+label%3Abug`

## Quick Start

### Installation

Preferred installation method: `pip` direct install.

#### Option A: Install from PyPI (target release channel)

```bash
pip install exmail-cli
```

After publishing to PyPI, this is the recommended way for all users.
The installed CLI command remains `mailcli`.

Publishing strategy: merge to `main` does not publish; pushing a version tag like `v0.1.0` publishes to PyPI.

#### Option B: Install from local source (current development stage)

```bash
cd ~/Downloads/mailcli
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
pip install .
```

Verify installation:

```bash
mailcli --help
```

### Configuration

Copy the example configuration to your home directory:

```bash
mkdir -p ~/.config/mailcli
cp config/config.example.toml ~/.config/mailcli/config.toml
```

Edit the configuration file with your email account details:

```toml
default_account = "exmail-main"

[accounts.exmail-main]
email = "your.name@example.com"
use_ssl = true

[accounts.exmail-main.imap]
host = "imap.exmail.qq.com"
port = 993

[accounts.exmail-main.smtp]
host = "smtp.exmail.qq.com"
port = 465

[accounts.exmail-main.auth]
raw = "your_app_password_or_token"

[quirks]
provider = "exmail"
```

## Usage

Detailed command guide (Chinese):

- `docs/COMMANDS.zh-CN.md`

## Architecture

- `docs/plan/`: execution plans and milestones
- `docs/architecture/`: architecture and directory conventions
- `src/mailcli/core/`: business logic
- `src/mailcli/providers/`: provider-specific quirks (e.g., Exmail)
- `src/mailcli/infra/`: infrastructure (IMAP/SMTP, config, output)
- `tests/`: unit and integration tests

## Development

Run tests:
```bash
source .venv/bin/activate
python -m pytest tests/ -v

# Or use the test script
./test.sh
```

See [TESTING.md](docs/TESTING.md) for detailed test coverage.

## Current Status (v0.1)

### Completed (M1-M3)
- **M1: CLI + Config + Diagnostics**
  - CLI framework with command groups
  - Configuration loading (TOML)
  - Error handling and output formatting (plain/json)
  - IMAP/SMTP connection adapters
  - Account management (list, default, diagnose)

- **M2: IMAP Operations**
  - Envelope list and search
  - Message read
  - Attachment list and download

- **M3: SMTP Operations**
  - Message send

### Summary
- 13 Python source files (~1200 lines)
- 3 test files with 14 tests
- Full support for Exmail IMAP/SMTP workflows
- All core commands support `--output json`

### Next Steps
- Additional provider support (Gmail, M365)
- Folder management
- Flag operations
- Message operations (write, reply, forward)
- HTML email support
- Multiple attachments
