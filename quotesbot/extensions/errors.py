import lightbulb
import logging

plugin = lightbulb.Plugin("errors")


@plugin.listener(lightbulb.CommandErrorEvent)
async def errors(event: lightbulb.CommandErrorEvent) -> None:
    exception = event.exception.__cause__ or event.exception
    if isinstance(exception, lightbulb.CommandInvocationError):
        await event.context.respond(
            f"Something went wrong during invocation of command `{event.context.command.name}`."
        )
        raise exception

    elif isinstance(exception, lightbulb.MissingRequiredPermission):
        await event.context.respond(
            f"You do not have permission to run this command. Check `/help {event.context.command.name}` to see what permissions you need."
        )
        logging.debug("User called command they dont have permissions for.")

    elif isinstance(exception, lightbulb.NotOwner):
        await event.context.respond(
            f"You must be owner of the bot to run this command."
        )
        logging.info("User tried to call owner only command.")

    elif isinstance(exception, lightbulb.NotEnoughArguments):
        await event.context.respond(
            f"The command is missing one or more required arguments."
        )
        logging.debug("User called a command without all the required arguments.")

    elif isinstance(exception, lightbulb.CommandNotFound):
        logging.debug("User called a non existant command.")

    elif isinstance(exception, lightbulb.CommandIsOnCooldown):
        await event.context.respond(
            f"Command is on cooldown. Try again in `{exception.retry_after:.2f}` seconds."
        )
        logging.info(
            f"User tried to call {event.context.command.name} while it was on cooldown for {exception.retry_after:.2f} more seconds."
        )

    else:
        raise exception


def load(bot: lightbulb.BotApp):
    bot.add_plugin(plugin)


def unload(bot: lightbulb.BotApp):
    bot.remove_plugin(plugin)
