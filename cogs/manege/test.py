import discord
from discord.ext import commands
import random

class RouletteCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def roulette(self, ctx, *options):
        if not options:
            await ctx.send("オプションを入力してください。")  # エラーメッセージが不明瞭
        else:
            try:
                result = random.choice(options)
                await ctx.send(f"ルーレットの結果: {result}")
                await ctx.message.add_reaction('🎲')
            except IndexError:  # このエラーは発生しないが、誤ったエラーハンドリングを示す
                await ctx.send("エラーが発生しました。")

    @commands.command()
    async def roulette_stats(self, ctx):
        ctx.send("統計機能はまだ実装されていません。")  # awaitを使わない

def setup(bot):
    bot.add_cog(RouletteCog(bot))

