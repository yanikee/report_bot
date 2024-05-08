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
    # botだった場合 -> return
    if message.author.bot:
      return

    # 返信メッセージを取得
    msg_id = message.reference.message_id
    msg = await message.channel.fetch_message(msg_id)

    # embedがなかった場合 -> return
    if not msg.embeds:
      return

    # threadを取得し、送信
    cha = await self.bot.fetch_channel(int(msg.embeds[0].url.split('/')[-1]))
    await cha.send(f"【報告者からの返信】\n{message.content}")

    # 返信用のbuttonを設置
    view = discord.ui.View()
    button_0 = discord.ui.Button(label="返信内容を編集", custom_id=f"report_edit_reply", style=discord.ButtonStyle.primary)
    button_1 = discord.ui.Button(label="送信する", custom_id=f"report_send", style=discord.ButtonStyle.red)
    button_2 = discord.ui.Button(label="もう返信しない", custom_id=f"report_cancel", style=discord.ButtonStyle.gray)
    view.add_item(button_0)
    view.add_item(button_1)
    view.add_item(button_2)
    await cha.send("【返信内容】\n下のボタンから編集してください。", view=view)

    # ありがとうメッセージ
    await message.channel.send("返信ありがとうございました。")



async def setup(bot):
  await bot.add_cog(ReplyToReply(bot))