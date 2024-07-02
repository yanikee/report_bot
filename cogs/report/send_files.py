from discord.ext import commands
from discord import app_commands
import discord
import os
import json
import aiofiles
import asyncio



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
      if interaction.message.embeds[0].description == "下のボタンから編集してください。":
        custom_id = "report_send_files_process"

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
      # embedを定義
      embed = discord.Embed(
        description="この埋め込みに__**返信する形**__でファイルを送信してください。(60秒以内)\n__**メンションはON**__にしてください。\n\n"
                    "⚠️⚠️⚠️\n送信されたファイルは、確認なしにすぐにユーザーに送信されます。ご注意ください。",
        color=0x95FFA1,
      )

      await interaction.response.edit_message(embed=embed, view=None)

      def check(message):
        return message.channel == interaction.channel and message.reference and message.attachments

      try:
        message = await self.bot.wait_for('message', timeout=10.0, check=check)

      except asyncio.TimeoutError:
        await interaction.message.delete()
        await interaction.followup.send('タイムアウトしました。\nメッセージが受信されませんでした。', ephemeral=True)
        await self.add_reply(interaction)
        return

      # ファイルを送信する
      path = f"data/report/private_report/{interaction.guild.id}.json"
      async with aiofiles.open(path, encoding='utf-8', mode="r") as f:
        contents = await f.read()
      report_dict = json.loads(contents)

      # report者を取得
      try:
        user_id = report_dict[str(interaction.channel.id)]
      except KeyError:
        await interaction.followup.send("ユーザーデータが存在しませんでした。", ephemeral=True)
        await interaction.message.delete()
        await self.add_reply(interaction)
        return
      user = await interaction.guild.fetch_member(user_id)

      # embedを定義
      # embed_1: お知らせ
      # embed_2: 返信内容
      embed = discord.Embed(
        url = interaction.channel.jump_url,
        description="## 匿名報告\n"
                    f"あなたの報告に、 {interaction.guild.name} の管理者からファイルが届きました。\n"
                    f"- __**このメッセージに返信**__(右クリック→返信)すると、{interaction.guild.name}の管理者に届きます。",
        color=0xF4BD44,
      )
      embed.set_footer(
        text=f"匿名報告 | {interaction.guild.name}",
        icon_url=interaction.guild.icon.replace(format='png').url if interaction.guild.icon else None,
      )

      #  attachments to files
      try:
        files = [await attachment.to_file() for attachment in message.attachments]
      except Exception:
        await interaction.followup.send("ファイル変換時に、不明なエラーが発生しました。\nサポートサーバーまでお越しください。", ephemeral=True)
        await interaction.message.delete()
        await self.add_reply(interaction)
        return

      # 返信する
      try:
        await user.send(embed=embed, files=files)
      except discord.error.Forbidden:
        await interaction.followup.send("報告者がDMを受け付けてないため、送信されませんでした。", ephemeral=True)
        await interaction.message.delete()
        return
      except Exception as e:
        await interaction.followup.send("不明なエラーが発生しました。サポートサーバーに問い合わせてください。", ephemeral=True)
        error = f"\n\n[ERROR]\n- {interaction.guild.id}\n{e}\n\n"
        print(error)
        await interaction.message.delete()
        await self.add_reply(interaction)
        return

      embed = discord.Embed(
        description=f"{interaction.user.mention}によって、ファイルが送信されました。",
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