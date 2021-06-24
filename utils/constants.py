import pymongo
from pathlib import Path

CLIENT = pymongo.MongoClient("localhost", 27017)
AZ_EMOJIS = [
    (b"\\U0001f1a".replace(b"a", bytes(hex(224 + (6 + i))[2:], "utf-8"))).decode(
        "unicode-escape"
    )
    for i in range(26)
]
GUILD_IDS = [418633879587520520]
REPLIT = False
ROOT_DIR: Path = Path(__file__).parent.parent.resolve()
COGS_DIR: Path = ROOT_DIR / "cogs"
COGS = [f"{COGS_DIR.parts[-1]}.{p.stem}" for p in COGS_DIR.glob("*.py")]
