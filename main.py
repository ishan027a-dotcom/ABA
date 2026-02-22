import discord
from discord.ext import commands
from datetime import datetime
import os
from flask import Flask
from threading import Thread

# ---------------- KEEP ALIVE ---------------- #

app = Flask('')

@app.route('/')
def home():
    return "Aries Attendance Bot Running ✅"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# ---------------- BOT CONFIG ---------------- #

TOKEN = os.getenv("DISCORD_TOKEN")
APP_ID = os.getenv("APPLICATION_ID")

TARGET_SERVER_ID = 770004215678369883
TARGET_CHANNEL_ID = 1426247870495068343
LEADER_ROLE_ID = 1412430417578954983

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents,
    application_id=APP_ID
)

active_sessions = {}

# ---------------- READY ---------------- #

@bot.event
async def on_ready():
    print(f"✅ {bot.user} Deployment Successful!")

# ---------------- MAIN ENGINE ---------------- #

@bot.event
async def on_message(message):

    if message.author.bot:
        return

    if message.guild is None or message.guild.id != TARGET_SERVER_ID:
        return

    if message.channel.id != TARGET_CHANNEL_ID:
        return

    content = message.content.lower().strip()
    user = message.author
    now = datetime.utcnow()
    timestamp = int(now.timestamp())

    is_leader = any(role.id == LEADER_ROLE_ID for role in user.roles)

# ================= ONLINE ================= #

    if content == "online":

        try:
            await message.delete()
        except:
            pass

        # Already Online Warning
        if user.id in active_sessions:

            warn = await message.channel.send(
                f"⚠️ {user.mention} You are already marked ONLINE"
            )

            await warn.delete(delay=3)
            return

        active_sessions[user.id] = now

        if is_leader:
            desc = f"🛡️ Leader **{user.mention}** is watching."
            color = 0xf1c40f
        else:
            desc = f"✅ **{user.mention}** has started their session."
            color = 0x2ecc71

        embed = discord.Embed(
            title="Status: ONLINE",
            description=desc,
            color=color
        )

        embed.set_author(name=user.display_name, icon_url=user.display_avatar.url)
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.add_field(name="Login Time", value=f"<t:{timestamp}:t>")

        await message.channel.send(embed=embed)

# ================= OFFLINE ================= #

    elif content == "offline":

        try:
            await message.delete()
        except:
            pass

        if user.id not in active_sessions:

            warn = await message.channel.send(
                f"⚠️ {user.mention} You are not marked ONLINE"
            )

            await warn.delete(delay=3)
            return

        start_time = active_sessions[user.id]
        duration = now - start_time

        hours, remainder = divmod(int(duration.total_seconds()), 3600)
        minutes, _ = divmod(remainder, 60)
        duration_str = f"{hours}h {minutes}m" if hours else f"{minutes}m"

        if is_leader:
            desc = f"🌑 Leader **{user.mention}** is now off-duty."
            color = 0x2f3136
        else:
            desc = f"🔴 **{user.mention}** session ended."
            color = 0xe74c3c

        embed = discord.Embed(
            title="Status: OFFLINE",
            description=desc,
            color=color
        )

        embed.set_author(name=user.display_name, icon_url=user.display_avatar.url)
        embed.add_field(name="Logged In", value=f"<t:{int(start_time.timestamp())}:t>", inline=True)
        embed.add_field(name="Logged Out", value=f"<t:{timestamp}:t>", inline=True)
        embed.add_field(name="Total Session", value=f"`{duration_str}`", inline=False)

        await message.channel.send(embed=embed)

        del active_sessions[user.id]

    await bot.process_commands(message)

# ---------------- RUN ---------------- #

keep_alive()

if TOKEN:
    bot.run(TOKEN)