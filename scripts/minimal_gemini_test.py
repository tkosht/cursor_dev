import asyncio
import logging
import os

import google.generativeai as genai
from google.generativeai.types import HarmBlockThreshold, HarmCategory

# ロギング設定
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    force=True,
)
logger = logging.getLogger(__name__)

# APIキーの読み込み
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# テスト用プロンプト
PROMPTS = [
    "Hello",
    "今日の東京の天気について、3つのポイントで簡潔に教えてください。",
    "私の好きな色は青色です。この情報を覚えておいてください。",
    "Tell me a short story about a friendly robot.",  # 一般的で無害と思われる英語プロンプト
]

# テスト用セーフティ設定 (最も緩い設定)
PERMISSIVE_SAFETY_SETTINGS = {
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
}


def _log_candidate_details(candidate, c_idx):
    """レスポンス候補の詳細をログに出力"""
    logger.info(f"  候補 {c_idx + 1}:")
    if hasattr(candidate, "finish_reason"):
        logger.info(
            f"    終了理由 (finish_reason): {candidate.finish_reason} "
            f"({candidate.finish_reason.name})"
        )
    else:
        logger.warning("    候補に終了理由属性がありません。")

    if hasattr(candidate, "safety_ratings"):
        logger.info("    セーフティ評価:")
        for rating in candidate.safety_ratings:
            logger.info(f"      カテゴリ: {rating.category.name},")
            logger.info(f"                 確率: {rating.probability.name}")
    else:
        logger.warning("    候補にセーフティ評価属性がありません。")

    if hasattr(candidate, "content") and hasattr(candidate.content, "parts"):
        logger.info(f"    コンテンツパート数: {len(candidate.content.parts)}")
        for p_idx, part in enumerate(candidate.content.parts):
            if hasattr(part, "text"):
                logger.info(f"      P{p_idx+1} Txt: {part.text[:100]}...")  # 長い場合は省略
            else:
                logger.info(f"      パート {p_idx+1}: テキストなし")
    else:
        logger.warning("    候補にコンテンツまたはパート属性がありません。")


def _log_prompt_feedback_details(response):
    """プロンプトフィードバックの詳細をログに出力"""
    if hasattr(response, "prompt_feedback"):
        logger.info("  プロンプトフィードバック:")
        if (
            hasattr(response.prompt_feedback, "block_reason")
            and response.prompt_feedback.block_reason
        ):
            logger.info("    ブロック理由:")
            logger.info(f"      {response.prompt_feedback.block_reason.name}")
        else:
            logger.info("    ブロック理由: なし")
        if hasattr(response.prompt_feedback, "safety_ratings"):
            logger.info("    セーフティ評価 (プロンプトフィードバック):")
            for rating in response.prompt_feedback.safety_ratings:
                logger.info(f"      カテゴリ: {rating.category.name}")
                logger.info(f"        確率: {rating.probability.name}")
    else:
        logger.warning("応答にプロンプトフィードバック属性がありません。")


def _log_response_details(response):
    """APIレスポンスの詳細をログに出力する補助関数"""
    logger.info("--- APIレスポンス詳細 ---")
    if hasattr(response, "text"):
        logger.info(f"応答テキスト: {response.text}")
    else:
        logger.warning("応答にテキスト属性がありません。")

    if hasattr(response, "candidates") and response.candidates:
        for c_idx, candidate in enumerate(response.candidates):
            _log_candidate_details(candidate, c_idx)
    else:
        logger.warning("応答に候補(candidates)がありません。")

    _log_prompt_feedback_details(response)
    logger.info("--------------------------")


async def run_minimal_test():
    """Gemini APIの最小構成テストを実行"""
    if not GEMINI_API_KEY:
        logger.error("環境変数 GEMINI_API_KEY が設定されていません。")
        return

    logger.info("Gemini API 最小構成テストを開始します...")
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel(
        "gemini-2.5-pro-preview-05-06", safety_settings=PERMISSIVE_SAFETY_SETTINGS
    )

    for i, prompt in enumerate(PROMPTS):
        logger.info(f"--- プロンプト {i+1}/{len(PROMPTS)} ---")
        logger.info(f"プロンプト内容: {prompt}")
        try:
            logger.debug("API呼び出し開始...")
            response = await model.generate_content_async(prompt)
            logger.debug("API呼び出し完了。")
            _log_response_details(response)

        except Exception as e:
            logger.error(
                f"プロンプト「{prompt}」の処理中にエラーが発生しました: "
                f"{type(e).__name__} - {e}"
            )
            import traceback
            logger.error(traceback.format_exc())

        await asyncio.sleep(1)  # APIへの連続リクエスト負荷を避ける

    logger.info("Gemini API 最小構成テストを終了します。")


if __name__ == "__main__":
    asyncio.run(run_minimal_test()) 