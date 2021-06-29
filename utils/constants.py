import pymongo
import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()
CLIENT = pymongo.MongoClient(os.getenv("CONNECTION_STRING"))
AZ_EMOJIS = [
    (b"\\U0001f1a".replace(b"a", bytes(hex(224 + (6 + i))[2:], "utf-8"))).decode(
        "unicode-escape"
    )
    for i in range(26)
]
GUILD_IDS = [418633879587520520, 842996863946326056]
REPLIT = False
ROOT_DIR: Path = Path(__file__).parent.parent.resolve()
COGS_DIR: Path = ROOT_DIR / "cogs"
COGS = [f"{COGS_DIR.parts[-1]}.{p.stem}" for p in COGS_DIR.glob("*.py")]
