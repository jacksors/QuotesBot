from __future__ import annotations
import lightbulb
import hikari
import logging
import quotesbot
import asyncio
from quotesbot import DB


plugin = lightbulb.Plugin("Quotes")


@plugin.listener(hikari.events.GuildMessageCreateEvent)
async def log_quote(message: hikari.events.GuildMessageCreateEvent) -> None:
    if (
        message.message.channel_id
        == DB.servers.find_one({"server_id": message.message.guild_id})["channel_id"]
    ):
        if message.author.is_bot and not message.content.startswith('"'):
            await asyncio.sleep(30)
            await message.message.delete()
        elif not message.author.is_bot:
            try:
                quote = quotesbot.GuildMessageQuote(message)
                DB.quotes.insert_one(
                    {
                        "quote": quote.text,
                        "author": quote.author_id,
                        "server_id": quote.guild_id,
                    }
                )
                logging.debug(f"Quote {quote.text} - {quote.author_id} inserted")
                await message.message.add_reaction("✅")
            except quotesbot.InvalidAuthor:
                await message.message.delete()
                await message.message.respond(
                    ":bangbang: Author could not be found! Please check `/help` for formatting instructions."
                )
                logging.debug(f"Invalid author from message {message.message.content}")
            except quotesbot.InvalidQuote:
                await message.message.delete()
                await message.message.respond(
                    ":bangbang: Quote text could not be found! Please check `/help` for formatting instructions."
                )
                logging.debug(
                    f"Invalid quote text from message {message.message.content}"
                )


@plugin.command()
@lightbulb.option(name="author", description="@Author of the quote", type=hikari.Member)
@lightbulb.option(
    name="quote",
    description="The quote to log",
)
@lightbulb.command(name="quote", description="Log a new quote")
@lightbulb.implements(lightbulb.SlashCommand, lightbulb.PrefixCommand)
async def quote(ctx: lightbulb.SlashContext | lightbulb.PrefixContext) -> None:
    """Log a quote into the database without putting it into the quotes channel
    Usage: /quote [quote goes here] [@author]"""
    quote = quotesbot.CommandQuote(ctx)
    DB.quotes.insert_one(
        {"quote": quote.text, "author": quote.author.id, "server_id": quote.guild_id}
    )
    await ctx.respond(f"Added quote by {await quotesbot.mention(ctx, quote.author.id)}")
    await quote.to_quotes_channel()


@plugin.command()
@lightbulb.command(name="mostquoted", description="Who has the most quotes?")
@lightbulb.implements(lightbulb.SlashCommand, lightbulb.PrefixCommand)
async def mostquoted(ctx: lightbulb.Context) -> None:
    """Command to display who has the most quotes attributed to them.
    Usage: /mostquoted"""
    if DB.quotes.count_documents({"server_id": ctx.guild_id}, limit=1) != 0:
        maxauthor = DB.quotes.aggregate(
            [
                {"$match": {"server_id": ctx.guild_id}},
                {"$unwind": "$author"},
                {"$sortByCount": "$author"},
            ]
        )
        maxauthor = list(maxauthor)[0]
        await ctx.respond(
            f"The user with the most quotes is {await quotesbot.mention(ctx, maxauthor['_id'])} with {maxauthor['count']} quotes to their name."
        )
    else:
        await ctx.respond(
            "This server doesn't have any quotes! Use `/help` to see how to add one."
        )


@plugin.command()
@lightbulb.option(
    name="author",
    description="Whose quote do you want to see?",
    required=False,
    type=hikari.Member,
)
@lightbulb.command(
    name="randomquote",
    description="Retrieve a random quote, optionally by a specific author",
)
@lightbulb.implements(lightbulb.SlashCommand, lightbulb.PrefixCommand)
async def randomquote(ctx: lightbulb.Context) -> None:
    """Command to display a random quote from either any user or a specific user.
    Usage: /randomquote (optional:@author)"""
    try:
        if ctx.options.author == None:
            document = DB.quotes.aggregate(
                [{"$match": {"server_id": ctx.guild_id}}, {"$sample": {"size": 1}}]
            )
            document = list(document)[0]
        else:
            document = DB.quotes.aggregate(
                [
                    {
                        "$match": {
                            "server_id": ctx.guild_id,
                            "author": ctx.options.author.id,
                        }
                    },
                    {"$sample": {"size": 1}},
                ]
            )
            document = list(document)[0]
        await ctx.respond(
            f"\"{document['quote']}\" - {await quotesbot.mention(ctx, document['author'])}"
        )
    except IndexError:
        logging.debug("Randomquote attempted in server with no quotes")
        await ctx.respond(
            f"Either this server or the author you mentioned does not have any quotes."
        )


@plugin.command()
@lightbulb.option(name="user", description="Tag a user!", type=hikari.Member)
@lightbulb.command(name="numquotes", description="View the number of quotes a user has")
@lightbulb.implements(lightbulb.SlashCommand, lightbulb.PrefixCommand)
async def numquotes(ctx: lightbulb.Context) -> None:
    try:
        count = DB.quotes.count_documents(
            {"author": ctx.options.user.id, "server_id": ctx.guild_id}
        )
        if count == 1:
            await ctx.respond(
                f"{await quotesbot.mention(ctx, ctx.options.user.id)} has 1 quote attributed to them."
        )
        else:
            await ctx.respond(
                f"{await quotesbot.mention(ctx, ctx.options.user.id)} has {count} quotes attributed to them."
        )
    except TypeError:
        logging.debug("User attempted numquotes in a server with no quotes")
        await ctx.respond("This server does not have any quotes.")


@plugin.command()
@lightbulb.command(name="Add to Quotes", description="")
@lightbulb.implements(lightbulb.MessageCommand)
async def quotemessage(ctx: lightbulb.MessageContext) -> None:
    author = ctx.options.target.author
    text = ctx.options.target.content
    quote = quotesbot.CommandQuote(ctx, text=text, author=author)
    if isinstance(text, str):
        DB.quotes.insert_one(
            {"quote": text, "author": author.id, "server_id": ctx.guild_id}
        )
        await ctx.respond(
            f"Message by {await quotesbot.mention(ctx, author)} added to quotes."
        )
        await quote.to_quotes_channel()
    else:
        await ctx.respond(f"Could not parse any text from the message!")


def load(bot: lightbulb.BotApp):
    bot.add_plugin(plugin)


def unload(bot: lightbulb.BotApp):
    bot.remove_plugin(plugin)
