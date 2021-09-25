__all__ = [
    "testyfuncB", 
    "sumCopper",
    "getCoinAsCopper",
    "sumCopper",
    "getPurseAsCopper",
    "formatCoin",
    "getInv",
    "getUserInv",
    "checkDM",
    "addToInv"]
from os import X_OK
from typing import Tuple
import discord
import re
import json
from inspect import currentframe, getframeinfo

from discord import user
import DndAssets

"""
COINPURSE
            _                                   
   ___ ___ (_)_ __    _ __  _   _ _ __ ___  ___ 
  / __/ _ \| | '_ \  | '_ \| | | | '__/ __|/ _ \
 | (_| (_) | | | | | | |_) | |_| | |  \__ \  __/
  \___\___/|_|_| |_| | .__/ \__,_|_|  |___/\___|
                     |_|                        
"""
def sumCopper(copper):
    returnTotal = ()
    if round(copper / 1000, 2) < 1:
        if round(copper / 100, 2) < 1:
            returnTotal = (copper, "cp")
        else:
            returnTotal = (copper / 100, "sp")
    else:
        returnTotal = (copper / 1000, "gp")
    return returnTotal

def formatCoin(coin: Tuple):
    formatStr = ""
    if coin[0] % 1 == 0:
        formatStr += "{:,.0f}"
    else:
        formatStr += "{:,.2f}"
    return f"{formatStr.format(coin[0])}{coin[1]}"

def getCoinAsCopper(coin):
    copper = 0
    if coin[1] == "gp":
        copper = coin[0] * 1000
    elif coin[1] == "sp":
        copper = coin[0] * 100
    else:
        copper = coin[0]
    return copper

def getPurseAsCopper(userId: str, showFull = False):
    purseDict = DndAssets.purseDict
    totalInCopper = 0
    selectedCoins = {
    "gp":purseDict[userId]["public"]["gp"],
    "sp":purseDict[userId]["public"]["sp"],
    "cp":purseDict[userId]["public"]["cp"]}
    if showFull:
        for c in userId["private"]:
            selectedCoins[c] += purseDict[userId]["private"][c]
    totalInCopper += getCoinAsCopper(selectedCoins["gp"], "gp")
    totalInCopper += getCoinAsCopper(selectedCoins["sp"], "sp")
    totalInCopper += selectedCoins["cp"]
    return totalInCopper

def modPurse(amount: int, coinPiece: str,  userId: str, private = False):
    purseDict = DndAssets.purseDict
    returnStr = ""
    coin = ()
    visibility = ""
    censor = ""
    totalStr = ""
    if private:
        visibility = "private"
        censor = "||"
    else:
        visibility = "public"
    
    if userId in purseDict and coinPiece in DndAssets.coinPieceList:
        coin[1] = coinPiece
        purseDict[userId][visibility][coin[1]] += amount
        if purseDict[userId][visibility][coin[1]]< 0:
                purseDict[userId][visibility][coin[1]] = 0
        coin[0] = purseDict[userId][visibility][coin[1]]
        formattedCoin = formatCoin(coin)
        
        if amount < 0:
            returnStr += f"Removed {abs(amount)}{coin[1]}. Total {coin[1]} is now {censor}{formattedCoin}{censor}"
        else:
            returnStr += f"{amount}{coin[1]} added to your {visibility} coinpurse (total of {censor}{formattedCoin}{censor}!)"
    else:
        returnStr += "Somethings wrong;"

    DndAssets.purseDict = purseDict
    return returnStr

def sumItemWorth(userId: str, isFull: bool):
    invDict = DndAssets.inventoryDict
    totalItemWorth = 0

    for (item) in list(invDict[userId].keys()):
        isItemPublic = invDict[userId][item]["public"]
        itemStock = invDict[userId][item]["stock"]

        if isFull:
            totalItemWorth += invDict[userId][item]["worth"] * itemStock 
        else:
            if isItemPublic:
                totalItemWorth += invDict[userId][item]["worth"] * itemStock
    return totalItemWorth

def getFormattedWealth(userid: str, isFull = False):
    purseDict = DndAssets.purseDict
    returnStr = "Coinpurse Contains:\n"
    formatStr = ""
    totalCoin = ()
    totalCoinCop = 0
    totalItemWorth = sumItemWorth(userid, isFull)

    for coinPiece in DndAssets.coinPieceList:
        pubCoin = (purseDict[userid]["public"][coinPiece],
            coinPiece)

        privCoin = (purseDict[userid]["private"][coinPiece],
            coinPiece)
        
        totalCoin += (pubCoin[0], pubCoin[1]) if not isFull else (pubCoin[0]+privCoin[0], pubCoin[1])
        if totalCoin[0]> 0:
            returnStr += f"\t -{formatCoin(totalCoin)}\n"
    
    purseWorth = formatCoin(
        sumCopper(
            getPurseAsCopper(userid, 
                isFull))
        )

    returnStr += f"For a total of {purseWorth} in coin."
    if totalItemWorth > 0:
        purseInCopper = getPurseAsCopper(
        userid, isFull
        )
        formattedItemWorth = formatCoin(sumCopper(totalItemWorth))
        totalWealth = formatCoin(sumCopper(totalItemWorth + getPurseAsCopper(userid, isFull)))

        returnStr += f"\n\nCombined with {formattedItemWorth} of treasure in the inventory, total wealth is {totalWealth}."
    return returnStr

def parseCoinStr(coinStr):
    coin = ()
    coinStr = coinStr.strip()
    coin[0] = coinStr[-2:]
    coin[1] = coinStr[:-2]
    
    copper = 0
    if coin[1] in ['gp', 'sp', 'cp']:
        isInt = intTryParse(coin[0])
        if isInt[0]:
            coin[0] = isInt[1]
            copper = getCoinAsCopper(coin)
    return sumCopper(copper)






"""
INVENTORY
  ___                      _                   
 |_ _|_ ____   _____ _ __ | |_ ___  _ __ _   _ 
  | || '_ \ \ / / _ \ '_ \| __/ _ \| '__| | | |
  | || | | \ V /  __/ | | | || (_) | |  | |_| |
 |___|_| |_|\_/ \___|_| |_|\__\___/|_|   \__, |
                                         |___/ 
"""

# Gets the user's inventoryDict
def getInv(userid, showFull = False):
    invDict = DndAssets.inventoryDict
    returnStr = f"<@{userid}>"
    inventoryUsers = list(invDict.keys())
    dupeBags = []
    bags = []
    
    if(userid in inventoryUsers):
        returnStr += "'s inventory\n\n"
        dupeBags = [sub["bag"] for sub in invDict[userid].values() if "bag" in sub.keys()]
        bags = list(set(dupeBags))
        bags = sorted(bags, key=lambda s: (not s, s))
        bagText = ""
        totalItemWorth = 0
        itemBuffer = ""

        for (bag) in bags:
            bagText = ""

            if bag =="":
                returnStr += f"\t**Not in a bag**:\n"
            else:
                returnStr += f"\t**{bag}**:\n"
            for (item) in list(invDict[userid].keys()):
                isPublic = invDict[userid][item]["public"]
                itemStock = invDict[userid][item]["stock"]

                if bag == invDict[userid][item]["bag"]:
                    if showFull and not isPublic:
                        itemBuffer = "||"
                    else:
                        itemBuffer = ""
                    
                    bagText += f"\n\t\t- {itemBuffer}{item}{itemBuffer}"
                    if itemStock < 1:
                        bagText += f"({itemStock})"

            if bagText == "":
                bagText += "\n\t\t-*Bag is empty*"
            returnStr += bagText
            
            totalWealth = getFormattedWealth

        returnStr += f"\n{totalWealth}"
    else:
        returnStr += f" has no items..."
    return returnStr

def checkDM(ctx, user: discord.user):
    isDmVar = False
    role = discord.utils.find(lambda r: r.name == 'DM', ctx.message.guild.roles)
    for serverRole in user.roles:
        if role.name.lower() == serverRole.name.lower():
            isDmVar = True
    return isDmVar

def modItemStock(userId: str, item: str, amount: int):
    invDict = DndAssets.inventoryDict
    global quotes

    returnStr = ""

    itemName = [invDict][userId][item]
    itemStock = [invDict][userId][item]["stock"]
    bag = [invDict][userId][item]["bag"]
    if itemStock >= 1 and amount < 0:
        if itemStock + amount < 0:
            del [invDict][userId][item]
            returnStr += f"Removed all of {itemName}(s) from {bag}! (originally had {itemStock}!)"
        else:
            [invDict][userId][item]["stock"] += amount
            returnStr += f"Removed {abs(amount)} {itemName}(s) from {bag}! (originally had {itemStock}!)"
    else:
        if amount < 1:
            del [invDict][userId][item]
            returnStr += f"Removed {itemName} from inventory!"
        else:
            [invDict][userId][item]["stock"] += amount
            returnStr += f"Added {amount} {itemName}(s) to {bag}! (originally had {itemStock})"

    DndAssets.inventoryDict = invDict
    return returnStr

def validateArgs(argsDict, argsModels):
    if set(argsDict.keys()) == set(argsModels):
        for arg in argsDict.keys():
            if type(argsModels[arg]) == int:
                tmp = intTryParse(argsDict[arg])
                if tmp[1]:
                    argsDict[arg] = tmp[0]
                else:
                    return False, f"{argsDict[arg]} needs to be an int!"

            elif type(argsDict[arg]) != type(argsModels[arg]):
                return False, f"{argsDict[arg]} needs to be {type(argsModels[arg])}"
    else:
        return False, "wuh oh"
        
    return True, "Success!"

def combineArgs(argModels, wholeStr):
    indices= []
    keys = []
    values = []
    argsList = list(argModels.keys()).copy()
    argsListRemove = argsList.copy()

    #split by arguments
    for i in range (0, len(argsList)):
        p = re.compile('|'.join(argsListRemove))
        m = p.search(wholeStr)
        if m:
            indices.append(int(m.span()[0]))
            indices.append(int(m.span()[1]))
            argsListRemove.remove(m.group(0))
    
    #indices.append(len(wholeStr))

    ##TODO removed a -1 to len, add it back and uncomment above if it breaks
    for i in range(0,len(indices), 2):

        for y in range(0,2):
            subStr = splitByIndex(
                wholeStr,
                indices,
                i,
                y)
            if subStr in argModels:
                if isinstance(argModels[subStr] , bool):
                    keys.append(subStr)
                    values.append(True)
                    break
                else:
                    keys.append(subStr)
            else:
                values.append(subStr)

    for i in range(0, len(values)):
        values[i] = values[i].rstrip().lstrip()
    
    argsDict = dict(zip(keys, values))
    return argsDict

def addToInv(ctx, userId, itemStr, argModels):
    invDict = DndAssets.inventoryDict
    returnStr = ""

    if userId not in invDict.keys():
        return "You don't have an inventory! Run inv init to get one!"
    
    combinedArgs = combineArgs(argModels, itemStr)
    
    if '-p' not in combineArgs.keys():
        combineArgs['-p'] = False
    if '-b' not in combineArgs.keys():
        combineArgs['-b'] = ""
    if '-q' not in combineArgs.keys():
        combineArgs['-s'] = 1
    if '-w' not in combineArgs.keys():
        combineArgs['-w'] = 0
    if '-u' not in combineArgs.keys():
        combineArgs['-u'] = ""
    
    if combineArgs['-u'] != "":
        if combineArgs['-u'] in list(invDict.keys()) and checkDM(
                ctx, ctx.message.author): 
            userId = combineArgs['-u']
        else:
            return errorWhoops(getframeinfo(currentframe()))

    validateResult = validateArgs(combineArgs, argModels)
    isValid = validateResult[0]
    if isValid:
        validArgs = validateResult[1]

        bag = validArgs['-b']
        item = validArgs['-i']
        itemStock = validArgs['-s']
        isPublic = validArgs['-p']
        itemWorth = validArgs['-w']
        
        if item in list(invDict[userId].keys()):
            invDict[userId][item]["stock"] += itemStock
            #This is adding its worth to itself
            invDict[userId][item]["worth"] += invDict[userId][item]["worth"]
        else:
            invDict[userId][item] = {
                "public":isPublic,
                "stock":itemStock,
                "bag":bag,
                "worth":itemWorth
            }
            
        if invDict[userId][item]["stock"] > 1:
            total = invDict[userId][item]["stock"]
            returnStr += f"Added {itemStock} {item}(s) to your inventory! (for a total of {total})"
        else:
            returnStr += f"Added {item} to your inventory!"
    else:
        returnStr += validateResult[1]
    return returnStr

def splitByIndex(wholeStr, indices, first, second):
    l = indices[first+second]
    if indices[first+second+1]:
        r = indices[first+second+1]
    else:
        r = len(wholeStr)
    splitStr = wholeStr[l:r]
    return splitStr

def getUserInv(ctx, userStr:str, showFull = False):
    returnStr = ""
    argModels = {"-u":str}
    userId = combineArgs(argModels, userStr)["-u"]


    returnStr += getInv(str(userId), showFull)

"""
  __  __ ___ ____   ____ 
 |  \/  |_ _/ ___| / ___|
 | |\/| || |\___ \| |    
 | |  | || | ___) | |___ 
 |_|  |_|___|____/ \____|
                         
"""

def errorWhoops(frameinfo):
    return f"Hhhuh something wrong {frameinfo.filename} {frameinfo.lineno}"
def testyfuncA():
    return(f"class work!!!")

def intTryParse(value):
    try:
        return int(value), True
    except ValueError:
        return value, False

def findByKey(data, target):
    for key, value in data.items():
        if isinstance(value, dict):
            yield from findByKey(value, target)
        elif key == target:
            yield value

def getUser(ctx, userId: str):
    userClean = userId.strip('<@!>')
    user = discord.utils.find(lambda m: m.id == int(userClean), 
        ctx.message.channel.guild.members)
    return user
