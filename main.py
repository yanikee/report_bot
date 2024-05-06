from discord.ext import commands
import discord
import os
import logging



cog_list = ["cogs.report", "cogs.reply_to_reply", "cogs.reply", "cogs.config"]

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!!!!!", intents=intents)
TOKEN = ""
guild_id = int(os.environ['Guild_id'])
yapibotcha_id = int(os.environ['yapibotcha_id'])


@bot.event
async def on_ready():
  for x in cog_list:
    await bot.load_extension(x)
    print(f"ロード完了：{x}")
  await bot.tree.sync()
  print("全ロード完了")
  guild = bot.get_guild(guild_id)
  channel = guild.get_channel(yapibotcha_id)
  await channel.send(f"{bot.user.mention} がオンラインになったよう。")


bot.run(TOKEN, log_level = logging.WARNING)