"""
Weather Agent

天気情報を提供するA2Aエージェント
デモ用のモック実装
"""

import random
import re
from datetime import datetime
from typing import Any, List

from python_a2a import AgentSkill, TaskState

from ..utils.config import A2AConfig
from .base_agent import BaseA2AAgent


class WeatherAgent(BaseA2AAgent):
    """天気情報を提供するA2Aエージェント"""
    
    def __init__(self):
        super().__init__(A2AConfig.WEATHER_AGENT)
        
        # デモ用の天気データ
        self.weather_data = {
            "東京": {"temp": 22, "condition": "晴れ", "humidity": 65},
            "大阪": {"temp": 25, "condition": "曇り", "humidity": 70},
            "名古屋": {"temp": 24, "condition": "雨", "humidity": 80},
            "福岡": {"temp": 26, "condition": "晴れ", "humidity": 60},
            "札幌": {"temp": 18, "condition": "曇り", "humidity": 55},
            "仙台": {"temp": 20, "condition": "晴れ", "humidity": 62},
        }
    
    def get_skills(self) -> List[AgentSkill]:
        """天気エージェントのスキル一覧"""
        return [
            AgentSkill(
                id="get_weather",
                name="現在の天気取得",
                description="指定された場所の現在の天気情報を取得します",
                tags=["weather", "current"],
                examples=[
                    "東京の天気を教えて",
                    "大阪の今の天気はどう？",
                    "名古屋の天気を知りたい"
                ]
            ),
            AgentSkill(
                id="get_forecast",
                name="天気予報取得",
                description="指定された場所の天気予報を取得します",
                tags=["weather", "forecast"],
                examples=[
                    "明日の東京の天気予報",
                    "週末の天気はどう？",
                    "来週の大阪の天気予報"
                ]
            )
        ]
    
    def get_current_weather(self, location: str) -> str:
        """現在の天気情報を取得"""
        if location in self.weather_data:
            data = self.weather_data[location]
            return (
                f"{location}の現在の天気:\n"
                f"天候: {data['condition']}\n"
                f"気温: {data['temp']}°C\n"
                f"湿度: {data['humidity']}%"
            )
        else:
            return f"申し訳ありません。{location}の天気情報は現在利用できません。"
    
    def get_weather_forecast(self, location: str, days: int = 3) -> str:
        """天気予報を取得（デモ用）"""
        if location not in self.weather_data:
            return f"申し訳ありません。{location}の天気予報は現在利用できません。"
        
        base_data = self.weather_data[location]
        forecast_text = f"{location}の{days}日間天気予報:\n\n"
        
        conditions = ["晴れ", "曇り", "雨", "晴れ時々曇り"]
        
        for day in range(days):
            # ランダムな変動を加える
            temp_variation = random.randint(-3, 3)
            humidity_variation = random.randint(-10, 10)
            
            forecast_day = datetime.now().day + day + 1
            condition = random.choice(conditions)
            temp = base_data["temp"] + temp_variation
            humidity = max(30, min(90, base_data["humidity"] + humidity_variation))
            
            forecast_text += (
                f"{forecast_day}日: {condition}, "
                f"{temp}°C, 湿度{humidity}%\n"
            )
        
        return forecast_text.strip()
    
    def process_task_text(self, task, text: str) -> Any:
        """テキストを処理してタスクを完了"""
        # 場所を抽出
        location = self._extract_location(text)
        
        if not location:
            # エラーメッセージを設定
            task.artifacts = [{
                "parts": [{"type": "text", "text": "場所を指定してください。例: 「東京の天気を教えて」"}]
            }]
            task.status = TaskState.INPUT_REQUIRED
            return task
        
        try:
            # 予報か現在の天気かを判断
            if any(word in text for word in ["予報", "明日", "来週", "週末"]):
                result = self.get_weather_forecast(location)
            else:
                result = self.get_current_weather(location)
            
            # 成功結果を設定
            task.artifacts = [{
                "parts": [{"type": "text", "text": result}]
            }]
            task.status = TaskState.COMPLETED
            return task
            
        except Exception as e:
            self.logger.error(f"Weather query failed: {e}")
            task.artifacts = [{
                "parts": [{"type": "text", "text": "天気情報の取得中にエラーが発生しました。"}]
            }]
            task.status = TaskState.FAILED
            return task
    
    def _extract_location(self, text: str) -> str:
        """テキストから場所を抽出"""
        # 都市名パターン
        locations = list(self.weather_data.keys())
        
        for location in locations:
            if location in text:
                return location
        
        # より一般的なパターンマッチング
        location_patterns = [
            r'([東西南北]?[都道府県市区町村]+)の天気',
            r'([東西南北]?[都道府県市区町村]+)は',
            r'([東西南北]?[都道府県市区町村]+)について',
        ]
        
        for pattern in location_patterns:
            match = re.search(pattern, text)
            if match:
                extracted = match.group(1)
                # 既知の場所かチェック
                for location in locations:
                    if location in extracted:
                        return location
        
        return ""


def main():
    """Weather Agentを起動"""
    agent = WeatherAgent()
    print(f"Starting Weather Agent on {agent.config.url}")
    agent.run_agent()


if __name__ == "__main__":
    main() 