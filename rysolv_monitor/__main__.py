"""

main entrypoint
"""
from queue import Queue
from threading import Thread
from argparse import ArgumentParser
import os

from pymongo import MongoClient

from rysolv_monitor import (
    RysolvBot,
    RysolvCrawler,
    RysolvDatabase
)

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

    queue = Queue()
    bot = RysolvBot(queue, parsed.telegram_token, _database)
    crawler = RysolvCrawler(queue, sleep_time=30)
    bot_thread = Thread(target=bot.run, args=())
    crawler_thread = Thread(target=crawler.run, args=())
    bot_thread.start()
    crawler_thread.start()
    print("All thread start")
    bot.run_telegram_bot()
    bot_thread.join()
    crawler_thread.join()

if __name__ == "__main__":
    main()
