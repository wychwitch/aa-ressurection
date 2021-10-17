__all__ = [
    "processModCoin",
    "processConvertCoin",
    "processTransferCoin",
    "getFormattedWealth",
    "processHideItem",
    "processMoveItem",
    "processAddItem",
    "processRemoveItem",
    "processDumpBag",
    "getInv",
    "checkDM",
    "cleanUserMention",
    "createCharacter",
    "testyfunc",
    "getAllChara",
    "switchChara",
    "processChangeDesc"
    ]
from os import X_OK
from typing import Tuple
import discord
from inspect import currentframe, getframeinfo
from CMDParsers import *
import math

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
#PROCESS FUNCS
def processModCoin(userId, commandStr, isRemove= False):
    returnStr = ""
    try:
         args = modCoinCMDparse(commandStr)
    except Exception as e:
        frameinfo = getframeinfo(currentframe())
        return f"Whoops! ping chair for this error: {e}\n\n{frameinfo.filename} @ line {frameinfo.lineno}"
    
    if args.help != "":
        return args.help

    coin = parseCoinStr(args.coin)
    if coin != (0, 'np'):
        if isRemove:
            coin = (coin[0] * -1, coin[1])
        returnStr += modPurse(userId, coin, args.private)
    else:
        returnStr += f"{args.coin} is not a valid coin!"
    return returnStr

def processConvertCoin(userId, commandStr):
    returnStr = ""
    visibilityText = ""
    try:
         args = convertCoinCMDparse(commandStr)
    except Exception as e:
        frameinfo = getframeinfo(currentframe())
        return f"Whoops! ping chair for this error: {e}\n\n{frameinfo.filename} @ line {frameinfo.lineno}"
    
    if args.help != "":
        return args.help
    
    if args.private:
        visibilityText = "private"
    else:
        visibilityText = "public"
    
    fromCoin = parseCoinStr(args.fromCoin)
    toCoin = args.toCoin
    if fromCoin != (0, 'np'):
        if toCoin.strip() in DndAssets.coinPieceList:
            returnStr += convertCoin(userId, fromCoin, toCoin, visibilityText)
        else:
            returnStr += f"{args.toCoin} is not a valid coin!"
    else:
        returnStr += f"{args.fromCoin} is not a valid coin!"
    
    return returnStr

def processTransferCoin(userId, commandStr):
    returnStr = ""
    try:
         args = transferCoinCMDparse(commandStr)
    except Exception as e:
        frameinfo = getframeinfo(currentframe())
        return f"Whoops! ping chair for this error: {e}\n\n{frameinfo.filename} @ line {frameinfo.lineno}"
    
    if args.help != "":
        return args.help

    if args.toPurse.lower() == "private":
        isPrivate = True
    elif args.toPurse.lower() == "public":
        isPrivate = False
    else:
        return "You need to specify a coin purse to transfer to! (public or private!)"
    coin = parseCoinStr(args.coin)
    if coin != (0, 'np'):
        returnStr += transferCoin(userId, coin, isPrivate)
    else:
        return f"{args.coin} isn't a valid coin!"
    
    return returnStr


## Normal Funcs
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

def getCoinAsCopperInt(coin):
    copper = 0
    if coin[1] == "gp":
        copper = coin[0] * 1000
    elif coin[1] == "sp":
        copper = coin[0] * 100
    else:
        copper = coin[0]
    return copper

def getPurseAsCopperInt(userId: str, showFull = False):
    purseDict = DndAssets.purseDict
    currChara = DndAssets.currentCharas[userId]
    totalInCopper = 0
    selectedCoins = {
    "gp":purseDict[userId][currChara]["public"]["gp"],
    "sp":purseDict[userId][currChara]["public"]["sp"],
    "cp":purseDict[userId][currChara]["public"]["cp"]
    }
    if showFull:
        for c in purseDict[userId][currChara]["private"]:
            selectedCoins[c] += purseDict[userId][currChara]["private"][c]
    totalInCopper += getCoinAsCopperInt((selectedCoins["gp"], "gp"))
    totalInCopper += getCoinAsCopperInt((selectedCoins["sp"], "sp"))
    totalInCopper += selectedCoins["cp"]
    return totalInCopper

def modPurse(userId, coin, private = False):
    purseDict = DndAssets.purseDict
    currChara = DndAssets.currentCharas[userId] 
    returnStr = ""
    visibility = ""
    censor = ""
    if private:
        visibility = "private"
        censor = "||"
    else:
        visibility = "public"
    
    if userId in list(purseDict.keys()):
        purseDict[userId][currChara][visibility][coin[1]] += coin[0]
        remainingCoin = (purseDict[userId][currChara][visibility][coin[1]], coin[1])
        formattedCoin = formatCoin(remainingCoin)
        
        if coin[0] < 0:
            returnStr += f"Removed {abs(coin[0])}{coin[1]}. Total {coin[1]} is now {censor}{formattedCoin}{censor}"
        else:
            returnStr += f"{coin[0]}{coin[1]} added to your {visibility} coinpurse (total of {censor}{formattedCoin}{censor}!)"
    else:
        returnStr += "Somethings wrong;"
    DndAssets.purseDict = purseDict
    DndAssets.saveAll()
    return returnStr

def sumItemWorth(userId: str, isFull: bool):
    invDict = DndAssets.inventoryDict
    currChara = DndAssets.currentCharas[userId] 
    totalItemWorth = 0

    for (item) in list(invDict[userId][currChara].keys()):
        isItemPrivate = invDict[userId][currChara][item]["private"]
        itemStock = invDict[userId][currChara][item]["stock"]
        itemWorth = invDict[userId][currChara][item]["worth"]

        if isItemPrivate:
            if isFull:
                totalItemWorth += itemWorth * itemStock 
        else:
            totalItemWorth += itemWorth * itemStock
    return totalItemWorth

def getFormattedWealth(userid: str, isFull = False, isPrivate = False):
    purseDict = DndAssets.purseDict
    currChara = DndAssets.currentCharas[userid] 
    returnStr = ""
    totalCoin = ()
    totalItemWorth = sumItemWorth(userid, isFull)
    if isFull:
        returnStr += f"Both of <@!{userid}>'s coinpurses contain in total:\n"
    elif isPrivate:
        returnStr += f"<@!{userid}>'s private coinpurse contains:\n"
    else:
        returnStr += f"<@!{userid}>'s public coinpurse contains:\n"

    for coinPiece in DndAssets.coinPieceList:
        pubCoin = (purseDict[userid][currChara]["public"][coinPiece],
            coinPiece)

        privCoin = (purseDict[userid][currChara]["private"][coinPiece],
            coinPiece)

        if isFull:
            totalCoin = (pubCoin[0]+privCoin[0], pubCoin[1])
        elif isPrivate:
            totalCoin = (privCoin[0], privCoin[1])
        else:
            totalCoin = (pubCoin[0], pubCoin[1])
            
        if totalCoin[0]> 0:
            returnStr += f"\t -{formatCoin(totalCoin)}\n"
    
    purseWorth = formatCoin(
        sumCopper(
            getPurseAsCopperInt(userid, 
                isFull))
        )
    if returnStr == "\nCoinpurse Contains:":
        returnStr += " Nothing :(\n"
    else:
        returnStr += f"\nFor a total of {purseWorth} in coin."
    if totalItemWorth > 0:
        formattedItemWorth = formatCoin(sumCopper(totalItemWorth))
        totalWealth = formatCoin(sumCopper(totalItemWorth + 
            getPurseAsCopperInt(userid, isFull)))

        returnStr += f"\nCombined with {formattedItemWorth} of treasure in the inventory, total wealth is {totalWealth}."
    return returnStr

def parseCoinStr(coinStr):
    
    coinStr = coinStr.strip()
    coin = (coinStr[:-2],coinStr[-2:])
    
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

def transferCoin(userId:str, coin:tuple, toPrivate = False):
    purseDict = DndAssets.purseDict
    currChara = DndAssets.currentCharas[userId]
    purseTo = ""
    purseFrom = ""
    if toPrivate:
        purseTo = "private"
        purseFrom = "public"
    else:
        purseTo = "public"
        purseFrom = "private"
    
    purseCoin = (purseDict[userId][currChara][purseFrom][coin[1]], coin[1])
    
    if coin[0] > purseCoin[0]:
        return f"You don't have {formatCoin(coin)} to move! You have {formatCoin(purseCoin)}"
    result = purseCoin[0] - coin[0]
    purseDict[userId][currChara][purseFrom][purseCoin[1]] = result
    purseDict[userId][currChara][purseTo][purseCoin[1]] += coin[0]
    totalCoin = (purseDict[userId][currChara][purseTo][purseCoin[1]], f'{coin[1]}')
    
    DndAssets.purseDict = purseDict
    DndAssets.saveAll()
    return f"Moved {formatCoin(coin)} from {purseFrom} to {purseTo} (it now hjas {formatCoin(totalCoin)}"

def convertCoin(userId, coin, convertTo, visibility):
    purseDict = DndAssets.purseDict
    coinRates = DndAssets.coinRates
    coinPieceList =  DndAssets.coinPieceList
    currChara = DndAssets.currentCharas[userId] 
    returnStr = ""

    if canAfford(userId, coin, visibility):
        if coinPieceList.index(coin[1]) < coinPieceList.index(convertTo):
            result = coin[0] * coinRates[f"{coin[1]}Rate"][convertTo]
            purseDict[userId][currChara][visibility][coin[1]] -= coin[0]
            purseDict[userId][currChara][visibility][convertTo] += result
            DndAssets.purseDict = purseDict
            DndAssets.saveAll()
            returnStr += f"Successfully converted {coin[0]}{coin[1]} into {result}{convertTo} "
        else:
            result = coin[0] / coinRates[f"{coin[1]}Rate"][convertTo]
            if result % 1 == 0:
                purseDict[userId][currChara][visibility][coin[1]] -= coin[0]
                purseDict[userId][currChara][visibility][convertTo] += result
                DndAssets.purseDict = purseDict
                DndAssets.saveAll()
                returnStr += f"Successfully converted {coin[0]}{coin[1]} into {int(result)}{convertTo} "
            else:
                returnStr += "Could not convert evenly!"
    else:
        returnStr += "You cannot afford to convert this!"
    
    return returnStr

def canAfford(userId, coin, visibility):
    purseDict = DndAssets.purseDict
    currChara = DndAssets.currentCharas[userId]
    if purseDict[userId][currChara][visibility][coin[1]] - coin[0] < 0:
        return False
    else:
        return True


"""
INVENTORY
      ___                      _                   
     |_ _|_ ____   _____ _ __ | |_ ___  _ __ _   _ 
      | || '_ \ \ / / _ \ '_ \| __/ _ \| '__| | | |
      | || | | \ V /  __/ | | | || (_) | |  | |_| |
     |___|_| |_|\_/ \___|_| |_|\__\___/|_|   \__, |
                                             |___/ 
"""
## PROCESS FUNCS
def processHideItem(ctx, userId, itemStr, isPrivate):
    invDict = DndAssets.inventoryDict
    returnStr = ""
    try:
        args = invHideCMDParse(itemStr)
    except Exception as e:
        frameinfo = getframeinfo(currentframe())
        return f"Whoops! ping chair for this error: {e}\n\n{frameinfo.filename} @ line {frameinfo.lineno}"

    if args.help != "":
        return args.help

    if args.user:
        if checkDM(ctx, userId):
            userId = args.user.strip('@<>')
        else:
            return "You arent dm!!"
    if userId not in invDict.keys():
        return f"<@!{userId}> doesn't have a character! Run character create to get one!"
    
    if args.item:
        returnStr += setItemVisibility(userId, args.item, isPrivate)
    elif args.bag:
        returnStr += setBagVisibility(userId, args.bag, isPrivate)
    else:
        frameinfo = getframeinfo(currentframe())
        return f"Oh!! idek how the fuck you got here but ping chair for me to investigate this info:\n\n{frameinfo.filename} @ line {frameinfo.lineno}"
    return returnStr

def processMoveItem(ctx, userId, movStr):
    invDict = DndAssets.inventoryDict
    returnStr = ""

    args = None

    try:
        args = invMovCMDParse(movStr)
    except Exception as e:
        frameinfo = getframeinfo(currentframe())
        return f"Whoops! ping chair for this error: {e}\n\n{frameinfo.filename} @ line {frameinfo.lineno}"
    if args.help != "":
        return args.help
    if args.user:
        if checkDM(ctx, userId):
            userId = args.user.strip('@<>')
        else:
            return "You aren't a dm!!!"

    if userId not in list(invDict.keys()):
        return f"<@!{userId}> doesn't have an inventory! Run inv init to get one!"
    
    if args.item:
        item = isItemInInv(userId, args.item)
        if item[0]:
            bag = isBagInInv(userId, args.bag)
            returnStr += moveItem(userId, item[1], bag[1])                
        else:
            returnStr += f"You don't have {item[1]}!"
    else:
        returnStr += "You need to supply an item!! use -i <item name> or --item <item name>"
            
    return returnStr

def processAddItem(ctx, userId, itemStr):
    returnStr = ""
    
    args = None

    try:
        args = invAddCMDParse(itemStr)
    except Exception as e:
        frameinfo = getframeinfo(currentframe())
        return f"Whoops! ping chair for this error: {e}\n\n{frameinfo.filename} @ line {frameinfo.lineno}"
    if args.help != "":
        return args.help
    
    if args.user:
        if checkDM(ctx, userId):
            userId = args.user.strip('@!<>')
        else:
            return "You aren't a dm!!!"
    if args.item:
        if type(args.item) == list:
            for i in range(0, len(args.item)):
                returnStr += addItem(userId, args, args.item[i])
        else:
            returnStr += addItem(userId, args)
    return returnStr

def processRemoveItem(ctx, userId, remStr):
    invDict = DndAssets.inventoryDict
    args = None

    try:
         args = invRemCMDParse(remStr)
    except Exception as e:
        frameinfo = getframeinfo(currentframe())
        return f"Whoops! ping chair for this error: {e}\n\n{frameinfo.filename} @ line {frameinfo.lineno}"
    if args.help != "":
        return args.help
    if args.user:
        if checkDM(ctx, userId):
            userId = args.user.strip('@<!>')
        else:
            return "You aren't a dm!!!"

    if userId not in invDict.keys():
        return f"@<{userId}> doesn't have an inventory! Run inv init to get one!"

    if args.item:
        return removeItem(userId, args.item, args.stock, args.all)
    elif args.bag != "":
            return removeBag(userId, args.bag)
    else:
        return "You need to supply an item or bag!!"

def processDumpBag(ctx, userId, bagStr):
    invDict = DndAssets.inventoryDict
    returnStr = ""

    args = None

    try:
        args = invDumpCMDParse(bagStr)
    except Exception as e:
        frameinfo = getframeinfo(currentframe())
        return f"Whoops! ping chair for this error: {e}\n\n{frameinfo.filename} @ line {frameinfo.lineno}"
    if args.help != "":
        return args.help
    if args.user:
        if checkDM(ctx, userId):
            userId = args.user.strip('@!<>')
        else:
            return "You aren't a dm!!!"

    if userId not in list(invDict.keys()):
        returnStr += "You dont have an inventory! Run init"
    else:
        bag = isBagInInv(userId, args.fromBag)
        if bag[0]:
            toBag = isBagInInv(userId, args.toBag)
            returnStr += f"\n{dumpBag(userId, bag[1], toBag[1])}"
    return returnStr

def processChangeDesc(ctx, userId, cmdStr):
    invDict = DndAssets.inventoryDict
    returnStr = ""
    args = None

    try:
        args = changeDescCMDParse(cmdStr)
    except Exception as e:
        frameinfo = getframeinfo(currentframe())
        return f"Whoops! ping chair for this error: {e}\n\n{frameinfo.filename} @ line {frameinfo.lineno}"
    if args.help != "":
        return args.help
    if args.user:
        if checkDM(ctx, userId):
            userId = args.user.strip('@<!>')
        else:
            return "You aren't a dm!!!"

    if userId not in list(invDict.keys()):
        return f"<@!{userId}> doesn't have a character! Run chara create <name> to get one!"

    if args.item:
        if args.desc:
            return changeItemDesc(userId, args.item, args.desc)
        else:
            return "You need to supply a description!"
    else:
        return "You need to supply an item!"

def processLookItem(ctx, userId, cmdStr):
    invDict = DndAssets.inventoryDict
    args = None

    try:
        args = lookCMDParse(cmdStr)
    except Exception as e:
        frameinfo = getframeinfo(currentframe())
        return f"Whoops! ping chair for this error: {e}\n\n{frameinfo.filename} @ line {frameinfo.lineno}"
    
    if args.help != "":
        return args.help
    
    if args.user:
        if args.full:
            if checkDM(ctx, userId):
                userId = args.user.strip('@<!>')
            else:
                return "You aren't a dm!!! You can't use -f on a user!"
        userId = args.user.strip('@<!>')

    if userId not in list(invDict.keys()):
        return f"<@!{userId}> doesn't have a character! Run chara create <name> to get one!"

    if args.item:
        return look(userId, args.item, args.full)
    else:
        return "You need to supply an item!"

## Utility Funcs
def getInv(userid, showFull = False):
    invDict = DndAssets.inventoryDict
    bagIds = DndAssets.bagIds
    currChara = DndAssets.currentCharas[userid]
    returnStr = f"<@!{userid}>\n{currChara}"
    inventoryUsers = list(invDict.keys())
    dupeBags = []
    bags = []
    
    if(userid in inventoryUsers):
        returnStr += "'s inventory\n"
        dupeBags = [sub["bag"] for sub in invDict[userid][currChara].values() if "bag" in sub.keys()]
        bags = list(set(dupeBags))
        bags = sorted(bags, key=lambda s: (not s, s))
        bagText = ""
        totalWealth = ""

        for (bag) in bags:
            bagText = ""

            if bag =="":
                returnStr += f"\n\t**Not in a bag**:"
            else:
                returnStr += f"\n\t**({bagIds[userid][currChara][bag]}){bag}**:"
            for (item) in list(invDict[userid][currChara].keys()):
                isPrivate = invDict[userid][currChara][item]["private"]
                itemStock = invDict[userid][currChara][item]["stock"]
                itemWorth = invDict[userid][currChara][item]["worth"]
                itemDesc = invDict[userid][currChara][item]["desc"]

                if bag == invDict[userid][currChara][item]["bag"]:
                    if isPrivate:
                        if showFull:
                            bagText += f"\n\t\t- ||{item}"
                            if itemStock > 1:
                                bagText += f"({itemStock})||"
                            else:
                                bagText += f"||"
                            if itemWorth > 0:
                                bagText += f"\n\t\t\t- ||Worth {formatCoin(sumCopper(itemWorth))}||"
                            if itemDesc != "":
                                bagText += f"\n\t\t\t- ||Description: *{itemDesc}*||"
                    else:
                        bagText += f"\n\t\t- {item}"
                        if itemStock > 1:
                                bagText += f"({itemStock})"
                        if itemWorth > 0:
                                bagText += f"\n\t\t\t- Worth {formatCoin(sumCopper(itemWorth))}"
                        if itemDesc != "":
                                bagText += f"\n\t\t\t- Description: *{itemDesc}*"
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
    DndAssets.saveAll()
    return returnStr

#TODO but like low priority, split this into 2 functions, one that validates and one that actually removes w/o checking
def addItem(userId, args, itemName = ""):
    invDict = DndAssets.inventoryDict
    currChara = DndAssets.currentCharas[userId]
    if itemName != "":
        item = isItemInInv(userId, itemName)
    else:
        item = isItemInInv(userId, args.item)
    bagText = ""
    if item[0]:
        #This is adding its worth to itself
        singleItemWorth = divideItemWorth(invDict[userId][currChara][item[1]]["worth"], invDict[userId][currChara][item[1]]["stock"])
        invDict[userId][currChara][item[1]]["stock"] += args.stock
        invDict[userId][currChara][item[1]]["worth"] = invDict[userId][currChara][item[1]]["stock"] * singleItemWorth
    else:
        bag = isBagInInv(userId, args.bag)
        bagText += bag[1]
        invDict[userId][currChara][item[1]] = {
            "private":args.private,
            "stock":args.stock,
            "bag":bag[1],
            "desc":args.desc,
            "worth":getCoinAsCopperInt(parseCoinStr(args.worth))
        }
    if bagText == "":
        bagText = "the inventory"
    DndAssets.inventoryDict= invDict
    DndAssets.saveAll()
    return f"Added {item[1]} to {currChara}'s' {bagText}!\n"


# Only assumes valid userId
def removeItem(userId, itemName, amount= 1, isAll = False):
    invDict = DndAssets.inventoryDict
    currChara = DndAssets.currentCharas[userId]
    returnStr = ""
    item = isItemInInv(userId, itemName)
    if item[0]:
        singleItemWorth = divideItemWorth(invDict[userId][currChara][item[1]]["worth"], invDict[userId][currChara][item[1]]["stock"])
        bag = invDict[userId][currChara][itemName]["bag"]
        invDict[userId][currChara][item[1]]["stock"] -= amount
        stock = invDict[userId][currChara][itemName]["stock"]
        invDict[userId][currChara][item[1]]["worth"] -= math.ceil((singleItemWorth * amount))
        if stock<=0 or isAll:
            del invDict[userId][currChara][item[1]]
            DndAssets.inventoryDict = invDict
            returnStr = f"Removed all of {item[1]} from {currChara}'s {bag}!"
        else:
            returnStr = f"Removed {amount} {item[1]}(s) from {currChara}'s' {bag}! (there is {stock} left)."
        DndAssets.inventoryDict= invDict
        DndAssets.saveAll()
    else:
        returnStr = f"You don't have {item[1]} in your inventory!"
    return returnStr

def isItemInInv(userId, itemName):
    invDict = DndAssets.inventoryDict
    currChara = DndAssets.currentCharas[userId]
    onlyItems = list(invDict[userId][currChara].keys())
    for i in range(len(onlyItems)):
        if itemName.lower() == onlyItems[i].lower():
            return True, onlyItems[i]
    return False, itemName


def setItemVisibility(userId, itemName, isPrivate):
    invDict = DndAssets.inventoryDict
    currChara = DndAssets.currentCharas[userId]
    returnStr = ""
    item = isItemInInv(userId, itemName)
    if item[0]:
        invDict[userId][currChara][item[1]]["private"] = isPrivate
        DndAssets.inventoryDict= invDict
        DndAssets.saveAll() 
        if invDict[userId][currChara][item[1]]["private"]:
            returnStr = f"You hid {item[1]}!"
        else:
            returnStr = f"You unhid {item[1]}!"
    return returnStr

def dumpBag(userId, fromBag, toBag):
    invDict = DndAssets.inventoryDict
    currChara = DndAssets.currentCharas[userId]
    movedItems = ""
    toBagText = f"to {toBag}!"
    if toBag == "":
        toBagText = "out of your bag!"
    for item in invDict[userId][currChara]:
        checkBag = invDict[userId][currChara][item]["bag"]
        print(repr(checkBag))
        print(repr(fromBag))
        if checkBag.strip() == fromBag.strip():
            movedItems += f"\n\t-{item}"
            invDict[userId][currChara][item]["bag"] = toBag
    DndAssets.inventoryDict= invDict
    DndAssets.saveAll()
    return f"Moved the following items {toBagText} {movedItems}"
    

    ## in this code discover if moving single item or dumping bag, and behave appropriately

def moveItem(userId, item, bag = ""):
    invDict = DndAssets.inventoryDict
    currChara = DndAssets.currentCharas[userId]
    oldBag = invDict[userId][currChara][item]["bag"]
    if bag != "":
        invDict[userId][currChara][item]["bag"] = bag
        DndAssets.inventoryDict= invDict
        DndAssets.saveAll()
        return f"Moved {item} from {oldBag} to {bag}!"
    else:
        invDict[userId][currChara][item]["bag"] = ""
        DndAssets.inventoryDict= invDict
        DndAssets.saveAll() 
        return f"Dumped {item} out of {oldBag}!"

def removeBag(userId, bagName):
    invDict = DndAssets.inventoryDict
    currChara = DndAssets.currentCharas[userId]
    bag = isBagInInv(userId, bagName)
    if bag[0]:
        for item in list(invDict[userId].keys()):
            if invDict[userId][currChara][item]["bag"] == bag[1]:
                invDict[userId][currChara][item]["bag"] = ""
        DndAssets.inventoryDict= invDict
        DndAssets.saveAll()
        return f"Dumped all items from {bagName}!"
    else:
        return "Couldn't find bag..."

def setBagVisibility(userId, bag, isPrivate = True):
    invDict = DndAssets.inventoryDict
    currChara = DndAssets.currentCharas[userId]
    visiText = ""
    if isPrivate:
        visiText = "hidden"
    else:
        visiText = "unhidden"
    isBag = isBagInInv(userId, bag)

    if isBag[0]:
        for item in list(invDict[userId].keys()):
            if invDict[userId][currChara][item]["bag"] == isBag[1]:
                invDict[userId][currChara][item]["private"] = isPrivate
                DndAssets.inventoryDict= invDict
                DndAssets.saveAll()
        return f"All items in {isBag[1]} are now {visiText}!"
    else:
        return "Whoops!"

def getBagId(userId, bagName):
    bagIds = DndAssets.bagIds
    currChara = DndAssets.currentCharas[userId]
    bagId = 0
    foundId = False, "None"
    for bag in bagIds[userId][currChara]:
        if bagName == str((bag.key())):
            bagId = bag
            foundId = True, bag
            break


    return foundId, bagId

def isBagIdValid(userId, bagId):
    bagIds = DndAssets.bagIds
    currChara = DndAssets.currentCharas[userId]
    foundName = (False, "")
    if userId in list(bagIds.keys()):
        for bag in list(bagIds[userId][currChara].keys()):
            if bag == bagId:
                foundName = (True, bag)
                break
    return foundName

def isBagInInv(userId, bag):
    invDict = DndAssets.inventoryDict
    currChara = DndAssets.currentCharas[userId]
    isBagInt = intTryParse(bag)
    foundBag = (False, bag)
    if isBagInt[1]:
        foundBag = isBagIdValid(userId, bag)
    else:
        dupeBags = [sub["bag"] for sub in invDict[userId][currChara].values() if "bag" in sub.keys()]
        bags = list(set(dupeBags))
        for bagName in bags:
            if bag.lower() == bagName.lower():
                foundBag = (True, bagName)
        if not foundBag[0]:
            addNewBagId(userId, bag)
    return foundBag

def addNewBagId(userId, bag):
    bagIds = DndAssets.bagIds
    currChara = DndAssets.currentCharas[userId]
    bagIds[userId][currChara]["--bagNum"] +=1
    bagIds[userId][currChara][bag] = bagIds[userId][currChara]["--bagNum"]
    DndAssets.bagIds = bagIds

def changeItemDesc(userId, itemName, desc):
    invDict = DndAssets.inventoryDict
    chara = DndAssets.currentCharas[userId]

    item = isItemInInv(userId, itemName)

    if not item[0]:
        return f"You dont have {item[1]} in your inventory!"
    else:
        invDict[userId][chara][item[1]]["desc"] = desc
        DndAssets.inventoryDict = invDict
        DndAssets.saveAll()
        return f"Set item description to *{desc}*!!"

def look(userId, itemName, isFull):
    invDict = DndAssets.inventoryDict
    chara = DndAssets.currentCharas[userId]

    item = isItemInInv(userId, itemName)


    if not item[0]:
        return f"{chara} doesn't have {item[1]} in their inventory!"
    else:
        isPrivate = invDict[userId][chara][item[1]]["private"]
        if isPrivate:
            if isFull:
                return lookAtItem(userId, chara, itemName)
            else:
                return f"{chara} doesn't have {item[1]} in their inventory!"
        else:
            return lookAtItem(userId, chara, item[1])

def lookAtItem(userId, chara, itemName):
    returnStr = ""
    invDict = DndAssets.inventoryDict
    desc = invDict[userId][chara][itemName]["desc"]
    worth = invDict[userId][chara][itemName]["worth"]
    stock = invDict[userId][chara][itemName]["stock"]
    isPrivate = invDict[userId][chara][itemName]["private"]
    bag = invDict[userId][chara][itemName]["bag"]
    if bag == "":
        bag = "Inventory"
    totalWorth = sumCopper(worth)
    singleItemWorth = ""
    visibility = ""
    if desc == "":
        desc = "This item has no description."
    if isPrivate:
        visibility = f"{itemName} is currently hidden!"
    else:
        visibility = f"{itemName} is currently visible to everyone!"
    returnStr += f"**{itemName}** held by **{chara}** in their **{bag}**"
    returnStr += f"\n-{visibility}"
    returnStr += f"\n-Description: *{desc}*"
    returnStr += f"\n-Stock: {stock}"
    if worth > 0:
        returnStr += f"\n-This item's total worth is {formatCoin(totalWorth)}"
        if stock > 1:
            singleItemWorth = sumCopper(worth / stock)
            returnStr += f" (Each individual item is worth {formatCoin(singleItemWorth)})"
    return returnStr

"""
CHARACTER
"""

def getAllChara(userId):
    currChara = DndAssets.currentCharas[userId]
    charaList = []
    returnStr = ""
    if userId not in list(DndAssets.inventoryDict.keys()):
        return "You don't have a character! Create one by going `character create <character name>`"
    
    charaList = list(DndAssets.inventoryDict[userId].keys())
    returnStr += f"<@!{userId}>'s characters:"
    for i in range(0, len(charaList)):
        returnStr += f"\n{i+1}: {charaList[i]}"
        if charaList[i] == currChara:
            returnStr += " <- Current Character!"

    return returnStr

def createCharacter(userId, characterName):
    charaDict = DndAssets.currentCharas
    inv = DndAssets.inventoryDict
    purse = DndAssets.purseDict
    bagIds = DndAssets.bagIds
    chara = isCharacter(userId, characterName)
    if chara[0]:
        return f"You need to pick a new name! You already have a character named {chara[1]}"
    else:
        if userId not in list(inv.keys()):
            inv[userId] = {}
            purse[userId] = {}
        inv[userId][chara[1]] = {}
        bagIds[userId] = {chara[1]:{"--bagNum":0}}
        purse[userId][chara[1]] = {
            "public":{
            "gp":0,
            "sp":0,
            "cp":0
            },
            "private":{
                "gp":0,
                "sp":0,
                "cp":0
            }
        }
        charaDict[userId] = chara[1]
        DndAssets.purseDict = purse
        DndAssets.inventoryDict = inv 
        DndAssets.currentCharas = charaDict
        DndAssets.bagIds = bagIds
        DndAssets.saveAll()

        return f"<@!{userId}> has created the character {chara[1]}!"

def switchChara(userId, characterName):
    currentCharas = DndAssets.currentCharas
    chara = isCharacter(userId, characterName)
    if not chara[0]:
        return f"<@!{userId}> {chara[1]} isn't a valid character name!  Are you missing a last name? Here's your characters: \n\n{getAllChara(userId)}" 
    else:
        currentCharas[userId] = chara[1]
        DndAssets.saveAll()
        return f"<@!{userId}> has switched to {chara[1]}!"

def isCharacter(userId, charaName):
    invDict = DndAssets.inventoryDict
    try:
        onlyCharas = list(invDict[userId].keys())
    except KeyError:
        return False, charaName
    for i in range(len(onlyCharas)):
        if charaName.lower() == onlyCharas[i].lower():
            return True, onlyCharas[i]
    return False, charaName



"""
MISC
     __  __ ___ ____   ____ 
    |  \/  |_ _/ ___| / ___|
    | |\/| || |\___ \| |    
    | |  | || | ___) | |___ 
    |_|  |_|___|____/ \____|
                            
"""
def errorWhoops(frameinfo):
    return f"Hhhuh something wrong {frameinfo.filename} {frameinfo.lineno}"

def testyfunc(string):
    args = invAddCMDParse(string)
    return(f"{args.help}")

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

