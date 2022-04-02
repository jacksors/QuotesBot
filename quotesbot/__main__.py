"""QuotesBot Main"""
import os
from quotesbot.bot import bot

if os.name != "nt":
    import uvloop

    uvloop.install()

if __name__ == "__main__":
    bot.load_extensions_from("./quotesbot/extensions")
    bot.run()
