from discord.ext import commands
from discord import app_commands
import discord



class Help(commands.Cog):
  def __init__(self, bot: commands.Bot):
    self.bot = bot

  @app_commands.command(name="help", description='helpコマンドです。')
  async def report(self, interaction:discord.Interaction):
    description = ("## setting\n"
            "- 報告を受け取りたいチャンネルで`/config`を実行（サーバー管理者専用コマンド）\n"
            "## 使い方\n"
            "1. 報告したいメッセージを右クリック(長押し)\n"
            "2. 「アプリ」をクリック(タップ)\n"
            "3. 【サーバー管理者に報告】をクリック(タップ)")
    embed=discord.Embed(
      description=description,
      color=0xF4BD44,
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot):
  await bot.add_cog(Help(bot))