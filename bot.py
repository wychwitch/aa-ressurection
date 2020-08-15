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
    with open("json/"+filename, "w") as dtb:
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
        trigger_regexes = ["\\b"+trigger+"\\b" for trigger in ping_triggers]
        if any([re.search(trigger_regex, lower_text) for trigger_regex in trigger_regexes]):
            print("first if")
            #having problems with this V 
            user = discord.utils.find(lambda m: m.id == int(user_id), message.channel.guild.members)
            # ping only if user exists or has read permissions
            print("user =="+str(user))
            if (user and message.channel.permissions_for(user).read_messages and message.author != bot.user and message.author != user):
                print("second if")
                await send_dm(user,"#{}: <{}> {}".format(message.channel, message.author.name, message.content))

@bot.group(aliases=["quotes", "q"], pass_context=True)
async def quote(ctx):
    """Quotes!

    Running the command without any arguments will display a random quote.
    """
    if ctx.invoked_subcommand is None:
        try:
            print("before random choice")
            emptykey = random.choice(list(quotes.keys()))
            print("after random choice")
        except IndexError:
            await ctx.channel.send("There are no quotes.")
            return
        await ctx.channel.send(quotes[emptykey])

@quote.command(name="add", aliases=["new", "create" "a"])
async def quote_new(ctx,name, *, body: str):
    global quotes
    print("okay the bare bones worked")
    """Add a new quote."""
    quote_body = f"<{name}> {body}"
    print("this is before the first if")
    if quote_body not in quotes.values():
        print("before num")
        quotes["num"] = quotes["num"] + 1
        quote_body = str(quotes["num"]) + ": " + quote_body
        print("before dict add")
        quotes[str(quotes["num"])] = quote_body
        update_db(quotes, "quotes.json")
        print("num update worked")
        await ctx.channel.send("Quote " + str(quotes["num"]) + " added.")
    else:
        await ctx.channel.send("That quote already exists.")

@quote.command(name="get", aliases=["g"])
async def quote_get(ctx,qnum: str):
    if qnum in quotes.keys():
        await ctx.channel.send(quotes[qnum])
    else:
        await ctx.channel.send("couldn't find quote")

@quote.command(name="find", aliases=["search", "f"])
async def quote_find(ctx,*, found: str):
    print("before foundquotes")
    foundquotes = []
    print("after found quotes summoning")
    for (qnum, quote) in quotes.items():
        if (found in quote):
            foundquotes.append(qnum)
            print("after every loop")
    if len(foundquotes) == 0:
           await ctx.channel.send("couldn't find anything")
           print("after it failed to find anythin")
    elif len(foundquotes) == 1:
           await ctx.channel.send(quotes[foundquotes[0]])
    elif len(foundquotes) > 1 and len(foundquotes) <= 10:
           await ctx.channel.send(quotes[foundquotes[0]] + " " + "Also found in the following quotes" + " " + ", ".join(foundquotes[1:11]))
    elif len(foundquotes) > 10:
           await ctx.channel.send(quotes[foundquotes[0]] + " " + "Also found in the following quotes" + " " + ", ".join(foundquotes[1:11]) + " and many more....")
           print (quotes[foundquotes[0]] )


@quote.command(name="edit", aliases=["e"])
async def quote_edit(ctx,n, name, *, body: str):
   new_quote_body = f"<{name}> {body}"
   foundQuote = False
   print("before for loop")
   for qnum in quotes.keys():
       if (n is qnum and n != "num"):
        foundQuote = True

        new_quote_body = str(n) + ": " + new_quote_body
        quotes[str(n)] = new_quote_body
        update_db(quotes, "quotes.json")
        await ctx.channel.send("The quote was sucessfully edited")
   if (foundQuote == False):
        await ctx.channel.send("couldnt find quote to edit")

@quote.command(name="number", aliases=["num"])
async def db_number(ctx):
    global quotes
    await ctx.channel.send("There are " + str(quotes["num"]) + " quotes in the database")

@quote.command(name="rain", aliases=["r"])
async def quote_rain(ctx,n: int = 5):
    output_str = ""
    global quotes
    for i in range(n):
        random_index = random.randrange(0, quotes["num"])
        output_str += quotes[str(random_index)] + "\n"
    await ctx.channel.send(output_str)



bot.run(config["token"])

