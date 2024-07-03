from discord.ext import commands
from discord import app_commands
import discord
import os
import json
import aiofiles



class Reply(commands.Cog):
  def __init__(self, bot: commands.Bot):
    self.bot = bot

  @commands.Cog.listener()
  async def on_interaction(self, interaction:discord.Interaction):
    try:
      custom_id = interaction.data["custom_id"]
    except KeyError:
      return

    # privateのやつがなかった場合 -> return
    if custom_id in ["report_reply", "report_edit_reply", "report_send"]:
      path = f"data/report/private_report/{interaction.guild.id}.json"
      if not os.path.exists(path):
        await interaction.response.send_message("guildファイルが存在しません。サポートサーバーに問い合わせてください。", ephemeral=True)
        return

    if custom_id == "report_reply":
      # buttonの削除
      await interaction.message.edit(view=None)

      # reply_numを定義
      path = f"data/report/guilds/{interaction.guild.id}.json"
      async with aiofiles.open(path, encoding='utf-8', mode="r") as f:
        contents = await f.read()
      report_dict = json.loads(contents)
      report_dict["reply_num"] += 1
      async with aiofiles.open(path, mode="w") as f:
        contents = json.dumps(report_dict, indent=2, ensure_ascii=False)
        await f.write(contents)

      # thread作成, 送信
      thread = await interaction.message.create_thread(name=f"report_reply-{str(report_dict['reply_num']).zfill(4)}")

      view = discord.ui.View()
      button_0 = discord.ui.Button(label="返信内容を編集", custom_id=f"report_edit_reply", style=discord.ButtonStyle.primary, row=0)
      button_1 = discord.ui.Button(label="送信する", custom_id=f"report_send", style=discord.ButtonStyle.red, row=0)
      button_2 = discord.ui.Button(label="ファイルを送信する", custom_id=f"report_send_file", style=discord.ButtonStyle.green, row=1)
      view.add_item(button_0)
      view.add_item(button_1)
      view.add_item(button_2)

      embed=discord.Embed(
        title="返信内容",
        description="下のボタンから編集してください。",
        color=0x95FFA1,
      )
      await thread.send(embed=embed, view=view)

      await interaction.response.send_message("こちらのスレッドから返信を行えます。", ephemeral=True)


    # スレッド内での返信編集
    elif custom_id == "report_edit_reply":
      modal = EditReplyModal(interaction.message)
      await interaction.response.send_modal(modal)


    elif custom_id == "report_send":
      async with aiofiles.open(path, encoding='utf-8', mode="r") as f:
        contents = await f.read()
      private_dict = json.loads(contents)

      # 報告者を取得
      try:
        reporter_id = private_dict[str(interaction.channel.id)]
      except KeyError:
        await interaction.response.send_message("データが存在しませんでした。")
        return
      reporter = await interaction.guild.fetch_member(reporter_id)

      # embedを定義
      embed = discord.Embed(
        url=interaction.channel.jump_url,
        description="## 匿名報告\n"
                    f"あなたの報告に、 {interaction.guild.name} の管理者から返信が届きました。\n"
                    f"- __**このメッセージに返信**__(右クリック→返信)すると、{interaction.guild.name}の管理者に届きます。\n\n"
                    f"## 返信内容\n{interaction.message.embeds[0].description}",
        color=0xF4BD44,
      )
      embed.set_footer(
        text=f"匿名報告 | {interaction.guild.name}",
        icon_url=interaction.guild.icon.replace(format='png').url if interaction.guild.icon else None,
      )

      try:
        await reporter.send(embed=embed)
      except discord.errors.Forbidden:
        await interaction.response.send_message("報告者がDMを受け付けてないため、送信されませんでした。")
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
        custom_id="report_add_reply",
      )
      view.add_item(button)
      await interaction.channel.send(view=view)
      await interaction.channel.add_user(interaction.user)


    # 追加返信ボタンが押されたときの処理
    elif custom_id == "report_add_reply" or custom_id == "add_reply":
      view = discord.ui.View()
      button_0 = discord.ui.Button(label="返信内容を編集", custom_id=f"report_edit_reply", style=discord.ButtonStyle.primary, row=0)
      button_1 = discord.ui.Button(label="送信する", custom_id=f"report_send", style=discord.ButtonStyle.red, row=0)
      button_2 = discord.ui.Button(label="ファイルを送信する", custom_id=f"report_send_file", style=discord.ButtonStyle.green, row=1)
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


    elif custom_id == "report_cancel":
      await interaction.message.delete()


class EditReplyModal(discord.ui.Modal):
  def __init__(self, msg):
    super().__init__(title=f'報告への返信用modal')
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
  await bot.add_cog(Reply(bot))