# Quotes-Discord-Bot

This bot manages a "quotes" system for discord servers. Users can put quotes into a channel, the bot records the quotes, and then users can recall a random quote with "+randomquote". Also has a few more smaller features.

To use the bot, first run `pip install -r requirements.txt` to get the required libraries. Next, paste your bot key from the Discord dev portal into bot_token.py. Make sure that you have all of the intents enabled. Finally, run `python3 main.py` to start the bot.

Commands:

+mostquoted 

    Outputs the person with the most quotes attributed to them\n
+randomquote 

    Outputs a random quote from the user-specified quotes channel.
+numquotes (@user)
    
    Outputs the number of quotes that the person mentioned has attributed to them.
+setquoteschannel

    Type this in the channel you wish to be your servers quotes channel. In order to run this command, you must have the role "QuotesBot Admin"
+delquoteschannel 

    Type this in the channel your quotes channel if you wish for it to no longer be a quotes channel. In order to run this command, you must have the role "QuotesBot Admin"
+save

    Will back up a prior quotes channel if you have one. Run it in the server you wish to add to your quotes database. Note that the quotes must be formatted correctly. In order to run this command, you must have the role "QuotesBot Admin"
