import lightbulb
import hikari


class CustomHelp(lightbulb.BaseHelpCommand):
    async def send_bot_help(self, ctx: lightbulb.Context):
        embed = hikari.Embed(title="QuotesBot")
        embed.add_field(
            name="Get started",
            value="Start by setting a channel for quotes to be added to by running `/setquoteschannel` and add a quote by sending a message to that channel or using `/quote`!\n\nYou may view more specific help on a command using `/help [command]`, but here is a quick list:\n`/quote`\n`/mostquoted`\n`/randomquote`\n`/numquotes`\n`/delquote` (requires Permissions -> Manage Messages)\n`/setquoteschannel` (requires Permissions -> Manage Channels)\n`/togglementions` (requires Permissions -> Manage Server)",
        )
        embed.add_field(
            name="Formatting quotes",
            value='All quotes placed into the quotes channel must be formatted as `"quote" @author`, including the quotation marks, in order to be read by the bot. Otherwise they will be deleted from the channel.',
        )
        embed.add_field(
            name="A note on slash commands",
            value="All of the commands in this help wil be referred to as `/` commands, however all of them may be used in the same way with the `+` prefix if you prefer. Just be careful doing this, as some fields by some commands require, for example, that someone be @tted instead of just named. **If you invited the bot to your server before ~March 30 2022, you likely will not have slash commands enabled. You can reinvite it [here](https://discord.com/api/oauth2/authorize?client_id=799028695368073255&permissions=11328&scope=bot%20applications.commands) to enable them.** This will not affect any quotes you already have.",
        )
        embed.add_field(
            name="Right click -> Apps -> Add to Quotes",
            value="If slash commands are enabled for you, you can right click a message, choose apps, and choose Add to Quotes. This will log the message as a quote by the user who sent the message. ",
        )

        await ctx.respond(embed=embed)

    async def send_plugin_help(self, ctx: lightbulb.Context, plugin: lightbulb.Plugin):
        await self.object_not_found(ctx, plugin)

    async def send_command_help(
        self, ctx: lightbulb.Context, command: lightbulb.Command
    ):
        if command.name == "quote":
            embed = hikari.Embed(title="`/quote [text] [@author]`")
            embed.add_field(
                name="Description",
                value='Used to quote someone without typing it in the quotes channel. Allows you to save quotes without a designated quotes channel. If you do have one, the quotes will be placed in the channel by the bot. The text field does not need quotes, so for example if trying to instert a quote that said "howdy" by @QuotesBot, use `/quote howdy @QuotesBot`.',
            )
            await ctx.respond(embed=embed)
        elif command.name == "mostquoted":
            embed = hikari.Embed(title="`/mostquoted`")
            embed.add_field(
                name="Description",
                value="Returns the user with the most quotes and the number of quotes they have attributed to them.",
            )
            await ctx.respond(embed=embed)
        elif command.name == "randomquote":
            embed = hikari.Embed(title="`/randomquote (optional: @user)`")
            embed.add_field(
                name="Description",
                value="Returns a random quote from your servers quotes database. Optionally, mention a user to get a random quote authored by them.",
            )
            await ctx.respond(embed=embed)
        elif command.name == "numquotes":
            embed = hikari.Embed(title="`/numquotes [@user]`")
            embed.add_field(
                name="Description",
                value="Returns the number of quotes a user has attributed to them.",
            )
            await ctx.respond(embed=embed)
        elif command.name == "setquoteschannel":
            embed = hikari.Embed(title="`/setquoteschannel [#channel]`")
            embed.add_field(
                name="Description",
                value="Sets the designated quotes channel to the mentioned channel. The user running this command must have channel management permissions enabled.",
            )
            await ctx.respond(embed=embed)
        elif command.name == "delquote":
            embed = hikari.Embed(title="`/delquote [text] [@author]`")
            embed.add_field(
                name="Description",
                value="Delete a quote from the database, used similarly to `/quote`. The text field does not need quotes, and the quote must match exactly to how it is stored for the bot to find and delete it. The person running this command must have manage message permissions enabled.\n\nNote that this will not delete the message in the quotes channel, only from the database.",
            )
            await ctx.respond(embed=embed)
        elif command.name == "togglementions":
            embed = hikari.Embed(title="`/togglementions`")
            embed.add_field(
                name="Description",
                value="Toggles whether a the author of the quote is mentioned or not when randomquote and numquotes are run. On by default, but turn you may turn off to avoid excessive mentions in large servers. In order to run this command, you must have manage server permissions enabled.",
            )
            await ctx.respond(embed=embed)
        else:
            self.object_not_found(ctx, command)

    async def send_group_help(self, ctx: lightbulb.Context, group):
        await self.object_not_found(ctx, group)

    async def object_not_found(self, ctx: lightbulb.Context, obj):
        await ctx.respond(
            f"Help for `{obj}` not found. Use `/help` to see a list of commands."
        )


def load(bot):
    bot.d.old_help_command = bot.help_command
    bot.help_command = CustomHelp(bot)


def unload(bot):
    bot.help_command = bot.d.old_help_command
    del bot.d.old_help_command
