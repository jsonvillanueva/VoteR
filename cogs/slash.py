import asyncio
import bson
import discord
from collections import Counter
from discord.ext import commands
from discord_slash import cog_ext, SlashContext
from discord_slash.utils.manage_commands import create_option
from utils.base_cog import CustomCog
from poll import Poll
from textwrap import dedent
from utils.constants import AZ_EMOJIS, GUILD_IDS, CLIENT
from utils.functions import toast_message


class Slash(CustomCog):
    def __init__(self, bot: commands.Bot):
        super().__init__(bot)

    @cog_ext.cog_slash(
        name="close",
        description="Closes a poll and reveal its results.",
        guild_ids=GUILD_IDS,
        options=[
            create_option(
                name="poll_id",
                description="The poll to close.",
                option_type=3,
                required=True,
            ),
            create_option(
                name="remove",
                description="Remove from the DB? Defaults to True; Enter 0 for False.",
                option_type=4,
                required=False,
            )
        ],
    )
    async def _close(self, ctx: SlashContext, poll_id: str, remove=1):
        gid = str(ctx.guild_id)
        db = CLIENT[gid]
        polls = db.polls
        c = polls.find({"_id":bson.ObjectId(poll_id)},{"options":1, "voters":1, "_id":0})
        options, voters = None, None
        res = Counter()
        for cur in c:
            voters: list[dict] = cur["voters"]
            options: list[dict] = cur["options"]

        for voter in voters:
            res += Counter(voter["selection"])
        embed = discord.Embed(
            title="**Final Results**"
        )
        for ((k, d), v) in zip(options.items(), res.values()):
            embed.add_field(name=f"{k} {d}", value=v, inline=False)
        
        await ctx.send(embed=embed)
        if remove:
            query = {"_id": bson.ObjectId(poll_id)}

            result = polls.delete_one(query)
            if result.deleted_count:
                await toast_message(ctx, "Successfully deleted poll.")
            else:
                await toast_message(ctx, "Poll not found.")


    @cog_ext.cog_slash(
        name="count",
        description="Count the number of voters so far.",
        guild_ids=GUILD_IDS,
        options=[
            create_option(
                name="poll_id",
                description="The poll to count.",
                option_type=3,
                required=True,
            )
        ],
    )
    async def _count(self, ctx: SlashContext, poll_id: str):
        gid = str(ctx.guild_id)
        db = CLIENT[gid]
        polls = db.polls
        c = polls.find({"_id":bson.ObjectId(poll_id)},{"voters":1, "_id":0})
        unique_voters = None
        for cur in c:
            unique_voters = len(cur["voters"])
        if unique_voters > 1: 
            await ctx.send(f"There has been {unique_voters} unique voters.")
        elif unique_voters == 1:
            await ctx.send(f"There has been {unique_voters} unique voter.")
        else:
            await ctx.send(f"No one has voted.")

    @cog_ext.cog_slash(
        name="delete",
        description="Delete a poll in this server.",
        guild_ids=GUILD_IDS,
        options=[
            create_option(
                name="poll_id",
                description="The poll to be deleted.",
                option_type=3,
                required=True,
            )
        ],
    )
    async def _delete(self, ctx: SlashContext, poll_id: str):
        print(f"Deleting {poll_id}...")
        gid = str(ctx.guild_id)
        db = CLIENT[gid]
        polls = db.polls
        query = {"_id": bson.ObjectId(poll_id)}

        result = polls.delete_one(query)
        if result.deleted_count:
            await toast_message(ctx, "Successfully deleted poll.")
        else:
            await toast_message(ctx, "Poll not found.")

    @cog_ext.cog_slash(
        name="list",
        description="List polls active polls on the server.",
        guild_ids=GUILD_IDS,
    )
    async def _list(self, ctx: SlashContext):
        gid = str(ctx.guild_id)
        db = CLIENT[gid]
        polls = db.polls
        available = "\n".join(str(key["_id"]) for key in polls.find())
        if available:
            await toast_message(ctx, f"Available polls:\n{available}", 30)
        else:
            await toast_message(ctx, "No server polls available! :(", 2)

    @cog_ext.cog_slash(
        name="poll",
        description="Start a poll for this server.",
        guild_ids=GUILD_IDS,
        options=[
            create_option(
                name="question",
                description="Poll question.",
                option_type=3,
                required=True,
            ),
            create_option(
                name="option_a",
                description="First poll option.",
                option_type=3,
                required=True,
            ),
            create_option(
                name="option_b",
                description="Second poll option.",
                option_type=3,
                required=False,
            ),
            create_option(
                name="option_c",
                description="Third poll option.",
                option_type=3,
                required=False,
            ),
            create_option(
                name="option_d",
                description="Fourth poll option.",
                option_type=3,
                required=False,
            ),
            create_option(
                name="option_e",
                description="Fifth poll option.",
                option_type=3,
                required=False,
            ),
            create_option(
                name="option_f",
                description="Sixth poll option.",
                option_type=3,
                required=False,
            ),
            create_option(
                name="option_g",
                description="Seventh poll option.",
                option_type=3,
                required=False,
            ),
            create_option(
                name="option_h",
                description="Eigth poll option.",
                option_type=3,
                required=False,
            ),
            create_option(
                name="option_i",
                description="Ninth poll option.",
                option_type=3,
                required=False,
            ),
            create_option(
                name="option_j",
                description="Tenth poll option.",
                option_type=3,
                required=False,
            ),
        ],
    )
    async def _poll(self, ctx: SlashContext, question, **kwargs):
        options = dict(zip(AZ_EMOJIS, kwargs.values()))
        voters = [{"user": ctx.author_id}]
        poll = Poll(
            options=options, voters=voters
        )
        gid = str(ctx.guild_id)
        db = CLIENT[gid]
        polls = db.polls  # Collection of polls
        result = polls.insert_one(poll)
        poll.id = result.inserted_id

        embed = discord.Embed(
            title=f"Poll ID: {poll.id}",
            description="Anonymous Approval Voting",
        )
        embed.set_author(
            name=f" >> {ctx.author.display_name}", icon_url=ctx.author.avatar_url
        )
        embed.add_field(name="**Poll question:**", value=question, inline=True)

        for k, v in poll.options.items():
            embed.add_field(name=k, value=v, inline=False)

        msg = await ctx.send(
            embeds=[embed],
        )

    @cog_ext.cog_slash(
        name="vote",
        description="Vote in a poll in this server.",
        guild_ids=GUILD_IDS,
        options=[
            create_option(
                name="poll_id",
                description="The poll to vote in.",
                option_type=3,
                required=True,
            )
        ],
    )
    async def _vote(self, ctx: SlashContext, poll_id: str):
        gid = str(ctx.guild_id)
        db = CLIENT[gid]
        polls = db.polls
        cursor = polls.find({"_id": bson.ObjectId(poll_id)})
        options = None
        for p in cursor:
            options = p["options"]
        embed = discord.Embed(
            title=dedent(
                f"""
                Server: {gid}
                Poll: {poll_id}
                """
            ),
            description=dedent(
                """
                Select who you'd like to vote for then click ✅ to cast your vote!
                You can vote as many times as you'd like until the poll is **/closed**.
                If you don't receive a confirmation message, please recast your vote.
                Note: Only your final vote counts!
            """
            ),
        )

        for k, v in options.items():
            embed.add_field(name=k, value=v, inline=False)

        rs = ["✅"]
        rs.extend([r for r in options.keys()])
        m: discord.Message = await ctx.author.send(embed=embed)
        for r in rs:
            await m.add_reaction(r)


def setup(bot):
    bot.add_cog(Slash(bot))
