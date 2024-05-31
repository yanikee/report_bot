from discord.ext import commands
from discord import app_commands
import discord
import os
import json



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
      with open(path, encoding='utf-8', mode="r") as f:
        pticket_dict = json.load(f)

      # 報告者に返信
      user_id = pticket_dict[str(interaction.channel.id)]
      user = await interaction.guild.fetch_member(user_id)
      embed = discord.Embed(
        url = interaction.channel.jump_url,
        description=f"あなたの匿名ticketに関して、 {interaction.guild.name} の管理者から返信が届きました。\n"
                    "### ------------返信内容------------\n"
                    f"{interaction.message.embeds[0].description}\n"
                    "### --------------------------------\n"
                    "- あなたの情報(ユーザー名, idなど)が外部に漏れることは一切ありません。\n"
                    f"- __**このメッセージに返信**__(右クリック→返信)すると、{interaction.guild.name}の管理者に届きます。",
        color=0x9AC9FF,
      )
      try:
        await user.send(embed=embed)
        # view削除
        await interaction.message.edit(view=None)
        await interaction.response.send_message(f"{interaction.user.mention}が返信を行いました。")
        await interaction.message.add_reaction("✅")

      except discord.error.Forbidden:
        await interaction.response.send_message("匿名ticket送信者がDMを受け付けてないため、送信されませんでした。")
      except Exception as e:
        await interaction.response.send_message("不明なエラーが発生しました。サポートサーバーに問い合わせてください。")
        print(f"[ERROR]\n{e}")


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
    self.msg.embeds[0].description = self.reply.value
    await self.msg.edit(embed=self.msg.embeds[0])
    await interaction.response.defer(thinking=True)
    m = await interaction.followup.send("\u200b")
    await m.delete()



async def setup(bot):
  await bot.add_cog(PticketReply(bot))