from discord.ext import commands
from discord import app_commands
import discord

import os
import json
import aiofiles
import datetime

import error
import check



class ReplyToReply(commands.Cog):
  def __init__(self, bot: commands.Bot):
    self.bot = bot
    self.user_cooldowns = {}

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
      if "匿名報告 |" in msg.embeds[0].footer.text:
        pass
      elif "匿名Report |" in msg.embeds[0].footer.text:
        pass
      else:
        return
    else:
      if "------------返信内容------------" in msg.embeds[0].description:
        pass
      else:
        return

    # guild_block
    embed = await check.is_guild_block(bot=self.bot, guild=None, user_id=None, message=message, referenced_message=msg)
    if embed:
      await message.reply(embed=embed)
      return

    # cooldown
    embed, self.user_cooldowns = check.user_cooldown(message.author.id, self.user_cooldowns)
    if embed:
      await message.reply(embed=embed)
      return

    # threadを取得
    url_splited = msg.embeds[0].url.split('/')
    cha = self.bot.get_channel(int(url_splited[-1]))
    if not cha:
      report_cha = self.bot.get_channel(int(url_splited[-2]))
      if not report_cha:
        embed = error.generate(
          code="3-3-01",
          description="匿名Reportチャンネルでの権限が不足しているか、匿名Reportチャンネルが削除されています。\n**サーバー管理者さんに、`/settings`コマンドをもう一度実行するように伝えてください。**",
        )
        await message.channel.send(embed=embed)
        return
      else:
        try:
          msg = await report_cha.fetch_message(int(url_splited[-1]))
        except discord.errors.NotFound:
          embed = error.generate(
            code="3-3-02",
            description="匿名Reportが削除されています。\n**サーバー管理者さんに、`/settings`コマンドをもう一度実行するように伝えてください。**",
          )
          await message.channel.send(embed=embed)
          return
        else:
          # reply_numを定義
          path = f"data/report/guilds/{msg.guild.id}.json"
          async with aiofiles.open(path, encoding='utf-8', mode="r") as f:
            contents = await f.read()
          report_dict = json.loads(contents)
          # 存在しなかった場合は作る
          if not report_dict.get("reply_num"):
            report_dict["reply_num"] = 0
          report_dict["reply_num"] += 1
          # 保存
          async with aiofiles.open(path, mode="w") as f:
            contents = json.dumps(report_dict, indent=2, ensure_ascii=False)
            await f.write(contents)

          # thread作成, 送信
          await msg.edit(view=None)
          cha = await msg.create_thread(name=f"private_report-{str(report_dict['reply_num']).zfill(4)}")

    # block判定
    path = f"data/report/blocked/{cha.guild.id}.json"
    if os.path.exists(path):
      async with aiofiles.open(path, encoding='utf-8', mode="r") as f:
        contents = await f.read()
      blocked_dict = json.loads(contents)
      try:
        if blocked_dict[str(cha.id)] == True:
          await message.reply("サーバー管理者にブロックされているため、返信できません。")
          return
      except KeyError:
        pass

    # embedの定義
    embed=discord.Embed(
      title="ユーザーからの返信",
      description=message.content,
      color=0xF4BD44,
    )

    # ユーザーからの返信を送信
    try:
      await cha.send(embed=embed)
    except discord.errors.Forbidden:
      embed = error.generate(
        code="3-3-03",
        description=f"匿名Report送信チャンネルでの権限が不足しています。\n**サーバー管理者さんに、`/settings`コマンドをもう一度実行するように伝えてください。**",
      )
      await message.channel.send(embed=embed)
      return
    except Exception as e:
      e = f"\n[ERROR[3-2-05]]{datetime.datetime.now()}\n- USER_ID:{message.author.id}\n- GUILD_ID:{cha.guild.id}\n- CHANNEL_ID:{cha.id}\n{e}\n"
      print(e)
      embed = error.generate(
        code="3-3-04",
        description="返信できませんでした。\nサポートサーバーまでお問い合わせください。",
      )
      await message.channel.send(embed=embed)
      return

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

    # 返信用のbuttonを送信
    try:
      await cha.send(embed=embed, view=view)
    except Exception as e:
      e = f"\n[ERROR[3-2-06]]{datetime.datetime.now()}\n- USER_ID:{message.author.id}\n- GUILD_ID:{cha.guild.id}\n- CHANNEL_ID:{cha.id}\n{e}\n"
      print(e)
      embed = error.generate(
        code="3-3-05",
        description="操作が完了できませんでした。\nサポートサーバーまでお問い合わせください。",
      )
      await message.channel.send(embed=embed)
      return

    # リアクションを付ける
    await message.add_reaction("✅")



async def setup(bot):
  await bot.add_cog(ReplyToReply(bot))