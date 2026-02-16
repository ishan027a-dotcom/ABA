import discord
from discord.ext import commands
from datetime import datetime
import os
from flask import Flask
from threading import Thread

# --- RENDER PORT FIX ---
app = Flask('')

@app.route('/')
def home():
    return "Aries Bot is Online & Secure!"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()

# --- BOT CONFIGURATION ---
# IMPORTANT: Token ab environment variable se aayega
TOKEN = os.getenv("DISCORD_TOKEN") 

TARGET_SERVER_ID = 770004215678369883
TARGET_CHANNEL_ID = 1426247870495068343

class AriesBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = True 
        super().__init__(command_prefix="!", intents=intents)
        self.active_sessions = {}

bot = AriesBot()

@bot.event
async def on_ready():
    print(f'✅ Logged in as: {bot.user}')
    print('🔒 Security: Token loaded from Environment Variables')
    print('⏰ Time Sync: Using Discord Dynamic Timestamps')

@bot.event
async def on_message(message):
    if message.author == bot.user: return
    if message.guild is None or message.guild.id != TARGET_SERVER_ID: return
    if message.channel.id != TARGET_CHANNEL_ID: return

    content = message.content.lower().strip()
    user = message.author
    now = datetime.utcnow() 
    timestamp = int(now.timestamp()) 

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
            embed.add_field(name="Login Time", value=f"🕒 <t:{timestamp}:t>")
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
            embed.add_field(name="Logged In", value=f"<t:{int(start_time.timestamp())}:t>", inline=True)
            embed.add_field(name="Logged Out", value=f"<t:{timestamp}:t>", inline=True)
            embed.add_field(name="Total Session", value=f"⏳ `{duration_str}`", inline=False)
            embed.set_thumbnail(url=user.display_avatar.url)
            
            await message.channel.send(embed=embed)
            del bot.active_sessions[user.id]
        else:
            await message.channel.send(f"❓ {user.mention}, you were not marked online.", delete_after=5)

    await bot.process_commands(message)

# --- ADMIN LIST COMMAND ---
@bot.command()
@commands.has_permissions(administrator=True)
async def list(ctx):
    if not bot.active_sessions:
        await ctx.send("Empty list: No users are currently online.")
        return

    embed = discord.Embed(title="👥 Current Online Members", color=0x3498db)
    user_list = ""
    for user_id, start_time in bot.active_sessions.items():
        user = ctx.guild.get_member(user_id)
        name = user.display_name if user else f"User ID: {user_id}"
        user_list += f"• **{name}** (Started: <t:{int(start_time.timestamp())}:R>)\n"

    embed.add_field(name="Active Sessions", value=user_list, inline=False)
    await ctx.send(embed=embed)

if __name__ == "__main__":
    keep_alive()
    if TOKEN:
        bot.run(TOKEN)
    else:
        print("❌ ERROR: DISCORD_TOKEN is missing in Render settings!")
