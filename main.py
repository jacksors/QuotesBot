import discord
import csv
import operator
import re
import time
import os
import numpy as np
import random
import pymongo
from pymongo import MongoClient
from topggapi import setup
from random import choice
from random import randrange
from collections import Counter
from discord.ext import commands
from discord.ext.commands import MissingPermissions
from bot_token import *

intents = discord.Intents.default()
intents.guilds = True
intents.members = True
client = commands.Bot(command_prefix = '+', intents=intents)

client.remove_command('help')

cluster = MongoClient('')
db = cluster['discordbot']

def mention(ctx, usrid):
    collection = db['servers']
    results = collection.find_one({"server_id":ctx.message.guild.id})
    mention = results['mentions']
    if mention == True:
        msg = '<@' + str(usrid) + '>'
        return msg
    else:
        msg = '@' + str(ctx.guild.get_member(usrid))
        return msg

@client.event
async def on_ready():
    await client.change_presence(activity=discord.Game('+help'))
    setup(client)
    print('Bot is ready.')

@client.event
async def on_guild_join(guild):
    f = open('serverlist.txt', 'a')
    f.write(guild.name + '\n')
    f.close
    print('Joined %s' % guild.name)

@client.event
async def on_command_error(ctx, error):
   if isinstance(error, commands.MissingRequiredArgument):
       print("User tried a command without all required arguments")
       await(await ctx.send('Missing required argument.')).delete(delay=10)
   if isinstance(error, MissingPermissions):
       print("User without elevated permissions tried a command that requires them")
       await(await ctx.send('You must have the role QuotesBot Admin to run this command.')).delete(delay=10)
   else:
       print(error)

@client.event
async def on_message(message):
    collection = db['servers']
    if (collection.count_documents({ 'channel_id':message.channel.id }, limit = 1) != 0 and message.author != client.user):
        #copied from copy() below
        #sanitize message input
        history = re.sub(r'[\u201C\u201D\u201E\u201F\u2033\u2036]', '"', message.content)
        history = re.sub(r'[^A-Za-z0-9\s,.?!:;()@#$%^&*_+-=<>"-]+', '', history) + "\n"
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
            collection = db['quotes']
            collection.insert_one({'quote':quote, 'author':int(author), 'channel_id':message.channel.id, 'server_id':message.guild.id})
            await(await message.channel.send("Quote by <@" + author + "> added!")).delete(delay=10)
            return
        elif (message.content == "+setquoteschannel"):
            await message.delete()
            await(await message.channel.send("Channel is already set as the quotes channel!")).delete(delay=10)
            return
        elif (message.content == "+delquoteschannel"):
            await client.process_commands(message)
            return
        elif (message.content.startswith("+")):
            await message.delete()
            await(await message.channel.send("<@%s> please do not send commands in the quotes channel!" % message.author.id)).delete(delay=10)
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
    collection = db['servers']
    if collection.count_documents({ 'server_id':ctx.message.guild.id }, limit = 1) != 0:
        await(await ctx.send('Your server already has a quotes channel!')).delete(delay=10)
        print(True)
    else:
        collection.insert_one({'server_id': int(ctx.message.guild.id), 'channel_id': int(ctx.message.channel.id), 'mentions': True})
        await(await ctx.send('Channel %s set as quotes channel!' % client.get_channel(ctx.message.channel.id).mention)).delete(delay=10)
        print(False)

@client.command()
@commands.has_role('QuotesBot Admin')
async def delquoteschannel(ctx,*, message=None):
    if message == 'understood':
        collection = db['servers']
        collection.delete_many({ 'server_id':ctx.message.guild.id })
        collection = db['quotes']
        collection.delete_many({ 'server_id':ctx.message.guild.id })
        await ctx.send('Your server no longer has a designated quotes channel and all previous quotes have been erased from the database.')
    else:
        await ctx.send('WARNING! This command will delete all of your quotes from the database. The quotes will remain in your quotes channel, but they will not be recallable through any of the commands this bot provides. In order to run this command, you must type `+delquoteschannel understood`')

@client.command()
async def mostquoted(ctx):
    collection = db['quotes']
    if collection.count_documents({ 'server_id':ctx.message.guild.id }, limit = 1) != 0:
        maxauthor = collection.aggregate( [{ '$match': {'server_id':int(ctx.message.guild.id)}}, { "$unwind": "$author" }, { "$sortByCount": "$author" }] )
        maxauthor = list(maxauthor)[0]
        max_item_count = maxauthor['count']
        author = maxauthor['_id']
        await ctx.send('%s with %s quotes to their name.' % (mention(ctx, author),max_item_count))
    else:
        print('Usr attempted +mostquoted in srvr with no quotes')
        await(await ctx.send('This server does not have any quotes.')).delete(delay=10)

@client.command()
async def randomquote(ctx,*,message=None):
    collection = db['quotes']
    try:
        if (message == None):
            document = collection.aggregate([{ '$match': {'server_id':int(ctx.message.guild.id)}},{ '$sample': { 'size': 1 } }])
            document = list(document)[0]
        else:
            #get the userid that the message sender is querying about (using the same code that the message grabber for the quotes channel uses)
            history = re.sub(r'[^A-Za-z0-9\s,."-]+', '', message) + "\n"
            #Now for finding the author:
            #split the message into a list of individual "words"
            split_history = history.split(" ")
            #Substitute any non numberic characters for blank and grab the last word in the message (this assumes the author is the last word which it must be for this to work)
            author = re.sub(r'[^0-9]', '', split_history[-1])
            if author == '':
                await(await ctx.send('<@%s> not a valid author!' % ctx.author.id)).delete(delay=10)
                return
            document = collection.aggregate([{ '$match': {'server_id':int(ctx.message.guild.id)}},{ '$match': {'author':int(author)}},{ '$sample': { 'size': 1 } }])
            document = list(document)[0]
        await ctx.send(document['quote'] + " - %s" % mention(ctx, document['author']))
    except IndexError:
        print('User attempted +randomquote in server with no quotes')
        await ctx.send('Either this server or the author you mentioned does not have any quotes.')

@client.command()
async def numquotes(ctx,*,message):
    try:
        collection = db['quotes']
        #get the userid that the message sender is querying about (using the same code that the message grabber for the quotes channel uses)
        history = re.sub(r'[^A-Za-z0-9\s,."-]+', '', message) + "\n"
        #Now for finding the author:
        #split the message into a list of individual "words"
        split_history = history.split(" ")
        #Substitute any non numberic characters for blank and grab the last word in the message (this assumes the author is the last word which it must be for this to work)
        author = re.sub(r'[^0-9]', '', split_history[-1])
        count = collection.count_documents( {'author':int(author),'server_id':ctx.message.guild.id} )
        await ctx.send("%s has %s quote(s) attributed to them." % (mention(ctx, author),str(count)))
    except TypeError:
        print('User attempted +numquotes in server with no quotes')
        await ctx.send('This server does not have any quotes.')

@client.command()
@commands.has_role('QuotesBot Admin')
async def togglementions(ctx):
    collection = db['servers']
    mentions = collection.find_one({'server_id':ctx.message.guild.id})
    if mentions['mentions'] == True:
        collection.update_one({'server_id':ctx.message.guild.id},{'$set' : {'mentions':False}})
        await ctx.send('User mentions turned off.')
    else:
        collection.update_one({'server_id':ctx.message.guild.id},{'$set' : {'mentions':True}})
        await ctx.send('User mentions turned on.')

@client.command()
async def help(ctx):
    embed = discord.Embed(
        title = 'QuotesBot Help',
        colour = discord.Colour.blue()
        
    )
    embed.add_field(name='Quote Formatting', value='All quotes must be formatted as \"quote\" @author, or else they will be rejected by the bot.', inline=False)
    embed.add_field(name='+mostquoted', value='Outputs the person with the most quotes attributed to them.', inline=False)
    embed.add_field(name='+randomquote (optional: @user)', value='Outputs a random quote from the user-specified quotes channel. Optionally, mention a user to get a random quote attributed to them.   ', inline=False)
    embed.add_field(name='+numquotes @user', value='Type this and @ a user to see how many quotes they have attributed to them.', inline=False)
    embed.add_field(name='+setquoteschannel', value='Type this in the channel you wish to be your servers quotes channel. In order to run this command, you must have the role \"QuotesBot Admin\"', inline=False)
    embed.add_field(name='+delquoteschannel', value='Type this in the channel your quotes channel if you wish for it to no longer be a quotes channel. In order to run this command, you must have the role \"QuotesBot Admin\"', inline=False)
    embed.add_field(name='+togglementions', value='Toggles whether a the author of the quote is mentioned or not when randomquote and numquotes are run. On by default, but turn off to avoid excessive mentions in large servers. In order to run this command, you must have the role \"QuotesBot Admin\"', inline=False)
    embed.add_field(name='Links', value='[Github](https://github.com/jacksors/Quotes-Discord-Bot) | [Support Server](https://discord.gg/DmYw7CbXfT) | [Top.gg](https://top.gg/bot/799028695368073255)', inline=False)
    embed.set_footer(text="QuotesBot by @jackson#1001")
    await ctx.send(embed=embed)
    
client.run(BOT_TOKEN)
