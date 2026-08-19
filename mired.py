#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
import platform
import socket
import subprocess
import time
import urllib.request
from pathlib import Path

SCHEMA = "desarrollamo.mired.v1"


def run(cmd: list[str], timeout: float = 2.5) -> str:
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, check=False)
        return (p.stdout or "").strip()
    except Exception:
        return ""


def local_ip() -> str | None:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("1.1.1.1", 443))
        return s.getsockname()[0]
    except Exception:
        return None
    finally:
        s.close()


def gateway() -> str | None:
    system = platform.system()
    if system == "Windows":
        out = run(["powershell", "-NoProfile", "-Command", "(Get-NetRoute -DestinationPrefix '0.0.0.0/0' | Sort-Object RouteMetric | Select-Object -First 1 -ExpandProperty NextHop)"])
        return out or None
    if system == "Darwin":
        out = run(["route", "-n", "get", "default"])
        for line in out.splitlines():
            if "gateway:" in line:
                return line.split("gateway:", 1)[1].strip()
    out = run(["ip", "route", "show", "default"])
    parts = out.split()
    if "via" in parts:
        i = parts.index("via")
        if i + 1 < len(parts):
            return parts[i + 1]
    return None


def dns_servers() -> list[str]:
    system = platform.system()
    found: list[str] = []
    if system == "Windows":
        out = run(["powershell", "-NoProfile", "-Command", "(Get-DnsClientServerAddress -AddressFamily IPv4).ServerAddresses -join '\n'"])
        found = [x.strip() for x in out.splitlines() if x.strip()]
    elif system == "Darwin":
        out = run(["scutil", "--dns"])
        for line in out.splitlines():
            if "nameserver[" in line and ":" in line:
                found.append(line.split(":", 1)[1].strip())
    else:
        try:
            for line in Path("/etc/resolv.conf").read_text(errors="ignore").splitlines():
                if line.startswith("nameserver "):
                    found.append(line.split()[1])
        except Exception:
            pass
    return list(dict.fromkeys(found))[:6]


def timed_dns() -> dict:
    started = time.perf_counter()
    try:
        socket.getaddrinfo("example.com", 443)
        return {"ok": True, "elapsed_ms": round((time.perf_counter() - started) * 1000, 1), "target": "example.com"}
    except Exception as exc:
        return {"ok": False, "elapsed_ms": round((time.perf_counter() - started) * 1000, 1), "error": exc.__class__.__name__}


def timed_tcp() -> dict:
    started = time.perf_counter()
    try:
        with socket.create_connection(("1.1.1.1", 443), timeout=4):
            pass
        return {"ok": True, "elapsed_ms": round((time.perf_counter() - started) * 1000, 1), "target": "1.1.1.1:443"}
    except Exception as exc:
        return {"ok": False, "elapsed_ms": round((time.perf_counter() - started) * 1000, 1), "error": exc.__class__.__name__}


def timed_https() -> dict:
    started = time.perf_counter()
    req = urllib.request.Request("https://example.com/", headers={"User-Agent": "MiRed/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=5) as r:
            r.read(128)
            status = getattr(r, "status", 200)
        return {"ok": 200 <= status < 400, "status": status, "elapsed_ms": round((time.perf_counter() - started) * 1000, 1), "target": "https://example.com/"}
    except Exception as exc:
        return {"ok": False, "elapsed_ms": round((time.perf_counter() - started) * 1000, 1), "error": exc.__class__.__name__}


def public_ip() -> dict:
    req = urllib.request.Request("https://api.ipify.org?format=json", headers={"User-Agent": "MiRed/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=5) as r:
            data = json.loads(r.read().decode("utf-8"))
        return {"enabled": True, "ok": True, "ip": data.get("ip")}
    except Exception as exc:
        return {"enabled": True, "ok": False, "error": exc.__class__.__name__}


def score(checks: dict) -> int:
    weights = {"dns": 30, "tcp": 30, "https": 40}
    total = 0
    for name, weight in weights.items():
        if checks.get(name, {}).get("ok"):
            total += weight
    return total


def build_report(probe: bool, include_online: bool) -> dict:
    checks = {
        "dns": timed_dns() if probe else {"skipped": True},
        "tcp": timed_tcp() if probe else {"skipped": True},
        "https": timed_https() if probe else {"skipped": True},
    }
    return {
        "schema": SCHEMA,
        "generated_at": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat(),
        "privacy": {
            "lan_scan_performed": False,
            "mac_addresses_collected": False,
            "wifi_credentials_collected": False,
            "public_ip_requested": include_online,
        },
        "network": {
            "local_ip": local_ip(),
            "default_gateway": gateway(),
            "dns_servers": dns_servers(),
        },
        "checks": checks,
        "online": public_ip() if include_online else {"enabled": False},
        "summary": {"score": score(checks) if probe else None, "probe_enabled": probe},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="MiRed: diagnóstico seguro de conectividad")
    parser.add_argument("--online", action="store_true", help="consulta también la IP pública")
    parser.add_argument("--no-probe", action="store_true", help="omite pruebas externas de DNS/TCP/HTTPS")
    parser.add_argument("--output", help="guarda el reporte JSON")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args()
    report = build_report(not args.no_probe, args.online)
    text = json.dumps(report, ensure_ascii=False, indent=None if args.compact else 2)
    print(text)
    if args.output:
        Path(args.output).write_text(text + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
