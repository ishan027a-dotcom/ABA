import discord
from discord.ext import commands
from datetime import datetime
import os
import psutil
from flask import Flask
from threading import Thread

# ------------------- RENDER KEEP ALIVE -------------------

app = Flask(__name__)

@app.route('/')
def home():
    return "Aries Bot Running ✅"

def run_flask():
    port = int(os.environ.get("PORT", 10000))  # 🔥 Render Dynamic Port Fix
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_flask)
    t.start()

# ------------------- BOT CONFIG -------------------

TOKEN = os.getenv("DISCORD_TOKEN")

TARGET_SERVER_ID = 770004215678369883
TARGET_CHANNEL_ID = 1426247870495068343
LEADER_ROLE_ID = 1412430417578954983

class AriesBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = True
        
        super().__init__(
            command_prefix="!",
            intents=intents,
            reconnect=True
        )

        self.active_sessions = {}
        self.start_time = datetime.utcnow()

bot = AriesBot()

# ------------------- STATUS COMMAND -------------------

def get_bot_uptime():
    delta = datetime.utcnow() - bot.start_time
    hours, remainder = divmod(int(delta.total_seconds()), 3600)
    minutes, _ = divmod(remainder, 60)
    return f"{hours}h {minutes}m"

@bot.command()
@commands.has_permissions(administrator=True)
async def status(ctx):
    latency = round(bot.latency * 1000)
    memory = psutil.Process(os.getpid()).memory_info().rss / 1024**2

    embed = discord.Embed(title="⚙️ Aries Self-Diagnostic", color=0x3498db)
    embed.add_field(name="📡 Latency", value=f"`{latency}ms`", inline=True)
    embed.add_field(name="⏳ Uptime", value=f"`{get_bot_uptime()}`", inline=True)
    embed.add_field(name="💾 RAM", value=f"`{memory:.1f}MB`", inline=True)

    await ctx.send(embed=embed)

# ------------------- MAIN ATTENDANCE -------------------

@bot.event
async def on_message(message):
    if message.author == bot.user:
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

    if content == "online":
        try: await message.delete()
        except: pass

        if user.id not in bot.active_sessions:
            bot.active_sessions[user.id] = now

            greeting = f"🛡️ Leader {user.display_name} Online" if is_leader else f"✅ {user.display_name} Started Session"

            embed = discord.Embed(title="Status: ONLINE", description=greeting, color=0x2ecc71)
            embed.set_author(name=user.display_name, icon_url=user.display_avatar.url)
            embed.add_field(name="Arrival", value=f"<t:{timestamp}:t>")

            await message.channel.send(embed=embed)

    elif content == "offline":
        try: await message.delete()
        except: pass

        if user.id in bot.active_sessions:
            start_time = bot.active_sessions[user.id]
            duration = now - start_time

            hours, remainder = divmod(int(duration.total_seconds()), 3600)
            minutes, _ = divmod(remainder, 60)
            duration_str = f"{hours}h {minutes}m"

            embed = discord.Embed(title="Status: OFFLINE", color=0xe74c3c)
            embed.set_author(name=user.display_name, icon_url=user.display_avatar.url)

            embed.add_field(name="Logged In", value=f"<t:{int(start_time.timestamp())}:t>", inline=True)
            embed.add_field(name="Logged Out", value=f"<t:{timestamp}:t>", inline=True)
            embed.add_field(name="Total Session", value=duration_str, inline=False)

            await message.channel.send(embed=embed)
            del bot.active_sessions[user.id]

    await bot.process_commands(message)

# ------------------- READY -------------------

@bot.event
async def on_ready():
    print(f'✅ {bot.user} Deployment Successful!')

# ------------------- RUN -------------------

if __name__ == "__main__":
    keep_alive()
    if TOKEN:
        bot.run(TOKEN)