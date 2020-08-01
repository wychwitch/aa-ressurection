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
    print(f"QuoteBot v{VERSION} " + 'We have logged in as {0.user}'.format(bot))

@bot.command()
async def test(ctx):
    await discordPrint(ctx, "testt aaaa")

async def discordPrint(ctx, str):
    await ctx.send(str)

bot.run(config["token"])

#might be too clunky but i figured could be used for 90% of channel-response commands

