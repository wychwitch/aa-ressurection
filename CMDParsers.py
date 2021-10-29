import argparse

__all__ = [
    "invAddCMDParse",
    "invRemCMDParse",
    "invMovCMDParse",
    "invHideCMDParse",
    "invDumpCMDParse",
    "modCoinCMDparse",
    "convertCoinCMDparse",
    "transferCoinCMDparse",
    "changeDescCMDParse",
    "lookCMDParse"
    ]

# PARSERS REMOVE LATER AND PUT IN OWN MODULE
def invAddCMDParse(parseStr):
    parser = NoExitParser(description="Add Item Command", 
        usage = "inv add -i <item name> [-b <bag name>]  [-p] [-h] [-s <stock amount>] [-w <worth formatted like `1gp`>] [-u <user mention>]", epilog=" <Text> [-optionalCommand]", conflict_handler="resolve")
    
    
    required = parser.add_argument_group('required arguments')
    optional = parser.add_argument_group('optional arguments')
    
    optional.add_argument("-b","--bag", help="The bag you're adding the item to! Defaults to no bag.", nargs='+',
        default="", metavar='<bag name>', required=False, action=MyAction)
    
    optional.add_argument("--bulk", help="Allows you to add multiple different items at once using -i flags!",
            required=False, action='store_true')
    
    if "--bulk" in parseStr:
        required.add_argument("-i","--item", help="The item you're adding to your inventory!", nargs='+',
            required=False, metavar='<item name>', action=MyAppend)
    else:
        required.add_argument("-i","--item", help="The item you're adding to your inventory!", nargs='+',
            required=False, metavar='<item name>', action=MyAction)
    
    optional.add_argument("-p","--private", help="Marks the item as private!", 
        required=False, action='store_true')
    
    optional.add_argument("-h","--help", help="Displays this help message.", default="", dest="help", action=MyHelpAction)
    
    optional.add_argument("-s","--stock", help="The amount of the item you want to add!",
        default=1, metavar='<stock amount>', required=False, type=int)
    
    optional.add_argument("-w","--worth", help="How much the item is worth!", nargs='+',
        default="0cp", metavar='<worth amount>', required=False, action=MyAction)

    optional.add_argument("-d","--desc", help="How much the item is worth!", nargs='+',
        default="", metavar='<worth amount>', required=False, action=MyAction)
    
    optional.add_argument("-u","--user", metavar='<user mention>', help="The user you'll add the item to! Only usable by someone with the DM role.", 
        required=False, type=str)

    return parser.parse_args(parseStr.split())

def invRemCMDParse(parseStr):
    parser = NoExitParser(description="Remove Item Command",  
        usage = "inv remove -i <item name> [-b <bag name>]  [-h] [-s <stock amount>] [-a] [-u user mention>]", epilog=" <Text> [-optionalCommand]",conflict_handler="resolve")

    required = parser.add_argument_group('You must use at least one of these arguments')
    optional = parser.add_argument_group('optional arguments')

    required.add_argument("-b","--bag", 
        help="The bag to remove!", 
        nargs='+', default="", 
        required=False,  metavar='<bag name>',action=MyAction)

    required.add_argument("-i","--item", 
        help="The item to remove!", 
        nargs='+', required=False,  metavar='<item name>',action=MyAction)

    optional.add_argument("-a","--all", 
        help="Removing all of the item!", action='store_true')

    optional.add_argument("-s","--stock", help="The amount of the item to remove!",
        default=1, metavar='<stock amount>', required=False, type=int)

    optional.add_argument("-u","--user", help="The user mention!",  metavar='<user mention>',
        required=False, type=str)
    
    optional.add_argument("-h","--help", help="Displays this help message!", dest="help", default="", action=MyHelpAction)
    return parser.parse_args(parseStr.split())

def invMovCMDParse(parseStr):
    parser = NoExitParser(description="Move Item Command", usage = "inv move -i <item name> -b <bag name> [-h] [-u <user mention>]", epilog=" <Text> [-optionalCommand]", conflict_handler="resolve")

    required = parser.add_argument_group('required arguments')
    optional = parser.add_argument_group('optional arguments')

    required.add_argument("-b","--bag","-t","--to", dest='bag',
        help="The bag to move the item to!",  metavar='<bag name>',
        nargs='+', default="", 
        required=False, action=MyAction)

    required.add_argument("-i","--item", 
        help="The item to remove!", 
        nargs='+',  metavar='<item name>', required=False, action=MyAction)

    optional.add_argument("-u","--user", 
        help="User to target!", 
        required=False, action=MyAction)
    
    optional.add_argument("-h","--help", metavar='<user mention>', help="Displays this", default="", dest="help", action=MyHelpAction)
    
    return parser.parse_args(parseStr.split())

def invHideCMDParse(parseStr):
    parser = NoExitParser(description="Un/Hide Command", usage = "inv (un) -i <item name> [-b <bag name>] [-h] [-u <user mention>]", epilog=" <Text> [-optionalCommand]", conflict_handler="resolve")
    
    required = parser.add_argument_group('You must use at lease one of these arguments')
    optional = parser.add_argument_group('optional arguments')

    required.add_argument("-b","--bag", help="Bag to hide all the items inside of!", nargs='+',
     default="", metavar='<bag name>', required=False, action=MyAction)
    
    required.add_argument("-i","--item", help="Item to hide!", nargs='+', metavar='<item name>',
         required=False, action=MyAction)
    
    optional.add_argument("-u","--user", metavar='<user mention>', help="User whose item(s) to hide!", required=False, action=MyAction)
    
    optional.add_argument("-h","--help", help="Displays this!", default="", dest="help", action=MyHelpAction)
    return parser.parse_args(parseStr.split())

def invDumpCMDParse(parseStr):
    parser = NoExitParser(description="Dump Bag Command",usage = "inv dump -f <bag name> -t <bag name> [-h] [-u <user mention>]", epilog=" <Text> [-optionalCommand]", conflict_handler="resolve")
    
    required = parser.add_argument_group('required arguments')
    optional = parser.add_argument_group('optional arguments')

    required.add_argument("-f","--from", dest="fromBag" ,help="The bag you're dumping out!", nargs='+', metavar='<bag name>',
     default="", required=False, action=MyAction)
    
    required.add_argument("-t","--to", dest="toBag", help="The bag you're dumping into!", metavar='<bag name>', nargs='+',
         required=True, action=MyAction)
    
    optional.add_argument("-u","--user", metavar='<user mention>', help="User mention",
         required=False, action=MyAction)
    
    optional.add_argument("-h","--help", default="", help="This message!", dest="help", action=MyHelpAction)
    return parser.parse_args(parseStr.split())

def modCoinCMDparse(parseStr):
    parser = NoExitParser(description="Add/Remove Coin Command", usage = "inv add/remove -c <coin formatted like `1gp`> [-p] [-h] [-u <user mention>]", epilog=" <Text> [-optionalCommand]", conflict_handler="resolve")
    
    required = parser.add_argument_group('required arguments')
    optional = parser.add_argument_group('optional arguments')

    required.add_argument(dest="coin", help="Coin to add or remove from your coinpurse!", metavar='<coin in the format `1gp`>', nargs='+',
        default="0np", action=MyAction)
    
    optional.add_argument("-p","--private", help="Flag for adding to your private coinpurse!", 
        required=False, action='store_true')
    
    optional.add_argument("-u","--user", help="User mention!",
         required=False, action=MyAction)
    
    optional.add_argument("-h","--help", default="", help="This message!!!", dest="help", action=MyHelpAction)
    return parser.parse_args(parseStr.split())

def convertCoinCMDparse(parseStr):
    parser = NoExitParser(description="Convert Coin Command",  usage = "inv add/remove -f <coin formatted like `1gp`> -t <coin formatted like `1gp`> [-p] [-h] [-u <user mention>]", epilog=" <Text> [-optionalCommand]",conflict_handler="resolve")
    
    required = parser.add_argument_group('required arguments')

    optional = parser.add_argument_group('optional arguments')
    
    required.add_argument("-f","--from", dest="fromCoin", help="The coin you're converting from!", nargs='+',  metavar='<coin>',
     default="0np", required=False, action=MyAction)
    
    required.add_argument("-to","--to", dest="toCoin" ,help="The coin you're converting to!",
    metavar='<coin>', nargs='+',
     default="0np", required=False, action=MyAction)
    
    optional.add_argument("-p","--private", help="If you want to convert coin from your private coinpurse!", 
        required=False, action='store_true')
    
    optional.add_argument("-u","--user", metavar='<user metion>',help="User to hjsdfd!",
         required=False, action=MyAction)
    
    optional.add_argument("-h","--help", default="", help="This message!", dest="help", action=MyHelpAction)
    return parser.parse_args(parseStr.split())

def transferCoinCMDparse(parseStr):
    parser = NoExitParser(description="Transfer Coin Command", usage = "coin transfer -c <coin formatted as `1gp`> -t <target coinpurse, must be `public` or `private`>  [-h] [-u <user mention>]", epilog=" <Text> [-optionalCommand]", conflict_handler="resolve")

    required = parser.add_argument_group('required arguments')
    optional = parser.add_argument_group('optional arguments')

    required.add_argument("-c","--coin",help="test help!!!", nargs='+',
        default="0np", metavar='<coin>',required=False, action=MyAction)
    
    required.add_argument("-t","--toPurse", help="test help!!!", nargs='+', metavar='<receiving purse>',
        required=False, action=MyAction)
        
    optional.add_argument("-u","--user",metavar='<user mention>', help="The user who wil get their coin transferred! Can only be used as DM!",
         required=False, action=MyAction)
    
    optional.add_argument("-h","--help", default="", help="Displays this message!", dest="help", action=MyHelpAction)
    
    return parser.parse_args(parseStr.split())

def changeDescCMDParse(parseStr):
    parser = NoExitParser(description="Transfer Coin Command", usage = "coin transfer -c <coin formatted as `1gp`> -t <target coinpurse, must be `public` or `private`>  [-h] [-u <user mention>]", epilog=" <Text> [-optionalCommand]", conflict_handler="resolve")

    required = parser.add_argument_group('required arguments')
    optional = parser.add_argument_group('optional arguments')

    optional.add_argument("-h","--help", help="Displays this help message.", default="", dest="help", action=MyHelpAction)

    required.add_argument("-i","--item", help="The item you're adding to your inventory!", nargs='+',
            required=False, metavar='<item name>', action=MyAction)

    required.add_argument("-d","--desc",help="Description for the item!", nargs='+',
         metavar='<description>',required=False, action=MyAction)
    
    optional.add_argument("-u","--user", metavar='<user mention>', help="The user you'll add the item to! Only usable by someone with the DM role.", 
        required=False, type=str)
    
    return parser.parse_args(parseStr.split())

def lookCMDParse(parseStr):
    parser = NoExitParser(description="Transfer Coin Command", usage = "coin transfer -c <coin formatted as `1gp`> -t <target coinpurse, must be `public` or `private`>  [-h] [-u <user mention>]", epilog=" <Text> [-optionalCommand]", conflict_handler="resolve")

    required = parser.add_argument_group('required arguments')
    optional = parser.add_argument_group('optional arguments')

    optional.add_argument("-h","--help", help="Displays this help message.", default="", dest="help", action=MyHelpAction)

    required.add_argument("-i","--item", help="The item you're adding to your inventory!", nargs='+',
            required=False, metavar='<item name>', action=MyAction)

    required.add_argument("-d","--desc",help="Description for the item!", nargs='+',
         metavar='<description>',required=False, action=MyAction)
    
    optional.add_argument("-u","--user", metavar='<user mention>', help="The user you'll add the item to! Only usable by someone with the DM role.", 
        required=False, type=str)
    
    optional.add_argument("-f","--full", help="Shows item even if its hidden!", 
        required=False, action='store_true')
    
    return parser.parse_args(parseStr.split())

class NoExitParser(argparse.ArgumentParser):
    def error(self, message):
        raise ValueError(message)

# https://stackoverflow.com/questions/34256250/parsing-a-string-with-spaces-from-command-line-in-python
class MyAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, ' '.join(values))

class MyStripAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, ' '.join(values).strip('@<>'))

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

class MyHelpAction(argparse.Action):

    def __init__(self,
                 option_strings,
                 dest=argparse.SUPPRESS,
                 default=argparse.SUPPRESS,
                 help=None):
        super(MyHelpAction, self).__init__(
            option_strings=option_strings,
            dest=dest,
            default=default,
            nargs=0,
            help=help)

    def __call__(self, parser, namespace, values, option_string=None):
        help = parser.format_help()
        setattr(namespace, self.dest, help)

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