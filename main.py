@bot.event
async def on_message(message):
    try:
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

        # -------- ONLINE --------
        if content == "online":
            try: await message.delete()
            except: pass

            if user.id not in bot.active_sessions:
                bot.active_sessions[user.id] = now

                if is_leader:
                    desc = f"🛡️ **Leader {user.display_name} is now monitoring operations.**"
                    color = 0xf1c40f
                else:
                    desc = f"✅ **{user.display_name}** has started their duty session."
                    color = 0x2ecc71

                embed = discord.Embed(
                    title="🟢 STATUS: ONLINE",
                    description=desc,
                    color=color
                )
                embed.set_thumbnail(url=user.display_avatar.url)
                embed.add_field(name="Arrival Time", value=f"<t:{timestamp}:t>", inline=True)
                embed.set_footer(text="Aries Attendance System")

                await message.channel.send(embed=embed)

        # -------- OFFLINE --------
        elif content == "offline":
            try: await message.delete()
            except: pass

            if user.id in bot.active_sessions:
                start_time = bot.active_sessions[user.id]
                duration = now - start_time

                hours, remainder = divmod(int(duration.total_seconds()), 3600)
                minutes, _ = divmod(remainder, 60)
                duration_str = f"{hours}h {minutes}m" if hours else f"{minutes}m"

                if is_leader:
                    desc = f"🌑 **Leader {user.display_name} has gone off-duty.**"
                    color = 0x2f3136
                else:
                    desc = f"🔴 **{user.display_name}** session ended."
                    color = 0xe74c3c

                embed = discord.Embed(
                    title="🔴 STATUS: OFFLINE",
                    description=desc,
                    color=color
                )
                embed.set_thumbnail(url=user.display_avatar.url)
                embed.add_field(name="Logged In", value=f"<t:{int(start_time.timestamp())}:t>", inline=True)
                embed.add_field(name="Logged Out", value=f"<t:{timestamp}:t>", inline=True)
                embed.add_field(name="Total Session", value=f"⏳ {duration_str}", inline=False)
                embed.set_footer(text="Aries Attendance System")

                await message.channel.send(embed=embed)
                del bot.active_sessions[user.id]

        await bot.process_commands(message)

    except Exception as e:
        print("⚠️ Runtime Error:", e)