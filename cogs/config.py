from discord.ext import commands
from discord import app_commands
import discord
import os
import json


class Config(commands.GroupCog, group_name='report'):
  def __init__(self, bot: commands.Bot):
    self.bot = bot

  @app_commands.command(name="config", description='"report"を送信するチャンネルを設定します。')
  @app_commands.describe(channel='"report"を送信するチャンネル')
  async def report(self, interaction:discord.Interaction, channel:discord.TextChannel=None):
    if not interaction.channel.permissions_for(interaction.user).manage_channels:
      await interaction.response.send_message("権限不足です。\n`チャンネル管理`の権限が必要です。", ephemeral=True)
      return

    if not channel:
      channel = interaction.channel

    if channel.type != discord.ChannelType.text:
      await interaction.response.send_message("テキストチャンネルのみ設定可能です。", ephemeral=True)
      return

    # 保存
    report_dict = {
      "report_send_channel": channel.id,
      "reply_num": 0
    }
    path = f"data/report/guilds/{interaction.guild.id}.json"
    with open(path, mode="w") as f:
      json.dump(report_dict, f, indent=2, ensure_ascii=False)

    embed = discord.Embed(
      description=f'"report"を{channel.mention}に送信します。',
      color=0xF4BD44,
    )
    await interaction.response.send_message(embed=embed)



async def setup(bot):
  await bot.add_cog(Config(bot))