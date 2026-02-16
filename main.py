import discord
from discord.ext import commands
from datetime import datetime
import os
from flask import Flask
from threading import Thread

# --- RENDER PORT FIX (KEEP ALIVE) ---
app = Flask('')

@app.route('/')
def home():
    return "Aries Bot is Online!"

def run_flask():
    # Render default port 8080 use karta hai
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()

# --- BOT CONFIGURATION ---
# IMPORTANT: Use your actual Token here
TOKEN = "MTQ3MjkwODE3MjczMjY2NTg1Nw.Gd4-sj.RM_jIcoGU1Kme9Kz7T8OtxioktnnrQ_kaqzF8Q" 
TARGET_SERVER_ID = 770004215678369883
TARGET_CHANNEL_ID = 1426247870495068343

class AriesBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = True 
        super().__init__(command_prefix="!", intents=intents)
        self.active_sessions = {}
        self.start_time = datetime.now()

bot = AriesBot()

@bot.event
async def on_ready():
    print(f'✅ Logged in as: {bot.user}')
    print(f'🛡️ Secured for Server: {TARGET_SERVER_ID}')

@bot.event
async def on_message(message):
    if message.author == bot.user: return
    if message.guild is None or message.guild.id != TARGET_SERVER_ID: return
    if message.channel.id != TARGET_CHANNEL_ID: return

    content = message.content.lower().strip()
    user = message.author
    now = datetime.now()
    time_str = now.strftime("%I:%M %p")

    # --- ONLINE TRIGGER ---
    if content == "online":
        try: await message.delete()
        except: pass

        if user.id not in bot.active_sessions:
            bot.active_sessions[user.id] = now
            embed = discord.Embed(
                title="Status: ONLINE",
                description=f"✅ {user.mention} has started their session.",
                color=0x2ecc71
            )
            embed.add_field(name="Login Time", value=f"🕒 `{time_str}`")
            embed.set_thumbnail(url=user.display_avatar.url)
            await message.channel.send(embed=embed)
        else:
            await message.channel.send(f"⚠️ {user.mention}, you are already online!", delete_after=5)

    # --- OFFLINE TRIGGER ---
    elif content == "offline":
        try: await message.delete()
        except: pass

        if user.id in bot.active_sessions:
            start_time = bot.active_sessions[user.id]
            duration = now - start_time
            
            hours, remainder = divmod(int(duration.total_seconds()), 3600)
            minutes, _ = divmod(remainder, 60)
            duration_str = f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m"

            embed = discord.Embed(
                title="Status: OFFLINE",
                description=f"🔴 {user.mention} has ended their session.",
                color=0xe74c3c
            )
            embed.add_field(name="Logged In", value=start_time.strftime("%I:%M %p"), inline=True)
            embed.add_field(name="Logged Out", value=time_str, inline=True)
            embed.add_field(name="Total Session", value=f"⏳ `{duration_str}`", inline=False)
            embed.set_thumbnail(url=user.display_avatar.url)
            
            await message.channel.send(embed=embed)
            del bot.active_sessions[user.id]
        else:
            await message.channel.send(f"❓ {user.mention}, you were not marked online.", delete_after=5)

    await bot.process_commands(message)

# --- INSPECTION COMMAND ---
@bot.command()
@commands.has_permissions(administrator=True)
async def inspect(ctx):
    uptime = datetime.now() - bot.start_time
    latency = round(bot.latency * 1000)
    embed = discord.Embed(title="🔍 Bot Health Inspection", color=0xf1c40f)
    embed.add_field(name="Status", value="🟢 Online", inline=True)
    embed.add_field(name="Ping", value=f"`{latency}ms`", inline=True)
    embed.add_field(name="Active Users", value=f"`{len(bot.active_sessions)}`", inline=True)
    await ctx.send(embed=embed)

# --- START BOT ---
if __name__ == "__main__":
    keep_alive() # Flask server starts here
    try:
        bot.run(TOKEN)
    except discord.errors.LoginFailure:
        print("❌ Error: Invalid Token. Please reset your token in Discord Developer Portal.")
