#!/bin/bash
git add tests/test_admin.py tests/conftest.py
git commit -m "fix(tests): resolve admin auth secret mismatch and isolate test fixtures"
git push origin HEAD
