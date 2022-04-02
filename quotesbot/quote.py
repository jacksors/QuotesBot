import re
import hikari
import lightbulb
import logging
from quotesbot import DB, bot
from abc import ABC, abstractmethod


class InvalidAuthor(Exception):
    """Author is invalid."""


class InvalidQuote(Exception):
    """Quote is invalid."""


class Quote:
    """Base class for all quotes."""

    def __init__(self, kwargs) -> None:
        self.text = kwargs["text"]
        self.author = kwargs["author"]

    async def to_quotes_channel(self) -> None:
        try:
            quoteschannel = DB.servers.find_one({"server_id": self.guild_id})[
                "channel_id"
            ]
            if quoteschannel != 0:
                await self.ctx.bot.rest.create_message(
                    channel=quoteschannel,
                    content=f'"{self.text}" - {self.author.mention}',
                )
        except hikari.NotFoundError:
            pass
        except Exception as e:
            raise e

    def __repr__(self) -> str:
        return f"Text: {self.text} | Author_ID: {self.author.id} | Guild_ID: {self.guild_id}"

    def __str__(self) -> str:
        return f'"{self.text}" - {self.author.mention}'


class CommandQuote(Quote):
    """Quotes class to use when quote is generated from application command."""

    def __init__(self, ctx: lightbulb.Context, **kwargs) -> None:
        self.ctx = ctx
        if "text" in kwargs:
            super().__init__(kwargs)
            self.guild_id = ctx.guild_id
        else:
            self.text: str = ctx.options.quote
            self.author: hikari.Member = ctx.options.author
            self.guild_id = ctx.guild_id


class GuildMessageQuote(Quote):
    """Quotes class to use when quote is generated from a message."""

    def __init__(self, ctx: hikari.GuildMessageCreateEvent) -> None:
        self.ctx = ctx
        self.guild_id = ctx.message.guild_id
        self.text = self.__find_text()
        self.author_id = self.__find_author()

    def __find_text(self) -> str:
        try:
            message_fixedquotes = re.sub(
                r"[\u201C\u201D\u201E\u201F\u2033\u2036]", '"', self.ctx.message.content
            )
            text = re.findall(r"\"(.+?)\"", message_fixedquotes)[0]
        except Exception as e:
            raise InvalidQuote(e)
        return text

    def __find_author(self) -> hikari.Member:
        try:
            author_id = int(
                re.sub(r"[^0-9]", "", self.ctx.message.content.split(" ")[-1])
            )
        except Exception as e:
            raise InvalidAuthor(e)
        if author_id == "":
            raise InvalidAuthor("The author could not be found")
        return author_id
