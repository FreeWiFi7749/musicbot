from discord.ext import commands
import json
from dotenv import load_dotenv
import os

load_dotenv()

lavalink_host = os.getenv('LAVA_HOST')
lavalink_pass = os.getenv('LAVA_PASS')

class GuildNodeConfig(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        config = {
            "identifier": f"node_{guild.id}",
            "uri": f"https://{lavalink_host}:443",
            "password": lavalink_pass,
        }
        os.makedirs(f'data/music/lavalink/node/{guild.id}', exist_ok=True)
        with open(f'data/music/lavalink/node/{guild.id}/node_info.json', 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4)
        print(f"ギルド {guild.id} のためのLavalinkノード設定を作成しました。")

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        path = f'data/music/lavalink/node/{guild.id}/node_info.json'
        if os.path.exists(path):
            os.remove(path)
            print(f"ギルド {guild.id} のLavalinkノード設定を削除しました。")

async def setup(bot):
    await bot.add_cog(GuildNodeConfig(bot))
