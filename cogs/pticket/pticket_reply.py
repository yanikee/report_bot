from discord.ext import commands
from discord import app_commands
import discord
import os
import json
import aiofiles



class PticketReply(commands.Cog):
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
    if custom_id == "pticket_edit_reply":
      modal = EditReplyModal(interaction.message)
      await interaction.response.send_modal(modal)


    elif custom_id == "pticket_send":
      async with aiofiles.open(path, encoding='utf-8', mode="r") as f:
        contents = await f.read()
      pticket_dict = json.loads(contents)

      # pticket者を取得
      try:
        user_id = pticket_dict[str(interaction.channel.id)]
      except KeyError:
        await interaction.response.send_message("データが存在しませんでした。")
        return
      user = await interaction.guild.fetch_member(user_id)

      # embedを定義
      # embed_1: お知らせ
      # embed_2: 返信内容
      embed = discord.Embed(
        url = interaction.channel.jump_url,
        description="## 匿名ticket\n"
                    f"あなたの匿名ticketに、 {interaction.guild.name} の管理者から返信が届きました。\n"
                    f"- __**このメッセージに返信**__(右クリック→返信)すると、{interaction.guild.name}の管理者に届きます。\n\n"
                    f"## 返信内容\n{interaction.message.embeds[0].description}",
        color=0x9AC9FF,
      )
      embed.set_footer(
        text=f"匿名ticket | {interaction.guild.name}",
        icon_url=interaction.guild.icon.replace(format='png').url if interaction.guild.icon else None,
      )

      # 返信する
      try:
        await user.send(embed=embed)
      except discord.error.Forbidden:
        await interaction.response.send_message("匿名Ticket送信者がDMを受け付けてないため、送信されませんでした。")
        return
      except Exception as e:
        await interaction.response.send_message("不明なエラーが発生しました。サポートサーバーに問い合わせてください。")
        error = f"\n\n[ERROR]\n- {interaction.guild.id}\n{e}\n\n"
        print(error)
        return

      embed = interaction.message.embeds[0]
      embed.set_author(
        name=f"返信：{interaction.user.display_name}",
        icon_url=interaction.user.display_avatar.url,
      )
      await interaction.response.edit_message(embed=embed, view=None)

      # 追加返信ボタン設置
      view = discord.ui.View()
      button = discord.ui.Button(
        label="追加で返信する",
        style=discord.ButtonStyle.gray,
        custom_id="pticket_add_reply",
      )
      view.add_item(button)
      await interaction.channel.send(view=view)
      await interaction.channel.add_user(interaction.user)


    # 追加返信ボタンが押されたときの処理
    elif custom_id == "pticket_add_reply":
      view = discord.ui.View()
      button_0 = discord.ui.Button(label="返信内容を編集", custom_id=f"pticket_edit_reply", style=discord.ButtonStyle.primary, row=0)
      button_1 = discord.ui.Button(label="送信する", custom_id=f"pticket_send", style=discord.ButtonStyle.red, row=0)
      button_2 = discord.ui.Button(label="ファイルを送信する", custom_id=f"pticket_send_file", style=discord.ButtonStyle.green, row=1)
      view.add_item(button_0)
      view.add_item(button_1)
      view.add_item(button_2)

      embed=discord.Embed(
        title="返信内容",
        description="下のボタンから編集してください。",
        color=0x95FFA1,
      )
      await interaction.channel.send(embed=embed, view=view)
      await interaction.message.delete()


    elif custom_id == "pticket_cancel":
      await interaction.message.delete()


class EditReplyModal(discord.ui.Modal):
  def __init__(self, msg):
    super().__init__(title=f'匿名ticketへの返信用modal')
    self.msg = msg

    # modalのdefaultを定義
    if "下のボタンから編集してください。" in self.msg.embeds[0].description:
      default = None
    else:
      default = self.msg.embeds[0].description

    self.reply = discord.ui.TextInput(
      label="返信内容を入力（送信ボタンで一時保存できます。）",
      style=discord.TextStyle.long,
      default=default,
      required=True,
      row=0
    )
    self.add_item(self.reply)

  async def on_submit(self, interaction: discord.Interaction):
    # NOTE: 編集が適用されたことが分かりやすいように、わざとdeferしてる
    await interaction.response.defer()
    self.msg.embeds[0].description = self.reply.value
    await interaction.followup.edit_message(self.msg.id, embed=self.msg.embeds[0])



async def setup(bot):
  await bot.add_cog(PticketReply(bot))