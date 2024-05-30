import os
from discord.ext import commands
from discord import app_commands
import discord
import cog_list
from typing import List



cog_list = cog_list.cog_list
yappi = os.environ['yappi']

class Reload(commands.Cog):
  def __init__(self, bot: commands.Bot):
    self.bot = bot

  async def reload_choice(self, interaction: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
    choices = cog_list
    return [app_commands.Choice(name=choice, value=choice) for choice in choices if current.lower() in choice.lower()]

  @app_commands.command(name="reload",description="cogをreloadします。"  )
  @app_commands.autocomplete(choices=reload_choice)
  @app_commands.describe(choices="reloadしたいCogを選択してください")
  @app_commands.describe(all_reload="すべてのCogをreloadします")
  @app_commands.describe(cogs="reloadしたいCogを入力してください")
  async def reload(self, interaction: discord.Interaction, choices:str=None, all_reload:bool=None, cogs:str=None):
    if not await self.bot.is_owner(interaction.user):
      return await interaction.response.send_message("このコマンドは開発者専用です。", ephemeral=True)

    if all_reload:
      text = ""
      for x in cog_list:
        try:
          await self.bot.load_extension(x)
        except (commands.errors.ExtensionNotLoaded, commands.errors.ExtensionNotFound, commands.errors.NoEntryPointError, commands.errors.ExtensionFailed) as e:
          text += f"- {x}の再読み込みに失敗。\n - 理由：{e}"
          continue
        except commands.errors.ExtensionAlreadyLoaded:
          continue
        except app_commands.errors.CommandInvokeError:
          continue

        text += f"- {x}の再読み込みに成功\n"
        print(f"ロード完了：{x}")
      await self.bot.tree.sync()
      print("全ロード完了")
      text += "全ロード完了"
      await interaction.response.send_message(text, ephemeral=True)
      return

    elif cogs:
      choices = cogs

    try:
      await self.bot.reload_extension(choices)
    except (commands.errors.ExtensionNotLoaded, commands.errors.ExtensionNotFound, commands.errors.NoEntryPointError, commands.errors.ExtensionFailed) as e:
      await interaction.response.send_message(f"- {choices}の再読み込みに失敗。\n - 理由：{e}", ephemeral=True)
      return

    await interaction.response.send_message(f"{choices}の再読み込みに成功", ephemeral=True)
    await self.bot.tree.sync()
    print(f"リロード完了：{choices}")



async def setup(bot):
  await bot.add_cog(Reload(bot))