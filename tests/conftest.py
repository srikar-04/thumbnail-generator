"""Seam test harness (house pattern, per PRD Testing Decisions).

Every test drives the `thumb` CLI as a real subprocess against a temp working
directory, with providers left on their fake bindings, and asserts ONLY on what
lands on disk (folders, Status: lines, images, metadata, HTML) or on CLI output.
No test imports pipeline internals.
"""

import os
import subprocess
import sys

import pytest


@pytest.fixture()
def thumb(tmp_path):
    """Run `thumb <args>` in an isolated workspace; returns the CompletedProcess.

    The API key is stripped from the environment on purpose: fake-provider mode
    must work with no key and no network.
    """

    def run(*args, check=True, env=None):
        merged = os.environ.copy()
        merged.pop("GEMINI_API_KEY", None)
        if env:
            merged.update(env)  # per-test scripting (THUMB_* knobs, sentinel keys)
        result = subprocess.run(
            [sys.executable, "-m", "thumb", *args],
            cwd=tmp_path,
            capture_output=True,
            text=True,
            env=merged,
        )
        if check:
            assert result.returncode == 0, (
                f"thumb {' '.join(args)} exited {result.returncode}\n"
                f"stdout: {result.stdout}\nstderr: {result.stderr}"
            )
        return result

    run.root = tmp_path
    return run


@pytest.fixture()
def make_photo():
    """Create an input fixture photo (a plain portrait-shaped PNG)."""
    from PIL import Image

    def make(path, size=(400, 600), color=(180, 140, 120)):
        path.parent.mkdir(parents=True, exist_ok=True)
        Image.new("RGB", size, color).save(path)
        return path

    return make
