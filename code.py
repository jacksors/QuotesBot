import discord
import csv
import operator
import re
import time
import pandas as pd
import numpy as np
import random
from random import choice
from random import randrange
from collections import Counter
from discord.ext import commands

filename = 'quotesusernames.csv'

data = []

intents = discord.Intents.all()
intents.members = True
client = commands.Bot(command_prefix = '+', intents=intents)

client.remove_command('help')

def most_frequent(List): 
    occurence_count = Counter(List) 
    return occurence_count.most_common(1)[0][0]

def load_words():
       print("Loading word list from file...")
       wordlist = list()
       # 'with' can automate finish 'open' and 'close' file
       with open(filename) as f:
            # fetch one line each time, include '\n'
            for line in f:
                # strip '\n', then append it to wordlist
                wordlist.append(line.rstrip('\n'))
       print(" ", len(wordlist), "words loaded.")
       print('\n'.join(wordlist))
       return wordlist

@client.event
async def on_ready():
    await client.change_presence(activity=discord.Game('+help'))
    print('Bot is ready.')

"""@client.event
async def on_command_error(ctx, error):
    error = getattr(error, 'original', error)

    if isinstance(error, commands.CommandNotFound):
        return"""

@client.event
async def on_message(message):
    if (message.channel.id == 776876198231539743 and message.author.id != 799028695368073255):
        with open('quotesusernames.csv', 'a') as f:
            #copied from copy() below
            #sanitize message input
            history = re.sub(r'[^A-Za-z0-9\s,."-]+', '', message.content) + "\n"
            #find part of message within double quotes
            quote = re.findall(r'\"(.+?)\"',history)
            #strip [] from the output of the part of the message within double quotes
            quote = str(quote).strip("[]")
            #Now for finding the author:
            #split the message into a list of individual "words"
            split_history = history.split(" ")
            #Substitute any non numberic characters for blank and grab the last word in the message (this assumes the author is the last word which it must be for this to work)
            author = re.sub(r'[^0-9]', '', split_history[-1])
            #Onto the database interaction using Pandas (pd)
            #Make sure the message included a quote and author
            if (author != '' and quote != ''):
                #Define vars for each data table
                df1 = pd.read_csv('quotes.csv', sep=',')
                df2 = pd.DataFrame({'quotes':[quote],
                                    'author':[author]})
                #Append the new quote (df2) onto the old datatable with all the other quotes (df1)
                newdf = df1.append(df2, ignore_index=True)
                #write the new datatable to file
                newdf.to_csv('quotes.csv', index=False)
                #Output the result to discord
                await message.channel.send("Quote by <@" + author + "> added! Ignore and move to a new channel if your message was not a quote.")
            else:
                #If the user sends a message that isnt a quote delete the message, display the warning, and delete the warning after 10 seconds
                await message.delete()
                await(await message.channel.send("<@%s> please only send quotes! If you did send a quote, please format it so that the author's username is the last word." % message.author.id)).delete(delay=10)
    #Pass on any messages that are irrelevant (arent in the quotes channel or are by this robot)
    await client.process_commands(message)

"""@client.command()
async def copy(ctx):
    with open(filename, 'w') as f:
        async for message in ctx.history(limit=1000):
            history = re.sub(r'[^A-Za-z0-9\s,."-]+', '', message.content) + "\n"
            split_history = history.split(" ")
            regex_split_history = re.sub(r'[^0-9]', '', split_history[-1])
            f.write("{}\n".format(regex_split_history))

    await ctx.send('Done!')"""

"""@client.command()
async def save(ctx):
    with open('quotes.csv', 'a') as f:
        async for message in ctx.history(limit=1000):
            msg = re.sub(r'[^A-Za-z0-9\s,."-]+', '', message.content)
            print('msg sani done')
            id = np.nan
            quote = re.findall(r'\"(.+?)\"',msg)
            quote = str(quote).strip("[]")
            print(quote)
            split_msg = msg.split(" ")
            print('split msg')
            author = re.sub(r'[^0-9]', '', split_msg[-1])
            print('made author')
            csv_writer = csv.writer(f)
            print('defined csv_writer')
            csv_writer.writerow([quote, author])
            print('wrote to csv?')"""
                

@client.command()
async def mostquoted(ctx):
    userlist = load_words()
    while("" in userlist):
        userlist.remove("")
    await ctx.send("<@" + most_frequent(userlist) + "> with " + str(userlist.count(most_frequent(userlist))) + " quotes!")

@client.command()
async def randomquote(ctx):
    df = pd.read_csv('quotes.csv', sep=',')
    numrows = df.shape[0]
    rownum = random.randint(0,numrows)
    author = df.iat[rownum, 1]
    quote = df.iat[rownum, 0]
    await ctx.send(str(quote) + " - <@%s>" % author)

@client.command()
async def biggestdong(ctx):
    user = choice(ctx.message.channel.guild.members)
    await ctx.send("%s has the biggest dong!" % user.mention)

@client.command()
async def help(ctx):
    quoteschannel = client.get_channel(776876198231539743)
    embed = discord.Embed(
        title = 'RoboJackson Help',
        colour = discord.Colour.blue()
        
    )
    embed.add_field(name='+mostquoted', value='Outputs the person with the most quotes attributed to them.', inline=False)
    embed.add_field(name='+randomquote', value='Outputs a random quote from the %s channel.' % quoteschannel.mention, inline=False)
    embed.add_field(name='+biggestdong', value='Outputs the user with the largest dong.', inline=False)

    await ctx.send(embed=embed)
    
client.run('Nzk5MDI4Njk1MzY4MDczMjU1.X_9ndg.SDxJHT8fLa27-nP8xcNXwR6qreE')