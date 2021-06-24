from discord.ext import commands


class CustomCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.startup()
        self.bot = bot
        self.finishup()

    @classmethod
    def startup(cls):
        print(f"Loading {cls.__name__}...")

    @classmethod
    def finishup(cls):
        print(f"Finished loading {cls.__name__}!")
