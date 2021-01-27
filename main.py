import discord
import csv
import operator
import re
import time
import os
import pandas as pd
import numpy as np
import random
from random import choice
from random import randrange
from collections import Counter
from discord.ext import commands
from bot_token import *

intents = discord.Intents.default()
intents.members = True
client = commands.Bot(command_prefix = '+', intents=intents)

client.remove_command('help')

@client.event
async def on_ready():
    await client.change_presence(activity=discord.Game('+help'))
    print('Bot is ready.')

@client.event
async def on_message(message):
    df = pd.read_csv('channels.csv')
    if (message.channel.id in df.values and message.author != client.user):
        #copied from copy() below
        #sanitize message input
        history = re.sub(r'[\u201C\u201D\u201E\u201F\u2033\u2036]', '"', message.content)
        history = re.sub(r'[^A-Za-z0-9\s,."-]+', '', history) + "\n"
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
        if ((author != '' and quote != '')):
            #check if the channel's csv exists yet and create one if not
            if not os.path.exists(str(message.channel.id) + '.csv'):
                with open(str(message.channel.id) + '.csv', 'w') as f:
                    df = pd.DataFrame(columns = ['quote','author'])
                    df.to_csv(f, index=False)
            #Define vars for each data table
            df1 = pd.read_csv(str(message.channel.id) + '.csv')
            df2 = pd.DataFrame({'quote':[quote],
                                'author':[author]})
            #Append the new quote (df2) onto the old datatable with all the other quotes (df1)
            df3 = df1.append(df2, ignore_index=True)
            #write the new datatable to file
            df3.to_csv(str(message.channel.id) + '.csv', index=False)
            #Output the result to discord
            await(await message.channel.send("Quote by <@" + author + "> added!")).delete(delay=10)
            return
        elif (message.content == "+delqoteschannel"):
            await client.process_commands(message)
            return
        elif (message.content == "+setquoteschannel"):
            await(await message.channel.send("Channel is already set as the quotes channel!")).delete(delay=10)
            return
        else:
            #If the user sends a message that isnt a quote delete the message, display the warning, and delete the warning after 10 seconds
            await message.delete()
            await(await message.channel.send("<@%s> please only send quotes! If you did send a quote, please format it as \"Quote\" @Author" % message.author.id)).delete(delay=10)
            return
    #Pass on any messages that are irrelevant (arent in the quotes channel or are by this robot)
    await client.process_commands(message)

@client.command()
@commands.has_role('QuotesBot Admin')
async def setquoteschannel(ctx):
    past_channels = pd.read_csv('channels.csv')
    newchannel = pd.DataFrame({'Server_ID': [ctx.message.guild.id], 'Channel_ID': [ctx.message.channel.id]})
    new_list = past_channels.append(newchannel)
    new_list.to_csv('channels.csv', index=False)
    await(await ctx.send('Channel %s set as quotes channel!' % client.get_channel(ctx.message.channel.id).mention)).delete(delay=10)

@client.command()
@commands.has_role('QuotesBot Admin')
async def delquoteschannel(ctx):
    df = pd.read_csv('channels.csv')
    df = df[~df['Channel_ID'].isin([str(ctx.message.channel.id)])]
    df.to_csv('channels.csv', index=False)
    await(await ctx.send('Channel no longer a designated qutoes channel')).delete(delay=10)

@client.command()
@commands.has_role('QuotesBot Admin')
async def save(ctx):
    quote_list = []
    author_list = []
    async for message in ctx.history(limit=1000):
        msg = re.sub(r'[^A-Za-z0-9\s,."-]+', '', message.content)
        quote = re.findall(r'\"(.+?)\"',msg)
        quote = str(quote).strip("[]")
        split_msg = msg.split(" ")
        author = re.sub(r'[^0-9]', '', split_msg[-1])
        if (author != '' and quote != ''):
            quote_list.append(quote)
            author_list.append(author)
    df = pd.DataFrame({'quote': quote_list, 'author': author_list})
    del quote_list,author_list
    df.to_csv(str(ctx.message.channel.id) + '.csv', index=False)
    await(await ctx.send('Channel quotes saved!')).delete(delay=10)
                
@client.command()
async def mostquoted(ctx):
    channeldf = pd.read_csv('channels.csv')
    channelid = channeldf.loc[channeldf['Server_ID'] == ctx.message.guild.id, 'Channel_ID'].values[0]
    df = pd.read_csv(str(channelid) + '.csv', sep=',')
    items_counts = df['author'].value_counts()
    max_item = items_counts.max()
    df = df.author.mode()
    await ctx.send('<@%s> with %s quotes to their name.' % (df.values[0],max_item))

@client.command()
async def randomquote(ctx,*,message=None):
    if (message == None):
        channeldf = pd.read_csv('channels.csv')
        channelid = channeldf.loc[channeldf['Server_ID'] == ctx.message.guild.id, 'Channel_ID'].values[0]
        df = pd.read_csv(str(channelid) + '.csv', sep=',')
        numrows = df.shape[0]
        rownum = random.randint(0,numrows-1)
        author = df.iat[rownum, 1]
        quote = df.iat[rownum, 0]
    else:
        channeldf = pd.read_csv('channels.csv')
        channelid = channeldf.loc[channeldf['Server_ID'] == ctx.message.guild.id, 'Channel_ID'].values[0]
        df = pd.read_csv(str(channelid) + '.csv', sep=',')
         #get the userid that the message sender is querying about (using the same code that the message grabber for the quotes channel uses)
        history = re.sub(r'[^A-Za-z0-9\s,."-]+', '', message) + "\n"
        #Now for finding the author:
        #split the message into a list of individual "words"
        split_history = history.split(" ")
        #Substitute any non numberic characters for blank and grab the last word in the message (this assumes the author is the last word which it must be for this to work)
        author = re.sub(r'[^0-9]', '', split_history[-1])
        df = df.loc[df['author'] == int(author)]
        numrows = df.shape[0]
        rownum = random.randint(0,numrows-1)
        author = df.iat[rownum, 1]
        quote = df.iat[rownum, 0]
    await ctx.send(str(quote) + " - @%s" % ctx.guild.get_member(author))

@client.command()
async def numquotes(ctx,*,message):
    #var message = message content besides command
    #get correct csv file for server (var df)
    channeldf = pd.read_csv('channels.csv')
    channelid = channeldf.loc[channeldf['Server_ID'] == ctx.message.guild.id, 'Channel_ID'].values[0]
    df = pd.read_csv(str(channelid) + '.csv', sep=',')
    #get the userid that the message sender is querying about (using the same code that the message grabber for the quotes channel uses)
    history = re.sub(r'[^A-Za-z0-9\s,."-]+', '', message) + "\n"
    #Now for finding the author:
    #split the message into a list of individual "words"
    split_history = history.split(" ")
    #Substitute any non numberic characters for blank and grab the last word in the message (this assumes the author is the last word which it must be for this to work)
    author = re.sub(r'[^0-9]', '', split_history[-1])
    userquotes = df['author'].value_counts().to_dict()
    userquotes = userquotes[int(author)]
    await ctx.send("@%s has %s quote(s) attributed to them." % (ctx.guild.get_member(int(author)),str(userquotes)))


@client.command()
async def biggestdong(ctx):
    user = choice(ctx.message.channel.guild.members)
    await ctx.send("%s has the biggest dong!" % user.mention)

@client.command()
async def help(ctx):
    embed = discord.Embed(
        title = 'QuotesBot Help',
        colour = discord.Colour.blue()
        
    )
    embed.add_field(name='Quote Formatting', value='All quotes must be formatted as \"quote\" @author, or else they will be rejected by the bot.', inline=False)
    embed.add_field(name='+mostquoted', value='Outputs the person with the most quotes attributed to them.', inline=False)
    embed.add_field(name='+randomquote', value='Outputs a random quote from the user-specified quotes channel.', inline=False)
    embed.add_field(name='+numquotes', value='Type this and @ a user to see how many quotes they have attributed to them.', inline=False)
    embed.add_field(name='+setquoteschannel', value='Type this in the channel you wish to be your servers quotes channel. In order to run this command, you must have the role \"QuotesBot Admin\"', inline=False)
    embed.add_field(name='+delquoteschannel', value='Type this in the channel your quotes channel if you wish for it to no longer be a quotes channel. In order to run this command, you must have the role \"QuotesBot Admin\"', inline=False)
    embed.add_field(name='+save', value='Will back up a prior quotes channel if you have one. Run it in the server you wish to add to your quotes database. Note that the quotes must be formatted correctly. In order to run this command, you must have the role \"QuotesBot Admin\"', inline=False)
    await ctx.send(embed=embed)
    
client.run(BOT_TOKEN)
