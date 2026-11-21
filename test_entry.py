"""Tests for the joke entry (test-driven: written before main.py).

Checks the deliverable contract from the competition rules:
- entry.txt is UTF-8, 1-280 Unicode code points, not whitespace-only
- main.py is stdlib-only (AST check, no network imports)
- grader simulation: `python3 -P -s main.py` twice, byte-identical output
- the joke is about an AI coding agent and a demo crash
"""

import ast
import os
import subprocess
import sys

ENTRY_DIR = os.path.dirname(os.path.abspath(__file__))
MAIN_PY = os.path.join(ENTRY_DIR, "main.py")
OUT_DIR = os.environ.get("MAKEFUN_OUTPUT_DIR", os.path.join(ENTRY_DIR, ".out"))
ENTRY_TXT = os.path.join(OUT_DIR, "entry.txt")

# Python 3.13 stdlib top-level module names (allowlist approach: anything in
# sys.stdlib_module_names is stdlib; anything else is rejected).
STDLIB = sys.stdlib_module_names


def _run_main(env_extra=None):
    env = dict(os.environ)
    env["MAKEFUN_OUTPUT_DIR"] = OUT_DIR
    if env_extra:
        env.update(env_extra)
    return subprocess.run(
        [sys.executable, "-P", "-s", MAIN_PY],
        cwd=ENTRY_DIR,
        env=env,
        capture_output=True,
        text=True,
        timeout=60,
    )


def test_main_py_exists_and_stdlib_only():
    assert os.path.isfile(MAIN_PY), "main.py missing"
    tree = ast.parse(open(MAIN_PY, encoding="utf-8").read())
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                top = alias.name.split(".")[0]
                assert top in STDLIB, f"non-stdlib import: {alias.name}"
        elif isinstance(node, ast.ImportFrom):
            assert node.module is not None
            top = node.module.split(".")[0]
            assert top in STDLIB, f"non-stdlib import: {node.module}"
        elif isinstance(node, ast.Call):
            # forbid network / subprocess / os.system style escapes
            if isinstance(node.func, ast.Attribute):
                assert node.func.attr not in ("system", "popen", "execv", "execl"), \
                    "forbidden process call in main.py"


def test_grader_simulation_deterministic():
    r1 = _run_main()
    assert r1.returncode == 0, f"run 1 failed: {r1.stderr}"
    first = open(ENTRY_TXT, "rb").read()
    r2 = _run_main()
    assert r2.returncode == 0, f"run 2 failed: {r2.stderr}"
    second = open(ENTRY_TXT, "rb").read()
    assert first == second, "entry.txt differs between runs (not deterministic)"
    assert first, "entry.txt empty"


def test_entry_length_and_content():
    r = _run_main()
    assert r.returncode == 0, f"run failed: {r.stderr}"
    raw = open(ENTRY_TXT, "rb").read()
    text = raw.decode("utf-8")  # raises on invalid UTF-8
    assert 1 <= len(text) <= 280, f"{len(text)} code points, must be 1-280"
    assert text.strip(), "entry is whitespace-only"
    low = text.lower()
    assert "ai" in low and ("coding agent" in low or "agent" in low), \
        "joke must be about an AI coding agent"
    assert "crash" in low or "demo" in low, \
        "joke must involve the demo crash"
    assert "\n" not in text.strip(), "joke must be a single line"
    print(f"JOKE ({len(text)} code points): {text}")
