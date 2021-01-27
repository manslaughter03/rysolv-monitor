"""

main entrypoint
"""
from threading import Thread
from argparse import ArgumentParser
import os
import logging

from pymongo import MongoClient

from rysolv_monitor.crawler import RysolvCrawler
from rysolv_monitor.database import  RysolvDatabase
from rysolv_monitor.telegram_bot import RysolvBot
from rysolv_monitor.logger import configure_logger

def main() -> None:
    """

    main function
    :return:
    """
    parser = ArgumentParser()
    parser.add_argument("--verbose",
                        help="Set log level to DEBUG",
                        action="store_true",
                        default=os.getenv("VERBOSE"))
    parser.add_argument("--telegram-token",
                        type=str,
                        default=os.getenv("TELEGRAM_TOKEN", ""))
    parser.add_argument("--db-url",
                        type=str,
                        default=os.getenv("DB_URL", "127.0.0.1:27017"))
    parser.add_argument("--db-name",
                        type=str,
                        default=os.getenv("DB_NAME", "rysolv"))
    parsed = parser.parse_args()
    _db_client = MongoClient(f"mongodb://{parsed.db_url}")
    _database = RysolvDatabase(_db_client[parsed.db_name])

    log_level = logging.DEBUG if parsed.verbose else logging.INFO

    bot_logger = configure_logger("bot", log_level)
    bot = RysolvBot(parsed.telegram_token, _database, bot_logger)
#   bot.check_version()
    crawler_logger = configure_logger("crawler", log_level)
    crawler = RysolvCrawler(_database, crawler_logger, sleep_time=30)
    monitor_issue_thread = Thread(target=bot.run_monitor_issue, args=())
    monitor_comment_thread = Thread(target=bot.run_monitor_comment, args=())
    crawler_thread = Thread(target=crawler.run, args=())
    monitor_issue_thread.start()
    monitor_comment_thread.start()
    crawler_thread.start()
    bot.run_telegram_bot()
    monitor_issue_thread.join()
    monitor_comment_thread.join()
    crawler_thread.join()

if __name__ == "__main__":
    main()
