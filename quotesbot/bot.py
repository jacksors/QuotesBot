"""Bot and database"""
import lightbulb
from quotesbot import settings
from pymongo import MongoClient
import hikari
import logging


bot = lightbulb.BotApp(
    token=settings.BOT_TOKEN, prefix="+", help_slash_command=True
)


class DB:
    _db = MongoClient(settings.MONGO_URL)[settings.MONGO_DB]
    quotes = _db[settings.QUOTES_COLLECTION]
    servers = _db[settings.SERVERS_COLLECTION]


async def mention(ctx: lightbulb.Context, usrid: int) -> str:
    mention = DB.servers.find_one({"server_id": ctx.guild_id})["mentions"]
    if mention:
        msg = f"<@{usrid}>"
        return msg
    else:
        user = ctx.bot.cache.get_user(usrid)
        if user == None:
            user = await ctx.bot.rest.fetch_user(usrid)
            logging.debug("Fetching user from discord...")
        msg = f"@{user.username}#{user.discriminator}"
        return msg


@bot.listen(lightbulb.LightbulbStartedEvent)
async def set_presence(event: lightbulb.LightbulbStartedEvent):
    await bot.update_presence(
        status=hikari.Status.ONLINE,
        activity=hikari.Activity(
            name="/help (+help)", type=hikari.ActivityType.LISTENING
        ),
    )
    logging.info("Presence set")


@bot.command
@lightbulb.add_checks(lightbulb.checks.owner_only)
@lightbulb.option(name="extension", description="Extension to load")
@lightbulb.command(
    name="load", description="Load an extension", guilds=[settings.CONFIG_GUILD]
)
@lightbulb.implements(lightbulb.SlashCommand, lightbulb.PrefixCommand)
async def load(ctx: lightbulb.Context) -> None:
    try:
        bot.load_extensions(f"quotesbot.extensions.{ctx.options.extension}")
        await ctx.respond(f"`{ctx.options.extension}` loaded.")
    except lightbulb.errors.ExtensionAlreadyLoaded:
        await ctx.respond(f"`{ctx.options.extension}` already loaded!")
        logging.debug(
            f"Tried to load module {ctx.options.extension} but it was already loaded."
        )


@bot.command
@lightbulb.add_checks(lightbulb.checks.owner_only)
@lightbulb.option(name="extension", description="Extension to load")
@lightbulb.command(
    name="unload", description="Unload an extension", guilds=[settings.CONFIG_GUILD]
)
@lightbulb.implements(lightbulb.SlashCommand, lightbulb.PrefixCommand)
async def unload(ctx: lightbulb.Context) -> None:
    try:
        bot.unload_extensions(f"quotesbot.extensions.{ctx.options.extension}")
        await ctx.respond(f"`{ctx.options.extension}` unloaded.")
    except lightbulb.errors.ExtensionNotLoaded:
        await ctx.respond(f"`{ctx.options.extension}` not loaded!")
        logging.debug(
            f"Tried to unload module {ctx.options.extension} but it was not loaded."
        )


@bot.command
@lightbulb.add_checks(lightbulb.owner_only)
@lightbulb.option(name="extension", description="Extension to load")
@lightbulb.command(
    name="reload", description="Reload an extension", guilds=[settings.CONFIG_GUILD]
)
@lightbulb.implements(lightbulb.SlashCommand, lightbulb.PrefixCommand)
async def reload(ctx: lightbulb.Context) -> None:
    try:
        bot.reload_extensions(f"quotesbot.extensions.{ctx.options.extension}")
        await ctx.respond(f"`{ctx.options.extension}` reloaded.")
    except lightbulb.errors.ExtensionNotLoaded:
        await ctx.respond(f"`{ctx.options.extension}` not loaded!")
        logging.debug(
            f"Tried to reload module {ctx.options.extension} but it was not loaded."
        )
