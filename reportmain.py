from discord.ext import commands
import discord
import os
import logging
import cog_list


cog_list = cog_list.cog_list

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!!!!!", intents=intents)
TOKEN = os.environ["ReportBot_TOKEN"]
report_bot_service_cha = int(os.environ["report_bot_service_cha"])


@bot.event
async def on_ready():
  for x in cog_list:
    await bot.load_extension(x)
    print(f"ロード完了：{x}")
  await bot.tree.sync()
  print("全ロード完了")
  channel = bot.get_channel(report_bot_service_cha)
  await channel.send(f"{bot.user.mention} がオンラインになったよう。")

  path = "data/bot_version"
  with open(path, mode="r") as f:
    version = f.read()
  custom_activity = discord.Game(f"/help | ver{version}")
  await bot.change_presence(status=discord.Status.online,activity=custom_activity)


bot.run(TOKEN, log_level = logging.WARNING)