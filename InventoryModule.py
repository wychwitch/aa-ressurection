__all__ = [
    "sumCopper",
    "getCoinAsCopper",
    "sumCopper",
    "getPurseAsCopper",
    "formatCoin",
    "getInv",
    "getUserInv",
    "checkDM",
    "addToInv",
    "cleanUserMention",
    "getFormattedWealth",
    "userInit",
    "removeItem",
    "tryRemove",
    "togItemVisibility",
    "togBagItemVisibility",
    "tryHideCommand",
    "tryMove",
    "modPurse",
    "processModCoin",
    "testyfunc"
    ]
from os import X_OK
from typing import Tuple
import discord
import re
from inspect import currentframe, getframeinfo
import argparse

from discord import user
from discord.ext.commands.core import after_invoke
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
    "cp":purseDict[userId]["public"]["cp"]
    }
    if showFull:
        for c in purseDict[userId]["private"]:
            selectedCoins[c] += purseDict[userId]["private"][c]
    totalInCopper += getCoinAsCopper((selectedCoins["gp"], "gp"))
    totalInCopper += getCoinAsCopper((selectedCoins["sp"], "sp"))
    totalInCopper += selectedCoins["cp"]
    return totalInCopper

def modPurse(userId, coin, private = False):
    purseDict = DndAssets.purseDict
    returnStr = ""
    visibility = ""
    censor = ""
    if private:
        visibility = "private"
        censor = "||"
    else:
        visibility = "public"
    
    if userId in list(purseDict.keys()):
        purseDict[userId][visibility][coin[1]] += coin[0]
        remainingCoin = (purseDict[userId][visibility][coin[1]], coin[1])
        formattedCoin = formatCoin(remainingCoin)
        if coin[0] < 0:
            returnStr += f"Removed {abs(coin[0])}{coin[1]}. Total {coin[1]} is now {censor}{formattedCoin}{censor}"
        else:
            returnStr += f"{coin[0]}{coin[1]} added to your {visibility} coinpurse (total of {censor}{formattedCoin}{censor}!)"
    else:
        returnStr += "Somethings wrong;"
    DndAssets.purseDict = purseDict
    return returnStr

def sumItemWorth(userId: str, isFull: bool):
    invDict = DndAssets.inventoryDict
    totalItemWorth = 0

    for (item) in list(invDict[userId].keys()):
        isItemPrivate = invDict[userId][item]["private"]
        itemStock = invDict[userId][item]["stock"]
        itemWorth = invDict[userId][item]["worth"]

        if isItemPrivate:
            if isFull:
                totalItemWorth += itemWorth * itemStock 
        else:
            totalItemWorth += itemWorth * itemStock
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

        if isFull:
            totalCoin = (pubCoin[0]+privCoin[0], pubCoin[1])
        else:
            totalCoin = (pubCoin[0], pubCoin[1])
            
        if totalCoin[0]> 0:
            returnStr += f"\t -{formatCoin(totalCoin)}\n"
    
    purseWorth = formatCoin(
        sumCopper(
            getPurseAsCopper(userid, 
                isFull))
        )
    if returnStr == "\nCoinpurse Contains:":
        returnStr += " Nothing :(\n"
    else:
        returnStr += f"\nFor a total of {purseWorth} in coin."
    if totalItemWorth > 0:
        purseInCopper = getPurseAsCopper(
        userid, isFull
        )
        formattedItemWorth = formatCoin(sumCopper(totalItemWorth))
        totalWealth = formatCoin(sumCopper(totalItemWorth + getPurseAsCopper(userid, isFull)))

        returnStr += f"\nCombined with {formattedItemWorth} of treasure in the inventory, total wealth is {totalWealth}."
    return returnStr

def processModCoin(userId, commandStr, argModels, isRemove= False):

    combinedArgs  = combineArgs(argModels, commandStr)

    if '-p' not in combinedArgs.keys():
        combinedArgs['-p'] = False
    if '-u' not in combinedArgs.keys():
        combinedArgs['-u'] = ""
    if combinedArgs['-u'] != "":
        pass

    coin = parseCoinStr(combinedArgs['-c'])
    if coin != (0, 'np'):
        if isRemove:
            coin = (coin[0] * -1, coin[1])
        return modPurse(userId, coin, combinedArgs['-p'])
    else:
        return f"{combinedArgs['-c']} is not a valid coin!"

def parseCoinStr(coinStr):
    
    coinStr = coinStr.strip()
    coin = (coinStr[:-2],coinStr[-2:])
    
    copper = 0
    if coin[1] in ['gp', 'sp', 'cp']:
        isInt = intTryParse(coin[0])
        if isInt[1]:
            coin = (isInt[0], coin[1])

            return coin
        else:
            return (0, 'np')
    else:
        return (0, 'np')

def divideItemWorth(totalWorth: int, totalStock: int):
    return totalWorth / totalStock

def depositCoin(userId:str, coin:tuple, toPrivate = False):
    purseDict = DndAssets.purseDict
    purseTo = ""
    purseFrom = ""
    if toPrivate:
        purseTo = "private"
        purseFrom = "public"
    else:
        purseTo = "public"
        purseFrom = "private"
    
    purseCoin = (purseDict[userId][purseFrom][coin[1]], coin[1])
    
    if coin[0] > purseCoin[0]:
        return f"You don't have {formatCoin(coin)} to move! You have {formatCoin(purseCoin)}"
    purseCoin[0] -= coin[0]
    purseDict[userId][purseFrom][purseCoin[1]] = purseCoin[0]
    purseDict[userId][purseTo][purseCoin[1]] += coin[0]
    totalCoin = purseDict[userId][purseTo][purseCoin[1]]
    
    DndAssets.purseDict = purseDict
    return f"Moved {formatCoin(coin)} from {purseFrom} to {purseTo} (it now hjas {formatCoin(totalCoin)}"

def convertCoin(userId, coin, convertTo, isPrivate = False):
    purseDict = DndAssets.purseDict
    coinRates = DndAssets.coinRates
    visibility = ""
    coinPieceList =  DndAssets.coinPieceList
    convertedCoin = ()
    if isPrivate:
        visibility = "private"
    else:
        visibility = "public"

    if canAfford(userId, coin, visibility):
        if coinPieceList.index(coin[1]) < coinPieceList.index(coinPieceList):
            result = coin[0] / coinRates[convertTo]
            if result % 1 == 0:
                purseDict[userId][visibility][coin[1]] -= result
                purseDict[userId][visibility][convertTo] += result
                DndAssets.purseDict = purseDict
                return f"Successfully converted {coin[0]}{coin[1]} into {result} "
            else:
                return "Could not convert evenly!"
        else:
            return "What the fuck kinda coin are you converting"
    else:
        return "You cannot afford to convert this!"

def canAfford(userId, coin, visibility):
    purseDict = DndAssets.purseDict
    if purseDict[userId][visibility][coin[1]] - coin[0] < 0:
        return False
    else:
        return True

def processConvertCoin():
    pass 

def processDepositCoin():
    pass





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
    bagIds = DndAssets.bagIds
    returnStr = f"<@{userid}>"
    inventoryUsers = list(invDict.keys())
    dupeBags = []
    bags = []
    
    if(userid in inventoryUsers):
        returnStr += "'s inventory\n"
        dupeBags = [sub["bag"] for sub in invDict[userid].values() if "bag" in sub.keys()]
        bags = list(set(dupeBags))
        bags = sorted(bags, key=lambda s: (not s, s))
        bagText = ""
        totalItemWorth = 0
        itemBuffer = ""

        for (bag) in bags:
            bagText = ""

            if bag =="":
                returnStr += f"\n\t**Not in a bag**:"
            else:
                returnStr += f"\n\t**({bagIds[userid][bag]}){bag}**:"
            for (item) in list(invDict[userid].keys()):
                isPrivate = invDict[userid][item]["private"]
                itemStock = invDict[userid][item]["stock"]
                itemWorth = invDict[userid][item]["worth"]

                if bag == invDict[userid][item]["bag"]:
                    if isPrivate:
                        if showFull:
                            bagText += f"\n\t\t- ||{item}"
                            if itemStock > 1:
                                bagText += f"({itemStock})||"
                            else:
                                bagText += f"||"
                            if itemWorth > 0:
                                bagText += f"\n\t\t\t- ||Worth {formatCoin(sumCopper(itemWorth))}||"
                    else:
                        bagText += f"\n\t\t- {item}"
                        if itemStock > 1:
                                bagText += f"({itemStock})"
                        if itemWorth > 0:
                                bagText += f"\n\t\t\t- Worth {formatCoin(sumCopper(itemWorth))}"
                    
                    
                    

            if bagText == "":
                bagText += "\n\t\t-*Bag is empty*"
            returnStr += bagText
            
            totalWealth = getFormattedWealth(userid, showFull)

        returnStr += f"\n{totalWealth}"
    else:
        returnStr += f" has no items..."
    return returnStr

def checkDM(ctx, userName):
    isDmVar = False
    user = getUser(ctx, userName)
    role = discord.utils.find(lambda r: r.name == 'DM', ctx.message.guild.roles)
    for serverRole in user.roles:
        if role.name.lower() == serverRole.name.lower():
            isDmVar = True
            break
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
    if set(argsDict.keys()) == set(argsModels.keys()):
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
        
    return True, argsDict

#in arg models, --bulk would be a list object
def combineArgs(argModels, wholeStr, bulkKeyMatch = ("--bulk","-i"), listMode = False):
    indices= []
    keys = []
    values = []
    bulkValues = ()
    subStr = ""
    lastPos = 0
    argsList = list(argModels.keys()).copy()
    if '--bulk' in wholeStr:
        bulkIndex = argsList.index("--bulk")
        argsList.insert(0, argsList.pop(bulkIndex))
        values.append([])
    else:
        bulkKeyMatch = ("---","---")

    if listMode:
        for i in range (0, wholeStr.count(bulkKeyMatch[1])):
            argsList.append(bulkKeyMatch[1])
        for i in range (0, len(argsList)):
            argsList[i] = f"{argsList[i]}"
    argsListRemove = argsList.copy()
    
        
    #split by arguments
    for i in range (0, len(argsList)):
        p = re.compile('|'.join(argsListRemove))
        m = p.search(wholeStr, lastPos)
        if m:
            indices.append(int(m.span()[0]))
            indices.append(int(m.span()[1]))
            lastPos = int(m.span()[1])
            argsListRemove.remove(m.group(0))
    

    #indices.append(len(wholeStr))
    ##TODO removed a -1 to len, add it back and uncomment above if it breaks
    ##critical TODO FIX HOLY SHIT ITS BROKE
    for i in range(0,len(indices)):
        for y in range(0,1):
            subStr = splitByIndices(
                wholeStr,
                indices,
                i,
                y)
            if subStr.isspace() or subStr == '':
                break
            elif subStr in list(argModels.keys()):
                if isinstance(argModels[subStr] , bool):
                    keys.append(subStr)
                    values.append(True)
                    break
                elif subStr == bulkKeyMatch[1]:
                    break
                else:
                    keys.append(subStr)
            else:
                if keys[-1] == "--bulk":
                    values[-1].append(subStr.rstrip().lstrip())
                else:
                    values.append(subStr.rstrip().lstrip())
    

    argsDict = dict(zip(keys, values))
    return argsDict

#TODO but like low priority, split this into 2 functions, one that validates and one that actually removes w/o checking
def addItem(userId, itemName, itemValues):
    invDict = DndAssets.inventoryDict
    item = isItemInInv(userId, itemName)
    bagText = ""
    if item[0]:
        invDict[userId][item[1]]["stock"] += itemValues["itemStock"]
        #This is adding its worth to itself
        singleItemWorth = divideItemWorth(invDict[userId][item[1]]["worth"], invDict[userId][item[1]]["stock"])
        invDict[userId][item[1]]["worth"] = itemValues["-s"] * singleItemWorth
    else:
        bag = isBagInInv(userId, itemValues["-b"])
        bagText += bag[1]
        invDict[userId][item[1]] = {
            "private":itemValues["-p"],
            "stock":itemValues["-s"],
            "bag":bag[1],
            "worth":getCoinAsCopper(parseCoinStr(itemValues["-w"]))
        }
    if bagText == "":
        bagText = "the inventory"
    return f"Added {item[1]} to {bagText}!\n"

def addToInv(ctx, userId, itemStr, argModels):
    invDict = DndAssets.inventoryDict
    bagIds = DndAssets.bagIds
    
    returnStr = ""

    listMode = True

    bulkKeyPair = ()

    listMode = False

    if userId not in invDict.keys():
        return "You don't have an inventory! Run inv init to get one!"
    if re.search('--bulk', itemStr):
        listMode = True
    
    combinedArgs = combineArgs(argModels, itemStr, ('--bulk', '-i'), listMode)
    
    # change validateArgs logic so this whole block isnt needed
    if '-p' not in combinedArgs.keys():
        combinedArgs['-p'] = False
    if '-b' not in combinedArgs.keys():
        combinedArgs['-b'] = ""
    if '-s' not in combinedArgs.keys():
        combinedArgs['-s'] = 1
    if '-w' not in combinedArgs.keys():
        combinedArgs['-w'] = "0cp"
    if '-u' not in combinedArgs.keys():
        combinedArgs['-u'] = ""
    if '-i' not in combinedArgs.keys():
        combinedArgs['-i'] = ""
    if '--bulk' not in combinedArgs.keys():
        combinedArgs['--bulk'] = []
    else:
        combinedArgs['-i'] = "-i"
    
    if combinedArgs['-u'] != "":
        combinedArgs['-u'] = combinedArgs['-u'].strip('<@!>')
        if combinedArgs['-u'] in list(invDict.keys()) and checkDM(
                ctx, ctx.message.author): 
            userId = combinedArgs['-u']
        else:
            return errorWhoops(getframeinfo(currentframe()))

    validateResult = validateArgs(combinedArgs, argModels)
    isValid = validateResult[0]
    if isValid:
        validArgs = validateResult[1]
        if len(validArgs['--bulk']) > 0:
            for item in validArgs['--bulk']:
                returnStr += setUpItem(userId, item, validArgs)
        else:
            item = validArgs['-i']
            addItem(userId, item, validArgs)

        if invDict[userId][item]["stock"] > 1:
            total = invDict[userId][item]["stock"]
            returnStr += f"Added {item}(s) to your inventory! (for a total of {total})"
        else:
            returnStr += f"Added {item} to your inventory!"
    else:
        returnStr += validateResult[1]
    DndAssets.inventoryDict = invDict
    return returnStr

def splitByIndices(wholeStr, indices, first, second):
    l = indices[first+second]
    if first+second+1 in range (0, len(indices)):
        r = indices[first+second+1]
    else:
        r = len(wholeStr)
    splitStr = wholeStr[l:r]
    return splitStr

def setUpItem(userId, itemName, validArgs):
    bag = validArgs['-b']
    itemStock = validArgs['-s']
    isPrivate = validArgs['-p']
    itemWorth = getCoinAsCopper(parseCoinStr(validArgs['-w']))
    itemValues = {
        "bag":bag,
        "itemStock":itemStock,
        "isPrivate":isPrivate,
        "itemWorth":itemWorth
    }
    return addItem(userId, itemName, itemValues)

##TODO what is this. Was this supposed to be used with dm?? Why ctx??
def getUserInv(ctx, userId:str, showFull = False):
    returnStr = ""

    returnStr += getInv(str(userId), showFull)
    return returnStr

# TODO rename this
def tryRemove(ctx, userId, remStr, argModels):
    invDict = DndAssets.inventoryDict
    if userId not in invDict.keys():
        return "You don't have an inventory! Run inv init to get one!"

    combinedArgs = combineArgs(argModels, remStr)

    if '-u' not in combinedArgs.keys():
        combinedArgs['-u'] = ""
    if '-s' not in combinedArgs.keys():
        combinedArgs['-s'] = 1
    if '-b' not in combinedArgs.keys():
        combinedArgs['-b'] = "---"
    if '-i' not in combinedArgs.keys():
        combinedArgs['-i'] = "str"
    isValidArgs = validateArgs(combinedArgs, argModels)

    if isValidArgs[0]:
        validArgs = isValidArgs[1]
        if validArgs['-u'] != "":
            validArgs['-u'] = cleanUserMention(validArgs['-u'])
            if checkDM(ctx, userId):
                if validArgs['-u'] in list(invDict.keys()):
                    userId = validArgs['-u']
            else:
                return "You aren't the dm"
        if combinedArgs['-b'] != "---":
            return removeBag(userId, combinedArgs['-b'])
        else:
            return removeItem(userId, validArgs['-i'],validArgs['-s'])

# Only assumes valid userId
def removeItem(userId, itemName, amount= 1, isAll = False):
    invDict = DndAssets.inventoryDict
    returnStr = ""
    item = isItemInInv(userId, itemName)
    if item[0]:
        bag = invDict[userId][itemName]["bag"]
        invDict[userId][item[1]]["stock"] -= amount
        stock = invDict[userId][itemName]["stock"]
        if stock<=0 or isAll:
            del invDict[userId][item[1]]
            DndAssets.inventoryDict = invDict
            returnStr = f"Removed all of {item[1]} from {bag}!"
        else:
            returnStr = f"Removed {amount} {item[1]}(s) from {bag}! (there is {stock} left)."
        DndAssets.inventoryDict = invDict
    else:
        returnStr = f"You don't have {item[1]} in your inventory!"
    return returnStr

def isItemInInv(userId, itemName):
    invDict = DndAssets.inventoryDict
    onlyItems = list(invDict[userId].keys())
    for i in range(len(onlyItems)):
        if itemName == onlyItems[i].lower():
            return True, onlyItems[i]
    return False, itemName

def togItemVisibility(userId, itemName, isPrivate):
    invDict = DndAssets.inventoryDict
    returnStr = ""
    item = isItemInInv(userId, itemName)
    if item[0]:
        invDict[userId][item[1]]["private"] = isPrivate
        DndAssets.inventoryDict = invDict 
        if invDict[userId][item[1]]["private"]:
            returnStr = f"You hid {item[1]}!"
        else:
            returnStr = f"You unhid {item[1]}!"
    return returnStr

def tryHideCommand(userId, target, targetName, isPrivate):
    invDict = DndAssets.inventoryDict
    replyStr = ""
    if userId not in invDict.keys():
        replyStr += "You don't have an inventory! Run inv init to get one!"
    else:
        if target == '-i':
            replyStr += togItemVisibility(userId, targetName, isPrivate)
        elif target == '-b':
            replyStr += togBagItemVisibility(userId, targetName, isPrivate)
    return replyStr

def tryMove(userId, movStr, argModels):
    invDict = DndAssets.inventoryDict
    if userId not in list(invDict.keys()):
        return "You dont have an inventory! Run init"
    returnStr = ""
    
    combinedArgs = combineArgs(argModels, movStr)

    if not '-t' in (combinedArgs.keys()):
        combinedArgs['-t'] = ""
    if not '-i' in (combinedArgs.keys()):
        combinedArgs['-i'] = ""
    if not '-f' in (combinedArgs.keys()):
        combinedArgs['-f'] = ""

    if combinedArgs['-i'] == "" and combinedArgs['-f'] == "":
        return "You need to specify an item or a bag!"
    elif combinedArgs['-i'] != "":
        item = isItemInInv(userId, combinedArgs['-i'])
        if item[0]:
            if combinedArgs['-t'] == "":
                bag = isBagInInv(userId, combinedArgs['-t'])
                dupeBags = [sub["bag"] for sub in invDict[userId].values() if "bag" in sub.keys()]
                bags = list(set(dupeBags))
                for bagg in bags:
                    if invDict["userId"][item[1]][bagg] == bag[1]:
                        returnStr += f"\n{moveItem(userId, item[1], bag)}"
            else:
                bag = isBagInInv(userId, combinedArgs['-t'])
                returnStr += moveItem(userId, item[1], bag[1])                
        else:
            returnStr += f"You don't have {item[1]}!"
    elif combinedArgs['-f'] != "":
        bagOne = isBagInInv(userId, combinedArgs['-f'])
        if bagOne[0]:
            bagTwo = isBagInInv(userId, combinedArgs['-t'])
            returnStr += dumpBag(userId, bagOne, bagTwo)
    else:
        returnStr += "whayuh"
            
    return returnStr
        

def dumpBag(userId, fromBag, toBag):
    invDict = DndAssets.inventoryDict
    movedItems = ""
    returnStr = ""
    toBagText = f"to {toBag[1]}!"
    if toBag == "":
        toBagText = "out of your bag!"
    for item in invDict[userId]:
        if invDict[userId][item]["bag"] == fromBag[1]:
            movedItems += f"\n\t-{item}"
            invDict[userId][item]["bag"] = toBag[1]
    return f"Moved the following items {toBagText} {movedItems}"
    

    ## in this code discover if moving single item or dumping bag, and behave appropriately


def moveItem(userId, item, bag = ""):
    invDict = DndAssets.inventoryDict
    oldBag = invDict[userId][item]["bag"]
    if bag != "":
        invDict[userId][item]["bag"] = bag
        DndAssets.inventoryDict = invDict 
        return f"Moved {item} from {oldBag} to {bag}!"
    else:
        invDict[userId][item]["bag"] = ""
        DndAssets.inventoryDict = invDict 
        return f"Dumped {item} out of {oldBag}!"

def removeBag(userId, bagName):
    invDict = DndAssets.inventoryDict
    bag = isBagInInv(userId, bagName)
    if bag[0]:
        for item in list(invDict[userId].keys()):
            if invDict[userId][item]["bag"] == bag[1]:
                invDict[userId][item]["bag"] = ""
        DndAssets.inventoryDict = invDict
        return f"Dumped all items from {bagName}!"
    else:
        return "Couldn't find bag..."

def togBagItemVisibility(userId, bag, isPrivate = True):
    invDict = DndAssets.inventoryDict
    visiText = ""
    if isPrivate:
        visiText = "hidden"
    else:
        visiText = "unhidden"
    isBag = isBagInInv(userId, bag)

    if isBag[0]:
        for item in list(invDict[userId].keys()):
            if invDict[userId][item]["bag"] == isBag[1]:
                invDict[userId][item]["private"] = isPrivate
                DndAssets.inventoryDict = invDict
        return f"All items in {isBag[1]} are now {visiText}!"
    else:
        return "Whoops!"

def getBagId(userId, bagName):
    bagIds = DndAssets.bagIds
    bagId = 0
    foundId = False
    for bag in bagIds[userId]:
        if bagName == str((bag.key())):
            bagId = bag
            foundId = True, bag
            break


    return foundId, bagId

def getBagById(userId, bagId):
    bagIds = DndAssets.bagIds
    foundName = (False, "")
    if userId in list(bagIds.keys()):
        for bag in list(bagIds[userId].keys()):
            if bag == bagId:
                foundName = (True, bag)
                break
    return foundName

def isBagInInv(userId, bag):
    invDict = DndAssets.inventoryDict
    isBagInt = intTryParse(bag)
    foundBag = (False, bag)
    if isBagInt[1]:
        foundBag = getBagById(userId, bag)
    else:
        dupeBags = [sub["bag"] for sub in invDict[userId].values() if "bag" in sub.keys()]
        bags = list(set(dupeBags))
        for bagName in bags:
            if bag.lower() == bagName.lower():
                foundBag = (True, bagName)
        if not foundBag[0]:
            addNewBagId(userId, bag)
    return foundBag
    
def addNewBagId(userId, bag):
    bagIds = DndAssets.bagIds
    bagIds[userId]["--bagNum"] +=1
    bagIds[userId][bag] = bagIds[userId]["--bagNum"]
    DndAssets.bagIds = bagIds



"""
  __  __ ___ ____   ____ 
 |  \/  |_ _/ ___| / ___|
 | |\/| || |\___ \| |    
 | |  | || | ___) | |___ 
 |_|  |_|___|____/ \____|
                         
"""

def errorWhoops(frameinfo):
    return f"Hhhuh something wrong {frameinfo.filename} {frameinfo.lineno}"

def testyfunc(string):
    parser = NoExitParser(description="what is this desc")
    parser.add_argument("-t", help="test help", nargs='+', action=MyAction)
    parser.add_argument("-b", help="test help!!!", nargs='+', action=MyAction)
    huh = parser.parse_args(string.split())
    return(f"THIS IS THE T'S VALUE:{huh.t} THIS IS THE B'S VALUE:{huh.b}")

def intTryParse(value):
    if value != '':
        try:
            return int(value), True
        except ValueError:
            return value, False
    else:
        return value, False

def findByKey(data, target):
    for key, value in data.items():
        if isinstance(value, dict):
            yield from findByKey(value, target)
        elif key == target:
            yield value

def getUser(ctx, rawUser: str):
    userId = cleanUserMention(rawUser)
    user = discord.utils.find(lambda m: m.id == int(userId), 
        ctx.message.channel.guild.members)
    return user

def cleanUserMention(userStr: str):
    userId = userStr.strip('<@!>')
    return userId

def userInit(userId: str):
    invDict = DndAssets.inventoryDict
    purseDict = DndAssets.purseDict
    bagIds = DndAssets.bagIds

    if userId not in list(invDict.keys()):
        invDict[userId] = {}
        purseDict[userId] = {
            "public":{
            "gp":0,
            "sp":0,
            "cp":0
            },
            "private":{
                "gp":3,
                "sp":200,
                "cp":2
            }
        }
        bagIds[userId] = {"--bagNum":0}
        DndAssets.inventoryDict = invDict
        DndAssets.purseDict = purseDict
        DndAssets.bagIds = bagIds
        return "Initialized!!"
    else:
        return "You already have an inventory dumby"


class NoExitParser(argparse.ArgumentParser):
    def error(self, message):
        raise ValueError(message)


# https://stackoverflow.com/questions/34256250/parsing-a-string-with-spaces-from-command-line-in-python
class MyAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, ' '.join(values))