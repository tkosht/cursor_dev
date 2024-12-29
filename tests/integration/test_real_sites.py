"""
実際の企業サイトを使用した統合テスト
"""
import asyncio
import logging
import sys

import pytest

from app.llm.manager import LLMManager
from app.site_analyzer import SiteAnalyzer

# ログ設定
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)

# すべてのロガーのレベルをDEBUGに設定
for name in logging.root.manager.loggerDict:
    logging.getLogger(name).setLevel(logging.DEBUG)

# テスト対象の企業サイト（テスト負荷軽減のため1サイトのみ）
TARGET_SITES = [
    "https://www.accenture.com/jp-ja",  # アクセンチュア（日本）
]


@pytest.mark.asyncio
async def test_real_site_analysis():
    """
    実際の企業サイトで情報抽出をテスト
    """
    logger = logging.getLogger(__name__)
    logger.info("Starting test_real_site_analysis")
    
    llm_manager = LLMManager()
    logger.info("LLMManager initialized")
    
    for base_url in TARGET_SITES:
        logger.info(f"\n=== Starting analysis of {base_url} ===")
        
        async with SiteAnalyzer(llm_manager) as analyzer:
            try:
                logger.info("Initialized SiteAnalyzer")
                
                # サイト構造の解析
                logger.info("Starting site structure analysis")
                result = await analyzer.analyze_site_structure(base_url)
                logger.info("Completed site structure analysis")
                
                # 結果の表示（簡潔化）
                logger.info("\nSitemap URLs:")
                for url in result["sitemap"][:3]:  # 最初の3件のみ表示
                    logger.info(f"- {url}")
                
                logger.info("\nRelevant Pages:")
                for page in result["relevant_pages"][:2]:  # 最初の2件のみ表示
                    logger.info(f"\nURL: {page['url']}")
                    logger.info(f"Type: {page['page_type']}")
                    logger.info(f"Relevance Score: {page['relevance_score']:.2f}")
                
            except Exception as e:
                logger.error(f"Error analyzing {base_url}: {str(e)}", exc_info=True)
                continue

    logger.info("Test completed")


if __name__ == "__main__":
    asyncio.run(test_real_site_analysis()) 