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
    "userInit",
    "testyfunc"
    ]
from os import X_OK
from typing import Tuple
import discord
from inspect import currentframe, getframeinfo
from CMDParsers import *

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
    except Exception :
        return "Whoops! Ping chair for me pls!"

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
    try:
         args = convertCoinCMDparse(commandStr)
    except Exception :
        return "Whoops! Ping chair for me pls!"
    visibilityText = ""
    if args.private:
        visibilityText = "private"
    else:
        visibilityText = "public"
    
    fromCoin = parseCoinStr(args.fromCoin)
    toCoin = parseCoinStr(args.toCoin)
    if fromCoin != (0, 'np'):
        if toCoin != (0, 'np'):
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
    except Exception :
        return "Whoops! Ping chair for me pls!"
    
    if args.toPurse.lower() == "private" or args.toPurse.lower() == "public":
        fromCoin = parseCoinStr(args.fromCoin)
        toCoin = parseCoinStr(args.toCoin)
        if fromCoin != (0, 'np'):
            if toCoin != (0, 'np'):
                returnStr += convertCoin(userId, fromCoin, toCoin, args.toPurse.lower())
            else:
                returnStr += f"{args.toCoin} is not a valid coin!"
        else:
            returnStr += f"{args.fromCoin} is not a valid coin!"
    else:
        returnStr += "You need to specify a coin purse to transfer to! (public or private!)"
    
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
    totalInCopper = 0
    selectedCoins = {
    "gp":purseDict[userId]["public"]["gp"],
    "sp":purseDict[userId]["public"]["sp"],
    "cp":purseDict[userId]["public"]["cp"]
    }
    if showFull:
        for c in purseDict[userId]["private"]:
            selectedCoins[c] += purseDict[userId]["private"][c]
    totalInCopper += getCoinAsCopperInt((selectedCoins["gp"], "gp"))
    totalInCopper += getCoinAsCopperInt((selectedCoins["sp"], "sp"))
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
            getPurseAsCopperInt(userid, 
                isFull))
        )
    if returnStr == "\nCoinpurse Contains:":
        returnStr += " Nothing :(\n"
    else:
        returnStr += f"\nFor a total of {purseWorth} in coin."
    if totalItemWorth > 0:
        purseInCopper = getPurseAsCopperInt(
        userid, isFull
        )
        formattedItemWorth = formatCoin(sumCopper(totalItemWorth))
        totalWealth = formatCoin(sumCopper(totalItemWorth + getPurseAsCopperInt(userid, isFull)))

        returnStr += f"\nCombined with {formattedItemWorth} of treasure in the inventory, total wealth is {totalWealth}."
    return returnStr

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
    returnStr = ""
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
                returnStr += f"Successfully converted {coin[0]}{coin[1]} into {result} "
            else:
                returnStr += "Could not convert evenly!"
        else:
            result = coin[0] * coinRates[convertTo]
            purseDict[userId][visibility][coin[1]] -= result
            purseDict[userId][visibility][convertTo] += result
            DndAssets.purseDict = purseDict
            returnStr += f"Successfully converted {coin[0]}{coin[1]} into {result} "
    else:
        returnStr += "You cannot afford to convert this!"
    
    return returnStr

def canAfford(userId, coin, visibility):
    purseDict = DndAssets.purseDict
    if purseDict[userId][visibility][coin[1]] - coin[0] < 0:
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
    except Exception :
        returnStr +="Whoops! ping chair"

    if args.user:
        if checkDM(ctx, userId):
            userId = args.user.strip('@<>')
        else:
            return "You arent dm!!"
    if userId not in invDict.keys():
        returnStr += "You don't have an inventory! Run inv init to get one!"
    
    if args.item:
        returnStr += setItemVisibility(userId, args.item, isPrivate)
    elif args.bag:
        returnStr += setBagVisibility(userId, args.bag, isPrivate)
    else:
        returnStr += "Something wernt wrong!! bother chair"
    return returnStr

def processMoveItem(ctx, userId, movStr):
    invDict = DndAssets.inventoryDict
    returnStr = ""

    args = None

    try:
        args = invHideCMDParse(movStr)
    except Exception :
        returnStr +="Whoops! ping chair"
    if args.user:
        if checkDM(ctx, userId):
            userId = args.user.strip('@<>')

    if userId not in list(invDict.keys()):
        return "You dont have an inventory! Run init"
    
    if args.item:
        item = isItemInInv(userId, args.item)
        if item[0]:
            bag = isBagInInv(userId, args.bag)
            returnStr += moveItem(userId, item[1], bag[1])                
        else:
            returnStr += f"You don't have {item[1]}!"
    else:
        returnStr += "whayuh"
            
    return returnStr

def processAddItem(ctx, userId, itemStr):
    returnStr = ""
    
    itemArgs = None
    try:
        itemArgs = invAddCMDParse(itemStr)
    except Exception :
        return "Whoops! ping chair"

    if itemArgs.user:
        if checkDM(ctx, userId):
            userId = itemArgs.user.strip('@<>')
    if itemArgs.item:
        returnStr += addItem(userId, itemArgs)
    return returnStr

def processRemoveItem(ctx, userId, remStr):
    invDict = DndAssets.inventoryDict
    args = None

    try:
         args = invRemCMDParse(remStr)
    except Exception :
        return "Whoops! Ping chair for me pls!"

    if args.user:
        if checkDM(ctx, userId):
            userId = args.user.strip('@<>')

    if userId not in invDict.keys():
        return f"@<{userId}> doesn't have an inventory! Run inv init to get one!"

    if args.item:
        if args.bag != "":
            return removeBag(userId, args.bag)
        else:
            return removeItem(userId, args.item, args.stock)
    else:
        return "You need to supply an item!!"

def processDumpBag(ctx, userId, bagStr):
    invDict = DndAssets.inventoryDict
    returnStr = ""

    args = None

    try:
        args = invDumpCMDParse(bagStr)
    except Exception :
        returnStr +="Whoops! ping chair"
    if args.user:
        if checkDM(ctx, userId):
            userId = args.user.strip('@<>')

    if userId not in list(invDict.keys()):
        returnStr += "You dont have an inventory! Run init"
    else:
        bag = isBagInInv(userId, args.fromBag)
        if bag[0]:
            toBag = isBagInInv(userId. args.toBag)
            returnStr += f"\n{dumpBag(userId, bag[1], toBag[1])}"


## Utility Funcs
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

#TODO but like low priority, split this into 2 functions, one that validates and one that actually removes w/o checking
def addItem(userId, itemArgs):
    invDict = DndAssets.inventoryDict
    item = isItemInInv(userId, itemArgs.item)
    bagText = ""
    if item[0]:
        invDict[userId][item[1]]["stock"] += itemArgs.stock
        #This is adding its worth to itself
        singleItemWorth = divideItemWorth(invDict[userId][item[1]]["worth"], invDict[userId][item[1]]["stock"])
        invDict[userId][item[1]]["worth"] = invDict[userId][item[1]]["stock"] * singleItemWorth
    else:
        bag = isBagInInv(userId, itemArgs.bag)
        bagText += bag[1]
        invDict[userId][item[1]] = {
            "private":itemArgs.private,
            "stock":itemArgs.stock,
            "bag":bag[1],
            "worth":getCoinAsCopperInt(parseCoinStr(itemArgs.worth))
        }
    if bagText == "":
        bagText = "the inventory"
    return f"Added {item[1]} to {bagText}!\n"

## Add this to the add item func
def setUpItem(userId, itemName, validArgs):
    bag = validArgs['-b']
    itemStock = validArgs['-s']
    isPrivate = validArgs['-p']
    itemWorth = getCoinAsCopperInt(parseCoinStr(validArgs['-w']))
    itemValues = {
        "bag":bag,
        "itemStock":itemStock,
        "isPrivate":isPrivate,
        "itemWorth":itemWorth
    }
    return addItem(userId, itemName, itemValues)

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

def setItemVisibility(userId, itemName, isPrivate):
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

def setBagVisibility(userId, bag, isPrivate = True):
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

def isBagIdValid(userId, bagId):
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
        foundBag = isBagIdValid(userId, bag)
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
    parser = NoExitParser(description="what is this desc")
    parser.add_argument("-t", "--test", help="test help", nargs='+', action=MyAction)
    parser.add_argument("-b", help="test help!!!", nargs='+', action=MyAction)
    parser.add_argument("-i", help="test help!!!", nargs='+', action=MyAppend)
    parser.add_argument("-p", help="test help!!!", default=False, action='store_true')

    huh = parser.parse_args(string.split())
    return(f"THIS IS THE T'S VALUE:{huh.test} THIS IS THE B'S VALUE:{huh.b} is this?? {huh.p}\n\n i: {huh.i}")

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


