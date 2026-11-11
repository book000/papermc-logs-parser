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

The tool echoes every line of the log file to stdout while parsing, then prints the entries it considers new.

### Output files

Both files are written to the current working directory.

- `output.json`: all parsed entries as a JSON array.
- `data.json`: `{"count": <entries parsed>, "firstTime": "<time of the first entry>"}`. On the next run, if the first entry has the same time as `firstTime`, only the entries after the first `count` ones are printed. `output.json` always contains every entry.

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
  }
]
```

- `messages`: the message text, with continuation lines joined by `\n`.
- `raws`: the original lines of the entry, joined by `\n`.

### Known limitations

- The last entry of a file is not emitted (the final `Done` entry above is missing from the output).
- The time has no date, so entries from different days cannot be told apart.
- An empty or fully non-matching log makes `python -m src` fail with an `IndexError`.

## License

See [LICENSE](LICENSE).
