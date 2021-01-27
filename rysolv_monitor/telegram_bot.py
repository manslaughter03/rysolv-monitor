"""

telegram_bot module
"""
import re
from typing import List, Optional
from logging import Logger
import os

from telegram import Update
from telegram.ext import (
    Updater,
    CommandHandler,
)

import rysolv_monitor
from rysolv_monitor.database import (
    RysolvDatabase,
    RysolvCollections
)
from rysolv_monitor.utils import (
    url_from_issue,
    escape,
    parse_changelog
)
from rysolv_monitor.types import (
    Issue
)


class RysolvBot:
    """

    RysolvBot class
    """

    UUID_REGEX= r"\b[0-9a-f]{8}\b-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-\b[0-9a-f]{12}\b"
    TELEGRAM_USAGE_COMMANDS = [
        "/register - Sign up for receiving new issue",
        "/start - Sign up for receiving new issue",
        "/unregister - Stop receiving new issue",
        "/watch [ID]... - Watch one or multiple issue modification",
        "/list_watchers - List issue subscription",
        "/delete_watcher [ID]... - Delete issue subscription",
        "/version - Show current version",
        "/help - Print help message"
    ]
    def __init__(self,
                 telegram_token: str,
                 database: RysolvDatabase,
                 logger: Logger):
        self.updater = Updater(token=telegram_token, use_context=True)
        self.database = database
        self.logger = logger

    def check_version(self) -> None:
        """

        run bot
        :return:
        """
        _last_version = self.database.find_last_version()
        if not _last_version or _last_version != rysolv_monitor.__version__:
            _filepath = os.path.join(os.path.dirname(rysolv_monitor.__file__),
                                     "..",
                                     "changelog",
                                     "CHANGELOG.md")
            _change_log = parse_changelog(_filepath)
            if rysolv_monitor.__version__ in _change_log:
                msg = f"New version {rysolv_monitor.__version__}\n" \
                      f"{_change_log[rysolv_monitor.__version__]}"
                self.notify_users(escape(msg), self.database.find_users())
                _data_set = {"version": rysolv_monitor.__version__,
                             "text": _change_log[rysolv_monitor.__version__]}
                _result = self.database.write_changelog(_data_set)
#               if _result.updated_count == 0:
#                   self.logger.warning("Fail to add new changelog")

    def run_monitor_issue(self) -> None:
        """

        run monitoring issue
        :return:
        """
        self.logger.info("Run monitor issue")
        self._monitor_issue()

    def run_monitor_comment(self) -> None:
        """

        run monitor comment
        :return:
        """
        self.logger.info("Run monitor comment")
        self._monitor_comment()

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

    def _monitor_comment(self) -> None:
        """

        monitor comment
        :return:
        """
        pipeline = [{"$match": {"operationType": {"$in": ["insert", "update"]}}}]
        _collection = self.database.collections[RysolvCollections.Comments.name]
        with _collection.watch(pipeline, full_document="updateLookup") as stream:
            for change in stream:
                self.logger.info("Change on Comments collection operationType: %s",
                                 change["operationType"])
                _comment = Issue(change["fullDocument"])
                msg = "New modification on issue " \
                      f"[{escape(_comment['issue_id'])}]({url_from_issue(_comment['issue_id'])})"
                if change["operationType"] == "insert":
                    self.notify_users(msg, self.database.find_users())
                elif change["operationType"] == "update":
                    _filter = {"issue_id": _comment['issue_id']}
                    self.notify_users(msg,
                                      self.database.find_watch_issues(_filter))

    def _monitor_issue(self) -> None:
        """

        monitor issue
        :return:
        """
        pipeline = [{"$match": {"operationType": {"$in": ["insert", "update"]}}}]
        _collection = self.database.collections[RysolvCollections.Issues.name]
        with _collection.watch(pipeline, full_document="updateLookup") as stream:
            for change in stream:
                self.logger.info("operationType: %s", change["operationType"])
                _issue = Issue(change["fullDocument"])
                if change["operationType"] == "insert":
                    self.notify_users(str(_issue), self.database.find_users())
                elif change["operationType"] == "update":
                    msg = "New modification on issue " \
                          f"[{escape(_issue['id'])}]({url_from_issue(_issue['id'])})"
                    _filter = {"issue_id": _issue["id"]}
                    self.notify_users(msg,
                                      self.database.find_watch_issues(_filter))

    def notify_users(self, msg: str, users: List) -> None:
        """

        notify users
        :param msg:
        :param users
        :return:
        """
        for user in users:
            self.send_message(user_id=user["user_id"], text=msg)

    def send_message(self, user_id: int, text: str) -> None:
        """

        send message
        :param user_id:
        :param text:
        :return:
        """
        self.logger.debug("Send message %s %s", user_id, text)
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
        self.logger.info("Init all commands handler")
        self.updater.dispatcher.add_handler(CommandHandler("register", self.register))
        self.updater.dispatcher.add_handler(CommandHandler("start", self.register))
        self.updater.dispatcher.add_handler(CommandHandler("unregister", self.unregister))
        self.updater.dispatcher.add_handler(CommandHandler("watch", self.watch_issue))
        self.updater.dispatcher.add_handler(CommandHandler("list_watchers", self.list_watch_issue))
        self.updater.dispatcher.add_handler(CommandHandler("delete_watcher",
                                                           self.delete_watch_issue))
#       self.updater.dispatcher.add_handler(CommandHandler("comments", self.get_comments_by_issue))
        self.updater.dispatcher.add_handler(CommandHandler("version", self.get_version))
        self.updater.dispatcher.add_handler(CommandHandler("help", self.help_bot))

        # Start the Bot
        self.logger.info("Start telegram bot")
        self.updater.start_polling()

        self.updater.idle()

    def register(self, update: Update, _):
        """

        register handler
        :param update:
        """
        self.logger.info("/register -> Register new user")
        msg = "Hi! You will notified of new issues created on rysolv.com"
        result = self.database.update_user(update.message.from_user.id)
        if result.matched_count:
            msg = "Hi! You are already registered to rysolv notification"
        elif not result.acknowledged:
            msg = "Fail to register :("
        self.send_message(update.message.from_user.id, escape(msg))

    def unregister(self, update: Update, _):
        """

        unregister handler
        :param update:
        :return:
        """
        self.logger.info("/unregister -> Unregister user")
        result = self.database.delete_user(update.message.from_user.id)
        msg = ""
        if result.deleted_count == 1:
            msg = "Register has been successfully deleted"
        else:
            msg = "Register deletion failed"
        update.message.reply_text(escape(msg), parse_mode="MarkdownV2")

    @staticmethod
    def get_version(update: Update, _) -> None:
        """

        help bot handler
        :param update:
        :return:
        """
        msg = f"Current version {rysolv_monitor.__version__}"
        update.message.reply_text(escape(msg), parse_mode="MarkdownV2")

    def help_bot(self, update: Update, _) -> None:
        """

        help bot handler
        :param update:
        :return:
        """
        self.logger.info("/help -> User ask for help")
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

    def get_comments_by_issue(self, update: Update, _) -> None:
        """

        Get comments of issue
        :param update:
        :return:
        """
        _ids = self.find_all_uuid(update.message.text)
        if not _ids:
            update.message.reply_text(escape("Can't find issue"), parse_mode="MarkdownV2")
            return
        _id = next(iter(_ids))
        self.logger.info("/comments -> A user ask to get comments of issues %s", _id)
        _comments = self.database.find_comments({"issue_id": _id})
        msg = rf"*List of comment of {escape(_id)}\:*\n"
        for _comment in _comments:
            msg += "\n".join([escape(item["body"])
                              for item in _comment["comments"]])
#       else:
#           msg = "No comment found"
        self.send_message(update.message.from_user.id, msg)

    def watch_issue(self, update: Update, _) -> None:
        """

        watch issue handler
        :param update:
        :return:
        """
        _ids = self.find_all_uuid(update.message.text)
        self.logger.info("/watch -> A user ask to watch issues {_ids}")
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
