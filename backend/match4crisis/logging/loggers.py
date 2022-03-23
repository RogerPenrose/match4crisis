import json
import logging

from _collections import defaultdict
from socket import gethostname

import requests

logger = logging.getLogger(__name__)


def DiscordHandlerFactory(webhook_url):
    return DiscordHandler(webhook_url)

class DiscordHandler(logging.Handler):
    def __init__(self, webhook_url):
        self.webhook_url = webhook_url
        logging.Handler.__init__(self)

        notify_users=["everyone"]
        agent=gethostname()

        self._url = webhook_url
        self._agent = agent
        self._notify_users = notify_users
        self._header = self.create_header()
        self.name = ""

    def create_header(self):
        return {
            'User_Agent': self._agent
        }

    def discord_log(self, message):
        request = requests.post(self._url, headers=self._header, data={
            "content": message
            })
        if request.status_code == 404:
            raise requests.exceptions.InvalidURL(
                "Discord WebHook URL returned status 404, is the URL correct?\n"
                + "Response = %s" % request.text
            )

        if not request.ok:
            raise requests.exceptions.HTTPError(
                "Discord WebHook returned status code %s, Message = %s"
                % request.status_code, request.text
            )

    def emit(self, record):
        if self.webhook_url is None or self.webhook_url == "":
            return
        if getattr(record, "logHandlerException", None) == self.__class__:
            return  # This error was caused in this handler, no sense in trying again
        try:
            msg = self.format(record)
            users = '\n'.join(f'<@{user}>' for user in self._notify_users)
            self.write_to_discord("```%s```%s" % (msg, users))
        except Exception:
            self.handleError(record)
