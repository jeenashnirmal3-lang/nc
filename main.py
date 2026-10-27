import asyncio
import json
import logging
import random
import time
import os
import platform

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram.request import HTTPXRequest

# ─────────────────────────────────────────────────
#  CONFIG
# ─────────────────────────────────────────────────

TOKENS = [
    "8750782215:AAHBoaR0w7S8l1sSuynCXA_dlKNTlofxCeQ",
    "8938946739:AAFXI57xtz4XclOAY0Fz-3YxeuXde5oVPBs",
]

# ✅ FIX: Tera asli ID yahan hai (log se mila)
OWNER_IDS = [7929995368]

SUDO_FILE = "jeenash_sudo.json"
UNAUTHORIZED_MESSAGE = "JEENASH PERMA"

DELAY_MS = 2000
global_delay = DELAY_MS / 1000.0

# ─────────────────────────────────────────────────
#  LOGGING
# ─────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
)
logger = logging.getLogger("NC")
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("telegram.ext.Application").setLevel(logging.WARNING)
logging.getLogger("telegram.Bot").setLevel(logging.WARNING)

# ─────────────────────────────────────────────────
#  EMOJIS + GAALI TEXTS
# ─────────────────────────────────────────────────

NC_EMOJIS = [
    "💀","🔥","⚡","👑","🔱","💥","☠️","🩸","😈","👿",
    "🗿","🤡","💣","🦅","👺","⚰️","🔴","🎯","💢",
    "🐕","🐍","😹","😂","🤣","💔","💩","👎",
    "🥊","🏆","🌋","⚔️","🎤","📢","🚨","📡",
    "💫","⭐","✨","🎀","❤️","🖤","🧊","🌷","🩵","🌻",
]

TARGET_TEXTS = [
    "💀 {name} 𝐓𝐞𝐫𝐢 𝐌𝐚𝐚 𝐊𝐢 𝐂𝐡𝐮𝐭 𝐌𝐞 𝐌𝐞𝐫𝐚 𝐋𝐮𝐧𝐝 𝐅𝐚𝐬𝐚 𝐇𝐚𝐢 🐕🔥",
    "🩸 {name} 𝐓𝐞𝐫𝐢 𝐁𝐞𝐡𝐚𝐧 𝐊𝐨 𝐑𝐚𝐧𝐝𝐢 𝐁𝐚𝐧𝐚 𝐃𝐮𝐧𝐠𝐚 💀😈",
    "👑 {name} 𝐓𝐞𝐫𝐢 𝐌𝐚𝐚 𝐊𝐚 𝐁𝐡𝐨𝐬𝐝𝐚 𝐇𝐚𝐢 𝐌𝐚𝐢𝐧 🐍💥",
    "☠️ {name} 𝐓𝐞𝐫𝐚 𝐁𝐚𝐚𝐩 𝐌𝐞𝐫𝐚 𝐍𝐚𝐮𝐤𝐚𝐫 𝐇𝐚𝐢 🔱🖕",
    "🔥 {name} 𝐓𝐞𝐫𝐢 𝐌𝐚𝐚 𝐊𝐢 𝐂𝐡𝐮𝐭 𝐌𝐞 𝐀𝐚𝐠 𝐋𝐚𝐠𝐚 𝐃𝐮𝐧𝐠𝐚 😡💀",
    "⚡ {name} 𝐓𝐞𝐫𝐢 𝐁𝐞𝐡𝐚𝐧 𝐊𝐢 𝐂𝐡𝐮𝐭 𝐌𝐞 𝐌𝐞𝐫𝐚 𝐋𝐮𝐧𝐝 🐕💦",
    "💣 {name} 𝐓𝐞𝐫𝐢 𝐌𝐚𝐚 𝐊𝐨 𝐁𝐚𝐳𝐚𝐫 𝐌𝐞 𝐍𝐚𝐜𝐡𝐚𝐮𝐧𝐠𝐚 😈🔱",
    "🩸 {name} 𝐓𝐞𝐫𝐚 𝐊𝐡𝐚𝐧𝐝𝐚𝐚𝐧 𝐑𝐚𝐧𝐝𝐢 𝐊𝐚 𝐇𝐚𝐢 🖕💀",
    "⛧ {name} 𝐓𝐞𝐫𝐢 𝐌𝐚𝐚 𝐊𝐢 𝐆𝐚𝐚𝐧𝐝 𝐌𝐞 𝐌𝐞𝐫𝐚 𝐋𝐮𝐧𝐝 🤣🔥",
    "🔱 {name} 𝐓𝐞𝐫𝐢 𝐌𝐚𝐚 𝐊𝐨 𝐂𝐡𝐨𝐝 𝐊𝐞 𝐑𝐚𝐧𝐝𝐢 𝐁𝐚𝐧𝐚 𝐃𝐮𝐧𝐠𝐚 💀😈",
    "👿 {name} 𝐓𝐞𝐫𝐢 𝐁𝐞𝐡𝐚𝐧 𝐊𝐨 𝐂𝐡𝐨𝐝𝐮𝐧𝐠𝐚 𝐀𝐚𝐣 𝐑𝐚𝐚𝐭 🐕🔥",
    "💀 {name} 𝐓𝐞𝐫𝐢 𝐌𝐚𝐚 𝐊𝐚 𝐁𝐡𝐨𝐬𝐝𝐚 𝐇𝐚𝐢 𝐒𝐚𝐚𝐥𝐞 🖕💥",
    "🗿 {name} 𝐓𝐞𝐫𝐚 𝐁𝐚𝐚𝐩 𝐑𝐚𝐧𝐝𝐢 𝐊𝐚 𝐁𝐚𝐜𝐡𝐚 𝐇𝐚𝐢 😂💀",
    "🤡 {name} 𝐓𝐞𝐫𝐢 𝐌𝐚𝐚 𝐊𝐢 𝐂𝐡𝐮𝐭 𝐌𝐞 𝐊𝐮𝐭𝐭𝐚 𝐆𝐡𝐮𝐬𝐚 𝐃𝐮𝐧𝐠𝐚 🐕💦",
    "⚰️ {name} 𝐓𝐞𝐫𝐢 𝐁𝐞𝐡𝐚𝐧 𝐊𝐚 𝐁𝐡𝐨𝐬𝐝𝐚 𝐇𝐚𝐢 🔥🖕",
    "🔴 {name} 𝐓𝐞𝐫𝐢 𝐌𝐚𝐚 𝐊𝐨 𝐑𝐚𝐧𝐝𝐢 𝐁𝐚𝐧𝐚𝐮𝐧𝐠𝐚 𝐒𝐚𝐚𝐥𝐞 😈💀",
    "👺 {name} 𝐓𝐞𝐫𝐢 𝐌𝐚𝐚 𝐊𝐢 𝐆𝐚𝐚𝐧𝐝 𝐌𝐞 𝐋𝐚𝐭𝐡𝐢 𝐃𝐚𝐥 𝐃𝐮𝐧𝐠𝐚 🖕🔥",
    "💔 {name} 𝐓𝐞𝐫𝐢 𝐌𝐚𝐚 𝐊𝐚 𝐘𝐚𝐚𝐫 𝐌𝐚𝐢𝐧 𝐇𝐮 𝐒𝐚𝐚𝐥𝐞 🤣💀",
    "💩 {name} 𝐓𝐞𝐫𝐢 𝐌𝐚𝐚 𝐊𝐢 𝐂𝐡𝐮𝐭 𝐌𝐞 𝐓𝐡𝐮𝐤 𝐃𝐮𝐧𝐠𝐚 💦🐕",
    "🦅 {name} 𝐓𝐞𝐫𝐢 𝐌𝐚𝐚 𝐑𝐚𝐧𝐝𝐢 𝐇𝐚𝐢 𝐒𝐚𝐚𝐥𝐞 🔥💀",
    "⚡ {name} 𝐓𝐞𝐫𝐢 𝐁𝐞𝐡𝐚𝐧 𝐊𝐢 𝐂𝐡𝐮𝐭 𝐌𝐞 𝐌𝐞𝐫𝐚 𝐋𝐮𝐧𝐝 𝐅𝐚𝐬𝐚 💦😈",
    "🎤 {name} 𝐓𝐞𝐫𝐚 𝐊𝐡𝐚𝐧𝐝𝐚𝐚𝐧 𝐑𝐚𝐧𝐝𝐢 𝐊𝐚 𝐇𝐚𝐢 🖕💀",
    "💢 {name} 𝐓𝐞𝐫𝐢 𝐌𝐚𝐚 𝐊𝐨 𝐂𝐡𝐨𝐝 𝐊𝐞 𝐁𝐚𝐳𝐚𝐫 𝐌𝐞 𝐍𝐚𝐜𝐡𝐚𝐮𝐧𝐠𝐚 😈🔱",
    "👿 {name} 𝐓𝐞𝐫𝐢 𝐌𝐚𝐚 𝐊𝐢 𝐂𝐡𝐮𝐭 𝐌𝐞 𝐊𝐮𝐭𝐭𝐚 𝐂𝐡𝐨𝐝 𝐃𝐮𝐧𝐠𝐚 🐕🔥",
    "🗿 {name} 𝐓𝐞𝐫𝐚 𝐁𝐚𝐚𝐩 𝐌𝐞𝐫𝐚 𝐍𝐚𝐮𝐤𝐚𝐫 𝐇𝐚𝐢 𝐒𝐚𝐚𝐥𝐞 🖕💀",
    "🎯 {name} 𝐓𝐞𝐫𝐢 𝐁𝐞𝐡𝐚𝐧 𝐊𝐨 𝐑𝐚𝐧𝐝𝐢 𝐁𝐚𝐧𝐚𝐮𝐧𝐠𝐚 💦😈",
    "🩸 {name} 𝐓𝐞𝐫𝐢 𝐌𝐚𝐚 𝐊𝐢 𝐆𝐚𝐚𝐧𝐝 𝐌𝐞 𝐌𝐞𝐫𝐚 𝐋𝐮𝐧𝐝 🔥🐕",
    "💀 {name} 𝐓𝐞𝐫𝐢 𝐌𝐚𝐚 𝐊𝐚 𝐁𝐡𝐨𝐬𝐝𝐚 𝐇𝐚𝐢 𝐌𝐚𝐢𝐧 𝐒𝐚𝐚𝐥𝐞 🖕💥",
    "🦅 {name} 𝐓𝐞𝐫𝐢 𝐌𝐚𝐚 𝐊𝐢 𝐂𝐡𝐮𝐭 𝐌𝐞 𝐀𝐚𝐠 𝐋𝐚𝐠𝐚𝐮𝐧𝐠𝐚 😈💀",
    "🔥 {name} 𝐓𝐞𝐫𝐢 𝐁𝐞𝐡𝐚𝐧 𝐊𝐚 𝐁𝐡𝐨𝐬𝐝𝐚 𝐇𝐚𝐢 🐕🖕",
]

# ─────────────────────────────────────────────────
#  GLOBALS
# ─────────────────────────────────────────────────

SUDO_USERS = set(OWNER_IDS)
active = {}
START_TIME = time.time()

# ─────────────────────────────────────────────────
#  SUDO FILE
# ─────────────────────────────────────────────────

def load_sudo():
    global SUDO_USERS
    if os.path.exists(SUDO_FILE):
        try:
            with open(SUDO_FILE) as f:
                data = json.load(f)
            if isinstance(data, list):
                for x in data:
                    SUDO_USERS.add(int(x))
                logger.info(f"Loaded extra sudo: {data}")
        except Exception as e:
            logger.error(f"Sudo load failed: {e}")

def save_sudo():
    try:
        with open(SUDO_FILE, "w") as f:
            json.dump(list(SUDO_USERS), f)
    except Exception as e:
        logger.error(f"Sudo save failed: {e}")

def is_sudo(uid):
    return uid in SUDO_USERS

# ─────────────────────────────────────────────────
#  TASK CANCEL
# ─────────────────────────────────────────────────

async def _cancel_chat(chat_id):
    entry = active.pop(chat_id, None)
    if not entry:
        return None
    tasks = entry.get("tasks", [])
    for t in tasks:
        if not t.done():
            t.cancel()
    for t in tasks:
        try:
            await t
        except (asyncio.CancelledError, Exception):
            pass
    return entry

# ─────────────────────────────────────────────────
#  CORE LOOPS
# ─────────────────────────────────────────────────

async def nc_loop(bot, chat_id, text):
    while True:
        try:
            emo = random.choice(NC_EMOJIS)
            new_title = f"{text} {emo}"
            await bot.set_chat_title(chat_id, new_title)
            logger.info(f"✅ NC title set in {chat_id}: {new_title[:40]}")
        except asyncio.CancelledError:
            return
        except Exception as e:
            err = str(e)
            logger.error(f"❌ NC setChatTitle FAILED in {chat_id}: {err[:120]}")
            if "Too Many Requests" in err:
                await asyncio.sleep(10)
            elif "not enough rights" in err.lower() or "chat_admin_required" in err.lower():
                logger.error("👉 FIX: Bot ko admin banao + 'Change Group Info' permission do")
                await asyncio.sleep(15)
            elif "chat not found" in err.lower() or "bot is not a member" in err.lower():
                return
            else:
                await asyncio.sleep(3)
        try:
            await asyncio.sleep(global_delay)
        except asyncio.CancelledError:
            return

async def target_loop(bot, chat_id, name):
    idx = 0
    while True:
        try:
            txt = TARGET_TEXTS[idx % len(TARGET_TEXTS)].format(name=name)
            emo = random.choice(NC_EMOJIS)
            new_title = f"{txt} {emo}"
            await bot.set_chat_title(chat_id, new_title)
            logger.info(f"✅ TGT title set in {chat_id}: {new_title[:40]}")
            idx += 1
        except asyncio.CancelledError:
            return
        except Exception as e:
            err = str(e)
            logger.error(f"❌ TGT setChatTitle FAILED in {chat_id}: {err[:120]}")
            if "Too Many Requests" in err:
                await asyncio.sleep(10)
            elif "not enough rights" in err.lower() or "chat_admin_required" in err.lower():
                logger.error("👉 FIX: Bot ko admin banao + 'Change Group Info' permission do")
                await asyncio.sleep(15)
            elif "chat not found" in err.lower():
                return
            else:
                await asyncio.sleep(3)
        try:
            await asyncio.sleep(global_delay)
        except asyncio.CancelledError:
            return

# ─────────────────────────────────────────────────
#  PERMISSION
# ─────────────────────────────────────────────────

async def _reply_unauth(update):
    uid = update.effective_user.id
    uname = update.effective_user.username or update.effective_user.first_name
    logger.warning(f"🚫 UNAUTHORIZED: user_id={uid} @{uname}")
    await update.message.reply_text(
        f"🚫 JEENASH PERMA\n\n"
        f"🆔 𝐘𝐨𝐮𝐫 𝐈𝐃: `{uid}`\n"
        f"👑 𝐎𝐰𝐧𝐞𝐫 𝐈𝐃𝐬: {list(SUDO_USERS)}",
        parse_mode="Markdown",
    )

# ─────────────────────────────────────────────────
#  COMMANDS
# ─────────────────────────────────────────────────

async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    sudo_tag = "✅ SUDO" if is_sudo(uid) else "❌ NOT SUDO"
    await update.message.reply_text(
        f"╭━━━━〔 👑 𝐉𝐄𝐄𝐍𝐀𝐒𝐇 𝐏𝐄𝐑𝐌𝐀 〕━━━━╮\n"
        f"│\n"
        f"│  🔥 /nc <text>      → 𝐆𝐂 𝐓𝐢𝐭𝐥𝐞 𝐫𝐨𝐭𝐚𝐭𝐞\n"
        f"│  🎯 /target <name>  → 𝐆𝐚𝐚𝐥𝐢 𝐭𝐢𝐭𝐥𝐞 𝐫𝐨𝐭𝐚𝐭𝐞\n"
        f"│  🛑 /stop           → 𝐒𝐚𝐛 𝐛𝐚𝐧𝐝\n"
        f"│  📊 /status         → 𝐒𝐭𝐚𝐭𝐮𝐬\n"
        f"│  🔍 /whoami         → 𝐀𝐩𝐧𝐚 𝐈𝐃\n"
        f"│\n"
        f"│  🆔 𝐘𝐨𝐮𝐫 𝐈𝐃: `{uid}`\n"
        f"│  🔐 𝐒𝐭𝐚𝐭𝐮𝐬  : {sudo_tag}\n"
        f"│\n"
        f"╰━━━━━━━━━━━━━━━━━━━━━━╯",
        parse_mode="Markdown",
    )

async def whoami_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    uname = update.effective_user.username or update.effective_user.first_name
    chat = update.effective_chat
    await update.message.reply_text(
        f"👤 **User Info**\n"
        f"🆔 ID: `{uid}`\n"
        f"📛 Name: {uname}\n"
        f"💬 Chat ID: `{chat.id}`\n"
        f"📋 Chat type: {chat.type}\n"
        f"🔐 Sudo: {'✅ YES' if is_sudo(uid) else '❌ NO'}\n\n"
        f"👑 Allowed: `{list(SUDO_USERS)}`",
        parse_mode="Markdown",
    )

async def status_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not is_sudo(uid):
        return await _reply_unauth(update)
    try:
        import psutil
        ram_pct = psutil.virtual_memory().percent
        cpu_pct = psutil.cpu_percent(interval=0.3)
        ram_str = f"{ram_pct}%"
        cpu_str = f"{cpu_pct}%"
    except Exception:
        ram_str = cpu_str = "N/A"
    uptime = int(time.time() - START_TIME)
    await update.message.reply_text(
        f"📊 **STATUS**\n"
        f"🤖 Bots: {len(bots)}\n"
        f"💬 Active: {len(active)}\n"
        f"⏱️ Uptime: {uptime}s\n"
        f"🧠 RAM: {ram_str}\n"
        f"⚙️ CPU: {cpu_str}\n"
        f"🐍 Python: {platform.python_version()}",
        parse_mode="Markdown",
    )

async def nc_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    chat_id = update.message.chat_id
    logger.info(f"📥 /nc user={uid} chat={chat_id}")

    if not is_sudo(uid):
        return await _reply_unauth(update)

    text = " ".join(context.args) if context.args else "JEENASH PERMA"
    await _cancel_chat(chat_id)

    tasks = [asyncio.create_task(nc_loop(bot, chat_id, text)) for bot in bots]
    active[chat_id] = {"tasks": tasks, "mode": "nc", "label": text}

    await update.message.reply_text(
        f"🔥 **NC START**\n"
        f"📝 {text}\n"
        f"⏱️ {DELAY_MS}ms\n"
        f"🛑 /stop",
        parse_mode="Markdown",
    )

async def target_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    chat_id = update.message.chat_id
    logger.info(f"📥 /target user={uid} chat={chat_id}")

    if not is_sudo(uid):
        return await _reply_unauth(update)

    if context.args:
        name = " ".join(context.args)
    elif update.message.reply_to_message and update.message.reply_to_message.from_user:
        u = update.message.reply_to_message.from_user
        name = u.first_name or u.username or str(u.id)
    else:
        return await update.message.reply_text("⚠️ /target <name>")

    await _cancel_chat(chat_id)

    tasks = [asyncio.create_task(target_loop(bot, chat_id, name)) for bot in bots]
    active[chat_id] = {"tasks": tasks, "mode": "target", "label": name}

    await update.message.reply_text(
        f"🎯 **TARGET START**\n"
        f"👤 {name}\n"
        f"⏱️ {DELAY_MS}ms\n"
        f"🛑 /stop",
        parse_mode="Markdown",
    )

async def stop_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    chat_id = update.message.chat_id
    logger.info(f"📥 /stop user={uid} chat={chat_id}")

    if not is_sudo(uid):
        return await _reply_unauth(update)

    entry = await _cancel_chat(chat_id)
    if entry:
        await update.message.reply_text(f"🛑 STOPPED ({entry['mode'].upper()}) ✅")
    else:
        await update.message.reply_text("ℹ️ Kuch nahi chal raha.")

# ─────────────────────────────────────────────────
#  BUILD
# ─────────────────────────────────────────────────

request = HTTPXRequest(
    connect_timeout=30.0,
    read_timeout=30.0,
    write_timeout=30.0,
    pool_timeout=30.0,
)

bots = [Application.builder().token(t).request(request).build().bot for t in TOKENS]

def build_app(token):
    app = Application.builder().token(token).request(request).build()
    app.add_handler(CommandHandler("start",  start_cmd))
    app.add_handler(CommandHandler("whoami", whoami_cmd))
    app.add_handler(CommandHandler("status", status_cmd))
    app.add_handler(CommandHandler("nc",     nc_cmd))
    app.add_handler(CommandHandler("target", target_cmd))
    app.add_handler(CommandHandler("stop",   stop_cmd))
    return app

# ─────────────────────────────────────────────────
#  RUN
# ─────────────────────────────────────────────────

async def run_bots():
    if not TOKENS:
        print("❌ No tokens.")
        return

    load_sudo()

    print("\n" + "="*60)
    print("  🔍 STARTUP")
    print("="*60)
    print(f"  👑 OWNER_IDS : {OWNER_IDS}")
    print(f"  🔐 SUDO_USERS: {SUDO_USERS}")
    print(f"  📁 Sudo file : {os.path.abspath(SUDO_FILE)}")
    print(f"  ✅ Exists    : {os.path.exists(SUDO_FILE)}")
    print("="*60 + "\n")

    for i, b in enumerate(bots, 1):
        for attempt in range(1, 6):
            try:
                me = await b.get_me()
                print(f"✅ Bot {i}: @{me.username}")
                break
            except Exception as e:
                print(f"⚠️ Bot {i} attempt {attempt}/5: {type(e).__name__}")
                if attempt < 5:
                    await asyncio.sleep(3)

    apps = [build_app(t) for t in TOKENS]
    for i, app in enumerate(apps, 1):
        for attempt in range(1, 6):
            try:
                await app.initialize()
                await app.start()
                await app.updater.start_polling(drop_pending_updates=True)
                print(f"🚀 App {i} polling started")
                break
            except Exception as e:
                print(f"⚠️ App {i} attempt {attempt}/5: {type(e).__name__}")
                if attempt < 5:
                    await asyncio.sleep(3)

    print("\n✅ BOT RUNNING!")
    print("   /whoami   → apna ID")
    print("   /nc TEXT  → GC title change")
    print("   /target NAME → gaali title change")
    print("   /stop     → band")
    print("="*60 + "\n")

    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    asyncio.run(run_bots())