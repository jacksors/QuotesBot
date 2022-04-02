import hikari
import lightbulb
import logging
from quotesbot import DB

plugin = lightbulb.Plugin("serverinit")


@plugin.listener(hikari.events.GuildJoinEvent)
async def init_server(ctx: hikari.events.GuildJoinEvent) -> None:
    DB.servers.insert_one(
        {"server_id": ctx.guild_id, "channel_id": 0, "mentions": True}
    )
    logging.info(f"Bot joined and initialized {ctx.guild.name}")


@plugin.listener(hikari.events.GuildLeaveEvent)
async def leave_server(ctx: hikari.events.GuildLeaveEvent) -> None:
    DB.servers.delete_many({"server_id": ctx.guild_id})
    DB.quotes.delete_many({"server_id": ctx.guild_id})
    logging.info(f"Bot left and deleted {ctx.guild_id}")


def load(bot: lightbulb.BotApp):
    bot.add_plugin(plugin)


def unload(bot: lightbulb.BotApp):
    bot.remove_plugin(plugin)
