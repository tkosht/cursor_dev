"""
Calculator Agent

数学計算を実行するA2Aエージェント
基本的な計算機能とmath関数のサポート
"""

import math
import re
from typing import Any, List

from python_a2a import AgentSkill, TaskState

from ..utils.config import A2AConfig
from .base_agent import BaseA2AAgent


class CalculatorAgent(BaseA2AAgent):
    """数学計算を実行するA2Aエージェント"""
    
    def __init__(self):
        super().__init__(A2AConfig.CALCULATOR_AGENT)
        
        # 安全な数学関数のマッピング
        self.safe_functions = {
            'sin': math.sin,
            'cos': math.cos,
            'tan': math.tan,
            'log': math.log,
            'log10': math.log10,
            'sqrt': math.sqrt,
            'abs': abs,
            'pow': pow,
            'round': round,
            'pi': math.pi,
            'e': math.e,
        }
    
    def get_skills(self) -> List[AgentSkill]:
        """計算エージェントのスキル一覧"""
        return [
            AgentSkill(
                id="calculate",
                name="基本計算",
                description="四則演算などの基本的な数学計算を実行します",
                tags=["math", "calculation", "basic"],
                examples=[
                    "5 + 3 を計算して",
                    "12 * 15 はいくつ？",
                    "100 / 4 を教えて",
                    "2の3乗は？"
                ]
            ),
            AgentSkill(
                id="advanced_math",
                name="高度な数学計算",
                description="三角関数、対数、平方根などの高度な数学計算を実行します",
                tags=["math", "advanced", "functions"],
                examples=[
                    "sin(30度) を計算して",
                    "log(100) を求めて",
                    "√16 はいくつ？",
                    "π × 2 を計算"
                ]
            ),
            AgentSkill(
                id="solve_equation",
                name="方程式解決",
                description="簡単な方程式を解きます",
                tags=["math", "equation", "solving"],
                examples=[
                    "x + 5 = 12 を解いて",
                    "2x = 10 の解は？"
                ]
            )
        ]
    
    def basic_calculate(self, expression: str) -> str:
        """基本的な数学計算を実行"""
        try:
            # 式を安全化
            safe_expression = self._sanitize_expression(expression)
            
            if not safe_expression:
                return "計算式を理解できませんでした。例: 5 + 3, 10 * 2"
            
            # 計算実行
            result = eval(safe_expression, {"__builtins__": {}}, self.safe_functions)
            
            return f"計算結果: {expression} = {result}"
            
        except ZeroDivisionError:
            return "エラー: ゼロで割ることはできません。"
        except Exception as e:
            return f"計算エラー: {expression} を計算できませんでした。({str(e)})"
    
    def advanced_calculate(self, expression: str) -> str:
        """高度な数学計算を実行"""
        try:
            # 度数法を弧度法に変換
            expression = self._convert_degrees_to_radians(expression)
            
            # 安全化
            safe_expression = self._sanitize_expression(expression)
            
            if not safe_expression:
                return "数学式を理解できませんでした。例: sin(30), log(10), sqrt(16)"
            
            # 計算実行
            result = eval(safe_expression, {"__builtins__": {}}, self.safe_functions)
            
            return f"計算結果: {result}"
            
        except Exception as e:
            return f"計算エラー: {expression} を計算できませんでした。({str(e)})"
    
    def solve_simple_equation(self, equation: str) -> str:
        """簡単な方程式を解く"""
        try:
            # 基本的な一次方程式のパターンマッチング
            # x + a = b
            pattern1 = r'x\s*\+\s*(\d+)\s*=\s*(\d+)'
            match1 = re.search(pattern1, equation)
            if match1:
                a, b = int(match1.group(1)), int(match1.group(2))
                result = b - a
                return f"方程式 {equation} の解: x = {result}"
            
            # x - a = b
            pattern2 = r'x\s*-\s*(\d+)\s*=\s*(\d+)'
            match2 = re.search(pattern2, equation)
            if match2:
                a, b = int(match2.group(1)), int(match2.group(2))
                result = b + a
                return f"方程式 {equation} の解: x = {result}"
            
            # ax = b
            pattern3 = r'(\d+)x\s*=\s*(\d+)'
            match3 = re.search(pattern3, equation)
            if match3:
                a, b = int(match3.group(1)), int(match3.group(2))
                if a == 0:
                    return "エラー: 係数がゼロの方程式は解けません。"
                result = b / a
                return f"方程式 {equation} の解: x = {result}"
            
            return "申し訳ありません。この形式の方程式は現在サポートしていません。"
            
        except Exception as e:
            return f"方程式の解決中にエラーが発生しました: {str(e)}"
    
    def process_task_text(self, task, text: str) -> Any:
        """テキストを処理してタスクを完了"""
        try:
            # 計算の種類を判断
            if self._is_equation(text):
                result = self.solve_simple_equation(text)
            elif self._is_advanced_math(text):
                result = self.advanced_calculate(text)
            else:
                result = self.basic_calculate(text)
            
            # 成功結果を設定
            task.artifacts = [{
                "parts": [{"type": "text", "text": result}]
            }]
            task.status = TaskState.COMPLETED
            return task
            
        except Exception as e:
            self.logger.error(f"Calculation failed: {e}")
            task.artifacts = [{
                "parts": [{"type": "text", "text": "計算中にエラーが発生しました。計算式を確認してください。"}]
            }]
            task.status = TaskState.FAILED
            return task
    
    def _sanitize_expression(self, expression: str) -> str:
        """計算式を安全化"""
        # 危険な文字列を除去
        dangerous_patterns = [
            r'__', r'import', r'exec', r'eval', r'open', r'file',
            r'input', r'raw_input', r'compile'
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, expression, re.IGNORECASE):
                return ""
        
        # 基本的な数学記号と数字のみを許可
        allowed_chars = r'[0-9+\-*/().\s√πe]|sin|cos|tan|log|sqrt|pow|abs|pi'
        
        # 日本語の特殊記号を変換
        expression = expression.replace('√', 'sqrt')
        expression = expression.replace('π', 'pi')
        expression = expression.replace('×', '*')
        expression = expression.replace('÷', '/')
        
        # 数学表現を抽出
        math_parts = re.findall(allowed_chars, expression)
        return ''.join(math_parts)
    
    def _convert_degrees_to_radians(self, expression: str) -> str:
        """度数法を弧度法に変換"""
        # sin(30度) -> sin(30*pi/180)
        degree_pattern = r'(sin|cos|tan)\((\d+)度?\)'
        
        def convert_match(match):
            func, degree = match.groups()
            return f"{func}({degree}*pi/180)"
        
        return re.sub(degree_pattern, convert_match, expression)
    
    def _is_equation(self, text: str) -> bool:
        """方程式かどうかを判断"""
        return '=' in text and 'x' in text
    
    def _is_advanced_math(self, text: str) -> bool:
        """高度な数学関数が含まれているかを判断"""
        advanced_keywords = ['sin', 'cos', 'tan', 'log', 'sqrt', '√', 'π', 'pi']
        return any(keyword in text.lower() for keyword in advanced_keywords)


def main():
    """Calculator Agentを起動"""
    agent = CalculatorAgent()
    print(f"Starting Calculator Agent on {agent.config.url}")
    agent.run_agent()


if __name__ == "__main__":
    main() 