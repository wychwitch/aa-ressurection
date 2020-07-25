import discord
import linecache
import random
import re
import json

from os import path

# We should move the quote dictionary numbers to the dictionary itself, maybe with the key "num" that just stores an int. This further reduces the json bloat hgdhfdg

#might be too clunky but i figured could be used for 90% of channel-response commands
async def discordPrint(ctx, str):
    await ctx.send(str)
