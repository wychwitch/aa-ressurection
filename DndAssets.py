__all__ = [
    "init",
    "savePurse",
    "saveInv",
    "x",
    "inventoryDict",
    "purseDict",
    "bagIds",
    "coinPieceList",
    "coinRates",
    "saveAll",
    "currentCharas"
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
    global currentCharas
    with open("json/inventory.json") as inv_file:
        inventoryDict = dict(json.load(inv_file))
    with open("json/coin.json") as purse_file:
        purseDict = dict(json.load(purse_file))
    with open("json/bagId.json") as bag_file:
        bagIds = dict(json.load(bag_file))
    with open("json/currentCharacter.json") as chara_file:
        currentCharas = dict(json.load(chara_file))

def saveAll():
    update_db(inventoryDict, "inventory.json")
    update_db(purseDict, "coin.json")
    update_db(bagIds, "bagId.json")
    update_db(currentCharas, "currentCharacter.json")

def update_db(database, filename):
    with open("json/"+filename, "w") as dtb:
        json.dump(database, dtb, indent=4)