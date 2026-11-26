# papermc-logs-parser

Parses PaperMC server log files (the same format is used by Spigot and Bukkit) into structured JSON records.

Each record has the time, thread name, log level and message of one log entry. Lines that do not start a new entry, such as stack traces and other multi-line messages, are merged into the entry they follow.

## Requirements

Python 3. Only the standard library is used, so there is nothing to install.

## Usage

1. Edit `config.json` and set `path` to the log file to parse (the default is `logs/latest.log`).

   ```json
   {
       "path": "logs/latest.log"
   }
   ```

2. Run the tool from the repository root:

   ```bash
   python -m src
   ```

The tool prints the parsed entries it considers new to stdout.

### Output files

Both files are written to the current working directory.

- `output.json`: all parsed entries as a JSON array.
- `data.json`: the entry count, first entry time, source identity, file size, and a digest of the file content. On the next run, only entries after the saved count are printed if the source and previously read content still match. Otherwise, all entries are printed. Older cursor files are reset on the next run. `output.json` always contains every entry.

### Entry format

The parser matches lines of the form `[HH:MM:SS] [thread/LEVEL]: message`. For this log:

```text
[12:00:03] [Server thread/ERROR]: Oops
java.lang.RuntimeException: boom
	at Foo.bar(Foo.java:1)
[12:00:04] [Async Chat Thread - #0/INFO]: <Steve> hello
[12:00:05] [Server thread/INFO]: Done
```

the output is:

```json
[
  {
    "time": "12:00:03",
    "threadName": "Server thread",
    "level": "ERROR",
    "messages": "Oops\njava.lang.RuntimeException: boom\n\tat Foo.bar(Foo.java:1)",
    "raws": "[12:00:03] [Server thread/ERROR]: Oops\njava.lang.RuntimeException: boom\n\tat Foo.bar(Foo.java:1)"
  },
  {
    "time": "12:00:04",
    "threadName": "Async Chat Thread - #0",
    "level": "INFO",
    "messages": "<Steve> hello",
    "raws": "[12:00:04] [Async Chat Thread - #0/INFO]: <Steve> hello"
  },
  {
    "time": "12:00:05",
    "threadName": "Server thread",
    "level": "INFO",
    "messages": "Done",
    "raws": "[12:00:05] [Server thread/INFO]: Done"
  }
]
```

- `messages`: the message text, with continuation lines joined by `\n`.
- `raws`: the original lines of the entry, joined by `\n`.

### Known limitations

- The time has no date, so entries from different days cannot be told apart.
- Lines before the first entry are ignored.

## License

See [LICENSE](LICENSE).
