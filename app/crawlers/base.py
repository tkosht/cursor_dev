import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

import requests
from requests.exceptions import RequestException
from sqlalchemy.orm import Session


class BaseCrawler(ABC):
    """
    クローラーの基本クラス
    
    Attributes:
        session (Session): データベースセッション
        headers (Dict[str, str]): HTTPリクエストヘッダー
        timeout (int): リクエストタイムアウト（秒）
        max_retries (int): リトライ回数
        logger (logging.Logger): ロガー
    """
    
    def __init__(
        self,
        session: Optional[Session] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: int = 30,
        max_retries: int = 3
    ):
        """
        クローラーの初期化
        
        Args:
            session: データベースセッション
            headers: HTTPリクエストヘッダー
            timeout: リクエストタイムアウト（秒）
            max_retries: リトライ回数
        """
        self.session = session
        self.headers = headers or {
            'User-Agent': 'Mozilla/5.0 (compatible; CompanyDataBot/1.0)'
        }
        self.timeout = timeout
        self.max_retries = max_retries
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def _make_request(
        self,
        url: str,
        method: str = 'GET',
        **kwargs
    ) -> requests.Response:
        """
        HTTPリクエストの実行
        
        Args:
            url: リクエスト先URL
            method: HTTPメソッド
            **kwargs: requestsライブラリに渡す追加パラメータ
            
        Returns:
            Response: レスポンスオブジェクト
            
        Raises:
            RequestException: リクエスト失敗時
        """
        for attempt in range(self.max_retries):
            try:
                response = requests.request(
                    method,
                    url,
                    headers=self.headers,
                    timeout=self.timeout,
                    **kwargs
                )
                response.raise_for_status()
                return response
            
            except RequestException as e:
                self.logger.warning(
                    f"Request failed (attempt {attempt + 1}/{self.max_retries}): {str(e)}"
                )
                if attempt == self.max_retries - 1:
                    raise
        
        raise RequestException("Max retries exceeded")
    
    @abstractmethod
    def crawl(self) -> None:
        """
        クローリングの実行
        
        各クローラーで実装する必要があります。
        """
        pass
    
    def save(self, data: Any) -> None:
        """
        データの保存
        
        Args:
            data: 保存するデータ
        """
        if self.session is None:
            self.logger.warning("No database session available")
            return
        
        try:
            self.session.add(data)
            self.session.commit()
            self.logger.info(f"Saved data: {data}")
            
        except Exception as e:
            self.session.rollback()
            self.logger.error(f"Failed to save data: {str(e)}")
            raise 