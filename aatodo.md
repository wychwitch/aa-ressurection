Overhaul Item storage where the bags are just a tag like quantity and name, so items don't HAVE to be in a bag

Consider combining those items and instead include a -u @user flag

Inv (displays your inventory, -f show the full inv, even private items)

- Get @user (gets the inventory of other user (dm can show full inventory with -f)

- Add (gives yourself item) IMPLEMENTED

- Give @user (gives specified user the item, player has to have item to give it unless they're dm)

Remove (removes item from inventory, easy) 

Destroy @user (destroys item another players inventory, dm only)

Move item, bag (Moves item to the bag)

Move  -f bag  -t bag moves all items From bag To bag

For displaying items, first get distinct list of all the bag tags, then do smth to grab them something about using lists idk I'll figure it out when I get there 

Add quote authors
Also clean and comment code GOD
Bulk item add or remove support with multiple -i's

Also redo same example values so they contain if it should be a bool or not, gets rid of that one tag
 Dict of dict
Or not even that just check if sane value is bool and if so don't pair up and add a true

Will make the pairing more weirf but ghjjgbi can make it work
Var to hold argument until it gets assigned a value in pairing func
Add coins and character worth (by adding up any treasures they have)