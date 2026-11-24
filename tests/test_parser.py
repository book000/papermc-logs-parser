from src import parser


def test_preserves_trailing_whitespace_in_messages_and_raws(tmp_path):
    log = tmp_path / "whitespace.log"
    log.write_bytes(
        b"[12:00:00] [Server thread/INFO]: whitespace  \t\r\n"
        b"continuation \t\r\n"
        b"[12:00:01] [Server thread/INFO]: final \t"
    )

    logs = parser(str(log))

    assert logs[0]["messages"] == "whitespace  \t\ncontinuation \t"
    assert logs[0]["raws"] == (
        "[12:00:00] [Server thread/INFO]: whitespace  \t\ncontinuation \t"
    )
    assert logs[1]["messages"] == "final \t"
    assert logs[1]["raws"] == "[12:00:01] [Server thread/INFO]: final \t"


def test_last_entry_is_included(tmp_path):
    log = tmp_path / "latest.log"
    log.write_text(
        "[12:00:00] [Server thread/INFO]: Starting\n"
        "[12:00:01] [Server thread/WARN]: Failed\n"
        "\tat Foo.bar(Foo.java:1)\n"
        "[12:00:02] [Server thread/INFO]: Done\n",
        encoding="utf-8",
    )

    logs = parser(str(log))

    assert [e["messages"] for e in logs] == [
        "Starting",
        "Failed\n\tat Foo.bar(Foo.java:1)",
        "Done",
    ]
    assert logs[-1] == {
        "time": "12:00:02",
        "threadName": "Server thread",
        "level": "INFO",
        "messages": "Done",
        "raws": "[12:00:02] [Server thread/INFO]: Done",
    }


def test_file_without_header_lines_yields_no_entries(tmp_path):
    log = tmp_path / "noheader.log"
    log.write_text("\tat Foo.bar(Foo.java:1)\nplain text\n", encoding="utf-8")

    assert parser(str(log)) == []


def test_empty_file_yields_no_entries(tmp_path):
    log = tmp_path / "empty.log"
    log.write_text("", encoding="utf-8")

    assert parser(str(log)) == []
