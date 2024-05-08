import discord
from discord.ext import commands
import random

class RouletteCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def roulette(self, ctx, *options):
        if not options:
            await ctx.send("オプションを最低一つは入力してください。例: !roulette 選択肢1 選択肢2 選択肢3")
        else:
            result = random.choice(options)
            await ctx.send(f"ルーレットの結果: {result}")
            # 結果をリアクションで表示
            await ctx.message.add_reaction('🎲')

    @commands.command()
    async def roulette_stats(self, ctx):
        # 統計情報を表示するダミーのコマンド
        await ctx.send("統計機能はまだ実装されていません。")

def setup(bot):
    bot.add_cog(RouletteCog(bot))

