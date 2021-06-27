import os
import discord

from bson import ObjectId
from discord import user
from discord.ext import commands
from discord.raw_models import RawReactionActionEvent
from discord_slash import SlashCommand, SlashContext
from discord_slash.model import SlashCommandPermissionType
from discord_slash.utils.manage_commands import create_option, create_permission
from dotenv import load_dotenv
from utils.constants import GUILD_IDS, COGS, CLIENT
from utils.functions import toast_message
from textwrap import dedent
from typing import Optional

bot = commands.Bot(command_prefix="!")  # Voter#3125
slash = SlashCommand(bot, sync_commands=True, sync_on_cog_reload=True)
for cog in COGS:
    bot.load_extension(cog)


@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")
    await bot.change_presence(
        activity=discord.Activity(
            name="for /help and other commands.", type=discord.ActivityType.watching
        ),
    )


@slash.slash(
    name="r",
    description="Reload a specific cog.",
    guild_ids=GUILD_IDS,
    default_permission=False,
    options=[
        create_option(
            name="extension",
            description="The cog to reload.",
            option_type=3,
            required=False,
        )
    ],
)
@slash.permission(
    guild_id=GUILD_IDS[0],
    permissions=[
        create_permission(407970334013128705, SlashCommandPermissionType.USER, True)
    ],
)
async def r(ctx: SlashContext, extension: Optional[str] = None):
    if extension is None:
        await toast_message(ctx, "Reloading all extensions.")
        try:
            for cog in COGS:
                bot.reload_extension(cog)
            await toast_message(ctx, "Successfully reloaded all.")

        except Exception as e:
            await toast_message(ctx, e)
    else:
        await toast_message(ctx, f"Trying to reload {extension}...")
        try:
            bot.reload_extension(f"cogs.{extension}")
            await toast_message(ctx, f"Successfully reloaded {extension}")
        except Exception as e:
            await toast_message(ctx, e)


@slash.slash(name="help", description="Information on commands.", guild_ids=GUILD_IDS)
async def help(ctx: SlashContext):
    embed = discord.Embed(title="List of commands", color=0x4287F5)
    embed.add_field(
        name="/close [poll_id]",
        value="```Closes the poll and shows the results.```",
        inline=False,
    )
    embed.add_field(
        name="/delete [poll_id]",
        value="```Deletes the corresponding poll from the database.```",
        inline=False,
    )
    embed.add_field(
        name="/list",
        value="```List polls in this server.```",
        inline=False,
    )
    embed.add_field(
        name="/poll [Question] [option(s...)]",
        value="```Start a poll with question and options.```",
        inline=False,
    )
    embed.add_field(
        name="/vote [poll_id]",
        value="```Prompts a voting window where reactions can be made.```",
        inline=False,
    )
    embed.set_author(name=bot.user, icon_url=bot.user.avatar_url)
    await ctx.send(embed=embed, hidden=True)


@bot.event
async def on_raw_reaction_add(payload: RawReactionActionEvent):
    user_id = payload.user_id
    if user_id == 856138200838176789:
        return

    if payload.emoji.name == "✅":
        channel: discord.DMChannel = bot.get_channel(payload.channel_id)
        m: discord.Message = await channel.fetch_message(payload.message_id)
        reacts = m.reactions
        selection = {}
        for r in reacts[1:]:
            selection.update({str(r.emoji): r.count - 1})

        e: discord.Embed = m.embeds[0]
        string = e.title.split("\n")
        gid, poll_id = string
        gid = gid.split(" ")[1]
        poll_id = poll_id.split(" ")[1]
        db = CLIENT[gid]
        polls = db.polls

        # Insert if not exist
        polls.update_one(
            {
                "_id": ObjectId(poll_id),
                "voters": {"$not": {"$elemMatch": {"user": user_id}}},
            },
            {"$addToSet": {"voters": {"user": user_id, "selection": selection}}},
            upsert=False,
        )
        polls.update_one(
            {"_id": ObjectId(poll_id), "voters.user": user_id},
            {"$set": {"voters.$.selection": selection}},
            upsert=False,
        )
        await toast_message(channel, "Vote received!")


@bot.event
async def on_message(m):
    # Direct Message to Bot
    if type(m.channel) is discord.DMChannel and m.author != bot.user:
        await toast_message(
            m.channel,
            dedent(
                """
                Hey, there's nothing to do here!
                To vote in a poll, enter the slash command `/vote` in the channel where the poll was created.
                Your vote will be viewable *only to yourself* due to ephemeral messages.
                """
            ),
            20,
        )


if __name__ == "__main__":
    load_dotenv()
    bot.run(os.getenv("TOKEN"))
