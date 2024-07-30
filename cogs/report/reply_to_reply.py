from discord.ext import commands
from discord import app_commands
import discord
import os
import json
import aiofiles
import error



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

    # threadを取得
    try:
      cha = await self.bot.fetch_channel(int(msg.embeds[0].url.split('/')[-1]))
    except discord.errors.Forbidden:
      embed = error.generate(
        code="3-2-01",
        description="匿名Report送信チャンネルでの権限が不足しています。\n**サーバー管理者さんに、`/report config`コマンドをもう一度実行するように伝えてください。**",
      )
      await message.channel.send(embed=embed)
      return
    except discord.errors.NotFound:
      embed = error.generate(
        code="3-2-02",
        description="匿名Report送信チャンネルが削除されています。\n**サーバー管理者さんに、`/report config`コマンドをもう一度実行するように伝えてください。**",
      )
      await message.channel.send(embed=embed)
      return
    except Exception as e:
      error = f"\n\n[ERROR]\n- {message.guild.id}\n{e}\n\n"
      print(error)
      embed = error.generate(
        code="3-2-03",
        description="送信できませんでした。\nサポートサーバーまでお問い合わせください。",
      )
      await message.channel.send(embed=embed)
      return

    # block判定
    path = f"data/report/blocked/{cha.guild.id}.json"
    if os.path.exists(path):
      async with aiofiles.open(path, encoding='utf-8', mode="r") as f:
        contents = await f.read()
      blocked_dict = json.loads(contents)
      try:
        if blocked_dict[str(cha.id)] == True:
          await message.channel.send("サーバー管理者にブロックされているため、返信できません。")
          return
      except KeyError:
        pass

    # embedの定義
    embed=discord.Embed(
      title="報告者からの返信",
      description=message.content,
      color=0xF4BD44,
    )
    await cha.send(embed=embed)

    # 返信ボタンが設置されてたら削除
    async for msg in cha.history(limit=4):
      if msg.components:
        await msg.delete()
        break

    # attachmentがあった場合→送信
    if message.attachments:
      file_l = [await x.to_file() for x in message.attachments]
      await cha.send(files=file_l)

    # 返信用のbuttonを設置
    embed=discord.Embed(
        title="返信内容",
        description="下のボタンから編集してください。",
        color=0x95FFA1,
      )
    view = discord.ui.View()
    button_0 = discord.ui.Button(label="返信内容を編集", custom_id=f"report_edit_reply", style=discord.ButtonStyle.primary, row=0)
    button_1 = discord.ui.Button(label="送信する", custom_id=f"report_send", style=discord.ButtonStyle.red, row=0, disabled=True)
    button_2 = discord.ui.Button(label="ファイルを送信する", custom_id=f"report_send_file", style=discord.ButtonStyle.green, row=1)
    button_3 = discord.ui.Button(label="もう返信しない", custom_id=f"report_cancel", style=discord.ButtonStyle.gray, row=2)
    view.add_item(button_0)
    view.add_item(button_1)
    view.add_item(button_2)
    view.add_item(button_3)

    await cha.send(embed=embed, view=view)

    try:
      await message.add_reaction("✅")
    except discord.errors.Forbidden:
      embed = error.generate(
        code="3-2-04",
        description=f"匿名Report送信チャンネルでの権限が不足しています。\n**サーバー管理者さんに、`/report config`コマンドをもう一度実行するように伝えてください。**",
      )
      await message.channel.send(embed=embed)
    except Exception as e:
      error = f"\n\n[ERROR]\n- {message.guild.id}\n{e}\n\n"
      print(error)
      embed = error.generate(
        code="2-2-05",
        description="返信できませんでした。\nサポートサーバーまでお問い合わせください。",
      )
      await message.channel.send(embed=embed)
      return



async def setup(bot):
  await bot.add_cog(ReplyToReply(bot))