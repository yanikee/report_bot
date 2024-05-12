import os
from discord.ext import commands
from discord import app_commands
import discord
import check
import cog_list
from typing import List



cog_list = cog_list.cog_list
yappi = os.environ['yappi']

class Reload(commands.Cog):
  def __init__(self, bot: commands.Bot):
    self.bot = bot

  async def reload_choice(self,
        interaction: discord.Interaction,
        current: str,
    ) -> List[app_commands.Choice[str]]:
        choices = cog_list
        return [
            app_commands.Choice(name=choice, value=choice)
            for choice in choices if current.lower() in choice.lower()
        ]
  @app_commands.command(name="reload",description="cogをreloadします。"  )
  @app_commands.autocomplete(choices=reload_choice)
  @discord.app_commands.describe(choices="reloadしたいCogを選択してください")
  @discord.app_commands.describe(cogs="選択欄にないCogの手入力用")
  async def reload(self, interaction: discord.Interaction, choices:str=None, all:bool=None, cogs:str=None):
    if not await self.bot.is_owner(interaction.user):
      return await interaction.response.send_message("このコマンドは開発者専用です。", ephemeral=True)

    if all==True:
      for x in cog_list:
        await self.bot.load_extension(x)
        print(f"ロード完了：{x}")
      await self.bot.tree.sync()
      print("全ロード完了")
      await interaction.response.send_message("全ロード完了")
      return

    if cogs != None:
      choices = cogs
    await interaction.response.send_message(f"モジュール{choices}の再読み込みを開始します。")
    try:
      await self.bot.reload_extension(choices)
      await interaction.channel.send(f"モジュール{choices}の再読み込みが完了しました。")
      await self.bot.tree.sync()
      print(f"リロード完了：{choices}")
    except (commands.errors.ExtensionNotLoaded, commands.errors.ExtensionNotFound, commands.errors.NoEntryPointError, commands.errors.ExtensionFailed) as e:
      await interaction.channel.send(f"モジュール{choices}の再読み込みに失敗しました。\n理由：{e}")
      return



async def setup(bot):
  await bot.add_cog(Reload(bot))