if this then that
inv functs
- pairArgs == zipArguments
- splitByIndex == splitByIndices
- addToInv == addToInv
~~- getUser  == getUser~~
- ~~changeItemQuant == modItemStock~~
- invSanityCheck == validateArgs
- getInv == getInv
~~- checkIfDm == checkDM~~
- find_by_key == findByKey

coin funcs
- getAllCoinStr == getFormattedWealth
- formatConvCoin == formatCoin
- ~~getTotalItemWorth == sumItemWorth~~
- ~~modifyCoin == addSubPurse~~
- parseGpString == parseCoinPiece
- convertCoinPurse == sumPurseWorth
  - Remove function, instead use both getPurseAsCopper and sumCopper
- ~~coinPurseInCopper == getPurseAsCopper~~
~~- convertCoin == sumCopper~~
- ~~getCopper == getCoinAsCopper~~

General Formatting notes
+ quantity = stock
+ coin = tupledCoin or formatted as 11gp or so
+ coin (value) ==  coinVal
+ coinpurse = purse
+ yp == coinPiece
+ sane == valid
+ dm == DM
+ userid == userId
+ purseWorth
+ itemWorth
+ rgsValues = argsModels

Good Var Name notes
+ Choose a single word with meaning
+ Avoid generic names
+ prefix or suffix
+ consistant formatting
+ Pack Informaiton
+ Each function should contain a verb
+ 