__all__ = [
    "init",
    "savePurse",
    "saveInv",
    "x",
    "inventoryDict",
    "purseDict",
    "bagIds",
    "coinPieceList"
    ]
import json

inventoryDict = {}
purseDict = {}
coinPieceList = ["gp", "sp", "cp"]
bagIds = {}

def init():
    global inventoryDict
    global purseDict
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