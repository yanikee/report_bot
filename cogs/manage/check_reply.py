from discord.ext import commands
from discord import app_commands
import discord



class CheckReply(commands.Cog):
  def __init__(self, bot: commands.Bot):
    self.bot = bot

  @commands.Cog.listener()
  async def on_message(self, message):
    # DMではなかった場合 -> return
    if message.channel.type != discord.ChannelType.private:
      return
    # botだった場合 -> return
    if message.author.bot:
      return

    



async def setup(bot):
  await bot.add_cog(CheckReply(bot))