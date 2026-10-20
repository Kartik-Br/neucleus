#!/usr/bin/env python3
"""Serves index.html and exposes calc.calculate() as a small JSON API.

Put this file and index.html in the same folder as calc.py, then run:

    python3 server.py [port]

and open http://127.0.0.1:8000 (standard library only, nothing to install).
"""
import json
import math
import os
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from calc import calculate  # calc.py itself is used unchanged

MAX_BODY = 4096
MAX_EXPR = 500


def to_text(value):
    """Format a result for display: 54.0 -> 54, 0.30000000000000004 -> 0.3."""
    if isinstance(value, float):
        return format(value, ".12g")
    return str(value)


class Handler(BaseHTTPRequestHandler):
    def _send(self, status, body, content_type="application/json"):
        if isinstance(body, (dict, list)):
            body = json.dumps(body).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            try:
                with open(os.path.join(HERE, "index.html"), "rb") as f:
                    self._send(200, f.read(), "text/html; charset=utf-8")
            except FileNotFoundError:
                self._send(404, {"error": "index.html not found next to server.py"})
        elif self.path == "/api/health":
            self._send(200, {"ok": True})
        else:
            self._send(404, {"error": "Not found."})

    def do_POST(self):
        if self.path != "/api/calc":
            self._send(404, {"error": "Not found."})
            return

        try:
            length = int(self.headers.get("Content-Length") or 0)
        except ValueError:
            length = 0
        if length <= 0 or length > MAX_BODY:
            self._send(413, {"error": "Request too large."})
            return

        try:
            data = json.loads(self.rfile.read(length))
            expr = data["expr"]
            ans = data.get("ans", 0)
        except (ValueError, KeyError, TypeError):
            self._send(400, {"error": "Bad request."})
            return

        if (
            not isinstance(expr, str)
            or len(expr) > MAX_EXPR
            or isinstance(ans, bool)
            or not isinstance(ans, (int, float))
        ):
            self._send(400, {"error": "Bad request."})
            return

        try:
            value = calculate(expr, ans)
        except ZeroDivisionError:
            self._send(400, {"error": "Can't divide by zero."})
            return
        except (SyntaxError, ValueError):
            self._send(400, {"error": "Can't calculate that. Check the expression."})
            return
        except Exception:
            self._send(400, {"error": "That calculation is too large or too complex."})
            return

        if isinstance(value, bool):
            value = int(value)
        if isinstance(value, float) and not math.isfinite(value):
            self._send(400, {"error": "That result is too large."})
            return

        self._send(200, {"value": value, "text": to_text(value)})


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"Calc is running at http://127.0.0.1:{port}  (Ctrl+C to stop)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print()
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
