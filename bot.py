import linecache
import random
import re
import json
import discord
from discord import Game
from discord.ext import commands

from os import path

VERSION = "2.0.0"

# Grab the config variables
with open("json/config.json") as cfg:
    config = json.load(cfg)

with open("json/quotes.json") as qu:
    quotes = json.load(qu)

with open ("json/nsfwQuotes.json") as nsfwdic:
    nsfwQuotes = json.load(nsfwdic)

with open ("json/artQuotes.json") as artdic:
    artQuotes = json.load(artdic)

# Storing people's pings
with open("json/pings.json") as pings_file:
    pings_dict = json.load(pings_file)

# AZ Game Scores
with open("json/az_scores.json") as az_scores_file:
    az_scores = json.load(az_scores_file)

# AZ Game - no point in keeping a file for this
az_game = None
    
# Helper command to update the database
def update_db(database, filename):
    with open(filename, "w") as dtb:
        json.dump(database, dtb, indent=4)

description="""
Basic quote bot.
"""

bot = commands.Bot(commands.when_mentioned_or(config["prefix"]), description=description)

@bot.command(name="quit")
async def bot_quit(ctx):
    """Shut the bot down."""
    print("okay this quit print worked....")
    await discordPrint(ctx,":eyes: :wave:")
    await bot.logout()

@bot.event
async def on_ready():
    print(f"QuoteBot v{VERSION} " + f'We have logged in as {bot.user}')

@bot.command()
async def test(ctx):
    await discordPrint(ctx, "testt aaaa")

#might be too clunky but i figured could be used for 90% of channel-response commands
async def discordPrint(ctx, str):
    await ctx.send(str)

async def send_dm(member: discord.Member, content):
    channel = await member.create_dm()
    await channel.send(content)

@bot.event
async def on_message(message):
    await check_pings(bot, message)
    await bot.process_commands(message)

async def check_pings(bot, message):
    global pings_dict
    lower_text = message.content.lower()
    for user_id, ping_triggers in pings_dict.items():
        print("for loop")
        trigger_regexes = ["\\b"+trigger+"\\b" for trigger in ping_triggers]
        if any([re.search(trigger_regex, lower_text) for trigger_regex in trigger_regexes]):
            print("first if")
            #having problems with this V 
            user = discord.utils.find(lambda m: m.id == user_id, message.channel.guild.members)
            # ping only if user exists or has read permissions
            print("user =="+str(user))
            if (user and message.channel.permissions_for(user).read_messages):
                print("second if")
                await send_dm(user,"#{}: <{}> {}".format(message.channel, message.author.name, message.content))

bot.run(config["token"])

