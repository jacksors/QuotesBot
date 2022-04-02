import lightbulb
import logging
import hikari
import quotesbot

from quotesbot import DB

plugin = lightbulb.Plugin("Bot Administration")


@plugin.command()
@lightbulb.add_checks(
    lightbulb.checks.has_guild_permissions(hikari.Permissions.MANAGE_CHANNELS)
)
@lightbulb.option(
    name="channel",
    description="#Channel to set as quotes channel",
    type=hikari.GuildChannel,
)
@lightbulb.command(
    name="setquoteschannel",
    description="Set the quotes channel to allow users to view and log quotes",
)
@lightbulb.implements(lightbulb.SlashCommand, lightbulb.PrefixCommand)
async def setquoteschannel(ctx: lightbulb.Context) -> None:
    DB.servers.find_one_and_update(
        {"server_id": ctx.guild_id},
        {"$set": {"channel_id": ctx.options.channel.id}},
    )
    await ctx.respond(f"Quotes channel set to <#{ctx.options.channel.id}>")
    logging.debug(f"Quotes channel set to {ctx.options.channel.id}")


@plugin.command()
@lightbulb.add_checks(
    lightbulb.checks.has_guild_permissions(hikari.Permissions.MANAGE_MESSAGES)
)
@lightbulb.option(name="author", description="@Author of the quote", type=hikari.Member)
@lightbulb.option(name="quote", description="Text of the quote to delete")
@lightbulb.command(name="delquote", description="Delete a quote")
@lightbulb.implements(lightbulb.SlashCommand, lightbulb.PrefixCommand)
async def delquote(ctx: lightbulb.Context) -> None:
    quote = quotesbot.CommandQuote(ctx)
    count = DB.quotes.count_documents(
        {
            "quote": quote.text,
            "author": quote.author.id,
            "server_id": quote.guild_id,
        }
    )
    if count == 0:
        await ctx.respond(f"Could not find any quotes matching {quote}")
    elif count == 1:
        DB.quotes.delete_one(
            {
                "quote": quote.text,
                "author": quote.author.id,
                "server_id": quote.guild_id,
            }
        )
        await ctx.respond(f"Deleted 1 quote.")
    else:
        DB.quotes.delete_many(
            {
                "quote": quote.text,
                "author": quote.author.id,
                "server_id": quote.guild_id,
            }
        )
        await ctx.respond(f"Deleted {count} quotes.")
    logging.debug(f"Deleted {count} matching {quote}")


@plugin.command()
@lightbulb.add_checks(
    lightbulb.checks.has_guild_permissions(hikari.Permissions.MANAGE_GUILD)
)
@lightbulb.command(name="togglementions", description="Turn mentions on/off")
@lightbulb.implements(lightbulb.SlashCommand, lightbulb.PrefixCommand)
async def togglementions(ctx: lightbulb.Context) -> None:
    mentions = DB.servers.find_one({"server_id": ctx.guild_id})["mentions"]
    if mentions:
        DB.servers.update_one(
            {"server_id": ctx.guild_id}, {"$set": {"mentions": False}}
        )
        await ctx.respond("User mentions turned off.")
        logging.debug("User mentions disabled")
    else:
        DB.servers.update_one({"server_id": ctx.guild_id}, {"$set": {"mentions": True}})
        await ctx.respond("User mentions turned on.")
        logging.debug("User mentions enabled")


def load(bot: lightbulb.BotApp):
    bot.add_plugin(plugin)


def unload(bot: lightbulb.BotApp):
    bot.remove_plugin(plugin)
