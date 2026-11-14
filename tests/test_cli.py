import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
FIRST = "[12:00:00] [Server thread/INFO]: Synthetic first\n"
SECOND = "[12:00:01] [Server thread/INFO]: Synthetic second\n"


def run_cli(tmp_path):
    return subprocess.run(
        [sys.executable, "-m", "src"],
        cwd=tmp_path,
        env={**os.environ, "PYTHONPATH": str(ROOT)},
        capture_output=True,
        text=True,
        check=False,
    )


@pytest.mark.parametrize("text", ["", FIRST])
@pytest.mark.parametrize("existing_cursor", [False, True])
def test_no_parsed_entries_reset_cursor(tmp_path, text, existing_cursor):
    log = tmp_path / "server.log"
    log.write_text(text, encoding="utf-8")
    (tmp_path / "config.json").write_text(json.dumps({"path": str(log)}))
    if existing_cursor:
        (tmp_path / "data.json").write_text(
            json.dumps({"count": 5, "firstTime": "12:00:00"})
        )

    result = run_cli(tmp_path)

    assert result.returncode == 0, result.stderr
    assert result.stdout.splitlines()[-1] == "[]"
    assert json.loads((tmp_path / "output.json").read_text()) == []
    assert json.loads((tmp_path / "data.json").read_text()) == {
        "count": 0,
        "firstTime": None,
    }

    # A later completed entry is still reported after an empty/truncated file.
    log.write_text(FIRST + SECOND, encoding="utf-8")
    resumed = run_cli(tmp_path)
    assert resumed.returncode == 0, resumed.stderr
    output = json.loads((tmp_path / "output.json").read_text())
    assert len(output) == 1
    assert output[0]["time"] == "12:00:00"
    assert output[0]["messages"] == "Synthetic first"
    assert json.loads((tmp_path / "data.json").read_text()) == {
        "count": 1,
        "firstTime": "12:00:00",
    }
    assert "Synthetic first" in resumed.stdout.splitlines()[-1]
    repeated = run_cli(tmp_path)
    assert repeated.returncode == 0, repeated.stderr
    assert repeated.stdout.splitlines()[-1] == "[]"
