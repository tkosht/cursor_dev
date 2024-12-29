"""
統合テスト用のモックサーバー
"""

from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread
from typing import Dict, Optional
from urllib.parse import urlparse


class MockServerRequestHandler(BaseHTTPRequestHandler):
    """モックサーバーのリクエストハンドラー"""

    # パスごとのレスポンス
    responses: Dict[str, str] = {}

    def do_GET(self):
        """GETリクエストの処理"""
        parsed_path = urlparse(self.path).path
        if parsed_path in self.responses:
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(self.responses[parsed_path].encode("utf-8"))
        else:
            self.send_response(404)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"Not Found")

    def log_message(self, format: str, *args) -> None:
        """ログ出力を抑制"""
        pass


class MockServer:
    """モックサーバー"""

    def __init__(self, host: str = "localhost", port: int = 0):
        """
        初期化

        Args:
            host: ホスト名
            port: ポート番号（0の場合は空いているポートを自動割り当て）
        """
        self.host = host
        self.port = port
        self.server: Optional[HTTPServer] = None
        self.server_thread: Optional[Thread] = None

    def start(self) -> None:
        """サーバーの起動"""
        if self.server:
            return

        self.server = HTTPServer((self.host, self.port), MockServerRequestHandler)
        self.port = self.server.server_port  # 実際に割り当てられたポートを取得

        self.server_thread = Thread(target=self.server.serve_forever)
        self.server_thread.daemon = True
        self.server_thread.start()

    def stop(self) -> None:
        """サーバーの停止"""
        if self.server:
            self.server.shutdown()
            self.server.server_close()
            self.server = None
        if self.server_thread:
            self.server_thread.join()
            self.server_thread = None

    def set_responses(self, responses: Dict[str, str]) -> None:
        """
        レスポンスの設定

        Args:
            responses: パスごとのレスポンス内容
        """
        MockServerRequestHandler.responses = responses

    def clear_responses(self) -> None:
        """レスポンスのクリア"""
        MockServerRequestHandler.responses = {}

    @property
    def url(self) -> str:
        """サーバーのURL"""
        return f"http://{self.host}:{self.port}"
