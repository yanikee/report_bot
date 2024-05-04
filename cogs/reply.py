from discord.ext import commands
from discord import app_commands
import discord
import os



class Reply(commands.Cog):
  def __init__(self, bot: commands.Bot):
    self.bot = bot

  @app_commands.Cog.listener()
  async def on_interaction(self, interaction:discord.Interaction):
    try:
      custom_id = interaction.data["custom_id"]
    except KeyError:
      return

    if not "report_reply_" in custom_id:
      return

    msg_id = int(custom_id.replace("report_reply_", ""))
    msg = interaction.channel.fetch_message(msg_id)
    thread = await msg.create_thread(name="匿名報告への返信")

    msg = await thread.send(embeds=msg.embeds)

    # TODO: ここから
    view = discord.ui.View()
    button_0 = discord.ui.Button(label="返信", custom_id=f"report_reply_{msg.id}", qstyle=discord.ButtonStyle.primary)
    view.add_item(button_0)

    await msg.edit(view=view)


async def setup(bot):
  await bot.add_cog(Reply(bot))