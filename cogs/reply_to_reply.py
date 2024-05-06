from discord.ext import commands
from discord import app_commands
import discord
import os
import json



class ReplyToReply(commands.Cog):
  def __init__(self, bot: commands.Bot):
    self.bot = bot

  @commands.Cog.listener()
  async def on_message(self, message):
    # DMじゃなかった場合 -> return
    if message.channel.type != discord.ChannelType.private:
      return
    # 返信メッセージじゃなかった場合 -> return
    if message.type != discord.MessageType.reply:
      return

    # 返信メッセージを取得
    msg_id = message.reference.message_id
    msg = await message.channel.fetch_message(msg_id)

    # embedがなかった場合 -> return
    if not msg.embeds:
      return

    # threadを取得し、送信
    cha = await self.bot.fetch_channel(int(msg.embeds[0].url))
    await cha.send(f"【報告者からの返信】\n{message.content}")

    # 返信用のbuttonを設置
    view = discord.ui.View()
    button_0 = discord.ui.Button(label="返信内容を編集", custom_id=f"report_edit_reply", qstyle=discord.ButtonStyle.primary)
    button_1 = discord.ui.Button(label="送信する", custom_id=f"report_send", qstyle=discord.ButtonStyle.red)
    view.add_item(button_0)
    view.add_item(button_1)
    await cha.send("【返信内容】\n下のボタンから編集してください。", view=view)



async def setup(bot):
  await bot.add_cog(ReplyToReply(bot))