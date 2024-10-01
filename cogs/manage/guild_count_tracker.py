from discord import app_commands
from discord.ext import commands
from discord.ext import tasks
import discord

import matplotlib.pyplot as plt
import datetime
import aiofiles
import io
import os
import json



JST = datetime.timezone(datetime.timedelta(hours=+9), "JST")

try:
  report_bot_service_cha = int(os.environ["report_bot_service_cha_data"])
except KeyError:
  with open("env.json", mode="r") as f:
    content = json.load(f)
  report_bot_service_cha = int(content["report_bot_service_cha_data"])



class GuildCountTracker(commands.Cog):
  def __init__(self, bot: commands.Bot):
    self.bot = bot
    self.record_tasks.start()


  @tasks.loop(time=datetime.time(hour=0, minute=0, tzinfo=JST))
  async def record_tasks(self):
    # 鯖数を記録
    await self.record_guild_count()
    # plotする
    img_buffer = await self.plot_graph()
    # 送信チャンネル取得
    channel = self.bot.get_channel(report_bot_service_cha)
    # ファイル送信
    await channel.send(f"Guild_count: {len(self.bot.guilds)}", file=discord.File(img_buffer, 'guild_count_graph.png'))


  async def record_guild_count(self):
    # サーバー数を取得
    guild_count = len(self.bot.guilds)
    today = datetime.datetime.now().strftime('%Y-%m-%d')

    #CSVファイルにサーバー数を追記
    async with aiofiles.open('data/guild_counts.csv', mode='a') as csvfile:
      await csvfile.write(f'\n{today},{guild_count}')


  async def plot_graph(self):
    dates = []
    counts = []

    # 非同期でCSVファイルからデータを読み込み
    async with aiofiles.open('data/guild_counts.csv', mode='r') as csvfile:
      async for line in csvfile:
        row = line.strip().split(',')
        dates.append(datetime.datetime.strptime(row[0], '%Y-%m-%d'))
        counts.append(int(row[1]))

    # グラフを作成
    plt.figure(figsize=(10, 5))
    plt.plot(dates, counts, marker='o', color='b', linestyle='-', label='Guild Count')
    plt.xlabel('Date')
    plt.ylabel('Guild Count')
    plt.title('Report bot! Installations Over Time')
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()

    # メモリ上に画像を保存
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png')
    plt.close()
    img_buffer.seek(0)  # バッファを先頭に移動

    return img_buffer



async def setup(bot):
  await bot.add_cog(GuildCountTracker(bot))