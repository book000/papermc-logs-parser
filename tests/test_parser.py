from src import parser


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


def test_empty_file_yields_no_entries(tmp_path):
    log = tmp_path / "empty.log"
    log.write_text("", encoding="utf-8")

    assert parser(str(log)) == []
