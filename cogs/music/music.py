import discord
from discord.ext import commands
import wavelink
from dotenv import load_dotenv
import os


load_dotenv()

LAVA_HOST = os.getenv('LAVA_HOST')
LAVA_PASS = os.getenv('LAVA_PASS')

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.wavelink = wavelink.Pool()
        self.is_24_7_mode = False

    @commands.hybrid_group(name='music', aliases=['m'])
    async def music(self, ctx):
        """音楽関連のコマンドです。"""
        pass

    @music.command(name='join', aliases=['j'])
    async def join(self, ctx):
        """ボイスチャンネルに参加します。"""
        channel = ctx.author.voice.channel
        await channel.connect(cls=wavelink.Player)
        await ctx.send("ボイスチャンネルに参加しました。")

    @music.command(name='play', aliases=['p'])
    async def play(self, ctx, *, query: str):
        """曲を検索して再生します。"""
        if ctx.voice_client is None:
            await ctx.invoke(self.join)

        await ctx.defer()

        if "youtube.com" in query or "youtu.be" in query or "soundcloud.com" in query:
            tracks = await wavelink.Pool.fetch_tracks(query)
        else:
            tracks = await wavelink.Pool.fetch_tracks(f'ytsearch:{query}')
    
        if not tracks:
            return await ctx.send('その曲は見つかりませんでした。')

        player = ctx.voice_client

        # プレイリストか単一のトラックかのチェックと処理
        if isinstance(tracks, wavelink.Playlist):
            for track in tracks.tracks:
                player.queue.put(track)
            await ctx.send(f'プレイリストから{len(tracks.tracks)}曲をキューに追加しました。')
            continue_play = not player.playing
            if continue_play:
                await player.play(tracks.tracks[0])
                embed = await self.now_playing_embed(player.current, requester=ctx.author)
                await ctx.send(embed=embed, silent=True)
        else:  # 通常のトラックリスト
            track = tracks[0]  # 最初のトラックを取得
            track.extras = {"requester_id": ctx.author.id}  # リクエスターのIDを追加
            print(track.extras)

            if not player.playing:
                await player.play(track)
                embed = await self.now_playing_embed(player.current, requester=ctx.author)
                await ctx.send(embed=embed, silent=True)
            else:
                track_info = {"track": track, "requester": ctx.author}
                player.queue.put(track_info)
                await ctx.send(f'キューに追加しました: {track.title}')

    @music.command(name='pause', aliases=['pa'])
    async def pause(self, ctx):
        """音楽を一時停止します。"""
        if ctx.voice_client is None:
            await self.voice_none(ctx)
            return
        await ctx.voice_client.pause()
        await ctx.send("音楽を一時停止しました。")

    @music.command(name='resume', aliases=['r'])
    async def resume(self, ctx):
        """音楽の再生を再開します。"""
        if ctx.voice_client is None:
            await self.voice_none(ctx)
            return
        await ctx.voice_client.resume()
        await ctx.send("音楽の再生を再開しました。")

    @music.command(name='disconnect', aliases=['d'])
    async def disconnect(self, ctx):
        """ボイスチャンネルから切断します。"""
        if ctx.voice_client is None:
            await self.voice_none(ctx)
            return
        await ctx.voice_client.disconnect()
        await ctx.send("ボイスチャンネルから切断しました。")

    @music.command(name='volume', aliases=['v'])
    async def volume(self, ctx, volume: int):
        """音量を設定します。"""
        if ctx.voice_client is None:
            await self.voice_none(ctx)
            return
        await ctx.voice_client.set_volume(volume)
        await ctx.send(f"音量: {volume}")

    @music.command(name='queue', aliases=['q'])
    async def queue(self, ctx):
        """再生キューを表示します。"""
        if ctx.voice_client is None:
            await self.voice_none(ctx)
            return
        player = ctx.voice_client
        if not player.queue:
            return await ctx.send('再生キューは空です。')


        embed = discord.Embed(title='\u200B', color=0x00ff00)
        embed.description = '> **Music Queue**\n'
        total_seconds = sum(track.length for track in player.queue) // 1000
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        embed.set_footer(text=f'Queue - {len(player.queue)}曲 | Time - {hours}時間 {minutes}分')
        embed.set_image(url='https://image.frwi.net/uploads/D3E24B95-2EAE-4C18-AF8E-3DC8BEB31866.webp')
        queue_tracks = list(player.queue)

        if queue_tracks:
            extras_dict = dict(queue_tracks[0].extras)
            music_requester = extras_dict.get("requester_id", 0)
        else:
            music_requester = 0

        past_tracks = list(player.queue.history)
        past_tracks = past_tracks[-5:]

        queue_tracks = past_tracks + queue_tracks

        num_tracks = 9
        center_index = 4

        for i in range(num_tracks):
            track_index = i - center_index

            if track_index == 0:
                spaces = ''
            else:
                spaces = '  ' * (abs(track_index))

            track_position = track_index + len(past_tracks)
            if 0 <= track_position < len(queue_tracks):
                track_info = queue_tracks[track_position].title 
                track_url = queue_tracks[track_position].uri
            else:
                track_info = '-----'

            highlight_index = center_index - 1

            if i == highlight_index:
                if track_info == '-----':
                    embed.description += f'**{spaces}-----**\n'
                else:
                    embed.description += f'**{spaces}[{track_info}]({track_url})**\n'
            else:
                if track_info == '-----':
                    embed.description += f'{spaces}-----\n'
                else:
                    embed.description += f'{spaces}[{track_info}]({track_url})\n'

        # エンベッドを送信
        await ctx.send(embed=embed)

    @music.command(name='skip', aliases=['s'])
    async def skip(self, ctx):
        """曲をスキップします。"""
        if ctx.voice_client is None:
            await self.voice_none(ctx)
            return
        player = ctx.voice_client
        if not player.queue:
            return await ctx.send('再生キューは空です。')
        await player.stop()
        await ctx.send("曲をスキップしました。")

    @music.command(name='clear', aliases=['c'])
    async def clear(self, ctx):
        """再生キューをクリアします。"""
        if ctx.voice_client is None:
            await self.voice_none(ctx)
            return
        player = ctx.voice_client
        player.queue.clear()
        await ctx.send("再生キューをクリアしました。")

    @music.command(name='remove', aliases=['rm'])
    async def remove(self, ctx, index: int):
        """指定されたインデックスの曲を再生キューから削除します。"""
        if ctx.voice_client is None:
            await self.voice_none(ctx)
            return
        player = ctx.voice_client
        if index < 1 or index > len(player.queue):
            return await ctx.send('再生キューの範囲外のインデックスです。')
        removed_track = player.queue.pop(index - 1)
        await ctx.send(f'{removed_track.title} を再生キューから削除しました。')

    @music.command(name='shuffle', aliases=['sh'])
    async def shuffle(self, ctx):
        """再生キューをシャッフルします。"""
        if ctx.voice_client is None:
            await self.voice_none(ctx)
            return
        player = ctx.voice_client
        player.queue.shuffle()
        await ctx.send("再生キューをシャッフルしました。")

    @music.command(name='loop', aliases=['l'])
    async def loop(self, ctx, *, option: str = None):
        """再生キューをループ再生します。オプション: none, track, all"""
        if ctx.voice_client is None:
            await self.voice_none(ctx)  
            return      
        player = ctx.voice_client

        # オプションに基づいてループモードを設定
        if option == 'track':
            await player.queue.set_mode(wavelink.QueueMode.loop)
            mode_description = "現在のトラックをループ"
        elif option == 'all':
            await player.queue.set_mode(wavelink.QueueMode.loop_all)
            mode_description = "全てのトラックをループ"
        elif option == 'none':
            await player.queue.set_mode(wavelink.QueueMode.normal)
            mode_description = "ループなし"
        else:
            return await ctx.send("オプションは 'none', 'track', 'all' のいずれかである必要があります。")

        await ctx.send(f'ループモード変更: {mode_description}')

    @music.command(name='nowplaying', aliases=['np'])
    async def nowplaying(self, ctx):
        """現在再生中の曲を表示します。"""
        if ctx.voice_client is None:
            await self.voice_none(ctx)
            return
        player = ctx.voice_client
        if not player.current:
            return await ctx.send('再生中の曲はありません。')
        embed = await self.now_playing_embed(player.current, ctx.author)
        await ctx.send(embed=embed, silent=True)

    @music.command(name='24-7', aliases=['247'])
    async def twenty_four_seven(self, ctx, mode: bool):
        """24/7モードを設定します。"""
        self.is_24_7_mode = mode
        mode_status = "有効" if mode else "無効"
        await ctx.send(f"24/7モードを{mode_status}に設定しました。")


    @commands.Cog.listener()
    async def on_wavelink_track_end(self, payload: wavelink.TrackEndEventPayload) -> None:
        # payload.player が None でないことを確認
        if payload.player is None:
            print("payload.player が None です。")
            return
        
        if self.is_24_7_mode:
            if payload.player.queue.is_empty:
                return await payload.player.play(payload.track)
            
        if not hasattr(payload.player, 'queue'):
            print("payload.player に queue 属性がありません。")
            return

        if not payload.player.queue.is_empty:
            next_track = payload.player.queue.get()
            await payload.player.play(next_track)
            extras_dict = dict(next_track.extras)  # ExtrasNamespaceを辞書に変換
            requester_id = extras_dict.get("requester_id", 0)  # 辞書からrequester_idを取得、存在しない場合は0を使用
            requester = self.bot.get_user(requester_id) or None
            embed = await self.now_playing_embed(next_track, requester)
            await payload.player.channel.send(embed=embed, silent=True)

    async def now_playing_embed(self, track, requester):
        duration_minutes, duration_seconds = divmod(track.length // 1000, 60)

        embed = discord.Embed(title='Now Playing', color=0x00ff00)
        embed.add_field(name='Title', value=f"[{track.title}]({track.uri})", inline=False)
        embed.add_field(name='Duration', value=f'{duration_minutes}:{duration_seconds:02}', inline=False)
        if track.artwork:
            embed.set_thumbnail(url=track.artwork)
    
        if requester:
            embed.set_footer(text=f'Requested by {requester.display_name}\n{track.position}曲目', icon_url=requester.avatar.url)
        else:
            embed.set_footer(text=f'Requested by Unknown\n{track.position}曲目')

        return embed

    async def voice_none(self, ctx):
        await ctx.send("botがボイスチャンネルに接続していません\n`/music join` を使用してボイスチャンネルに参加させてください。", ephemeral=True)
        return 

async def setup(bot):
    await bot.add_cog(Music(bot))