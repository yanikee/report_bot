from discord.ext import commands
from discord import app_commands
import discord

import cog_list



dev_cog_list = cog_list.dev_cog_list

class Help(commands.Cog):
  def __init__(self, bot: commands.Bot):
    self.bot = bot

  @app_commands.command(name="quickstart", description='簡単設定')
  async def Quickstart(self, interaction:discord.Interaction):
    embed, view = self.quickstart_page_1()
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


  def quickstart_page_1(self):
    embed = discord.Embed(
      title="Quickstart (1/3)",
      description="",
      color=0xF4BD44,
    )
    view = discord.ui.View()
    button = discord.ui.Button(label="次へ", emoji="➡️", custom_id=f"quickstart_1_next", style=discord.ButtonStyle.primary, row=0)
    view.add_item(button)
    return embed, view


  @commands.Cog.listener()
  async def on_interaction(self, interaction):
    try:
      interaction.data["custom_id"]
    except KeyError:
      return

    if interaction.data["custom_id"] == "quickstart_page_1":
      embed = self.quickstart_page_1()
      await interaction.response.edit_message(embed=embed)

    elif interaction.data["custom_id"] == "quickstart_page_2":
      embed = discord.Embed(
        title="Quickstart (2/3)",
        description="",
        color=0xF4BD44,
      )
      view = discord.ui.View()
      button_0 = discord.ui.Button(label="戻る", custom_id=f"quickstart_page_1", style=discord.ButtonStyle.gray, row=0)
      button_1 = discord.ui.Button(label="保存して次へ", custom_id=f"quickstart_page_3", style=discord.ButtonStyle.primary, row=0)
      view.add_item(button_0)
      view.add_item(button_1)
      await interaction.response.edit_message(embed=embed, view=view)

    elif interaction.data["custom_id"] == "quickstart_page_3":
      embed = discord.Embed(
        title="Quickstart (2/3)",
        description="",
        color=0xF4BD44,
      )
      view = discord.ui.View()
      button_0 = discord.ui.Button(label="戻る", custom_id=f"quickstart_page_2", style=discord.ButtonStyle.gray, row=0)
      button_1 = discord.ui.Button(label="保存して終了", custom_id=f"quickstart_final", style=discord.ButtonStyle.primary, row=0)
      view.add_item(button_0)
      view.add_item(button_1)
      await interaction.response.edit_message(embed=embed, view=view)

    elif interaction.data["custom_id"] == "quickstart_final":
      embed = discord.Embed(
        title="Quickstart",
        description="",
        color=0xF4BD44,
      )
      await interaction.response.edit_message(embed=embed, view=None)



async def setup(bot):
  await bot.add_cog(Quickstart(bot))