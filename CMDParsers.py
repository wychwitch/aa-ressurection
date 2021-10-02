import argparse

__all__ = [
    "invAddCMDParse",
    "invRemCMDParse",
    "invMovCMDParse",
    "invHideCMDParse",
    "invDumpCMDParse",
    "modCoinCMDparse",
    "convertCoinCMDparse",
    "transferCoinCMDparse"
    ]

# PARSERS REMOVE LATER AND PUT IN OWN MODULE
def invAddCMDParse(parseStr):

    parser = NoExitParser(description="Add Command")
    parser.add_argument("-b","--bag", help="test help!!!", nargs='+',
     default="", required=False, action=MyAction)
    if "--bulk" in parseStr:
        parser.add_argument("--bulk", help="test help!!!", nargs='+',
         required=False, action=MyAction)
        parser.add_argument("-i","--item", help="test help!!!", nargs='+',
         required=False, action=MyAppend)
    else:
        parser.add_argument("-i","--item", help="test help!!!", nargs='+',
         required=False, action=MyAction)
    parser.add_argument("-p","--private", help="test help!!!", action='store_true')
    parser.add_argument("-s","--stock", help="test help!!!", nargs='+',
     default=1, required=False, type=int, action=MyAction)
    parser.add_argument("-w","--worth", help="test help!!!", nargs='+',
     default="0cp", required=False, action=MyAction)
    parser.add_argument("-u","--user", help="test help!!!", required=False, action=MyAction)

    return parser.parse_args(parseStr.split())

def invRemCMDParse(parseStr):
    parser = NoExitParser(description="Add Command")

    parser.add_argument("-b","--bag", 
        help="The bag to remove!", 
        nargs='+', default="", 
        required=False, action=MyAction)

    parser.add_argument("-i","--item", 
        help="The item to remove!", 
        nargs='+', required=False, action=MyAction)

    parser.add_argument("-a","--all", 
        help="Removing all of the item!", action='store_true')

    parser.add_argument("-s","--stock", 
        help="The stock for the item!", 
        nargs='+', default=1, 
        required=False, type=int, action=MyAction)

    parser.add_argument("-u","--user", 
        help="test help!!!", 
        required=False, action=MyAction)
    return parser.parse_args(parseStr.split())

def invMovCMDParse(parseStr):
    parser = NoExitParser(description="Add Command")

    parser.add_argument("-b","--bag","-t","--to", dest='bag',
        help="The bag to remove!", 
        nargs='+', default="", 
        required=False, action=MyAction)

    parser.add_argument("-i","--item", 
        help="The item to remove!", 
        nargs='+', required=False, action=MyAction)

    parser.add_argument("-u","--user", 
        help="test help!!!", 
        required=False, action=MyAction)
    return parser.parse_args(parseStr.split())

def invHideCMDParse(parseStr):
    parser = NoExitParser(description="Add Command")
    parser.add_argument("-b","--bag", help="test help!!!", nargs='+',
     default="", required=False, action=MyAction)
    parser.add_argument("-i","--item", help="test help!!!", nargs='+',
         required=True, action=MyAction)
    parser.add_argument("-u","--user", help="test help!!!", required=False, action=MyAction)

    return parser.parse_args(parseStr.split())

def invDumpCMDParse(parseStr):
    parser = NoExitParser(description="Add Command")
    parser.add_argument("-f","--from", dest="fromBag" ,help="test help!!!", nargs='+',
     default="", required=False, action=MyAction)
    parser.add_argument("-t","--to", dest="toBag", help="test help!!!", nargs='+',
         required=True, action=MyAction)
    parser.add_argument("-u","--user", help="test help!!!",
         required=False, action=MyAction)

    return parser.parse_args(parseStr.split())

def modCoinCMDparse(parseStr):
    parser = NoExitParser(description="Add Command")
    parser.add_argument("-c","--coin",help="test help!!!", nargs='+',
        default="0np", required=False, action=MyAction)
    parser.add_argument("-p","--private", help="test help!!!", 
        required=False, action='store_true')
    parser.add_argument("-u","--user", help="test help!!!",
         required=False, action=MyAction)

    return parser.parse_args(parseStr.split())

def convertCoinCMDparse(parseStr):
    parser = NoExitParser(description="Add Command")
    parser.add_argument("-f","--from", dest="fromCoin", help="test help!!!", nargs='+',
     default="0np", required=False, action=MyAction)
    parser.add_argument("-to","--to", dest="fromCoin" ,help="test help!!!", nargs='+',
     default="0np", required=False, action=MyAction)
    parser.add_argument("-p","--private", help="test help!!!", 
        required=False, action='store_true')
    parser.add_argument("-u","--user", help="test help!!!",
         required=False, action=MyAction)

    return parser.parse_args(parseStr.split())

def transferCoinCMDparse(parseStr):
    parser = NoExitParser(description="Add Command")
    parser.add_argument("-c","--coin",help="test help!!!", nargs='+',
        default="0np", required=False, action=MyAction)
    
    parser.add_argument("-t","--toPurse", help="test help!!!", nargs='+', 
        required=False, action=MyAction)
    parser.add_argument("-f","--fromPurse", help="test help!!!", 
         required=False, action=MyAction)
    parser.add_argument("-u","--user", help="test help!!!",
         required=False, action=MyAction)

    return parser.parse_args(parseStr.split())



class NoExitParser(argparse.ArgumentParser):
    def error(self, message):
        raise ValueError(message)

# https://stackoverflow.com/questions/34256250/parsing-a-string-with-spaces-from-command-line-in-python
class MyAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, ' '.join(values))

class MyAppend(argparse.Action):
    def __init__(self,
                 option_strings,
                 dest,
                 nargs=None,
                 const=None,
                 default=None,
                 type=None,
                 choices=None,
                 required=False,
                 help=None,
                 metavar=None):
        super(MyAppend, self).__init__(
            option_strings=option_strings,
            dest=dest,
            nargs=nargs,
            const=const,
            default=default,
            type=type,
            choices=choices,
            required=required,
            help=help,
            metavar=metavar)

    def __call__(self, parser, namespace, values, option_string=None):
        items = getattr(namespace, self.dest, None)
        items = my_copy_items(items)
        items.append(' '.join(values))
        setattr(namespace, self.dest, items)

def my_copy_items(items):
    if items is None:
        return []
    # The copy module is used only in the 'append' and 'append_const'
    # actions, and it is needed only when the default value isn't a list.
    # Delay its import for speeding up the common case.
    if type(items) is list:
        return items[:]
    import copy
    return copy.copy(items)