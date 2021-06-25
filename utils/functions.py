import asyncio
import discord

from discord.ext import commands
from discord_slash.context import SlashContext


async def throwaway_message(bot: commands.Bot, ctx: SlashContext, m: discord.Message):
    msg = m.content
    await msg.add_reaction("\U0001F5D1")

    def check(reaction, user):
        return str(reaction.emoji) == "\U0001F5D1" and user == ctx.author

    try:
        await bot.wait_for("reaction_add", check=check, timeout=60.0)
    except asyncio.TimeoutError:
        await msg.remove_reaction("\U0001F5D1", bot.user)
    else:
        await msg.delete()


async def toast_message(ctx: SlashContext, m: str, t=1.5):
    msg = await ctx.send(m)
    await asyncio.sleep(t)
    await msg.delete()
