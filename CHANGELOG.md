# Changelog

All notable changes to this project will be documented in this file.

The format is based on Keep a Changelog, and this project follows Semantic Versioning.

## [Unreleased]

## [0.1.0] - 2026-02-14

### Added
- PyPI release workflow triggered by version tags (`v*`).
- Automatic GitHub Release creation with built package artifacts attached.
- Initial EmailCLI scaffolding with package entrypoint `mailcli`.
- Core command groups: `account`, `folder`, `envelope`, `message`, `attachment`.
- Exmail-focused IMAP/SMTP workflows for list/search/read/send/attachment download.
- Folder listing command and server folder name visibility.
- Unified output mode support (`plain` and `json`) and debug mode.
- Basic test coverage for core and CLI flows.
- Chinese user documentation and release guide.
