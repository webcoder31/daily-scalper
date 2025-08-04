#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Main entry point for the Trading Strategy Backtester application.

This module serves as the primary entry point for the cryptocurrency trading
strategy backtesting application. It imports and executes the main CLI
interface from the cli module.
"""

import sys
from typing import NoReturn

from core.interactive_cli import main


def run_application() -> NoReturn:
    """
    Run the Trading Strategy Backtester application.
    
    This function serves as the main entry point that starts the CLI interface
    and handles the application exit code properly. Command line arguments are
    automatically parsed and processed by the CLI module.
    
    Raises:
        SystemExit: Always exits with the return code from the CLI main function.
    """
    sys.exit(main())


if __name__ == "__main__":
    run_application()