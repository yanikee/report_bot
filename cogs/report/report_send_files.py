from discord.ext import commands
from discord import app_commands
import discord
import os
import json
import aiofiles
import asyncio
import datetime
import error



class ReportSendFiles(commands.Cog):
  def __init__(self, bot: commands.Bot):
    self.bot = bot

  @commands.Cog.listener()
  async def on_interaction(self, interaction:discord.Interaction):
    try:
      custom_id = interaction.data["custom_id"]
    except KeyError:
      return


    # スレッド内での返信編集
    if custom_id == "report_send_file":
      path = f"data/report/private_report/{interaction.guild.id}.json"
      if not os.path.exists(path):
        e = f"[ERROR[3-5-01]]{datetime.datetime.now()}\n- GUILD_ID:{interaction.guild.id}\nJson file was not found"
        print(e)
        embed=error.generate(
          code="3-5-01",
          description="サーバーデータが存在しませんでした。\nサポートサーバーまでお問い合わせください。"
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return


      if interaction.message.embeds[0].description == "下のボタンから編集してください。":
        custom_id = "report_send_files_process"

      # 返信パネルのメッセージを編集していた場合の警告メッセージ
      else:
        # embedの定義
        embed = discord.Embed(
          description="編集中の返信メッセージが全て削除されます。\nよろしいですか？",
          color=0xFF0000,
        )

        # viewの定義
        view = discord.ui.View()
        button_1 = discord.ui.Button(
          label="ファイル送信に進む",
          style=discord.ButtonStyle.primary,
          custom_id="report_send_files_process",
        )
        button_2 = discord.ui.Button(
          label="戻る",
          style=discord.ButtonStyle.gray,
          custom_id="report_send_files_return",
        )
        view.add_item(button_1)
        view.add_item(button_2)

        await interaction.response.edit_message(embeds=[interaction.message.embeds[0], embed], view=view)
        return


    if custom_id == "report_send_files_process":
      # ファイル送信のembedを定義, 送信
      embed = discord.Embed(
        description="この埋め込みに__**返信する形**__でファイルを送信してください。(60秒以内)\n__**メンションはON**__にしてください。\n\n"
                    "⚠️注意⚠️\n送信されたファイルは、確認なしにすぐにユーザーに送信されます。ご注意ください。",
        color=0x95FFA1,
      )
      await interaction.response.edit_message(embed=embed, view=None)

      # ファイル送信を待つ
      def check(message):
        return message.channel == interaction.channel and message.reference and message.attachments
      try:
        message = await self.bot.wait_for('message', timeout=60.0, check=check)
      except asyncio.TimeoutError:
        await interaction.message.delete()
        await interaction.followup.send('タイムアウトしました。\nメッセージが受信されませんでした。', ephemeral=True)
        await self.add_reply(interaction)
        return

      # report者を取得
      path = f"data/report/private_report/{interaction.guild.id}.json"
      async with aiofiles.open(path, encoding='utf-8', mode="r") as f:
        contents = await f.read()
      report_dict = json.loads(contents)

      try:
        user_id = report_dict[str(interaction.channel.id)]
      except KeyError:
        e = f"\n[ERROR[3-5-02]]{datetime.datetime.now()}\n- GUILD_ID:{interaction.guild.id}\n- CHANNEL_ID:{interaction.channel.id}\nReporter_id was not found\n"
        print(e)
        embed=error.generate(
          code="3-5-02",
          description="ユーザーデータが存在しませんでした。\nサポートサーバーまでお問い合わせください。"
        )
        await interaction.followup.send(embed=embed)
        await interaction.message.delete()
        await self.add_reply(interaction)
        return

      try:
        user = await interaction.guild.fetch_member(user_id)
      except Exception:
        embed=error.generate(
          code="3-5-03",
          description="匿名Reportのユーザーを取得することができませんでした。\nユーザーは既にサーバーを抜けているかも...？"
        )
        await interaction.followup.send(embed=embed, ephemeral=True)
        await interaction.message.delete()
        await self.add_reply(interaction)
        return

      # embedを定義
      embed = discord.Embed(
        url = interaction.channel.jump_url,
        description="## 匿名Report\n"
                    f"あなたの報告に、『{interaction.guild.name}』の管理者からファイルが届きました。\n"
                    f"- __**このメッセージに返信**__(右クリック→返信)すると、このサーバーの管理者に届きます。",
        color=0xF4BD44,
      )
      embed.set_footer(
        text=f"匿名Report | {interaction.guild.name}",
        icon_url=interaction.guild.icon.replace(format='png').url if interaction.guild.icon else None,
      )

      #  attachments to files
      try:
        files = [await attachment.to_file() for attachment in message.attachments]
      except Exception as e:
        e = f"\n[ERROR[3-5-04]]{datetime.datetime.now()}\n- GUILD_ID:{interaction.guild.id}\n{e}\n"
        print(e)
        embed=error.generate(
          code="3-5-04",
          description="ファイル変換時に、不明なエラーが発生しました。\nサポートサーバーまでお問い合わせください。",
        )
        await interaction.followup.send(embed=embed, ephemeral=True)
        await interaction.message.delete()
        await self.add_reply(interaction)
        return

      # fileを返信する
      try:
        await user.send(embed=embed, files=files)
      except discord.errors.Forbidden:
        embed=error.generate(
          code="3-5-05",
          description="匿名Report送信者がDMを受け付けてないため、送信されませんでした。",
        )
        await interaction.followup.send(embed=embed)
        await interaction.message.delete()
        return
      except Exception as e:
        e = f"\n[ERROR[3-5-06]]{datetime.datetime.now()}\n- GUILD_ID:{interaction.guild.id}\n{e}\n"
        print(e)
        embed=error.generate(
          code="3-5-06",
          description="不明なエラーが発生しました。サポートサーバーまでお問い合わせください。",
        )
        await interaction.followup.send(embed=embed)
        await interaction.message.delete()
        await self.add_reply(interaction)
        return

      # 確認メッセージを送信
      embed = discord.Embed(
        description=f"{interaction.user.mention}がファイルを送信しました。",
        color=0x95FFA1,
      )
      await interaction.message.delete()
      await message.add_reaction("✅")
      await interaction.channel.send(embed=embed)
      await self.add_reply(interaction)


    # 「戻る」を選択した場合
    elif custom_id == "report_send_files_return":
      view = discord.ui.View()
      button_0 = discord.ui.Button(label="返信内容を編集", custom_id=f"report_edit_reply", style=discord.ButtonStyle.primary, row=0)
      button_1 = discord.ui.Button(label="送信する", custom_id=f"report_send", style=discord.ButtonStyle.red, row=0)
      button_2 = discord.ui.Button(label="ファイルを送信する", custom_id=f"report_send_file", style=discord.ButtonStyle.green, row=1)
      view.add_item(button_0)
      view.add_item(button_1)
      view.add_item(button_2)

      await interaction.response.edit_message(embed=interaction.message.embeds[0], view=view)


  async def add_reply(self, interaction):
    # 追加返信ボタン設置
    view = discord.ui.View()
    button_1 = discord.ui.Button(
      label="追加で返信する",
      style=discord.ButtonStyle.gray,
      custom_id="report_add_reply",
    )
    view.add_item(button_1)
    await interaction.channel.send(view=view)
    await interaction.channel.add_user(interaction.user)



async def setup(bot):
  await bot.add_cog(ReportSendFiles(bot))