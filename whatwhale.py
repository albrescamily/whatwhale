"""whatwhale - turn a plain-English request into a docker command and run it."""

import argparse
import json
import os
import platform
import shlex
import subprocess
import sys
import urllib.request

DEFAULT_URL = os.environ.get("WHATWHALE_URL", "http://localhost:8081")

SYSTEM_PROMPT = (
    f"Translate the request into a single Docker CLI command for {platform.system()}. "
    "Reply with ONLY the command on one line, starting with 'docker'. No explanation, no markdown. "
    "If it cannot be done with one docker command, reply with 'ERROR: <short reason>'."
)


def ask_model(url, request):
    """Ask an OpenAI-compatible server (e.g. llama-server) and return the reply's non-empty lines."""
    payload = {
        "temperature": 0,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": request},
        ],
    }
    req = urllib.request.Request(
        url.rstrip("/") + "/v1/chat/completions",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        text = json.load(resp)["choices"][0]["message"]["content"]
    # ignore blank lines and markdown fences the model may add anyway
    return [l.strip() for l in text.splitlines() if l.strip() and not l.strip().startswith("```")]


def main():
    parser = argparse.ArgumentParser(prog="whatwhale", description="Ask for a docker command in plain English.")
    parser.add_argument("request", nargs="+", help='e.g. "list running containers"')
    parser.add_argument("--url", default=DEFAULT_URL, help=f"LLM server URL (default: {DEFAULT_URL})")
    parser.add_argument("-n", "--dry-run", action="store_true", help="only print the command")
    parser.add_argument("-c", "--confirm", action="store_true", help="ask before running")
    args = parser.parse_args()

    try:
        lines = ask_model(args.url, " ".join(args.request))
    except OSError as e:
        sys.exit(f"error: could not reach {args.url}: {e}")
    except (KeyError, IndexError, ValueError) as e:
        sys.exit(f"error: unexpected response from the server: {e}")

    command = lines[0] if len(lines) == 1 else ""
    if command.upper().startswith("ERROR:"):
        sys.exit(command)
    try:
        argv = shlex.split(command)
    except ValueError:
        argv = []
    if argv[:1] != ["docker"] or {"&&", "||", ";", "|", ">", ">>", "<", "&"} & set(argv):
        sys.exit("error: refusing to run, the model did not return a single docker command:\n  " + "\n  ".join(lines))

    print(f"$ {command}")
    if args.dry_run:
        return
    if args.confirm and input("Run? [y/N] ").strip().lower() not in ("y", "yes"):
        return
    try:
        sys.exit(subprocess.run(argv).returncode)  # no shell, so nothing can be injected
    except FileNotFoundError:
        sys.exit("error: 'docker' was not found on PATH")


if __name__ == "__main__":
    main()
