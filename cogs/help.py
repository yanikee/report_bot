from discord.ext import commands
from discord import app_commands
import discord
import os
import json



class Help(commands.Cog):
  def __init__(self, bot: commands.Bot):
    self.bot = bot

  @app_commands.checks.has_permissions(manage_channels=True)
  @app_commands.command(name="help", description='helpコマンドです。')
  async def report(self, interaction:discord.Interaction):
    description = ("## setting"
            "- `報告を受け取りたいチャンネルで/config`を実行"
            "## 使い方"
            "1. 報告したいメッセージを右クリック(長押し)"
            "2. 「アプリ」をクリック(タップ)"
            "3. 【サーバー管理者に報告】をクリック(タップ)")
    embed=discord.Embed(
      description=description,
      color=None
    )
    await interaction.response.send_message(embed=embed)


async def setup(bot):
  await bot.add_cog(Help(bot))