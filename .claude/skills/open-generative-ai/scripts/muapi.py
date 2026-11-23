#!/usr/bin/env python3
"""Minimal MuAPI client (stdlib only), mirroring Open-Generative-AI's src/lib/muapi.js.

Usage:
  muapi.py run <endpoint> [-p key=value ...] [--json '{...}'] [--out DIR] [--timeout SEC]
  muapi.py upload <file>                 # -> prints hosted URL
  muapi.py result <request_id> [--out DIR] [--timeout SEC]
  muapi.py models [filter]               # grep the bundled catalog

Auth: MUAPI_API_KEY env var, sent as the `x-api-key` header.
Base URL: MUAPI_BASE_URL (default https://api.muapi.ai).
"""
import argparse, json, mimetypes, os, pathlib, sys, time, urllib.error, urllib.parse, urllib.request, uuid

BASE = os.environ.get("MUAPI_BASE_URL", "https://api.muapi.ai").rstrip("/")
SUCCESS = {"completed", "succeeded", "success"}
FAILURE = {"failed", "error", "cancelled", "canceled"}
HERE = pathlib.Path(__file__).resolve().parent


def die(msg, code=1):
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(code)


def api_key():
    key = (os.environ.get("MUAPI_API_KEY") or "").strip()
    if not key:
        die("MUAPI_API_KEY is not set. Get a key at https://muapi.ai and export MUAPI_API_KEY=...")
    return key


def request(method, path, body=None, headers=None, raw=None):
    h = {"x-api-key": api_key(), **(headers or {})}
    data = raw
    if body is not None:
        data = json.dumps(body).encode()
        h["Content-Type"] = "application/json"
    req = urllib.request.Request(f"{BASE}{path}", data=data, method=method, headers=h)
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return json.loads(r.read().decode() or "{}")
    except urllib.error.HTTPError as e:
        detail = e.read().decode(errors="replace")[:500]
        if e.code in (401, 403):
            die(f"HTTP {e.code}: invalid or missing API key (or host blocked by network policy). {detail}")
        if e.code == 402:
            die(f"HTTP 402: insufficient MuAPI credits. {detail}")
        raise RuntimeError(f"HTTP {e.code}: {detail}")
    except urllib.error.URLError as e:
        die(f"cannot reach {BASE}: {e.reason} (if this is a proxy 403, allow api.muapi.ai in the network policy)")


def coerce(v):
    try:
        return json.loads(v)
    except ValueError:
        return v


def poll(request_id, timeout):
    deadline = time.time() + timeout
    while time.time() < deadline:
        time.sleep(2)
        try:
            res = request("GET", f"/api/v1/predictions/{request_id}/result")
        except RuntimeError as e:
            if "HTTP 5" in str(e):
                continue
            raise
        status = str(res.get("status", "")).lower()
        if status in SUCCESS:
            return res
        if status in FAILURE:
            err = res.get("error")
            msg = err.get("message") if isinstance(err, dict) else err or res.get("message")
            die(f"generation failed ({request_id}): {msg}")
        print(f"... {status or 'pending'}", file=sys.stderr)
    die(f"timed out; resume later with: muapi.py result {request_id}")


def outputs(res):
    outs = res.get("outputs") or []
    if not outs:
        u = res.get("url") or (res.get("output") or {}).get("url")
        outs = [u] if u else []
    return outs


def download(urls, out_dir):
    out = pathlib.Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    paths = []
    for u in urls:
        name = pathlib.Path(urllib.parse.urlparse(u).path).name or f"{uuid.uuid4().hex}.bin"
        dest = out / name
        urllib.request.urlretrieve(u, dest)
        paths.append(str(dest))
    return paths


def finish(res, args):
    urls = outputs(res)
    result = {"request_id": res.get("request_id") or res.get("id"), "status": res.get("status"), "outputs": urls}
    if args.out and urls:
        result["files"] = download(urls, args.out)
    print(json.dumps(result, indent=2))


def cmd_run(args):
    payload = json.loads(args.json) if args.json else {}
    for kv in args.param or []:
        k, _, v = kv.partition("=")
        payload[k] = coerce(v)
    endpoint = args.endpoint.strip("/")
    print(f"POST {BASE}/api/v1/{endpoint} {json.dumps(payload)}", file=sys.stderr)
    sub = request("POST", f"/api/v1/{endpoint}", body=payload)
    rid = sub.get("request_id") or sub.get("id")
    if not rid:
        return finish(sub, args)
    print(f"request_id: {rid}", file=sys.stderr)
    finish(poll(rid, args.timeout), args)


def cmd_result(args):
    finish(poll(args.request_id, args.timeout), args)


def cmd_upload(args):
    p = pathlib.Path(args.file)
    if not p.is_file():
        die(f"no such file: {p}")
    boundary = uuid.uuid4().hex
    ctype = mimetypes.guess_type(p.name)[0] or "application/octet-stream"
    body = (f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"{p.name}\"\r\n"
            f"Content-Type: {ctype}\r\n\r\n").encode() + p.read_bytes() + f"\r\n--{boundary}--\r\n".encode()
    res = request("POST", "/api/v1/upload_file", raw=body,
                  headers={"Content-Type": f"multipart/form-data; boundary={boundary}"})
    url = res.get("url") or res.get("file_url") or (res.get("data") or {}).get("url")
    if not url:
        die(f"no URL in upload response: {res}")
    print(url)


def cmd_models(args):
    text = (HERE.parent / "references" / "models.md").read_text()
    section = ""
    for line in text.splitlines():
        if line.startswith("## "):
            section = line[3:]
        elif line.startswith("| `") and (not args.filter or args.filter.lower() in line.lower()):
            print(f"[{section.split(' — ')[0]}] {line}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    r = sp.add_parser("run"); r.add_argument("endpoint")
    r.add_argument("-p", "--param", action="append", help="key=value (value parsed as JSON if possible)")
    r.add_argument("--json", help="full JSON payload; -p values are merged on top")
    r.add_argument("--out", help="download outputs into this directory")
    r.add_argument("--timeout", type=int, default=1800)
    r.set_defaults(fn=cmd_run)
    g = sp.add_parser("result"); g.add_argument("request_id")
    g.add_argument("--out"); g.add_argument("--timeout", type=int, default=1800); g.set_defaults(fn=cmd_result)
    u = sp.add_parser("upload"); u.add_argument("file"); u.set_defaults(fn=cmd_upload)
    m = sp.add_parser("models"); m.add_argument("filter", nargs="?"); m.set_defaults(fn=cmd_models)
    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
