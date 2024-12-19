from discord.ext import commands
import discord



class CheckReply(commands.Cog):
  def __init__(self, bot: commands.Bot):
    self.bot = bot

  async def is_not_reply(self, message) -> None:
    embed = discord.Embed(
      description="# 返信できていません！\nbotからの匿名Report/匿名Ticketのメッセージに対して、「右クリック」→「返信」を行ってください！",
      color=0xff4b00,
    )
    embed.set_footer(text="このメッセージは15秒後に削除されます")

    await message.reply(embed=embed, delete_after=15)
    await message.add_reaction("❌")
    return

  @commands.Cog.listener()
  async def on_message(self, message):
    # DMではなかった場合 -> return
    if message.channel.type != discord.ChannelType.private:
      return
    # botだった場合 -> return
    if message.author.bot:
      return

    # 返信メッセージじゃなかった場合 -> 警告後、return
    if message.type != discord.MessageType.reply:
      await self.is_not_reply(message)
      return

    # 返信メッセージを取得
    msg_id = message.reference.message_id
    msg = await message.channel.fetch_message(msg_id)

    # 返信msgにembedがなかった場合 -> 警告後、return
    if not msg.embeds:
      await self.is_not_reply(message)
      return

    # 匿名Report, 匿名Ticketのembedじゃなかった場合 -> 警告後、return
    if msg.embeds[0].footer:
      if any(keyword in msg.embeds[0].footer.text for keyword in ["匿名報告 |", "匿名Report |", "匿名ticket |", "匿名Ticket |"]):
        pass
      else:
        await self.is_not_reply(message)
        return
    else:
      if "------------返信内容------------" in msg.embeds[0].description:
        pass
      else:
        await self.is_not_reply(message)
        return



async def setup(bot):
  await bot.add_cog(CheckReply(bot))