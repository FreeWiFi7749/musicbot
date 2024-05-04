import json
import os
from discord.ext import commands
import wavelink

def load_node_config(guild_id):
    """ 特定のギルドのLavalinkノード設定をロードします。 """
    path = f"data/music/lavalink/node/{guild_id}/node_info.json"
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as file:
            config = json.load(file)
        return config
    else:
        raise FileNotFoundError("ノード設定ファイルが存在しません。")

async def connect_node(self, guild_id):
    try:
        config = load_node_config(guild_id)
        # Node オブジェクトをリストに包む
        node = wavelink.Node(**config, client=self)

        await self.wavelink.connect(nodes=[node])
        print(f"ギルド {guild_id} のノードに接続しました。")
        return node
    except Exception as e:
        print(f"ギルド {guild_id} のノード接続に失敗しました: {e}")
        return None

