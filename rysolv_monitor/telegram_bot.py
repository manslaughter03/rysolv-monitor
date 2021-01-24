"""

telegram_bot module
"""
from queue import Queue
from datetime import datetime
import re
from typing import List, Optional

from telegram import Update
from telegram.ext import (
    Updater,
    CommandHandler,
)

from .utils import (
    url_from_issue,
    escape,
)
from .types import (
    Issue
)


class RysolvBot:
    """

    RysolvBot class
    """

    UUID_REGEX= r"\b[0-9a-f]{8}\b-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-\b[0-9a-f]{12}\b"
    TELEGRAM_USAGE_COMMANDS = [
        "/register - Sign up for receiving new issue",
        "/unregister - Stop receiving new issue",
        "/watch [ID]... - Watch one or multiple issue modification",
        "/list_watchers - List issue subscription",
        "/delete_watcher [ID]... - Delete issue subscription",
        "/help - Print help message"
    ]
    def __init__(self,
                 queue: Queue,
                 telegram_token: str,
                 database):
        self.updater = Updater(token=telegram_token, use_context=True)
        self.queue = queue
        self.database = database

    def run(self) -> None:
        """

        run bot
        :return:
        """
        self._monitor_issue()

    @staticmethod
    def _find_issue_by_id(issues: List[Issue], _id: str) -> Optional[Issue]: # pylint: disable=unsubscriptable-object
        """

        find issue by id
        :param issues:
        :param _id:
        :return:
        """
        _result = None
        for issue in issues:
            if issue["id"] == _id:
                _result = issue
                break
        return _result

    def _monitor_issue(self):
        while True:
            _issues = self.queue.get()
            for user in self.database.find_users():
                _new_issues = [item for item in _issues
                               if item["createdDate"] > datetime.utcfromtimestamp( \
                                   user["last_update"])]
                for issue in _new_issues:
                    self.send_message(user_id=user["user_id"], text=str(issue))
                self.database.update_user(user["user_id"])
            for watcher in self.database.find_watch_issues():
                issue = self._find_issue_by_id(_issues, watcher["issue_id"])
                if issue["modifiedDate"] > datetime.utcfromtimestamp(watcher["last_update"]):
                    msg = "New modification on issue" \
                          f"[{escape(watcher['issue_id'])}]({url_from_issue(watcher['issue_id'])})"
                    self.send_message(user_id=watcher["user_id"], text=msg)
                self.database.update_watch_issue(watcher["user_id"], watcher["issue_id"])
            self.queue.task_done()

    def send_message(self, user_id: int, text: str) -> None:
        """

        send message
        :param user_id:
        :param text:
        :return:
        """
        self.updater.bot.send_message(chat_id=user_id,
                                      text=text,
                                      parse_mode="MarkdownV2")

    def run_telegram_bot(self):
        """

        run telegram bot
        :return:
        """
        # bot command design
        # /start => start receiving new issue
        # /watch {id} => allow to receive all update on issue
        self.updater.dispatcher.add_handler(CommandHandler("register", self.register))
        self.updater.dispatcher.add_handler(CommandHandler("unregister", self.unregister))
        self.updater.dispatcher.add_handler(CommandHandler("watch", self.watch_issue))
        self.updater.dispatcher.add_handler(CommandHandler("list_watchers", self.list_watch_issue))
        self.updater.dispatcher.add_handler(CommandHandler("delete_watcher",
                                                           self.delete_watch_issue))
        self.updater.dispatcher.add_handler(CommandHandler("help", self.help_bot))

        # Start the Bot
        print("Start telegram bot")
        self.updater.start_polling()

        self.updater.idle()

    def register(self, update: Update, _):
        """

        register handler
        :param update:
        """
        msg = "Hi! You will notified of new issues created on rysolv.com"
        result = self.database.update_user(update.message.from_user.id)
        if result.matched_count:
            msg = "Hi! You are already registered to rysolv notification"
        elif not result.acknowledged:
            msg = "Fail to register :("
        update.message.reply_text(escape(msg), parse_mode="MarkdownV2")

    def unregister(self, update: Update, _):
        """

        unregister handler
        :param update:
        :return:
        """
        result = self.database.delete_user(update.message.from_user.id)
        msg = ""
        if result.deleted_count == 1:
            msg = "Register has been successfully deleted"
        else:
            msg = "Register deletion failed"
        update.message.reply_text(escape(msg), parse_mode="MarkdownV2")

    def help_bot(self, update: Update, _) -> None:
        """

        help bot handler
        :param update:
        :return:
        """
        msg = "*List of available commands:*\n"
        msg += "\n".join(self.TELEGRAM_USAGE_COMMANDS)

        update.message.reply_text(escape(msg), parse_mode="MarkdownV2")

    @classmethod
    def find_all_uuid(cls, text: str) -> List:
        """

        find all uuid from string
        :param text:
        :return:
        """
        return set(re.findall(cls.UUID_REGEX, text))

    def list_watch_issue(self, update: Update, _):
        """

        list watch issue handler
        :param update:
        :return:
        """
        _watch_issues = list(self.database.find_watch_issues())
        msg = "*List of watchers:*\n"

        if _watch_issues:
            msg += "\n".join([rf"\* Issue [{escape(item['issue_id'])}]" \
                              f"({url_from_issue(item['issue_id'])})"
                              for item in _watch_issues])
        else:
            msg = "No watcher found"
        update.message.reply_text(msg, parse_mode="MarkdownV2")

    def delete_watch_issue(self, update: Update, _):
        """

        delete watch issue
        :param update:
        :return:
        """
        _ids = self.find_all_uuid(update.message.text)
        if not _ids:
            update.message.reply_text(escape("Can't find issue to delete"), parse_mode="MarkdownV2")
        for _id in _ids:
            result = self.database.delete_watch_issue(user_id=update.message.from_user.id,
                                                      issue_id=_id)
            msg = ""
            if result.deleted_count == 1:
                msg = f"Watcher ({_id}) has been successfully deleted"
            else:
                msg = f"Watcher ({_id}) deletion failed!"
            update.message.reply_text(escape(msg), parse_mode="MarkdownV2")

    def watch_issue(self, update: Update, _) -> None:
        """

        watch issue handler
        :param update:
        :return:
        """
        _ids = self.find_all_uuid(update.message.text)
        for _id in _ids:
            result = self.database.update_watch_issue(user_id=update.message.from_user.id,
                                                      issue_id=_id)
            msg = ""
            if result.matched_count == 1:
                msg = f"You have already a watcher with id: {_id}"
            elif result.upserted_id:
                msg = f"Watcher ({_id}) has been successfully added"
            else:
                msg = f"Watcher ({_id}) added failed!"
            update.message.reply_text(escape(msg), parse_mode="MarkdownV2")
