"""Main module for running the crawler."""
import json
import logging
from datetime import datetime
from pathlib import Path

from .nitori import NitoriCrawler

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main() -> None:
    """Run the Nitori crawler."""
    storage_dir = Path("data/nitori")
    storage_dir.mkdir(parents=True, exist_ok=True)

    logger.info("Starting Nitori crawler...")
    with NitoriCrawler(storage_dir=storage_dir) as crawler:
        data = crawler.crawl()

        # Save the crawled data
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = storage_dir / f"nitori_data_{timestamp}.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        logger.info(f"Data saved to {output_file}")


if __name__ == "__main__":
    main()
