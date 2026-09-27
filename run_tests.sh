#!/usr/bin/env bash
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete 2>/dev/null
backend/.venv/bin/python -m pytest backend/tests/ -v
