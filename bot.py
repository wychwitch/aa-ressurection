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
    if message.author == bot.user:
           # we do not want the bot to reply to itself
        return
    if az_game != None:
        print("there IS a game")
        if (' ' not in message.content.strip()):
            print("this IS testing if message works")
            await update_az_game(bot,message)
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

@quote.command(name="rain")
async def quote_rain(ctx,n: int = 5):
    output_str = ""
    global quotes
    for i in range(n):
        random_index = random.randrange(0, quotes["num"])
        output_str += quotes[str(random_index)] + "\n"
    await ctx.channel.send(output_str)

#Remove command group, serving mostly as a warning
@quote.group(name="remove", pass_context=True)
async def remove(ctx):
    if ctx.invoked_subcommand is None:
        await ctx.channel.send("use Latest to remove the last added quote")
    global quotes
    qnum = quotes["num"]
    qstr = quotes[str(quotes["num"])]
    del quotes[str(quotes["num"])]
    quotes["num"] = quotes["num"] - 1
    update_db(quotes, "quotes.json")
    await ctx.channel.send(f"quote \"{qstr}\" was removed")
"""
 _______    ______________________      __ 
 \      \  /   _____/\_   _____/  \    /  
 /   |   \ \_____  \  |    __) \   \/\/   /
/    |    \/        \ |     \   \        / 
\____|__  /_______  / \___  /    \__/\  /  
        \/        \/      \/          \/ 
"""

@bot.group(aliases=["nsfw"], pass_context=True)
async def nsfwQuote(ctx):
    """nsfwQuotes!

    Running the command without any arguments will display a random nsfwQuote.
    """
    if ctx.invoked_subcommand is None:
        try:
            print("before random choice")
            emptykey = random.choice(list(nsfwQuotes.keys()))
            print("after random choice")
        except IndexError:
            await ctx.channel.send("There are no nsfwQuotes.")
            return
        await ctx.channel.send(nsfwQuotes[emptykey])


@nsfwQuote.command(name="add", aliases=["new", "create" "a"])
async def nsfwQuote_new(ctx,name, *, body: str):
    global nsfwQuotes
    print("okay the bare bones worked")
    """Add a new nsfwQuote."""
    nsfwQuote_body = f"<{name}> {body}"
    print("this is before the first if")
    if nsfwQuote_body not in nsfwQuotes.values():
        print("before num")
        nsfwQuotes["num"] = nsfwQuotes["num"] + 1
        nsfwQuote_body = str(nsfwQuotes["num"]) + ": " + nsfwQuote_body
        print("before dict add")
        nsfwQuotes[str(nsfwQuotes["num"])] = nsfwQuote_body
        update_db(nsfwQuotes, "nsfwQuotes.json")
        print("num update worked")
        await ctx.channel.send("nsfwQuote " + str(nsfwQuotes["num"]) + " added.")
    else:
        await ctx.channel.send("That nsfwQuote already exists.")

@nsfwQuote.command(name="get", aliases=["g"])
async def nsfwQuote_get(ctx,qnum: str):
    if qnum in nsfwQuotes.keys():
        await ctx.channel.send(nsfwQuotes[qnum])
    else:
        await ctx.channel.send("couldn't find nsfwQuote")

@nsfwQuote.command(name="find", aliases=["search", "f"])
async def nsfwQuote_find(ctx,*, found: str):
    print("before foundNsfwQuotes")
    foundNsfwQuotes = []
    print("after found nsfwQuotes summoning")
    for (qnum, nsfwQuote) in nsfwQuotes.items():
        if (found in nsfwQuote):
            foundNsfwQuotes.append(qnum)
            print("after every loop")
    if len(foundNsfwQuotes) == 0:
           await ctx.channel.send("couldn't find anything")
           print("after it failed to find anythin")
    elif len(foundNsfwQuotes) == 1:
           await ctx.channel.send(nsfwQuotes[foundNsfwQuotes[0]])
    elif len(foundNsfwQuotes) > 1 and len(foundNsfwQuotes) <= 10:
           await ctx.channel.send(quotes[foundNsfwQuotes[0]] + " " + "Also found in the following nsfwQuotes" + " " + ", ".join(foundNsfwQuotes[1:11]))
    elif len(foundNsfwQuotes) > 10:
           await ctx.channel.send(nsfwQuotes[foundNsfwQuotes[0]] + " " + "Also found in the following nsfwQuotes" + " " + ", ".join(foundNsfwQuotes[1:11]) + " and many more....")
           print (nsfwQuotes[foundNsfwQuotes[0]] )


@nsfwQuote.command(name="edit", aliases=["e"])
async def nsfwQuote_edit(ctx,n, name, *, body: str):
   new_nsfwQuote_body = f"<{name}> {body}"
   foundNsfwQuote = False
   print("before for loop")
   for qnum in nsfwQuotes.keys():
       if (n is qnum and n != "num"):
        foundNsfwQuote = True

        new_nsfwQuote_body = str(n) + ": " + new_nsfwQuote_body
        nsfwQuotes[str(n)] = new_nsfwQuote_body
        update_db(nsfwQuotes, "nsfwQuotes.json")
        await ctx.channel.send("The nsfwQuote was sucessfully edited")
   if (foundNsfwQuote == False):
        await ctx.channel.send("couldnt find nsfwQuote to edit")

@nsfwQuote.command(name="number", aliases=["num"])
async def nsfwdb_number(ctx):
    global nsfwQuotes
    await ctx.channel.send("There are " + str(nsfwQuotes["num"]) + " nsfwQuotes in the database")

@nsfwQuote.command(name="rain")
async def nsfwQuote_rain(ctx,n: int = 5):
    output_str = ""
    global nsfwQuotes
    for i in range(n):
        random_index = random.randrange(0, nsfwQuotes["num"])
        output_str += nsfwQuotes[str(random_index)] + "\n"
    await ctx.channel.send(output_str)

#Remove command group, serving mostly as a warning
@nsfwQuote.group(name="remove", pass_context=True)
async def nsfwRemove(ctx):
    global nsfwQuotes
    deletedQuote = nsfwQuotes[str(nsfwQuotes["num"])]
    del nsfwQuotes[str(nsfwQuotes["num"])]
    nsfwQuotes["num"] = nsfwQuotes["num"] - 1
    update_db(nsfwQuotes, "nsfwQuotes.json")
    await ctx.channel.send(f"The Quote \"{deletedQuote}\" was removed")

"""
     _              _____         ____      _      __  __   _____ 
    / \            |__  /        / ___|    / \    |  \/  | | ____|
   / _ \    _____    / /        | |  _    / _ \   | |\/| | |  _|  
  / ___ \  |_____|  / /_        | |_| |  / ___ \  | |  | | | |___ 
 /_/   \_\         /____|        \____| /_/   \_\ |_|  |_| |_____|
                                                                  

Cannibalized from: 
https://github.com/cameronleong/guesstheword

"""


class AZGame:
    poke_list_url = "https://pastebin.com/tmqw0xns"
    def __init__(self, string):
        if string == "az":
            wordlist = "json/az_words.txt"
            wordlistlines = 115810                  
        elif string == "poke":
            wordlist = "json/pokemon.txt"
            wordlistlines = 893
        #number of lines in the wordlist you're using
        linenumber = random.randint(1, wordlistlines)       
        #pick a random line number
        az_word = linecache.getline(wordlist, linenumber).strip()  
        #linecache lets you pull a single line instead of the entire file
        print("AZ Game answer " + az_word)
        self.answer = az_word.strip()
        self.left = linecache.getline(wordlist, 1).strip()
        self.right = linecache.getline(wordlist, wordlistlines).strip()
        self.wordlist = wordlist
        self.wordlistlines = wordlistlines

@bot.group(pass_context = True)
async def az(ctx):
    global az_game
    if ctx.invoked_subcommand is None:
        if (az_game):
            await ctx.channel.send("Your range is: {} --- {}".format(az_game.left, az_game.right))
        else: 
            await ctx.channel.send("Starting an az game")
            az_game = AZGame("az")
            await ctx.channel.send("Your range is: {} --- {}".format(az_game.left, az_game.right))

@az.command(name="poke", aliases=['pk'])
async def az_poke(ctx):
    global az_game
    if az_game is not None:
        await ctx.channel.send("You have an az game going. Your range is: {} --- {}".format(az_game.left, az_game.right))
    else:
        az_game = AZGame("poke")
        await ctx.channel.send("Your range is: {} --- {}".format(az_game.left, az_game.right))
    

@az.command(name="help")
async def az_help(ctx):
    await ctx.send("""`!az` starts a new game or lists the range
`!az abc` will list out the alphabet
`!az end` will end the current game
`!az top` will list the 3 top winners
`!az scores [@users]` will list the wins of the mentioned users""")

@az.command(name="abc", description="say the alphabet")
async def az_abc(ctx):
    await ctx.send('a b c d e f g h i j k l m n o p q r s t u v w x y z')

@az.command(name="end", description="end the current game")
async def az_end(ctx):
    global az_game
    if (az_game):
        await ctx.channel.send("Now closing az game, the answer was " + az_game.answer)
        if "poke" in az_game.wordlist:
            await ctx.channel.send('http://bulbapedia.bulbagarden.net/wiki/'+az_game.answer)
        else:
            await ctx.channel.send('http://www.merriam-webster.com/dictionary/'+az_game.answer)
        
        az_game = None
    else:
        await ctx.channel.send("There is no ongoing game")
    
# called in the on_message event
async def update_az_game(bot, message):
    global az_game
    # az game ignores messages with multiple words/has spaces
    if (not az_game or ' ' in message.content.strip()):
        return

    guess = message.content.strip().lower()
    # if the answer is correct, update scores and end the game
    if (guess == az_game.answer):
        player_score = await add_score(message.author)
        await message.channel.send( "The answer was {answer}. {player} wins! {player} has won {wins} times.".format(answer=az_game.answer, player=message.author.name, wins=player_score))
        if "poke" in az_game.wordlist:
            await message.channel.send('http://bulbapedia.bulbagarden.net/wiki/'+az_game.answer)
        else:
            await message.channel.send("http://www.merriam-webster.com/dictionary/" + az_game.answer)
        az_game = None
    # if the answer is not correct but is a word, update the range
    elif await check_string(guess) and az_game.left < guess and az_game.right > guess:
        if guess < az_game.answer:
            az_game.left = guess
        else:
            az_game.right = guess
        await message.channel.send( 'Your range is: {} --- {}'.format(az_game.left, az_game.right))

async def check_string(w):
    global az_game
    if (' ' not in w):                  
        with open(az_game.wordlist) as f:
            #print('Iterating...')
            for line in f:                  
                if w.strip().lower() == line.strip().lower():
                    #print(line)
                    return True
    return False

          
@az.command(name = "top", pass_context = True, description="list the top three player of az")
async def az_top(ctx):
    global az_scores
    scoreStr= "\n         :star: Top 3 Players :star: \n\n"
    top_players = sorted(az_scores, key=az_scores.get, reverse=True)[:3]
    #print(top_players)
    for rank, top_player in enumerate(top_players):
        #print(scoreStr)
        player = discord.utils.find(lambda m: m.id == int(top_player), ctx.message.channel.server.members)
        if (player):
            scoreStr += " :military_medal:  #{}: {} won {} times\n".format(rank+1, player.name, az_scores[top_player])
    await ctx.channel.send(scoreStr)

@az.command(name = "score", pass_context = True, description="give the numberof times someone has beat the game")  
async def az_score(ctx, *, msg:str):
    global az_scores
    scoreStr = ""
    sorted_mentions = sorted(ctx.message.mentions, key=lambda x: x.name.lower())
    #print(", ".join([m.name for m in sorted_mentions]))
    for player in sorted_mentions:
        if player.id in az_scores:
            scoreStr+="{} - {} wins\n".format(player.name, az_scores[player.id])
        else:
            scoreStr+="{} - 0 wins\n".format(player.name)
    await ctx.channel.send(scoreStr)            

@az.command(name="pokelist", description="the list of pokemon the bot uses")
async def az_pokelist(ctx):
    await ctx.channel.send(AZGame.poke_list_url)

async def add_score(user):
    if user.id in az_scores:
        az_scores[user.id] += 1
    else:
        az_scores[user.id] = 1
    update_db(az_scores, "az_scores.json")
    return az_scores[user.id]











bot.run(config["token"])

