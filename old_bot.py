import discord
import linecache
import random
import re
import json

from os import path
from discord import Game
from discord.ext import commands as c

VERSION = "1.1.0"

# Grab the config variables
with open("config.json") as cfg:
    config = json.load(cfg)

with open("dicti.json") as dic:
    dicti = json.load(dic)

with open ("num.json") as numb:
    num = json.load(numb)

with open ("nsfwdicti.json") as nsfwdic:
    nsfwdicti = json.load(nsfwdic)

with open ("nsfwnum.json") as nsfwnumb:
    nsfwnum = json.load(nsfwnumb) 

with open ("art.json") as artdic:
    artdicti = json.load(artdic)

with open ("artnum.json") as artnumb:
    artnum = json.load(artnumb)

# Storing people's pings
with open("pings.json") as pings_file:
    pings_dict = json.load(pings_file)

# AZ Game Scores
with open("az_scores.json") as az_scores_file:
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
bot = c.Bot(c.when_mentioned_or(config["prefix"]), description=description)

# Check for if the user running a command is the bot's owner.
def is_owner():
    return c.check(lambda ctx: ctx.message.author.id == config["owner"])

# Change avatar and username
async def update_profile(name, picture):
    if path.isfile(picture):
        with open(picture, "rb") as avatar:
            await bot.edit_profile(avatar=avatar.read())
            print("Bot avatar set.")
        await bot.edit_profile(username=name)
        print("Bot name set.")

# Events
@bot.event
async def on_ready():
    print("Attempting to set username and avatar.")
    try:
        await update_profile(config["bot_name"], config["avatar"])
    except Exception as err:
        print(f"Error setting name or avatar: {err}")

    print("============READY")
    print(f"QuoteBot v{VERSION}")
    print(f"Logged in as: {bot.user.name} ({bot.user.id})")
    print("============READY")

@bot.event
async def on_command_error(err, ctx):
    channel = ctx.message.channel
    if isinstance(err, c.CheckFailure):
        await bot.send_message(channel, "You don't have permission to do that.")
    elif isinstance(err, c.MissingRequiredArgument):
        await bot.send_message(channel, "Missing argument(s).")

@bot.event
async def on_message(message):
    if message.author == bot.user:
           # we do not want the bot to reply to itself
        return
    if (' ' not in message.content.strip()):
        await update_az_game(bot, message)
    await check_pings(bot, message)
    # At the end, deal with all the other commands
    await bot.process_commands(message)
        

# Commands
@bot.command(name="quit")
@is_owner()
async def bot_quit():
    """Shut the bot down."""
    print("okay this quit print worked....")
    await bot.say(":eyes: :wave:")
    await bot.logout()

@bot.command(name="status")
@is_owner()
async def bot_status(*, status: str = None):
    """Change the bot's 'playing' status.

    Running this command without any arguments will turn the 'playing' status off'
    """
    game = Game(name=status)
    await bot.change_status(game=game)

@bot.command(name="info")
async def bot_info():
    """Display info about the bot."""
    await bot.say(f"QuoteBot v{VERSION}")

@bot.group(aliases=["quotes", "q"], pass_context=True)
async def quote(ctx):
    """Quotes!

    Running the command without any arguments will display a random quote.
    """
    if ctx.invoked_subcommand is None:
        try:
            print("before random choice")
            emptykey = random.choice(list(dicti.keys()))
            print("after random choice")
        except IndexError:
            await bot.say("There are no quotes.")
            return
        await bot.say(dicti[emptykey])
        
@quote.command(name="add", aliases=["new", "create" "a"])
async def quote_new(name, *, body: str):
    global num
    print("okay the bare bones worked")
    """Add a new quote."""
    quote_body = f"<{name}> {body}"
    print("this is before the first if")
    if quote_body not in dicti.values():
        print("before num")
        num = num + 1
        quote_body = str(num) + ": " + quote_body
        print("before dict add")
        dicti[str(num)] = quote_body
        print("before num update")
        update_db(num, "num.json")
        print("before dicti update")
        update_db(dicti, "dicti.json")
        print("num update worked")
        await bot.say("Quote " + str(num) + " added.")
    else:
        await bot.say("That quote already exists.")

@quote.command(name="get", aliases=["g"])
async def quote_get(qnum: str):
    if qnum in dicti.keys():
        await bot.say(dicti[qnum])
    else:
        await bot.say("couldn't find quote")

@quote.command(name="find", aliases=["search", "f"])
async def quote_get(*, found: str):
    print("before foundquotes")
    foundquotes = []
    print("after found quotes summoning")
    for (qnum, quote) in dicti.items():
        if (found in quote):
            foundquotes.append(qnum)
            print("after every loop")
    if len(foundquotes) == 0:
           await bot.say("couldn't find anything")
           print("after it failed to find anythin")
    elif len(foundquotes) == 1:
           await bot.say(dicti[foundquotes[0]])
    elif len(foundquotes) > 1 and len(foundquotes) <= 10:
           await bot.say(dicti[foundquotes[0]] + " " + "Also found in the following quotes" + " " + ", ".join(foundquotes[1:11]))
    elif len(foundquotes) > 10:
           await bot.say(dicti[foundquotes[0]] + " " + "Also found in the following quotes" + " " + ", ".join(foundquotes[1:11]) + " and many more....")
           print (dicti[foundquotes[0]] )

#The edit command to change the dicti's variables
@quote.command(name="edit", aliases=["e"])
async def quote_edit(n, name, *, body: str):
   new_quote_body = f"<{name}> {body}"
   TorF = False
   print("before for loop")
   for qnum in dicti.keys():
       if (n is qnum):
        TorF = True

        new_quote_body = str(n) + ": " + new_quote_body
        dicti[str(n)] = new_quote_body
        update_db(dicti, "dicti.json")
        await bot.say("The quote was sucessfully edited")
   if (TorF == False):
        await bot.say("couldnt find quote to edit")

@quote.command(name="number", aliases=["num"])
async def db_number():
    await bot.say("There are " + str(num) + " quotes in the database")

@quote.command(name="rain", aliases=["r"])
async def quote_rain(n: int = 5):
    output_str = ""
    for i in range(n):
        random_index = random.randrange(0, num)
        output_str += dicti[str(random_index)] + "\n"
    await bot.say(output_str)

#Remove command group, serving mostly as a warning
#@quote.group(name="remove", aliases=["r"], pass_context=True)
#async def remove(ctx):
#    if ctx.invoked_subcommand is None:
#        await bot.say("use Latest to remove the last added quote")
#Actual command to be called to delete the latest quote
#@remove.command(name="latest", aliases=["l"])
#async def latest():
#    del dicti[num]
#    num = num - 1
#    await bot.say("last entry wss removed")




# NSFW QUOTES

@bot.group(pass_context=True)
async def nsfw(ctx):
    """Quotes!

    Running the command without any arguments will display a random quote.
    """
    if ctx.invoked_subcommand is None:
        try:
            print("before random choice")
            emptykey = random.choice(list(nsfwdicti.keys()))
            print("after random choice")
        except IndexError:
            await bot.say("There are no quotes.")
            return
        await bot.say(nsfwdicti[emptykey])
        
@nsfw.command(name="add", aliases=["new", "create" "a"])
async def nsfw_new(name, *, body: str):
    global nsfwnum
    print("okay the bare bones worked")
    """Add a new quote."""
    nsfw_body = f"<{name}> {body}"
    print("this is before the first if")
    if nsfw_body not in nsfwdicti.values():
        print("before num")
        nsfwnum = nsfwnum + 1
        nsfw_body = str(nsfwnum) + ": " + nsfw_body
        print("before dict add")
        nsfwdicti[str(nsfwnum)] = nsfw_body
        print("before num update")
        update_db(nsfwnum, "nsfwnum.json")
        print("before dicti update")
        update_db(nsfwdicti, "nsfwdicti.json")
        print("num update worked")
        await bot.say("Quote " + str(nsfwnum) + " added.")
    else:
        await bot.say("That nsfw quote already exists.")

@nsfw.command(name="get", aliases=["g"])
async def nsfw_get(qnum: str):
    if qnum in nsfwdicti.keys():
        await bot.say(nsfwdicti[qnum])
    else:
        await bot.say("couldn't find nsfwquote")

@nsfw.command(name="find", aliases=["search", "f"])
async def nsfw_get(*, found: str):
    print("before foundquotes")
    foundnsfw = []
    print("after found quotes summoning")
    for (qnum, nsfw) in nsfwdicti.items():
        if (found in nsfw):
            foundnsfw.append(qnum)
            print("after every loop")
    if len(foundnsfw) == 0:
           await bot.say("couldn't find anything")
           print("after it failed to find anythin")
    elif len(foundnsfw) == 1:
           await bot.say(nsfwdicti[foundnsfw[0]])
    elif len(foundnsfw) > 1 and len(foundnsfw) <= 10:
           await bot.say(nsfwdicti[foundnsfw[0]] + " " + "Also found in the following quotes" + " " + ", ".join(foundquotes[1:11]))
    elif len(foundnsfw) > 10:
           await bot.say(nsfwdicti[foundnsfw[0]] + " " + "Also found in the following quotes" + " " + ", ".join(foundnsfw[1:11]) + " and many more....")
           print (nsfwdicti[foundquotes[0]] )

#The edit command to change the dicti's variables
@nsfw.command(name="edit", aliases=["e"])
async def nsfw_edit(n, name, *, body: str):
   new_nsfw_body = f"<{name}> {body}"
   TorF = False
   print("before for loop")
   for qnum in nsfwdicti.keys():
       if (n is qnum):
        TorF = True
        new_nsfw_body = str(n) + ": " + new_nsfw_body
        nsfwdicti[str(n)] = new_nsfw_body
        update_db(nsfwdicti, "dicti.json")
        await bot.say("The quote was sucessfully edited")
   if (TorF == False):
        await bot.say("couldnt find quote to edit")

@nsfw.command(name="number", aliases=["num"])
async def db_number():
    await bot.say("There are " + str(nsfwnum) + " quotes in the database")


#Art Quotes!!

@bot.group(pass_context=True)
async def art(ctx):
    """Quotes!

    Running the command without any arguments will display a random quote.
    """
    if ctx.invoked_subcommand is None:
        try:
            print("before random choice")
            emptykey = random.choice(list(artdicti.keys()))
            print("after random choice")
        except IndexError:
            await bot.say("There are no art.")
            return
        await bot.say(artdicti[emptykey])
        
@art.command(name="add", aliases=["new", "create" "a"])
async def art_new(name, *, body: str):
    global artnum
    print("okay the bare bones worked")
    """Add a new quote."""
    art_body = f"<{name}> {body}"
    print("this is before the first if")
    if art_body not in artdicti.values():
        print("before num")
        artnum = artnum + 1
        art_body = str(artnum) + ": " + art_body
        print("before dict add")
        artdicti[str(artnum)] = art_body
        print("before num update")
        update_db(artnum, "artnum.json")
        print("before dicti update")
        update_db(artdicti, "art.json")
        print("num update worked")
        await bot.say("Art " + str(artnum) + " added.")
    else:
        await bot.say("That art already exists.")

@art.command(name="get", aliases=["g"])
async def art_get(qnum: str):
    if qnum in artdicti.keys():
        await bot.say(artdicti[qnum])
    else:
        await bot.say("couldn't find art")

@art.command(name="find", aliases=["search", "f"])
async def art_get(*, found: str):
    print("before foundquotes")
    foundart = []
    print("after found quotes summoning")
    for (qnum, art) in artdicti.items():
        if (found in art):
            foundart.append(qnum)
            print("after every loop")
    if len(foundart) == 0:
           await bot.say("couldn't find anything")
           print("after it failed to find anythin")
    elif len(foundart) == 1:
           await bot.say(artdicti[foundart[0]])
    elif len(foundart) > 1 and len(foundart) <= 10:
           await bot.say(artdicti[foundart[0]] + " " + "Also found in the following arts" + " " + ", ".join(foundart[1:11]))
    elif len(foundart) > 10:
           await bot.say(artdicti[foundart[0]] + " " + "Also found in the following artss" + " " + ", ".join(foundart[1:11]) + " and many more....")
           print (artdicti[foundart[0]] )

#The edit command to change the dicti's variables
@art.command(name="edit", aliases=["e"])
async def art_edit(n, name, *, body: str):
   new_art_body = f"<{name}> {body}"
   TorF = False
   print("before for loop")
   for qnum in artdicti.keys():
       if (n is qnum):
        TorF = True
        new_art_body = str(n) + ": " + new_art_body
        artdicti[str(n)] = new_art_body
        update_db(artdicti, "artdicti.json")
        await bot.say("The qart was sucessfully edited")
   if (TorF == False):
        await bot.say("couldnt find art to edit")

@art.command(name="number", aliases=["num"])
async def db_number():
    await bot.say("There are " + str(artnum) + " quotes in the database")




"""
  ____    _                       ____            _   _ 
 |  _ \  (_)   ___    ___        |  _ \    ___   | | | |
 | | | | | |  / __|  / _ \       | |_) |  / _ \  | | | |
 | |_| | | | | (__  |  __/       |  _ <  | (_) | | | | |
 |____/  |_|  \___|  \___|       |_| \_\  \___/  |_| |_|
                                                        
Copy/Pasted from:
https://github.com/Rapptz/discord.py/blob/master/examples/basic_bot.py

"""

@bot.command()
async def roll(dice : str):
    """Rolls a dice in NdN format."""
    try:
        rolls, limit = map(int, dice.split('d'))
    except Exception:
        await bot.say('Format has to be in NdN!')
        return

    result = ', '.join(str(random.randint(1, limit)) for r in range(rolls))
    await bot.say(result)


"""
  ____ ___ _   _  ____ ____  
 |  _ \_ _| \ | |/ ___/ ___| 
 | |_) | ||  \| | |  _\___ \ 
 |  __/| || |\  | |_| |___) |
 |_|  |___|_| \_|\____|____/ 
                             
This one is just me. Wasn't sure what to Google.

"""

@bot.group(aliases=["ping", "p"], pass_context = True)
async def pings(ctx):
    if ctx.invoked_subcommand is None:
        user_id = ctx.message.author.id
        if (user_id in pings_dict):
            await bot.say("Your pings are: {}".format(", ".join(pings_dict[user_id])))
        else: 
            await bot.say("You don't have any pings set up")

@pings.command(name="help")
async def pings_help():
    await bot.say("""`!pings`
    lists out what speel will ping you on
`!pings add [rest of line]`
    tells speel to ping you on [rest of line]
`!pings del [rest of line]`
    tells speel to stop pinging you on [rest of line]""")

@pings.command(name="add", pass_context = True)
async def pings_add(ctx, *, msg : str):
    global pings_dict
    user_id = ctx.message.author.id
    if user_id not in pings_dict:
        pings_dict[user_id] = []
    pings_dict[user_id].append(msg.strip())
    update_db(pings_dict, "pings.json")
    #print(pings_dict)

@pings.command(name="del", pass_context = True)
async def pings_del(ctx, *, msg : str):
    global pings_dict
    user_id = ctx.message.author.id
    if ((user_id in pings_dict) and (msg.strip() in pings_dict[user_id])):
        pings_dict[user_id].remove(msg.strip())
        update_db(pings_dict, "pings.json")
    else:
        await bot.say("That wasn't a ping that was set up")
    #print(pings_dict)

# call in the on_message event
async def check_pings(bot, message):
    global pings_dict
    lower_text = message.content.lower()
    for user_id, ping_triggers in pings_dict.items():
        trigger_regexes = ["\\b"+trigger+"\\b" for trigger in ping_triggers]
        if any([re.search(trigger_regex, lower_text) for trigger_regex in trigger_regexes]):
            user = discord.utils.find(lambda m: m.id == user_id, message.channel.server.members)
            # ping only if user exists or has read permissions
            if (user and message.channel.permissions_for(user).read_messages):
                await bot.send_message(user, "#{}: <{}> {}".format(message.channel, message.author.name, message.content))


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
        if string is "az":
            wordlist = "json/az_words.txt"
            wordlistlines = 115810                  
        elif string is "poke":
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
            await bot.say("Your range is: {} --- {}".format(az_game.left, az_game.right))
        else: 
            await bot.say("Starting an az game")
            az_game = AZGame("az")
            await bot.say("Your range is: {} --- {}".format(az_game.left, az_game.right))

@az.command(name="poke", aliases=['pk'])
async def az_poke():
    global az_game
    if az_game is not None:
        await bot.say("You have an az game going. Your range is: {} --- {}".format(az_game.left, az_game.right))
    else:
        az_game = AZGame("poke")
        await bot.say("Your range is: {} --- {}".format(az_game.left, az_game.right))
    

@az.command(name="help")
async def az_help():
    await bot.say("""`!az` starts a new game or lists the range
`!az abc` will list out the alphabet
`!az end` will end the current game
`!az top` will list the 3 top winners
`!az scores [@users]` will list the wins of the mentioned users""")

@az.command(name="abc", description="say the alphabet")
async def az_abc():
    await bot.say('a b c d e f g h i j k l m n o p q r s t u v w x y z')

@az.command(name="end", description="end the current game")
async def az_end():
    global az_game
    if (az_game):
        await bot.say("Now closing az game, the answer was " + az_game.answer)
        if "poke" in az_game.wordlist:
            await bot.say('http://bulbapedia.bulbagarden.net/wiki/'+az_game.answer)
        else:
            await bot.say('http://www.merriam-webster.com/dictionary/'+az_game.answer)
        
        az_game = None
    else:
        await bot.say("There is no ongoing game")
    
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
        await bot.send_message(message.channel, "The answer was {answer}. {player} wins! {player} has won {wins} times.".format(answer=az_game.answer, player=message.author.name, wins=player_score))
        if "poke" in az_game.wordlist:
            await bot.send_message(message.channel, 'http://bulbapedia.bulbagarden.net/wiki/'+az_game.answer)
        else:
            await bot.send_message(message.channel, "http://www.merriam-webster.com/dictionary/" + az_game.answer)
        az_game = None
    # if the answer is not correct but is a word, update the range
    elif await check_string(guess) and az_game.left < guess and az_game.right > guess:
        if guess < az_game.answer:
            az_game.left = guess
        else:
            az_game.right = guess
        await bot.send_message(message.channel, 'Your range is: {} --- {}'.format(az_game.left, az_game.right))

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
        player = discord.utils.find(lambda m: m.id == top_player, ctx.message.channel.server.members)
        if (player):
            scoreStr += " :military_medal:  #{}: {} won {} times\n".format(rank+1, player.name, az_scores[top_player])
    await bot.say(scoreStr)

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
    await bot.say(scoreStr)            

@az.command(name="pokelist", description="the list of pokemon the bot uses")
async def az_pokelist():
    await bot.say(AZGame.poke_list_url)

async def add_score(user):
    if user.id in az_scores:
        az_scores[user.id] += 1
    else:
        az_scores[user.id] = 1
    update_db(az_scores, "az_scores.json")
    return az_scores[user.id]

bot.run(config["token"])
