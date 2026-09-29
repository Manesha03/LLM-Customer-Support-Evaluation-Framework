import argparse
import json
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from chatbot import get_response


ROOT = Path(__file__).resolve().parents[1]
WEB_DIR = ROOT / "web"


class ShopEaseHandler(BaseHTTPRequestHandler):
    provider = "rules"
    model = "gpt-5-mini"
    ollama_host = "http://localhost:11434"

    def do_GET(self):
        if self.path in {"/", "/index.html"}:
            self.send_file(WEB_DIR / "index.html", "text/html; charset=utf-8")
            return
        if self.path == "/styles.css":
            self.send_file(WEB_DIR / "styles.css", "text/css; charset=utf-8")
            return
        if self.path == "/app.js":
            self.send_file(WEB_DIR / "app.js", "application/javascript; charset=utf-8")
            return
        self.send_error(404, "File not found")

    def do_POST(self):
        if self.path != "/api/chat":
            self.send_error(404, "Endpoint not found")
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
            message = str(payload.get("message", "")).strip()
            if not message:
                raise ValueError("Message cannot be empty.")

            answer = get_response(self.provider, self.model, message, self.ollama_host)
            self.send_json({"response": answer})
        except Exception as error:
            self.send_json({"error": str(error)}, status=400)

    def send_file(self, path, content_type):
        if not path.exists():
            self.send_error(404, "File not found")
            return
        content = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def send_json(self, payload, status=200):
        content = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def log_message(self, format, *args):
        sys.stderr.write("%s - %s\n" % (self.address_string(), format % args))


def main():
    parser = argparse.ArgumentParser(description="Run the ShopEase browser chatbot.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--provider", choices=["rules", "openai", "ollama"], default="rules")
    parser.add_argument("--model", default="gpt-5-mini")
    parser.add_argument("--ollama-host", default="http://localhost:11434")
    args = parser.parse_args()

    ShopEaseHandler.provider = args.provider
    ShopEaseHandler.model = args.model
    ShopEaseHandler.ollama_host = args.ollama_host

    server = ThreadingHTTPServer((args.host, args.port), ShopEaseHandler)
    print(f"ShopEase web chatbot running at http://{args.host}:{args.port}")
    print("Press Ctrl+C to stop.")
    server.serve_forever()


if __name__ == "__main__":
    main()
