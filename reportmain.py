from discord.ext import commands
import discord

import os
import logging
import aiofiles
import argparse
from dotenv import load_dotenv

from modules import cogs


parser = argparse.ArgumentParser(description="report_bot!を起動する")
parser.add_argument("-dev", action="store_true", help="開発モードで実行")
parser.add_argument("-reset", action="store_true", help="何も読み込まない")
args = parser.parse_args()

if args.dev:
  cog_list = cogs.get_cogs()
  dev_cog_list = cogs.get_dev_cogs()
elif args.reset:
  cog_list = []
  dev_cog_list = None
else:
  cog_list = cogs.get_cogs()
  dev_cog_list = None


load_dotenv(override=True)

try:
  TOKEN = os.environ.get("ReportBot_TOKEN")
  report_bot_service_cha = int(os.environ.get("report_bot_service_cha"))
except Exception:
  print("TOKEN, report_bot_service_chaを取得できませんでした")
  TOKEN = ""
  report_bot_service_cha = ""


intents = discord.Intents.none()
intents.messages = True
intents.guilds = True

bot = commands.Bot(command_prefix="!!!!!", intents=intents)

# カスタム絵文字を定義
bot.emojis_dict = {
  "add": "<:add:1335909447687733300>",
  "arrow_back": "<:arrow_back:1335907900920565780>",
  "new_label": "<:new_label:1335916826114392126>",
  "person_alert": "<:person_alert:1335916869714055209>",
  "reply": "<:reply:1335932856899342397>",
  "report": "<:report:1335916894775021579>",
  "edit": "<:edit:1335899691983831070>",
  "send": "<:send:1335899659553738815>",
  "upload_file": "<:upload_file:1335899677186326559>",
  "delete": "<:delete:1335899643049017355>",
}

@bot.event
async def on_ready():
  for x in cog_list:
    await bot.load_extension(x)
    print(f"ロード完了：{x}")

  if dev_cog_list:
    for x in dev_cog_list:
      await bot.load_extension(x)
      print(f"ロード完了：{x}")

  await bot.tree.sync()
  print("全ロード完了")
  channel = bot.get_channel(report_bot_service_cha)
  await channel.send(f"{bot.user.mention} がオンラインになったよう。")

  path = "data/bot_version"
  async with aiofiles.open(path, mode="r", encoding="UTF-8") as f:
    version = await f.read()
  custom_activity = discord.Game(f"/help | ver{version}")
  await bot.change_presence(status=discord.Status.online,activity=custom_activity)


bot.run(TOKEN, log_level = logging.WARNING)