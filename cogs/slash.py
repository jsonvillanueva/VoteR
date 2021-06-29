import asyncio
import bson
import discord
from collections import defaultdict
from discord.ext import commands
from discord_slash import cog_ext, SlashContext
from discord_slash.utils.manage_commands import create_option
from utils.base_cog import CustomCog
from utils.poll import Poll
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
            ),
        ],
    )
    async def _close(self, ctx: SlashContext, poll_id: str, remove=1):
        gid = str(ctx.guild_id)
        db = CLIENT[gid]
        polls = db.polls
        c = polls.find({"_id": bson.ObjectId(poll_id)})
        poll_info, voters = {}, []
        res = defaultdict(int)
        for cur in c:
            poll_info = cur
        if "voters" in poll_info:  # Since there aren't any voters at poll creation time
            voters: list[dict] = poll_info["voters"]
        options: list[dict] = poll_info["options"]
        author = poll_info["author"]
        avatar_url = poll_info["avatar_url"]
        question = poll_info["question"]

        for voter in voters:
            for k, v in voter["selection"].items():
                res[k] += v

        embed = discord.Embed(
            title=f"Poll ID: {poll_id}", description="**Final Results**"
        )
        embed.set_author(
            name=f"Author: {author}", icon_url=f"https://cdn.discordapp.com{avatar_url}"
        )
        embed.add_field(name="**Poll question:**", value=question, inline=True)
        for k, v in sorted(res.items(), key=lambda x: x[1], reverse=True):
            embed.add_field(name=f"{k} {options[k]}", value=v, inline=False)

        total_voters = str(len(voters))
        embed.add_field(
            name=f"Total voters: {total_voters}",
            value=f"Delete specified: {'True' if remove else 'False'}",
        )

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
        cur = polls.find({"_id": bson.ObjectId(poll_id)}, {"voters": 1, "_id": 0})
        unique_voters = 0
        for c in cur:
            if "voters" in c:
                unique_voters = len(c["voters"])
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
        no_selection = {o: 0 for o in options.keys()}
        # voters = [{"user": ctx.author_id, "selection": no_selection}]
        poll = Poll(
            author=ctx.author.name,
            avatar_url=ctx.author.avatar_url._url,
            channel_id=ctx.channel_id,
            options=options,
            question=question,
        )
        gid = str(ctx.guild_id)
        db = CLIENT[gid]
        polls = db.polls
        result = polls.insert_one(poll)
        poll.id = result.inserted_id

        embed = discord.Embed(
            title=f"Poll ID: {poll.id}",
            description="Anonymous Approval Voting",
        )
        embed.set_author(
            name=f"Author: {ctx.author.display_name}", icon_url=ctx.author.avatar_url
        )
        embed.add_field(name="**Poll question:**", value=question, inline=True)

        for k, v in poll.options.items():
            embed.add_field(name=k, value=v, inline=False)

        await ctx.send(
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
        cursor = None
        try:
            cursor = polls.find({"_id": bson.ObjectId(poll_id)})
        except:
            await ctx.author.send(
                f"You tried voting with poll_id: {poll_id} which is an invalid poll ID. Please try again."
            )
            return

        options = None
        channel_id = None
        for p in cursor:
            options = p["options"]
            channel_id = p["channel_id"]
        if ctx.channel_id != channel_id:
            await ctx.send(
                f"{ctx.author}, you must use `/vote` in the channel the poll was created in."
            )
            return
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
