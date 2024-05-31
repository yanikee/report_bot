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

    path = f"data/pticket/guilds/{interaction.guild.id}.json"
    if not os.path.exists(path):
      await interaction.response.send_message("サーバー管理者に`/pticket config`コマンドを実行するよう伝えてください。", ephemeral=True)
      return

    try:
      [x async for x in interaction.user.history(limit=1)]
    except discord.errors.Forbidden:
      await interaction.response.send_message("このbotからDMを受け取れるように設定してください！\n（テストメッセージをbotに送信するなど）", ephemeral=True)
      return

    modal = PrivateTicketModal()
    await interaction.response.send_modal(modal)


class PrivateTicketModal(discord.ui.Modal):
  def __init__(self):
    super().__init__(title=f'匿名ticketモーダル')

    self.first_pticket = discord.ui.TextInput(
      label="ticket内容を入力",
      style=discord.TextStyle.long,
      default=None,
      placeholder="（ちなみに）\n後ほどbotのDMに、添付ファイルなどを送信できます。",
      required=True,
      row=0
    )
    self.add_item(self.first_pticket)

  async def on_submit(self, interaction: discord.Interaction):
    # embedの定義
    embed=discord.Embed(
      title="匿名ticket",
      description=self.first_pticket.value,
      color=0x9AC9FF,
    )

    # pticket_channelの取得
    path = f"data/pticket/guilds/{interaction.guild.id}.json"
    with open(path, encoding='utf-8', mode="r") as f:
      report_dict = json.load(f)
    cha = interaction.guild.get_channel(report_dict["report_send_channel"])

    try:
      msg = await cha.send(f"<@{1237001692977827920}>", embed=embed)
    except discord.errors.Forbidden:
      await interaction.response.send_message(f"匿名ticket送信チャンネルでの権限が不足しています。\n**サーバー管理者さんに、`/pticket config`コマンドをもう一度実行するように伝えてください。**\n\n### ------------匿名ticket------------\n{self.first_pticket.value}", ephemeral=True)
      return
    except Exception as e:
      await interaction.response.send_message(f"不明なエラーが発生しました。\nサポートサーバーに問い合わせてください。\n\n### ------------匿名ticket------------\n{self.first_pticket.value}", ephemeral=True)
      print(e)
      return

    # pticket送信者idを保存{msg.id: user.id}
    path = f"data/pticket/pticket/{interaction.guild.id}.json"
    if os.path.exists(path):
      with open(path, encoding='utf-8', mode="r") as f:
        pticket_dict = json.load(f)
    else:
      pticket_dict = {}

    pticket_dict[str(msg.id)] = interaction.user.id

    with open(path, mode="w") as f:
      json.dump(pticket_dict, f, indent=2, ensure_ascii=False)


    # pticket_numを定義
    path = f"data/pticket/guilds/{interaction.guild.id}.json"
    with open(path, encoding='utf-8', mode="r") as f:
      report_dict = json.load(f)
    report_dict["pticket_num"] += 1
    with open(path, mode="w") as f:
      json.dump(report_dict, f, indent=2, ensure_ascii=False)

    # thread作成, button送信
    thread = await msg.create_thread(name=f"private_ticket-{str(report_dict['pticket_num']).zfill(4)}")

    view = discord.ui.View()
    button_0 = discord.ui.Button(label="返信内容を編集", custom_id=f"pticket_edit_reply", style=discord.ButtonStyle.primary)
    button_1 = discord.ui.Button(label="送信する", custom_id=f"pticket_send", style=discord.ButtonStyle.red)
    view.add_item(button_0)
    view.add_item(button_1)

    embed=discord.Embed(
      title="返信内容",
      description="下のボタンから編集してください。",
      color=0x8BFF85,
    )
    await thread.send(embed=embed, view=view)

    # 確認msg
    embed_1=discord.Embed(
      url=thread.jump_url,
      description=self.first_pticket.value,
      color=0x9AC9FF,
    )
    embed_2=discord.Embed(
      description="- ファイルを添付する場合や追加で何か送信する場合は、**このメッセージに返信**する形で送信してください。\n"
                  "- あなたの情報(ユーザー名, idなど)が外部に漏れることは一切ありません。",
      color=0x9AC9FF,
    )
    try:
      await interaction.user.send(embeds=[embed_1, embed_2])
    except Exception as e:
      await interaction.response.send_message("不明なエラーが発生しました。サポートサーバーに問い合わせてください。", ephemeral=True)
      print(e)
    else:
      await interaction.response.send_message("送信されました。\nこのbotのDMをご確認ください。", ephemeral=True)



async def setup(bot):
  await bot.add_cog(PrivateTicket(bot))