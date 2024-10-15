from discord import app_commands
from discord.ext import commands
import discord
import datetime
import aiofiles



class BotUpdate(commands.GroupCog, group_name='update'):
  def __init__(self, bot: commands.Bot):
    self.bot = bot

  @app_commands.command(
    name="report_bot",
    description="[開発者専用]report bot! のアップデート"
  )
  @app_commands.describe(channel="送信するチャンネルを選択してください。")
  @app_commands.describe(version="バージョンを指定してください。⚪︎.⚪︎.⚪︎の形が好ましいです。")
  @app_commands.describe(description="本文を入力してください。")
  async def update_bot(self, interaction:discord.Interaction, version:str, description:str, channel:discord.TextChannel=None):
    if not await self.bot.is_owner(interaction.user):
      return await interaction.response.send_message("このコマンドは開発者専用です。", ephemeral=True)

    if not channel:
      channel = interaction.channel
    embed = discord.Embed(
      title = f"__report bot! ver{version}__",
      url = channel.jump_url,
      description = description,
      color=0xffe7ab,
      timestamp=datetime.datetime.now(),
    )
    embed.set_footer(
      text = "\u200b",
      icon_url = self.bot.user.avatar.url,
    )
    await interaction.response.send_message(f"<#{channel.id}>に送ったよう", ephemeral=True)
    await channel.send(embed=embed)

    path = "data/bot_version"
    async with aiofiles.open(path, mode="w") as f:
      await f.write(version)
    custom_activity = discord.Game(f"/help | ver{version}")
    await self.bot.change_presence(status=discord.Status.online,activity=custom_activity)



async def setup(bot):
  await bot.add_cog(BotUpdate(bot))