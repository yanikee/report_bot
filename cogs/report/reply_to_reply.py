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

    # 匿名報告のembedじゃなかった場合 -> return
    if msg.embeds[0].footer:
      if not "匿名報告 |" in msg.embeds[0].footer.text:
        return
    else:
      if not "------------返信内容------------" in msg.embeds[0].description:
        return

    # threadを取得し、送信
    cha = await self.bot.fetch_channel(int(msg.embeds[0].url.split('/')[-1]))
    embed=discord.Embed(
      title="報告者からの返信",
      description=message.content,
      color=0x85ABFF,
    )
    await cha.send(embed=embed)

    # attachmentがあった場合→送信
    if message.attachments:
      file_l = [await x.to_file() for x in message.attachments]
      await cha.send(files=file_l)

    # 返信用のbuttonを設置
    view = discord.ui.View()
    button_0 = discord.ui.Button(label="返信内容を編集", custom_id=f"report_edit_reply", style=discord.ButtonStyle.primary)
    button_1 = discord.ui.Button(label="送信する", custom_id=f"report_send", style=discord.ButtonStyle.red)
    button_2 = discord.ui.Button(label="もう返信しない", custom_id=f"report_cancel", style=discord.ButtonStyle.gray)
    view.add_item(button_0)
    view.add_item(button_1)
    view.add_item(button_2)

    embed=discord.Embed(
        title="返信内容",
        description="下のボタンから編集してください。",
        color=0x8BFF85,
      )
    await cha.send(embed=embed, view=view)

    try:
      await message.add_reaction("✅")
    except discord.errors.Forbidden:
      await interaction.response.send_message(f"報告report送信チャンネルでの権限が不足しています。\n**サーバー管理者さんに、`/config`コマンドをもう一度実行するように伝えてください。** 1", ephemeral=True)
    except Exception as e:
      print(f"[ERROR]\n{e}")
      await message.channel.send("[ERROR]\n返信できませんでした。\nサポートサーバーまでお問い合わせください。")



async def setup(bot):
  await bot.add_cog(ReplyToReply(bot))