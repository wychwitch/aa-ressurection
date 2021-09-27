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
    "tryMove"]
from os import X_OK
from typing import Tuple
import discord
import re
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
    "cp":purseDict[userId]["public"]["cp"]
    }
    if showFull:
        for c in purseDict[userId]["private"]:
            selectedCoins[c] += purseDict[userId]["private"][c]
    totalInCopper += getCoinAsCopper((selectedCoins["gp"], "gp"))
    totalInCopper += getCoinAsCopper((selectedCoins["sp"], "sp"))
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

def parseCoinStr(coinStr):
    
    coinStr = coinStr.strip()
    coin = (coinStr[:-2],coinStr[-2:])
    
    copper = 0
    if coin[1] in ['gp', 'sp', 'cp']:
        isInt = intTryParse(coin[0])
        if isInt[0]:
            coin = (isInt[0], coin[1])
            copper = getCoinAsCopper(coin)
            return sumCopper(copper)
        else:
            return 0
    else:
        return 0

def divideItemWorth(totalWorth: int, totalStock: int):
    return totalWorth / totalStock

def depositCoin(userId:str, coin:tuple, moveToPrivate):
    purseDict = DndAssets.purseDict
    purseTo = ""
    purseFrom = ""
    if moveToPrivate:
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
                returnStr += f"\n\t**({bagIds[bag]}){bag}**:"
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
def combineArgs(argModels, wholeStr, bulkKeyMatch = (), listMode = False):
    indices= []
    keys = []
    values = []
    bulkValues = ()
    argsList = list(argModels.keys()).copy()
    argsListRemove = argsList.copy()

    if listMode:
        for i in range (0, wholeStr.count(bulkKeyMatch[1])):
            argsListRemove.append(bulkKeyMatch[1])
        
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
            subStr = splitByIndices(
                wholeStr,
                indices,
                i,
                y)
            if subStr in argModels:
                if isinstance(argModels[subStr] , bool):
                    keys.append(subStr)
                    values.append(True)
                    break
                elif subStr == bulkKeyMatch[1]:
                    break
                else:
                    keys.append(subStr)
            else:
                if keys[-1] == bulkKeyMatch[0]:
                    if not isinstance(values[-1], list):
                        values.append([])
                    values[-1].append(subStr.rstrip().lstrip())
                else:
                    values.append(subStr.rstrip().lstrip())
    

    argsDict = dict(zip(keys, values))
    return argsDict

#TODO but like low priority, split this into 2 functions, one that validates and one that actually removes w/o checking
def addItem(userId, itemName, itemValues):
    invDict = DndAssets.inventoryDict
    item = isItemInInv(itemName)
    if item[0]:
        invDict[userId][item[1]]["stock"] += itemValues["itemStock"]
        #This is adding its worth to itself
        singleItemWorth = divideItemWorth(invDict[userId][item[1]]["worth"], invDict[userId][item[1]]["stock"])
        invDict[userId][item[1]]["worth"] = itemValues["itemStock"] * singleItemWorth
    else:
        bag = isBagInInv(itemValues["bag"])
        invDict[userId][item[1]] = {
            "private":itemValues["isPrivate"],
            "stock":itemValues["itemStock"],
            "bag":bag[1],
            "worth":itemValues["itemWorth"]
        }

def addToInv(ctx, userId, itemStr, argModels):
    invDict = DndAssets.inventoryDict
    bagIds = DndAssets.bagIds
    
    returnStr = ""

    if userId not in invDict.keys():
        return "You don't have an inventory! Run inv init to get one!"
    
    combinedArgs = combineArgs(argModels, itemStr)
    
    # change validateArgs logic so this whole block isnt needed
    if '-p' not in combinedArgs.keys():
        combinedArgs['-p'] = False
    if '-b' not in combinedArgs.keys():
        combinedArgs['-b'] = ""
    if '-q' not in combinedArgs.keys():
        combinedArgs['-s'] = 1
    if '-w' not in combinedArgs.keys():
        combinedArgs['-w'] = "0cp"
    if '-u' not in combinedArgs.keys():
        combinedArgs['-u'] = ""
    if '-u' not in combinedArgs.keys():
        combinedArgs['-u'] = ""
    if '--bag' not in combinedArgs.keys():
        combinedArgs['--bag'] = []
    else:
        combinedArgs['-i'] = "-i"
    
    if combinedArgs['-u'] != "":
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
    item = isItemInInv(userId, itemName)
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
    return addItem(userId, item, itemValues)

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
def removeItem(userId, item, amount= 1, isAll = False):
    invDict = DndAssets.inventoryDict
    returnStr = ""
    stock = invDict[userId][item]["stock"]
    bag = invDict[userId][item]["bag"]
    if isItemInInv(item):
        invDict[userId][item]["stock"] -= amount
        if invDict[userId][item]["stock"] >=0 or isAll:
            del invDict[userId][item]
            DndAssets.inventoryDict = invDict
            returnStr = f"Removed all of {item} from {bag}!"
        else:
            returnStr = f"Removed {amount} {item}(s) from {bag}! (there is {stock} left)."
    else:
        returnStr = f"You don't have {item} in your inventory!"

def isItemInInv(userId, item):
    invDict = DndAssets.inventoryDict
    onlyItems = list(invDict[userId][item].keys())
    for i in range(len(onlyItems)):
        onlyItems[i] = onlyItems[i].lower()
    if item in onlyItems:
        return True, item
    else:
        return False, item

def togItemVisibility(userId, itemName, isPrivate):
    invDict = DndAssets.inventoryDict
    returnStr = ""
    item = isItemInInv(itemName)
    if item[0]:
        invDict[userId][item[1]]["private"] = isPrivate
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
                returnStr += moveItem(userId, combinedArgs['-i'])
            else:
                bag = isBagInInv(combinedArgs['-t'])
                returnStr += moveItem(item[1], bag[1])                
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
    toBagText = f"to {toBag}!"
    if toBag == "":
        toBagText = "out of your bag!"
    for item in invDict[userId]:
        if invDict[userId][item]["bag"] == fromBag:
            movedItems += f"\n\t-{item}"
            invDict[userId][item]["bag"] = toBag
    return f"Moved the following items {toBagText}{movedItems}"
    

    ## in this code discover if moving single item or dumping bag, and behave appropriately


def moveItem(userId, item, bag = ""):
    invDict = DndAssets.inventoryDict
    oldBag = invDict[item]["bag"]
    if bag != "":
        isBag = isBagInInv(userId, item)
        if isBag[0]:
            invDict[item]["bag"] = isBag[1]
            DndAssets.inventoryDict = invDict 
            return f"Moved {item} from {oldBag} to {isBag[1]}!"
        else:
            return "Incorrect bag name or id"
    else:
        invDict[item]["bag"] = ""
        DndAssets.inventoryDict = invDict 
        return f"Dumped {item} out of {oldBag}!"

def removeBag(userId, bag):
    invDict = DndAssets.inventoryDict
    isBag = isBagInInv(userId)
    if isBag[0]:
        for item in list(invDict[userId].keys()):
            if invDict[userId][item]["bag"] == isBag[1]:
                invDict[userId][item]["bag"] = ""
        DndAssets.inventoryDict = invDict
        return f"Dumped all items from {bag}!"
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
    invDict = DndAssets.inventoryDicts
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

    if user not in list(invDict.keys()):
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
        return "Initialized!!"
    else:
        return "You already have an inventory dumby"