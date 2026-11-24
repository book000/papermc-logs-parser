import ast
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIRST = "[12:00:00] [Server thread/INFO]: First\n"
SECOND = "[12:00:01] [Server thread/INFO]: Second\n"
REPLACEMENT = "[12:00:00] [Server thread/INFO]: Replacement\n"


def run_cli(directory):
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT)
    result = subprocess.run(
        [sys.executable, "-m", "src"],
        cwd=directory,
        env=env,
        check=True,
        capture_output=True,
        text=True,
    )
    return ast.literal_eval(result.stdout.strip())


def configure(directory, path):
    (directory / "config.json").write_text(json.dumps({"path": str(path)}))


def messages(entries):
    return [entry["messages"] for entry in entries]


def assert_saved_state(directory, log, expected_messages, first_time):
    content = log.read_bytes()
    stat = log.stat()
    assert json.loads((directory / "data.json").read_text()) == {
        "count": len(expected_messages),
        "firstTime": first_time,
        "source": {
            "path": str(log.resolve()),
            "device": stat.st_dev,
            "inode": stat.st_ino,
        },
        "size": len(content),
        "digest": hashlib.sha256(content).hexdigest(),
    }
    assert messages(json.loads((directory / "output.json").read_text())) == (
        expected_messages
    )


def test_append_only_prints_new_entries(tmp_path):
    log = tmp_path / "latest.log"
    log.write_text(FIRST)
    configure(tmp_path, log)
    assert messages(run_cli(tmp_path)) == ["First"]
    assert_saved_state(tmp_path, log, ["First"], "12:00:00")
    with log.open("a") as f:
        f.write(SECOND)
    assert messages(run_cli(tmp_path)) == ["Second"]
    assert_saved_state(tmp_path, log, ["First", "Second"], "12:00:00")
    assert run_cli(tmp_path) == []
    assert_saved_state(tmp_path, log, ["First", "Second"], "12:00:00")


def test_empty_first_run_then_append(tmp_path):
    log = tmp_path / "latest.log"
    log.write_text("")
    configure(tmp_path, log)
    assert run_cli(tmp_path) == []
    assert_saved_state(tmp_path, log, [], None)
    log.write_text(FIRST)
    assert messages(run_cli(tmp_path)) == ["First"]
    assert_saved_state(tmp_path, log, ["First"], "12:00:00")
    assert run_cli(tmp_path) == []


def test_replaced_file_resets_cursor(tmp_path):
    log = tmp_path / "latest.log"
    log.write_text(FIRST + SECOND)
    configure(tmp_path, log)
    run_cli(tmp_path)
    replacement = tmp_path / "replacement.log"
    replacement.write_text(REPLACEMENT)
    replacement.replace(log)
    assert messages(run_cli(tmp_path)) == ["Replacement"]
    assert_saved_state(tmp_path, log, ["Replacement"], "12:00:00")
    assert run_cli(tmp_path) == []


def test_truncated_and_rewritten_file_resets_cursor(tmp_path):
    log = tmp_path / "latest.log"
    log.write_text(FIRST + SECOND)
    configure(tmp_path, log)
    run_cli(tmp_path)
    log.write_text(REPLACEMENT)
    assert messages(run_cli(tmp_path)) == ["Replacement"]
    assert_saved_state(tmp_path, log, ["Replacement"], "12:00:00")
    assert run_cli(tmp_path) == []


def test_rewritten_prefix_of_same_size_resets_cursor(tmp_path):
    log = tmp_path / "latest.log"
    log.write_text(FIRST + SECOND)
    configure(tmp_path, log)
    run_cli(tmp_path)
    log.write_text(FIRST.replace("First", "Other") + SECOND)
    assert messages(run_cli(tmp_path)) == ["Other", "Second"]
    assert_saved_state(tmp_path, log, ["Other", "Second"], "12:00:00")


def test_source_change_resets_cursor(tmp_path):
    first = tmp_path / "first.log"
    second = tmp_path / "second.log"
    first.write_text(FIRST + SECOND)
    second.write_text(REPLACEMENT)
    configure(tmp_path, first)
    run_cli(tmp_path)
    configure(tmp_path, second)
    assert messages(run_cli(tmp_path)) == ["Replacement"]
    assert_saved_state(tmp_path, second, ["Replacement"], "12:00:00")


def test_legacy_cursor_resets(tmp_path):
    log = tmp_path / "latest.log"
    log.write_text(FIRST)
    configure(tmp_path, log)
    (tmp_path / "data.json").write_text(
        json.dumps({"count": 1, "firstTime": "12:00:00"})
    )
    assert messages(run_cli(tmp_path)) == ["First"]
    assert_saved_state(tmp_path, log, ["First"], "12:00:00")
