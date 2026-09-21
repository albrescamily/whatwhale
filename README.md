# whatwhale

Describe what you want in plain English. A local LLM (a GGUF model behind an OpenAI-compatible server such as `llama-server`) turns it into a Docker command, and whatwhale runs it.

## Usage

Start your model server first, for example with llama.cpp:

```
llama-server -m model.gguf --port 8081
```

Then:

```
whatwhale list all running containers
whatwhale -n stop the container named web        # -n: only print the command
whatwhale -c remove all stopped containers       # -c: ask before running
whatwhale --url http://192.168.1.10:8081 show images
```

| Option | Description |
| --- | --- |
| `--url URL` | Server URL (default `http://localhost:8081`, or env `WHATWHALE_URL`) |
| `-n`, `--dry-run` | Print the command without running it |
| `-c`, `--confirm` | Ask for confirmation before running |

To set the server address once:

```powershell
[Environment]::SetEnvironmentVariable("WHATWHALE_URL", "http://localhost:8081", "User")
```

## Safety

whatwhale runs the model's output **without confirmation by default**, so read what it prints. It only runs a single `docker ...` command, without a shell. Anything else, or output containing `&&`, `;`, `|`, `>` and similar, is refused. Docker commands can still be destructive (`docker rm -f`, `docker system prune`), so use `-c` or `-n` if you don't trust the model.

## Requirements

- Python 3.9+ (no third-party packages)
- Docker on your `PATH`
- An OpenAI-compatible server exposing `/v1/chat/completions`

## Run from source

```
python whatwhale.py list running containers
```

## Build the executable (Windows)

```powershell
.\build.ps1
```

This creates a single-file `dist\whatwhale.exe` that runs without Python. To call it from any folder, add `dist` to your user PATH:

```powershell
$dir = "C:\projects\whatwhale\dist"
$current = [Environment]::GetEnvironmentVariable("Path", "User")
[Environment]::SetEnvironmentVariable("Path", "$current;$dir", "User")
```

Then open a new terminal and run `whatwhale --help`.
