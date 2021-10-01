__all__ = [
    "init",
    "savePurse",
    "saveInv",
    "x",
    "inventoryDict",
    "purseDict",
    "bagIds",
    "coinPieceList",
    "coinRates"
    ]
import json

inventoryDict = {}
purseDict = {}
coinPieceList = ["gp", "sp", "cp"]
coinRates = {
    'gpRate':{'gp':1, 'sp':10, 'cp':1000},
    'spRate':{'gp':10,'sp':1, 'cp':100},
    'cpRate':{'gp':1000, 'sp':100, 'cp':1},

}
bagIds = {}

def init():
    global inventoryDict
    global purseDict
    global bagIds
    with open("json/inventory.json") as inv_file:
        inventoryDict = dict(json.load(inv_file))
    with open("json/coin.json") as purse_file:
        purseDict = dict(json.load(purse_file))
    with open("json/bagId.json") as bag_file:
        bagIds = dict(json.load(bag_file))

def savePurse():
    pass

def saveInv():
    pass