import discord
from discord.ext import commands
import aiohttp
import os
import json
import wavelink
from dotenv import load_dotenv

load_dotenv()

LAVA_HOST = os.getenv('LAVA_HOST')
LAVA_PASS = os.getenv('LAVA_PASS')

class GetLavalinkStatusCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def fetch_metrics(self):
        url = f'https://{LAVA_HOST}/metrics'
        auth = aiohttp.BasicAuth('lavalink', LAVA_PASS)
        async with aiohttp.ClientSession() as session:
            async with session.get(url, auth=auth) as response:
                if response.status == 200 and 'text/plain' in response.headers['Content-Type']:
                    return await response.text()
                else:
                    return None
                
    @commands.hybrid_command(name='lavalink_status')
    async def lavalink_status(self, ctx):
        """Lavalinkのステータスを取得します。"""
        try:
            data = await self.fetch_metrics()
            if data is not None:
                cpu_usage = self.extract_metric(data, 'process_cpu_seconds_total')
                memory_usage = self.extract_metric(data, 'jvm_memory_bytes_used{area="heap"', convert_to='MB')
                total_players = 0
                active_players = 0

                # 利用可能なノードを取得
                node = wavelink.Pool.get_node()

                # ノードに接続されているすべてのプレイヤーをイテレート
                for player in node.players.values():
                    guild = self.bot.get_guild(player.guild.id)
                    if guild:
                        channel_id = guild.voice_client.channel.id
                        total_players += len(guild.members)
                        # プレイヤーが接続されているか確認
                        if player.connected:
                            active_players += sum(1 for member in guild.get_channel(channel_id).members if not member.bot)


                node_info = await self.get_guild_node_info(ctx.guild.id)
                node_status = 'Online' if node_info else 'Offline'
                node_id = node_info.get('identifier', 'Not available') if node_info else 'Not available'
                player = self.wavelink.get_player(ctx.guild.id)  # 取得するプレイヤー
                node_ping = 'Not available'
                if player:  # プレイヤーが存在するか確認
                    node_ping = player.ping
                    node_ping = f'{node_ping / 1000:.3f}s' if node_ping != -1 else 'Not available'


                embed = discord.Embed(title='Lavalink Status', color=0x0ff00)
                embed.add_field(name='CPU Usage (seconds)', value=f'{cpu_usage}', inline=False)
                embed.add_field(name='Memory Usage (Heap MB)', value=f'{memory_usage}', inline=False)
                embed.add_field(name='Total Players', value=f'{active_players}/{total_players}', inline=False)
                embed.add_field(name='Node', value=f'Status: {node_status}\nID: {node_id}\nPING: {node_ping}', inline=False)

                await ctx.send(embed=embed)
            else:
                await ctx.send('レスポンスが期待した形式ではありません。')
        except Exception as e:
            await ctx.send(f'エラーが発生しました: {str(e)}')

    def extract_metric(self, data, keyword, convert_to=None):
        """指定されたキーワードに基づいてメトリクスを抽出し、必要に応じて単位を変換します。"""
        lines = [line for line in data.split('\n') if keyword in line]
        if not lines:
            return 'Not available'
        value = lines[0].split()[-1]
        if convert_to == 'MB':
            return f'{float(value) / 1024**2:.2f}'
        return value
    
    async def get_guild_node_info(self, guild_id):
        path = f'data/music/lavalink/node/{guild_id}/node_info.json'
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                node_info = json.load(f)
            return node_info
        else:
            return None
        
async def setup(bot):
    await bot.add_cog(GetLavalinkStatusCog(bot))
