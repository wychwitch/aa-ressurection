import linecache
import random
import re
import json
import argparse
import shlex
import re
import discord
from pprint import pprint
from discord import Game
from discord import user
from discord.ext import commands
from types import SimpleNamespace
import urllib.request
import pokebase
from decimal import Decimal
import asyncio

from os import path

VERSION = "2.0.0"

# enabling intents
intents = discord.Intents.default() 
intents.members = True

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

with open("json/inventory.json") as inv_file:
    inventoryDict = dict(json.load(inv_file))

with open("json/coin.json") as coin_file:
    coinDict = dict(json.load(coin_file))
    print(coinDict)

# AZ Game - no point in keeping a file for this
az_game = None

undercutGame = None

undercutMode = "uc"

ucUsers = []

playersSubmitted = 0
    
# Helper command to update the database
def update_db(database, filename):
    with open("json/"+filename, "w") as dtb:
        json.dump(database, dtb, indent=4)

description="""
Basic quote bot.
"""

bot = commands.Bot(commands.when_mentioned_or(config["prefix"]), intents=intents)

@bot.command(name="quit")
async def bot_quit(ctx):
    """Shut the bot down."""
    print("okay this quit print worked....")
    await discordPrint(ctx,":eyes: :wave:")
    await bot.logout()

@bot.event
async def on_ready():
    print(f"Discord.py v {discord.__version__} \nQuoteBot v{VERSION} We have logged in as {bot.user}")

@bot.command(name = "test",pass_context=True)
async def test(ctx, *, testStr):

    await discordPrint(ctx, 
    f"{parseGpString(testStr)}")

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
    
    if undercutGame != None:
        print("there IS an undercut")
        if (' ' not in message.content.strip()):
            print("this IS testing if message works")
            await update_uc_game(bot,message)

    if az_game != None:
        print("there IS a game")
        if (' ' not in message.content.strip()):
            print("this IS testing if message works")
            await update_az_game(bot,message)
    await check_pings(bot, message)
    await bot.process_commands(message)

async def check_pings(bot, message):
    global pings_dict
    #print("client users:", bot.users)
    #print("Message text: ",message.content)
    #print("Message Channel Name: ",message.channel.name)

    #print("\n".join(["{}: {}".format(m.name, m.id) for m in message.channel.guild.members]))

    #print("\n second members check: ",message.channel.guild.members)
    lower_text = message.content.lower()
    for user_id, ping_triggers in pings_dict.items():
        trigger_regexes = ["\\b"+trigger+"\\b" for trigger in ping_triggers]

        
        if any([re.search(trigger_regex, lower_text) for trigger_regex in trigger_regexes]):
            #print("first if in check pings")
            
            # Making sure the user is even in the server
            user = discord.utils.find(lambda m: m.id == int(user_id), message.channel.guild.members)
            #print("user == "+str(user))

            #ping only if user exists AND has read permissions AND is NOT the bot OR the person who is doing the pinging
            if (user and message.channel.permissions_for(user).read_messages and message.author != bot.user and message.author != user):
                #print("second if in check pings")
                await send_dm(user,"#{}: <{}> {}".format(message.channel, message.author.name, message.content))

@bot.group(aliases=["inv", "inventory"], pass_context=True)
async def invCMD(ctx):
    returnStr = ""
    if ctx.invoked_subcommand is None:
        returnStr += getInv(str(ctx.author.id))
        await ctx.channel.send(returnStr)

@invCMD.command(name="-f", pass_context=True)
async def invCMDFull(ctx):
    returnStr = ""
    returnStr += getInv(str(ctx.author.id), True)
    await ctx.channel.send(returnStr)

@invCMD.command(name="get", aliases=["g"], pass_context=True)
async def invGet(ctx, userId, fullArg = ""):
    returnStr = ""

    user = getUser(ctx, userId)

    commandUsr = getUser(ctx, str(ctx.message.author.id))

    if user:
        isDm = checkIfDm(ctx, commandUsr)
        if fullArg.lower() == "-f":
            if user.id == str(ctx.message.author.id) or isDm:
                returnStr += getInv(str(user.id), True)
            else:
                returnStr += "You dont have permission to check that inventory!"
        else:
            returnStr += getInv(str(user.id))
    else:
        returnStr += "That is not a valed user!"
    await ctx.channel.send(returnStr)

@invCMD.command(name="add", pass_context=True)
async def inventoryDictAdd(ctx, *, itemStr: str):
    userId = str(ctx.message.author.id)
    returnStr = ""
    argsList = ['-b','-i','-q','-p','-w']
    saneArgValues = {'-b':"string1",'-i':"string2",'-q':1,'-p':True, '-w':0}

    returnStr = addToInv(userId, itemStr, argsList, saneArgValues)
    
    if returnStr == "":
        await ctx.channel.send("something went wrong")
    else:
        await ctx.channel.send(returnStr)

def pairArgs(argsList, saneArgs, wholeStr):
    indices= []
    keys = []
    values = []
    parts ={}
    argsListRemove = argsList.copy()
    #split by arguments
    for i in range (0, len(argsList)):
        p = re.compile('|'.join(argsListRemove))
        m = p.search(wholeStr)
        if m:
            indices.append(int(m.span()[0]))
            indices.append(int(m.span()[1]))
            string = m.group(0)
            argsListRemove.remove(string)
    indices.append(len(wholeStr))


    for i in range(0,len(indices) - 1, 2):

        for y in range(0,2):
            subStr = splitByIndex(
                wholeStr,
                indices,
                i,
                y)
            if subStr in saneArgs:
                if isinstance(saneArgs[subStr] , bool):
                    keys.append(subStr)
                    values.append(True)
                    break
                else:
                    keys.append(subStr)
            else:
                values.append(subStr)

    for i in range(0, len(values)):
        values[i] = values[i].rstrip().lstrip()
    
    parts = dict(zip(keys, values))
    return parts
def splitByIndex(wholeStr, indices, first, second):
    l = indices[first+second]
    if indices[first+second+1]:
        r = indices[first+second+1]
    else:
        r = len(wholeStr)
    splitStr = wholeStr[l:r]
    return splitStr

def addToInv(userId, itemStr, argsList, saneArgValues):
    if userId not in inventoryDict.keys():
        return "You don't have an inventory! Run inv init to get one!"
    
    returnStr = ""
    
    pairedArgs = pairArgs(argsList, saneArgValues, itemStr)
    
    if '-p' not in pairedArgs.keys():
        pairedArgs['-p'] = False
    if '-b' not in pairedArgs.keys():
        pairedArgs['-b'] = ""
    if '-q' not in pairedArgs.keys():
        pairedArgs['-q'] = 1
    if '-w' not in pairedArgs.keys():
        pairedArgs['-w'] = 0

    isSane = invSanityCheck(pairedArgs, saneArgValues)

    if(isSane[0]):
            bag = pairedArgs['-b']
            item = pairedArgs['-i']
            itemQuant = pairedArgs['-q']
            isPublic = pairedArgs['-p']
            itemWorth = pairedArgs['-w']
            if item in list(inventoryDict[userId].keys()):
                inventoryDict[userId][item]["quantity"] += itemQuant
                inventoryDict[userId][item]["worth"] += inventoryDict[userId][item]["worth"]
            else:
                inventoryDict[userId][item] = {
                    "public":isPublic,
                    "quantity":itemQuant,
                    "bag":bag,
                    "worth":itemWorth
                }
                
            if inventoryDict[userId][item]["quantity"] > 1:
                total = inventoryDict[userId][item]["quantity"]
                returnStr += f"Added {itemQuant} {item}(s) to your inventory! (for a total of {total})"
            else:
                returnStr += f"Added {item} to your inventory!"
    else:
        returnStr += isSane[1]
    return returnStr

#TODO check if this works
def parseGpString(string):
    string = string.strip()
    coinType = string[-2:]
    coinAmount = string[:-2]
    copper = 0
    if coinType in ['gp', 'sp', 'cp']:
        coinInt = intTryParse(coinAmount)
        if coinInt[1]:
            copper = getCopper(coinInt[1], coinType)
    return convertCoin(copper)


def changeItemQuant(userId, bag, itemIndex, amount: int):
    global inventoryDict
    global quotes

    returnStr = ""

    itemName = [inventoryDict][0][userId][bag][itemIndex]["name"]
    itemQuantity = [inventoryDict][0][userId][bag][itemIndex]["quantity"]
    if itemQuantity >= 1 and amount < 0:
        if itemQuantity + amount < 0:
            del [inventoryDict][0][userId][bag][itemIndex]
            returnStr += f"Removed all of {itemName}(s) from {bag}! (originally had {itemQuantity}!)"
        else:
            newItemQuantity = [inventoryDict][0][userId][bag][itemIndex]["quantity"] + amount
            [inventoryDict][0][userId][bag][itemIndex]["quantity"] += amount
            returnStr += f"Removed {abs(amount)} {itemName}(s) from {bag}! (originally had {itemQuantity}!)"
    else:
        if amount < 1:
            del [inventoryDict][0][userId][bag][itemIndex]
            returnStr += f"Removed {itemName} from inventory!"
        else:
            newItemQuantity = [inventoryDict][0][userId][bag][itemIndex]["quantity"] + amount
            [inventoryDict][0][userId][bag][itemIndex]["quantity"] += amount
            returnStr += f"Added {amount} {itemName}(s) to {bag}! (originally had {itemQuantity})"
    return returnStr


def invSanityCheck(argsList, argsValues):
    if set(argsList.keys()) != set(argsValues):
        return False, "wuh oh"
    else:
        for arg in argsList.keys():
            print(argsList[arg])
            print(argsValues[arg])
            
            if type(argsValues[arg]) == int:
                if intTryParse(argsList[arg])[1]:
                    argsList[arg] = intTryParse(argsList[arg])[0]
                else:
                    return False, f"{argsList[arg]} needs to be an int!"

            elif type(argsList[arg]) != type(argsValues[arg]):
                if argsValues[arg] == bool:
                    return False, f"{argsList[arg]} needs to go last in command!"
                else:
                    return False, f"{argsList[arg]} needs to be {type(argsValues[arg])}"
                
    return True, "pass"




def intTryParse(value):
    try:
        return int(value), True
    except ValueError:
        return value, False



# Gets the user's inventoryDict
def getInv(userid, showPrivate = False):
    global inventoryDict
    print(inventoryDict)
    returnStr = f"<@{userid}>"
    inventoryUsers = list(inventoryDict.keys())
    dupeBags = []
    bags = []
    
    if(userid in inventoryUsers):
        returnStr += "'s inventory\n\n"
        dupeBags = [sub["bag"] for sub in inventoryDict[userid].values() if "bag" in sub.keys()]
        bags = list(set(dupeBags))
        bags = sorted(bags, key=lambda s: (not s, s))
        bagText = ""
        totalItemWorth = 0

        for (bag) in bags:
            if bag =="":
                returnStr += f"\t**Not in a bag**:\n"
            else:
                returnStr += f"\t**{bag}**:\n"
            for (item) in list(inventoryDict[userid].keys()):
                isItemPublic = inventoryDict[userid][item]["public"]
                itemQuantity = inventoryDict[userid][item]["quantity"]
                if bag == inventoryDict[userid][item]["bag"]:
                    if showPrivate:
                        totalItemWorth += inventoryDict[userid][item]["worth"]
                        if isItemPublic:
                            if itemQuantity == 1:
                                bagText += f"\t\t- {item}\n"
                            else:
                                bagText += f"\t\t- {item} ({itemQuantity})\n"
                        else:
                            if itemQuantity == 1:
                                bagText += f"\t\t- ||{item}||\n"
                            else:
                                bagText += f"\t\t- ||{item} ({itemQuantity})||\n"
                    else:
                        if isItemPublic:
                            totalItemWorth += inventoryDict[userid][item]["worth"]  
                            if itemQuantity == 1:
                                bagText += f"\t\t- {item}\n"
                            else:
                                bagText += f"\t\t- {item} ({itemQuantity})\n"
            if bagText == "":
                bagText += "\t\t-Bag is empty\n"
            returnStr += bagText
            bagText = ""
            totalCoin = convertCoin(totalItemWorth + coinPurseInCopper(coinDict[userid]))
            totalCoinStr = f"{'{:,.2f}'.format(totalCoin[0])}{totalCoin[1]}"

        returnStr += f"\n\tCurrently has {totalCoinStr} ({'{:,.2f}'.format(convertCoin(totalItemWorth)[0])}{convertCoin(totalItemWorth)[1]} in treasures)\n"
    else:
        returnStr += f" has no items..."
    return returnStr

def find_by_key(data, target):
    for key, value in data.items():
        if isinstance(value, dict):
            yield from find_by_key(value, target)
        elif key == target:
            yield value

@bot.group(aliases=["coin", "c"], pass_context=True)
async def coinCMD(ctx):
    trailingZeroes = ""
    returnStr = ""
    if ctx.invoked_subcommand is None:
        returnStr += getAllCoinStr(str(ctx.author.id))
        await ctx.channel.send(returnStr)

def getAllCoinStr(userid, isFull = False):
    global coinDict
    returnStr = "Coinpurse Contains:\n"
    formatStr = ""
    totalCoin = 0
    totalCoinCop = 0
    totalItemWorth = getTotalItemWorth(userid, isFull)

    for coin in coinDict[userid]["public"]:
        pubCoin = (coinDict[userid]["public"][coin],
        coin)
        privCoin = (coinDict[userid]["private"][coin],coin)
        totalCoin = (pubCoin[0], pubCoin[1]) if not isFull else (pubCoin[0]+privCoin[0], pubCoin[1])
        if totalCoin[0]> 0:
            returnStr += f"\t -{formatConvCoin(totalCoin)}\n"
    
    finishCoin = formatConvCoin(
        convertCoin(coinPurseInCopper(str(userid), isFull))
        )

    returnStr += f"For a total of {finishCoin}"
    if totalItemWorth > 0:
        totalCoinCop = coinPurseInCopper(
        userid, isFull
        )
        convertedWorth = formatConvCoin(convertCoin(totalItemWorth))
        completeWorth = formatConvCoin(convertCoin(totalItemWorth + coinPurseInCopper(userid, isFull)))
        returnStr += f"\n\nPlus an additional {convertedWorth} of treasures, for a grand sum of {completeWorth}."
    return returnStr
    

def formatConvCoin(coin):
    formatStr = ""
    if coin[0] % 1 == 0:
        formatStr += "{:,.0f}"
    else:
        formatStr += "{:,.2f}"
    return f"{formatStr.format(coin[0])}{coin[1]}"

def getTotalItemWorth(userId, isFull):
    global inventoryDict
    totalItemWorth = 0

    for (item) in list(inventoryDict[userId].keys()):
        isItemPublic = inventoryDict[userId][item]["public"]
        itemQuantity = inventoryDict[userId][item]["quantity"]
        bag = inventoryDict[userId][item]["bag"]

        if isFull:
            totalItemWorth += inventoryDict[userId][item] 
        else:
            if isItemPublic:
                totalItemWorth += inventoryDict[userId][item]["worth"]  
    return totalItemWorth

@coinCMD.command(name="-f", pass_context=True)
async def privCoinCMD(ctx):
    returnStr = ""
    returnStr += f"||You have {'{:,.2f}'.format(convertCoinPurse(str(ctx.author.id), True)[0])}{convertCoinPurse(str(ctx.author.id))[1]}||"
    await ctx.channel.send(returnStr)

@coinCMD.command(aliases=["add", "a"], pass_context=True)
async def addCoinCMD(ctx, amount, coin, private = "", user=None):
    returnStr = ""
    if not user:
        user = ctx.message.author
    userId = str(user.id)
    cointTryInt = intTryParse(amount)
    if not cointTryInt[1] or cointTryInt[0] < 0:
        returnStr += f"<@{userId}> You need to provide a valid positive int!"
    else:
        returnStr += modifyCoin(cointTryInt[0],coin,private,userId)
    await ctx.channel.send(returnStr)

@coinCMD.command(aliases=["remove", "r"], pass_context=True)
async def reCoinCMD(ctx, amount, coin, private = "", user=None):
    returnStr = ""
    if not user:
        user = ctx.message.author
    userId = str(user.id)
    cointTryInt = intTryParse(amount)
    if not cointTryInt[1]:
        returnStr += f"<@{userId}> You need to provide a valid int!"
    else:
        returnStr += modifyCoin((-1 * abs(cointTryInt[0])),coin,private,userId)
    await ctx.channel.send(returnStr)
    

def modifyCoin (amount, coin, private, userId):
    global coinDict
    returnStr = ""
    coinList = ["gp", "sp", "cp"]
    if amount < 0:
        returnStr += f"Removed {abs(amount)} "
    else:
        returnStr += f"Added {amount} "
    if coin not in coinList:
        returnStr += f"Coin needs to be gp, sp, or cp, not {coin}"
    else:
        if private == "-p":
            coinDict[userId]["private"][coin] += amount
            coinTotal = coinDict[userId]["private"][coin]
            returnStr += f"{coin} to your (private) coinpurse (total of {coinTotal}!)"
        else:
            coinDict[userId]["public"][coin] += amount
            coinTotal = coinDict[userId]["public"][coin]
            returnStr += f"{coin} to your coinpurse (total of {coinTotal}!)"
    print(coinDict[userId])
    return returnStr

def checkIfDm(ctx, user):
    isDmVar = False
    role = discord.utils.find(lambda r: r.name == 'DM', ctx.message.guild.roles)
    for serverRole in user.roles:
        if role.name.lower() == serverRole.name.lower():
            isDmVar = True
    return isDmVar

def getUser(ctx, userId):
    userClean = userId.strip('<@!>')
    user = discord.utils.find(lambda m: m.id == int(userClean), 
        ctx.message.channel.guild.members)
    return user


def convertCoinPurse(userId, showPrivate = False):
    global coinDict
    coinPurse = coinDict[userId]
    totalInCopper = coinPurseInCopper(coinPurse, showPrivate)
    returnTotal = convertCoin(totalInCopper)
    print(totalInCopper, returnTotal)
    print(round(returnTotal[0], 2))
    return (round(returnTotal[0],2), returnTotal[1])

def coinPurseInCopper(userId, showPrivate = False):
    global coinDict
    totalInCopper = 0
    selectedCoins = {
    "gp":coinDict[userId]["public"]["gp"],
    "sp":coinDict[userId]["public"]["sp"],
    "cp":coinDict[userId]["public"]["cp"]}
    if showPrivate:
        for coin in userId["private"]:
            selectedCoins[coin] += coinDict[userId]["private"][coin]
    totalInCopper += getCopper(selectedCoins["gp"], "gp")
    totalInCopper += getCopper(selectedCoins["sp"], "sp")
    totalInCopper += selectedCoins["cp"]
    return totalInCopper

def convertCoin(copper):
    returnTotal = ()
    if round(copper / 1000, 2) < 1:
        if round(copper / 100, 2) < 1:
            returnTotal = (copper, "cp")
        else:
            returnTotal = (copper / 100, "sp")
    else:
        returnTotal = (copper / 1000, "gp")
    return returnTotal

def getCopper(coin, yp):
    copper = 0
    if yp == "gp":
        copper = coin * 1000
    elif yp == "sp":
        copper = coin * 100
    else:
        copper = coin
    return copper
    




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
    onlyQuotes = iter(quotes.items())
    next(onlyQuotes)
    print("after found quotes summoning")
    for (qnum, quote) in onlyQuotes:
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
   if (n.lower() == "last"):
       n = list(quotes.keys())[-1]
       foundQuote = True
   else:
       for qnum in quotes.keys():
        if (n == qnum and n != "num"):
            foundQuote = True
            break
   if(foundQuote == True):
        new_quote_body = str(n) + ": " + new_quote_body
        quotes[str(n)] = new_quote_body
        update_db(quotes, "quotes.json")
        print("quote successfully edited!")
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
    print("before foundNSFW")
    foundNSFW = []
    onlyNsfw = iter(nsfwQuotes.items())
    next(onlyNsfw)
    print("after found quotes summoning")
    for (qnum, nsfwQuote) in onlyNsfw:
        if (found in nsfwQuote):
            foundNSFW.append(qnum)
            print("after every loop")
    if len(foundNSFW) == 0:
           await ctx.channel.send("couldn't find anything")
           print("after it failed to find anythin")
    elif len(foundNSFW) == 1:
           await ctx.channel.send(nsfwQuotes[foundNSFW[0]])
    elif len(foundNSFW) > 1 and len(foundNSFW) <= 10:
           await ctx.channel.send(nsfwQuotes[foundNSFW[0]] + " " + "Also found in the following nsfw quotes" + " " + ", ".join(foundNSFW[1:11]))
    elif len(foundNSFW) > 10:
           await ctx.channel.send(nsfwQuotes[foundNSFW[0]] + " " + "Also found in the following nsfw quotes" + " " + ", ".join(foundNSFW[1:11]) + " and many more....")
           print (quotes[foundNSFW[0]] )


@nsfwQuote.command(name="edit", aliases=["e"])
async def nsfwQuote_edit(ctx,n, name, *, body: str):
   new_nsfwQuote_body = f"<{name}> {body}"
   foundNsfwQuote = False
   print("before for loop")
   if (n.lower() == "last"):
       n = list(nsfwQuotes.keys())[-1]
       foundNsfwQuote = True
   else:
       for qnum in nsfwQuotes.keys():
        if (n == qnum and n != "num"):
            foundNsfwQuote = True
            break;
   if(foundNsfwQuote == True):
        new_nsfwQuote_body = str(n) + ": " + new_nsfwQuote_body
        nsfwQuotes[str(n)] = new_nsfwQuote_body
        update_db(nsfwQuotes, "nsfwQuotes.json")
        print("nsfw successfully edited!")
        await ctx.channel.send("The nsfw quote was sucessfully edited")
   if (foundNsfwQuote == False):
        await ctx.channel.send("couldnt find nsfw quote to edit")

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

@az.command(name="end", description="end the current game", aliases=["quit", "stop"])
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




##UNDERCUT

class UCPlayer:
    def __init__(self):
        self.points = 0
        self.lastNum = 0
        self.numCombo = 1
            
    def setPoints(self, points):
        self.points += points

class UnderCutGame:
    mode = ""
    def __init__(self, mode, user1, user2):
        self.mode = mode
        self.user1 = user1
        self.user2 = user2
        self.player1 = UCPlayer()
        self.player2 = UCPlayer()
        self.players = {user1 : self.player1, user2 : self.player2}
        self.playerSubmit = {user1 : 0, user2 : 0}
        self.game = True
        self.gameWon = False

    def calculate_points(self):
        points1 = self.playerSubmit[self.user1]
        points2 = self.playerSubmit[self.user2]
        self.playerSubmit[self.user1] = 0
        self.playerSubmit[self.user2] = 0

        returnString = ""

        if self.mode == "uc":
            if points1 != points2 - 1 and points1 != points2 + 1:
                self.players[self.user1].setPoints(points1)
                self.players[self.user2].setPoints(points2)
                returnString = f"{self.user1} gained {points1} points \n{self.user2} gained {points2} points"
            elif points1 > points2:
                self.players[self.user2].setPoints(points1 + points2)
                returnString = f"**UNDERCUT!!**\n{self.user2} gained {points2 + points1} points ({points1} stolen)"
            else:
                self.players[self.user1].setPoints(points1 + points2)
                returnString = f"**UNDERCUT!!**\n{self.user1} gained {points2 + points1} points ({points2} stolen)"
        
        elif self.mode == "flaunt":
            if self.players[self.user1].lastNum == points1:
                self.players[self.user1].numCombo += 1
            else:
                self.players[self.user1].numCombo = 1
                self.players[self.user1].lastNum = points1
                
            if self.players[self.user2].lastNum == points2:
                self.players[self.user2].numCombo += 1
            else:
                self.players[self.user2].numCombo = 1
                self.players[self.user2].lastNum = points2
            
            adjustedPoiints1 = points1 * self.players[self.user1].numCombo
            adjustedPoiints2 = points2 * self.players[self.user2].numCombo
            if points1 != points2 - 1 and points1 != points2 + 1:
                
                self.players[self.user1].setPoints(adjustedPoiints1)
                self.players[self.user2].setPoints(adjustedPoiints2)
                returnString = f"{self.user1} gained {adjustedPoiints1} points ({points1}x{self.players[self.user1].numCombo}) \n{self.user2} gained {adjustedPoiints2} points ({points2}x{self.players[self.user2].numCombo}) "
            
            elif points1 > points2:
                self.players[self.user2].setPoints(adjustedPoiints2 + adjustedPoiints1)
                returnString = f"**UNDERCUT!!**\n {self.user2} gained {adjustedPoiints2 + adjustedPoiints1}points ({points2}x{self.players[self.user2].numCombo}) + ({points1}x{self.players[self.user1].numCombo} stolen)"
                self.players[self.user1].numCombo = 1
            
            else:
                self.players[self.user1].setPoints(adjustedPoiints2 + adjustedPoiints1)
                returnString = f"**UNDERCUT!!**\n {self.user1} gained {adjustedPoiints2+adjustedPoiints1} points ({points1}x{self.players[self.user1].numCombo}) + ({points2}x{self.players[self.user2].numCombo} stolen)"
                self.players[self.user2].numCombo = 1
        
        elif self.mode == "flaunt2":
            if self.players[self.user1].lastNum == points1:
                self.players[self.user1].numCombo += 1
            else:
                self.players[self.user1].numCombo = 1
                self.players[self.user1].lastNum = points1
                
            if self.players[self.user2].lastNum == points2:
                self.players[self.user2].numCombo += 1
            else:
                self.players[self.user2].numCombo = 1
                self.players[self.user2].lastNum = points2
            
            adjustedPoiints1 = pow(points1,self.players[self.user1].numCombo)
            adjustedPoiints2 = pow(points2, self.players[self.user2].numCombo) 
            if points1 != points2 - 1 and points1 != points2 + 1:
                
                self.players[self.user1].setPoints(adjustedPoiints1)
                self.players[self.user2].setPoints(adjustedPoiints2)
                returnString = f"{self.user1} gained {adjustedPoiints1} points ({points1}^{self.players[self.user1].numCombo}) \n{self.user2} gained {adjustedPoiints2} points ({points2}^{self.players[self.user2].numCombo}) "
            
            elif points1 > points2:
                self.players[self.user2].setPoints(adjustedPoiints2 + adjustedPoiints1)
                returnString = f"**UNDERCUT!!**\n {self.user2} gained {adjustedPoiints2 + adjustedPoiints1}points ({points2}^{self.players[self.user2].numCombo}) + ({points1}^{self.players[self.user1].numCombo} stolen)"
                self.players[self.user1].numCombo = 1
            
            else:
                self.players[self.user1].setPoints(adjustedPoiints2 + adjustedPoiints1)
                returnString = f"**UNDERCUT!!**\n {self.user1} gained {adjustedPoiints2+adjustedPoiints1} points ({points1}^{self.players[self.user1].numCombo}) + ({points2}^{self.players[self.user2].numCombo} stolen)"
                self.players[self.user2].numCombo = 1
        
        elif self.mode == "flaunt3":
            if self.players[self.user1].lastNum == points1:
                self.players[self.user1].numCombo += 1
            else:
                self.players[self.user1].numCombo = 1
                self.players[self.user1].lastNum = points1
                
            if self.players[self.user2].lastNum == points2:
                self.players[self.user2].numCombo += 1
            else:
                self.players[self.user2].numCombo = 1
                self.players[self.user2].lastNum = points2
            
            adjustedPoiints1 = points1 + self.players[self.user1].numCombo - 1
            adjustedPoiints2 = points2 + self.players[self.user2].numCombo - 1
            if points1 != points2 - 1 and points1 != points2 + 1:
                
                self.players[self.user1].setPoints(adjustedPoiints1)
                self.players[self.user2].setPoints(adjustedPoiints2)
                returnString = f"{self.user1} gained {adjustedPoiints1} points ({points1}+{self.players[self.user1].numCombo}) \n{self.user2} gained {adjustedPoiints2} points ({points2}+{self.players[self.user2].numCombo}) "
            
            elif points1 > points2:
                self.players[self.user2].setPoints(adjustedPoiints2 + adjustedPoiints1)
                returnString = f"**UNDERCUT!!**\n {self.user2} gained {adjustedPoiints2 + adjustedPoiints1}points ({points2}+{self.players[self.user2].numCombo}) + ({points1}+{self.players[self.user1].numCombo} stolen)"
                self.players[self.user1].numCombo = 1
            
            else:
                self.players[self.user1].setPoints(adjustedPoiints2 + adjustedPoiints1)
                returnString = f"**UNDERCUT!!**\n {self.user1} gained {adjustedPoiints2+adjustedPoiints1} points ({points1}+{self.players[self.user1].numCombo}) + ({points2}+{self.players[self.user2].numCombo} stolen)"
                self.players[self.user2].numCombo = 1
        
        self.checkIfWon()
        returnString += "\n\n"+self.status()
        if self.gameWon == True:
            if self.players[self.user1].points > self.players[self.user2].points:
                returnString += f"\n\n***{self.user1} WON***"
            else:
                returnString += f"\n\n***{self.user2} WON***"
        return returnString

    def status(self):
        return f"@{self.user1}: {self.players[self.user1].points} points total\n@{self.user2}: {self.players[self.user2].points} points total"
    def checkIfWon(self):
        if self.players[self.user1].points >= 40 or self.players[self.user2].points >= 40:
            self.gameWon = True

@bot.event
async def on_reaction_add(reaction, user):
    global undercutGame
    global undercutMode
    global ucUsers

    if user == bot.user:
           # we do not want the bot to reply to itself
        return

    if undercutGame == None and reaction.emoji == '👍' and reaction.message.author == bot.user:
        if "undercut" in reaction.message.content:
            ucUsers.append(user)
            if len(ucUsers) == 2:
                undercutGame = UnderCutGame(undercutMode, ucUsers[0], ucUsers[1])
                await reaction.message.channel.send(f"**GAME: START**\n{undercutGame.status()}")

@bot.event
async def on_reaction_remove(reaction, user):
    global undercutGame
    global ucUsers
    if user == bot.user:
           # we do not want the bot to reply to itself
        return

    if undercutGame == None and reaction.emoji == '👍' and reaction.message.author == bot.user:
        if "undercut" in reaction.message.content:
            ucUsers.remove(user)
            pass


@bot.group(aliases=["uc"])
async def undercut(ctx):
    global undercutGame
    if ctx.invoked_subcommand is None:
        if (undercutGame):
            await ctx.channel.send(f"Current scores:\n{undercutGame.user1}: {undercutGame.player1.points}\n{undercutGame.user2}: {undercutGame.player2.points}")
        else: 
            gameJoin = await ctx.channel.send("Starting an undercut game. React to this message with 👍 to join!!")
            await gameJoin.add_reaction('👍')

@undercut.command(name="flaunt", aliases=["fl"])
async def ucFlaunt(ctx):
    global undercutMode
    global undercutGame
    undercutMode = "flaunt"
    
    if ctx.invoked_subcommand is None:
        if (undercutGame):
            await ctx.channel.send(f"Current scores:\n{undercutGame.user1}: {undercutGame.player1.points}\n{undercutGame.user2}: {undercutGame.player2.points}")
        else: 
            gameJoin = await ctx.channel.send("Starting an undercut (FLAUNT) game. React to this message with 👍 to join!!")
            await gameJoin.add_reaction('👍')

@undercut.command(name="flaunt2", aliases=["fl2"])
async def ucFlaunt2(ctx):
    global undercutMode
    global undercutGame
    undercutMode = "flaunt2"
    
    if ctx.invoked_subcommand is None:
        if (undercutGame):
            await ctx.channel.send(f"Current scores:\n{undercutGame.user1}: {undercutGame.player1.points}\n{undercutGame.user2}: {undercutGame.player2.points}")
        else: 
            gameJoin = await ctx.channel.send("Starting an undercut (FLAUNT 2) game. React to this message with 👍 to join!!")
            await gameJoin.add_reaction('👍')

@undercut.command(name="flaunt3", aliases=["fl3"])
async def ucFlaunt3(ctx):
    global undercutMode
    global undercutGame
    undercutMode = "flaunt3"
    
    if ctx.invoked_subcommand is None:
        if (undercutGame):
            await ctx.channel.send(f"Current scores:\n{undercutGame.user1}: {undercutGame.player1.points}\n{undercutGame.user2}: {undercutGame.player2.points}")
        else: 
            gameJoin = await ctx.channel.send("Starting an undercut (FLAUNT 3) game. React to this message with 👍 to join!!")
            await gameJoin.add_reaction('👍')

@undercut.command(name="end", aliases=["quit", "stop"])
async def ucEnd(ctx):
    global undercutGame
    if undercutGame:
        await ctx.send("Now closing Undercut game. Scores are \n" + undercutGame.status())
        undercutGame = None
    else:
        await ctx.send("There isnt an ongoing undercut game")

@undercut.command(name="help")
async def uc_help(ctx):
    await ctx.send("""`!undercut` starts a new game or lists the current scores
`!undercut flaunt` will start a game with flaunt rules
`!undercut flaunt2` will start a game with flaunt2 rules
`!undercut flaunt3` will start a game with flaunt3 rules
`!undercut end`  quits the currently running undercut game
`!undercut rules` explains the rules bewteen the different modes""")

@undercut.command(name="rules")
async def uc_rules(ctx):
    await ctx.send("""`undercut` basic game of undercut. Gamble points to earn and try to undercut your opponent's to steal their's instead.
`flaunt` Same as above, but if you pick the same number multiple times in a row your points will be multiplied by the number of times you picked the same number
`flaunt2` Same as above, but instead of it being multiplied it is brought to the power of your number combo. The 3rd time you gamble 2 you'll get 8 points for example.
`flaunt3` same as above, but instead your number combo is added to your points. """)

async def update_uc_game(bot,message):
    global undercutGame
    global playersSubmitted
    if (not undercutGame or ' ' in message.content.strip()):
        return
    
    bargin = message.content.strip('|')
    if bargin.isdigit():
        if message.author in undercutGame.players.keys():
            if int(bargin) >= 1 and int(bargin) <= 5:
                if undercutGame.playerSubmit[message.author] == 0:
                    undercutGame.playerSubmit[message.author] = int(bargin)
                    await message.delete()
                    playersSubmitted += 1
                    await message.channel.send("Got your bargain!")
                else:
                    await message.channel.send("You already submitted!")
            else:
                await message.channel.send("Invalid number! Please type a number between 1 and 5")

        else:
            await message.channel.send("You aren't playing!")
    if playersSubmitted == 2:
        playersSubmitted = 0
        await message.channel.send(undercutGame.calculate_points())
    
    if undercutGame.gameWon:
        global ucUsers
        await message.channel.send(f"GAME IS OVER...")
        ucUsers = []
        undercutGame = None
        


##POKEMON

class blindPokemon:
    # last is 898
    genList = [
        {
            "start":1,
            "end":151
        },
        {
            "start":152,
            "end":251
        },
        {
            "start":252,
            "end":386
        },
        {
            "start":387,
            "end":493
        },
        {
            "start":494,
            "end":649
        },
        {
            "start":650,
            "end":721
        },
        {
            "start":722,
            "end":807
        },
        {
            "start":808,
            "end":898
        }
    ]
    def pokeParse(self, pokeUrl):
        url = pokeUrl
        request = urllib.request.Request(url)
        request.add_header('User-Agent', 'cheese')
        data = urllib.request.urlopen(request).read()
        x = json.loads(data, object_hook=lambda d: SimpleNamespace(**d))
        return x
    #just check if [pokemon-name]-mega exists or not, and coinflip between them if it does
    def __init__(self, gen, time):
        self.gen = gen
        self.time = time
        if (self.gen):
            difference = self.genList[self.gen - 1]["end"] - self.genList[self.gen - 1]["start"] + 1

            print(difference)
            self.pokeRangeInt = (self.genList[self.gen - 1]["start"], self.genList[self.gen - 1]["end"]+1)
        else:
            self.pokeRangeInt = (0, 899)
        
        i = random.randrange(self.pokeRangeInt[0], self.pokeRangeInt[1])
        
        self.pokemon = pokebase.pokemon(i)
        #self.pokemon = pokebase.pokemon("meowth")

        if(len(self.pokemon.species.varieties) > 1):
            i = random.randint(0,len(self.pokemon.species.varieties)-1)
            self.pokemon = pokebase.pokemon(self.pokemon.species.varieties[i].pokemon.name)

        self.img = pokebase.SpriteResource('pokemon', self.pokemon.id, other_sprites=True, official_artwork=True)

        print(len(self.pokemon.species.varieties))
    

@bot.command(name="pokedraw", description="pokemon draw??")
async def pokedraw(ctx, gen = None, time = 60):

    error = None

    if(gen):
        genParsed = intTryParse(gen)
        if(genParsed[1] and genParsed[0] > 0 and genParsed[0] < 9):
            gen = genParsed[0]
        else:
            if (gen.lower() == "a" or gen.lower() == "all" or gen.lower() == "any"):
                gen = None
            else:
                error = "Invalid Gen Number!"
    timeParsed = intTryParse(time)
    
    if(not timeParsed[1]):
        error = "Invalid time!"
    elif(timeParsed[0] > 4 and timeParsed[0] < 500):
        time = timeParsed[0]
    else:
        error = "Either too short or too long!"

    if (error):
        await ctx.channel.send(error)
    else:

        msg = await ctx.channel.send("loading pokemon...")
        pokeBlind = blindPokemon(gen, time)
        
        await msg.edit(content="Loaded!!")
        second = pokeBlind.time
        embedVar = discord.Embed(title=pokeBlind.pokemon.name, color=0x206694)
        embedVar.add_field(name="timer", value=f"{second}", inline=False)
        embedVar.set_image(url="https://i.imgur.com/J5nOPP0.png")
        await msg.edit(embed=embedVar)
        while True:
                second -= 1
                if second == 0:
                    embedVar.set_image(url=pokeBlind.img.url)
                    embedVar.set_field_at(0, name="timer", value=f"finished", inline=False)
                    await msg.edit(embed=embedVar)
                    break
                embedVar.set_field_at(0, name="timer", value=f"{second}", inline=False)
                await msg.edit(embed=embedVar)
                await asyncio.sleep(1)
        

## Stole from https://stackoverflow.com/questions/2262333/is-there-a-built-in-or-more-pythonic-way-to-try-to-parse-a-string-to-an-integer
def intTryParse(value):
    try:
        return int(value), True
    except ValueError:
        return value, False









bot.run(config["token"])

