from discord.ext import commands
from discord import app_commands
import discord
import os
import json



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
      await interaction.message.delete()

      # embedを定義
      embed = discord.Embed(
        description="この埋め込みに**返信する形**でファイルを送信してください。\nメンションはonにしてください。\n\n"
                    "⚠️⚠️ここで送信されたファイルは、確認なしにいきなりユーザーに送信されます。ご注意ください。",
        color=0x95FFA1,
      )
      msg_1 = await interaction.response.send_message(embed=embed)

      def check(message):
        return message.channel == interaction.channel and message.reference and message.attachments

      try:
        message = await self.bot.wait_for('message', timeout=60.0, check=check)

      except asyncio.TimeoutError:
        await interaction.followup.send('タイムアウトしました。メッセージが受信されませんでした。', ephemeral=Ture)
        await asyncio.sleep(3)
        await msg_1.delete()
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
        await interaction.followup.send("ユーザーデータが存在しませんでした。", ephemeral=True)
        await asyncio.sleep(3)
        await msg_1.delete()
        return
      user = await interaction.guild.fetch_member(user_id)

      # embedを定義
      # embed_1: お知らせ
      # embed_2: 返信内容
      embed = discord.Embed(
        url = interaction.channel.jump_url,
        description="## 匿名ticket\n"
                    f"あなたの匿名ticketに、 {interaction.guild.name} の管理者からファイルが届きました。\n"
                    f"- __**このメッセージに返信**__(右クリック→返信)すると、{interaction.guild.name}の管理者に届きます。\n\n"
                    f"ファイルにはウイルスなどが仕込まれている可能性もあるため、ご注意ください。",
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
        await interaction.followup.send("ファイル変換時に、不明なエラーが発生しました。\nサポートサーバーまでお越しください。", ephemeral=True)
        await asyncio.sleep(3)
        await msg_1.delete()
        return

      # 返信する
      try:
        await user.send(embed=embed, files=files)
      except discord.error.Forbidden:
        await interaction.followup.send("匿名Ticket送信者がDMを受け付けてないため、送信されませんでした。", ephemeral=True)
        await asyncio.sleep(3)
        await msg_1.delete()
        return
      except Exception as e:
        await interaction.followup.send("不明なエラーが発生しました。サポートサーバーに問い合わせてください。", ephemeral=True)
        error = f"\n\n[ERROR]\n- {interaction.guild.id}\n{e}\n\n"
        print(error)
        await asyncio.sleep(3)
        await msg_1.delete()
        return

      embed = discord.Embed(
        description=f"{interaction.user.mention}によって、ファイルが送信されました。",
        color=0x95FFA1,
      )
      await msg_1.edit(embed=embed, view=None)

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