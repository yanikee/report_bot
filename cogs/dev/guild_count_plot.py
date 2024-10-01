from discord import app_commands
from discord.ext import commands
import discord

from cogs.manage import guild_count_tracker

class GuildCountPlot(commands.GroupCog, group_name='guild_count'):
  def __init__(self, bot: commands.Bot):
    self.bot = bot

  @app_commands.command(name="plot", description="[開発者専用]plotしますよ")
  async def update_bot(self, interaction:discord.Interaction):
    if not await self.bot.is_owner(interaction.user):
      return await interaction.response.send_message("このコマンドは開発者専用です。", ephemeral=True)

    GuildCountTracker = guild_count_tracker.GuildCountTracker(self.bot)
    img_buffer = await GuildCountTracker.plot_graph()
    await interaction.response.send_message(f"Guild_count: {len(self.bot.guilds)}", file=discord.File(img_buffer, 'guild_count_graph.png'))



async def setup(bot):
  await bot.add_cog(GuildCountPlot(bot))