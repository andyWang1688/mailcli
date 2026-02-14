#!/usr/bin/env python3
"""Test runner script for Mail CLI."""

import subprocess
import sys


def run_command(cmd: list[str]) -> bool:
    """Run a command and return True if successful."""
    result = subprocess.run(cmd, capture_output=False)
    return result.returncode == 0


def main() -> int:
    """Main entry point."""
    print("=" * 60)
    print("Mail CLI v0.1 Test Suite")
    print("=" * 60)
    print()

    # Check if venv exists
    if not run_command(["test", "-d", ".venv"]):
        print("Error: Virtual environment not found.")
        print("Please run: python3 -m venv .venv")
        return 1

    # Activate venv and install dependencies
    print("Step 1: Checking dependencies...")
    if not run_command([".venv/bin/python", "-c", "import click"]):
        print("Installing dependencies...")
        run_command([".venv/bin/pip", "install", "click", "tomli", "pytest"])
    print("✓ Dependencies OK")
    print()

    # Run tests
    print("Step 2: Running tests...")
    result = subprocess.run(
        [".venv/bin/python", "-m", "pytest", "tests/", "-v"],
        env={**subprocess.os.environ, "PYTHONPATH": "src"},
    )
    print()

    if result.returncode == 0:
        print("=" * 60)
        print("All tests passed! ✓")
        print("=" * 60)
        return 0
    else:
        print("=" * 60)
        print("Some tests failed. See output above.")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
