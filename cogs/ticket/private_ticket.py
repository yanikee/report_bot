from discord.ext import commands
from discord import app_commands
import discord
import os
import json



class PrivateTicket(commands.Cog):
  def __init__(self, bot: commands.Bot):
    self.bot = bot

  # private_ticketからthreadを作る
  @commands.Cog.listener()
  async def on_interaction(self, interaction):
    try:
      if interaction.data["custom_id"] != "private_ticket":
        return
    except KeyError:
      return

    modal = PrivateTicketModal()
    await interaction.response.send_modal(modal)


class PrivateTicketModal(discord.ui.Modal):
  def __init__(self, ):
    super().__init__(title=f'匿名ticketモーダル')

    self.first_pticket = discord.ui.TextInput(
      label="ticket内容を入力",
      style=discord.TextStyle.long,
      default=None,
      placeholder="添付ファイルは、後ほどbotのDMにて送信できます。",
      required=True,
      row=0
    )
    self.add_item(self.reply)

  async def on_submit(self, interaction: discord.Interaction):
    # embedの定義
    embed=discord.Embed(
      title="匿名ticket",
      description=self.first_pticket.value,
      color=0xF4BD44,
    )

    # report_send_channelの取得
    path = f"data/report/guilds/{interaction.guild.id}.json"
    with open(path, encoding='utf-8', mode="r") as f:
      report_dict = json.load(f)
    cha = interaction.guild.get_channel(report_dict["report_send_channel"])

    try:
      msg = await cha.send(f"<@{1237001692977827920}>", embeds=embed)
    except discord.errors.Forbidden:
      await interaction.response.send_message("報告チャンネルでの権限が不足しています。\n**サーバー管理者さんに、`/config`コマンドをもう一度実行するように伝えてください。**", ephemeral=True)
      return

    # reply_numを定義
    path = f"data/pticket/guilds/{interaction.guild.id}.json"
    with open(path, encoding='utf-8', mode="r") as f:
      report_dict = json.load(f)
    report_dict["reply_num"] += 1
    with open(path, mode="w") as f:
      json.dump(report_dict, f, indent=2, ensure_ascii=False)

    # thread作成, 送信
    thread = await interaction.message.create_thread(name=f"report_reply-{str(report_dict['reply_num']).zfill(4)}")

    view = discord.ui.View()
    button_0 = discord.ui.Button(label="返信内容を編集", custom_id=f"report_edit_reply", style=discord.ButtonStyle.primary)
    button_1 = discord.ui.Button(label="送信する", custom_id=f"report_send", style=discord.ButtonStyle.red)
    view.add_item(button_0)
    view.add_item(button_1)

    embed=discord.Embed(
      title="返信内容",
      description="下のボタンから編集してください。",
      color=0x8BFF85,
    )
    await thread.send(embed=embed, view=view)

    await interaction.response.send_message("送信されました。\nこのbotのDMをご確認ください。", ephemeral=True)
    # ここから
    await interaction.user.send(embed=embed)


async def setup(bot):
  await bot.add_cog(PrivateTicket(bot))