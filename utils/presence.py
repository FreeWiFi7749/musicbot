import discord
import random
import asyncio

presences = [
    {"type": "Listening", "name": "作業用BGMを再生中", "state": "BGM From SoundCloud"},

]

async def update_presence(bot):
    while not bot.is_closed():
        presence = random.choice(presences)
        if presence["type"] == "Custom":
            activity = discord.Activity(type=discord.ActivityType.custom, name=presence["name"])
        else:
            activity_type = getattr(discord.ActivityType, presence["type"].lower(), discord.ActivityType.playing)
            activity = discord.Activity(type=activity_type, name=presence["name"], state=presence.get("state", None))
        
        await bot.change_presence(activity=activity)
        await asyncio.sleep(15)