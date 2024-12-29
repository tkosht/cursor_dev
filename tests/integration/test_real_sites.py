"""
実際の企業サイトを使用した統合テスト
"""
import asyncio

import pytest

from app.llm.manager import LLMManager
from app.site_analyzer import SiteAnalyzer

# テスト対象の企業サイト（テスト負荷軽減のため1サイトのみ）
TARGET_SITES = [
    "https://www.nitorihd.co.jp",
]


@pytest.mark.asyncio
async def test_real_site_analysis():
    """
    実際の企業サイトで情報抽出をテスト
    """
    llm_manager = LLMManager()
    
    for base_url in TARGET_SITES:
        print(f"\n=== Analyzing {base_url} ===")
        
        async with SiteAnalyzer(llm_manager) as analyzer:
            try:
                # サイト構造の解析
                result = await analyzer.analyze_site_structure(base_url)
                
                # 結果の表示（簡潔化）
                print("\nSitemap URLs:")
                for url in result["sitemap"][:3]:  # 最初の3件のみ表示
                    print(f"- {url}")
                
                print("\nRelevant Pages:")
                for page in result["relevant_pages"][:2]:  # 最初の2件のみ表示
                    print(f"\nURL: {page['url']}")
                    print(f"Type: {page['page_type']}")
                    print(f"Relevance Score: {page['relevance_score']:.2f}")
                
            except Exception as e:
                print(f"Error analyzing {base_url}: {str(e)}")
                continue


if __name__ == "__main__":
    asyncio.run(test_real_site_analysis()) 