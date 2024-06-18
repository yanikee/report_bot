from discord.ext import commands, tasks



class ChangeStatus(commands.Cog):
  def __init__(self, bot: commands.Bot):
    self.bot = bot
    self.change_status.start()

  def cog_unload(self):
    self.change_status.cancel()

  @tasks.loop(seconds=30)
  async def change_status(self):
    path = "data/bot_version"
    with open(path, mode="r") as f:
      version = f.read()
    custom_activity = discord.Game(f"/help | ver{version}")
    await bot.change_presence(status=discord.Status.online, activity=custom_activity)

    await asyncio.sleep(30)

    custom_activity = discord.Game(f"/help | {len(self.bot.guilds):,}guilds / {len(self.bot.users):,}users")
    await bot.change_presence(status=discord.Status.online, activity=custom_activity)



async def setup(bot):
  await bot.add_cog(ChangeStatus(bot))