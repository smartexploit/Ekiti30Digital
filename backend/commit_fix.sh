#!/bin/bash
git add tests/conftest.py
git commit -m "fix(tests): safely monkeypatch settings attributes without violating property setters"
git push origin HEAD
