from discord.ext import commands
from discord import app_commands
import discord
import os
import json
import aiofiles



class Notification(commands.Cog):
  def __init__(self, bot: commands.Bot):
    self.bot = bot

  @app_commands.command(name="notification", description='[開発者専用]全サーバーに通知を送信します。')
  @app_commands.describe(msg_id='こいつを送信するお')
  async def notification(self, interaction:discord.Interaction, msg_id:str):
    if not await self.bot.is_owner(interaction.user):
      return await interaction.response.send_message("このコマンドは開発者専用です。", ephemeral=True)

    msg = await interaction.channel.fetch_message(int(msg_id))
    content = msg.content.replace(f"{self.bot.user.mention}","")

    guild_id_l = os.listdir("data/report/guilds")

    await interaction.response.send_message(f"{len(guild_id_l)}サーバーに送信するお")

    for guild_id in guild_id_l:
      path = f"data/report/guilds/{guild_id}"
      async with aiofiles.open(path, encoding='utf-8', mode="r") as f:
        contents = await f.read()
      report_dict = json.loads(contents)
      cha_id = report_dict["report_send_channel"]
      cha = self.bot.get_channel(int(cha_id))

      try:
        await cha.send(content, embeds=msg.embeds, files=[x.to_file() for x in msg.attachments])
      except Exception as e:
        await interaction.channel.send(e)

    await interaction.followup.send("終わったお")


async def setup(bot):
  await bot.add_cog(Notification(bot))