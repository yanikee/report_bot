from discord.ext import commands
from discord import app_commands
import discord
import os
import json
import aiofiles
import asyncio
import error



class PticketSendFiles(commands.Cog):
  def __init__(self, bot: commands.Bot):
    self.bot = bot

  @commands.Cog.listener()
  async def on_interaction(self, interaction:discord.Interaction):
    try:
      custom_id = interaction.data["custom_id"]
    except KeyError:
      return

    path = f"data/pticket/pticket/{interaction.guild.id}.json"

    # スレッド内での返信編集
    if custom_id == "pticket_send_file":
      if interaction.message.embeds[0].description == "下のボタンから編集してください。":
        custom_id = "pticket_send_files_process"

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
          custom_id="pticket_send_files_process",
        )
        button_2 = discord.ui.Button(
          label="戻る",
          style=discord.ButtonStyle.gray,
          custom_id="pticket_send_files_return",
        )
        view.add_item(button_1)
        view.add_item(button_2)

        await interaction.response.edit_message(embeds=[interaction.message.embeds[0], embed], view=view)
        return


    if custom_id == "pticket_send_files_process":
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
        message = await self.bot.wait_for('message', timeout=60.0, check=check)

      except asyncio.TimeoutError:
        await interaction.message.delete()
        await interaction.followup.send('タイムアウトしました。\nメッセージが受信されませんでした。', ephemeral=True)
        await self.add_reply(interaction)
        return

      # ファイルを送信する
      path = f"data/pticket/pticket/{interaction.guild.id}.json"
      async with aiofiles.open(path, encoding='utf-8', mode="r") as f:
        contents = await f.read()
      pticket_dict = json.loads(contents)

      # pticket者を取得
      try:
        user_id = pticket_dict[str(interaction.channel.id)]
      except KeyError:
        embed=error.generate(
          code="2-4-01",
          description="ユーザーデータが存在しませんでした。"
        )
        await interaction.followup.send(embed=embed, ephemeral=True)
        await interaction.message.delete()
        await self.add_reply(interaction)
        return
      user = await interaction.guild.fetch_member(user_id)

      # embedを定義
      # embed_1: お知らせ
      # embed_2: 返信内容
      embed = discord.Embed(
        url = interaction.channel.jump_url,
        description="## 匿名ticket\n"
                    f"あなたの匿名ticketに、 {interaction.guild.name} の管理者からファイルが届きました。\n"
                    f"- __**このメッセージに返信**__(右クリック→返信)すると、{interaction.guild.name}の管理者に届きます。",
        color=0x9AC9FF,
      )
      embed.set_footer(
        text=f"匿名ticket | {interaction.guild.name}",
        icon_url=interaction.guild.icon.replace(format='png').url if interaction.guild.icon else None,
      )

      #  attachments to files
      try:
        files = [await attachment.to_file() for attachment in message.attachments]
      except Exception:
        embed=error.generate(
          code="2-4-02",
          description="ファイル変換時に、不明なエラーが発生しました。\nサポートサーバーまでお問い合わせください。",
        )
        await interaction.followup.send(embed=embed, ephemeral=True)
        await interaction.message.delete()
        await self.add_reply(interaction)
        return

      # 返信する
      try:
        await user.send(embed=embed, files=files)
      except discord.error.Forbidden:
        embed=error.generate(
          code="2-4-03",
          description="匿名Ticket送信者がDMを受け付けてないため、送信されませんでした。",
        )
        await interaction.followup.send(embed=embed)
        await interaction.message.delete()
        return
      except Exception as e:
        embed=error.generate(
          code="2-4-04",
          description="不明なエラーが発生しました。サポートサーバーまでお問い合わせください。",
        )
        await interaction.followup.send(embed=embed)
        error = f"\n\n[ERROR]\n- {interaction.guild.id}\n{e}\n\n"
        print(error)
        await interaction.message.delete()
        await self.add_reply(interaction)
        return

      embed = discord.Embed(
        description=f"{interaction.user.mention}がファイルを送信しました。",
        color=0x95FFA1,
      )
      await interaction.message.delete()
      await message.add_reaction("✅")
      await interaction.channel.send(embed=embed)
      await self.add_reply(interaction)


    # 「戻る」を選択した場合
    elif custom_id == "pticket_send_files_return":
      view = discord.ui.View()
      button_0 = discord.ui.Button(label="返信内容を編集", custom_id=f"pticket_edit_reply", style=discord.ButtonStyle.primary, row=0)
      button_1 = discord.ui.Button(label="送信する", custom_id=f"pticket_send", style=discord.ButtonStyle.red, row=0)
      button_2 = discord.ui.Button(label="ファイルを送信する", custom_id=f"pticket_send_file", style=discord.ButtonStyle.green, row=1)
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
      custom_id="pticket_add_reply",
    )
    view.add_item(button_1)
    await interaction.channel.send(view=view)
    await interaction.channel.add_user(interaction.user)



async def setup(bot):
  await bot.add_cog(PticketSendFiles(bot))