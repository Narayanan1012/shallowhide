import discord
import os
from dotenv import load_dotenv
import google.generativeai as genai
import yt_dlp
import asyncio
import datetime
import re
import pytz

load_dotenv()

FFMPEG_PATH = r"C:\ffmpeg\bin"
discord.FFmpegPCMAudio.executable = FFMPEG_PATH
ffmpeg_options = {'options': '-vn'}

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-pro")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
client = discord.Client(intents=intents)

voice_clients = {}
music_queues = {}
reminders = {}
polls = {}

DEFAULT_TIMEZONE = pytz.timezone("Asia/Kolkata")


def get_youtube_url(song_name):
    search_query = f"ytsearch:{song_name}"
    ydl_opts = {
        "format": "bestaudio/best",
        "noplaylist": True,
        "quiet": True,
        "default_search": "ytsearch",
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(search_query, download=False)
            if "entries" in info and info["entries"]:
                return info["entries"][0]["url"]
            return None
        except Exception as e:
            print(f"Error getting YouTube URL: {e}")
            return None

async def play_next(guild):
    guild_id = guild.id
    if guild_id not in music_queues or not music_queues[guild_id]:
        return

    try:
        next_song = music_queues[guild_id].pop(0)
        voice_client = voice_clients.get(guild_id)

        if voice_client and voice_client.is_connected():
            source = discord.FFmpegPCMAudio(next_song, **ffmpeg_options)
            voice_client.play(source, after=lambda e: asyncio.run_coroutine_threadsafe(play_next(guild), client.loop))
    except Exception as e:
        print(f"Error playing next song: {e}")

async def display_queue(ctx):
    guild_id = ctx.guild.id

    if guild_id not in music_queues or not music_queues[guild_id]:
        await ctx.send("The music queue is currently empty.")
        return

    queue_text = "**Music Queue:**\n"
    for i, song in enumerate(music_queues[guild_id]):
        queue_text += f"{i+1}. {song}\n"

    await ctx.send(queue_text)


async def check_reminders():
    while True:
        now_utc = datetime.datetime.now(pytz.utc)
        to_remove = []

        for user_id, user_reminders in reminders.items():
            for r in user_reminders[:]:
                remind_time, text, channel_id, timezone_str = r
                timezone = pytz.timezone(timezone_str)
                remind_time_utc = remind_time.astimezone(pytz.utc)

                if now_utc >= remind_time_utc:
                    try:
                        channel = client.get_channel(channel_id)
                        if channel:
                            user = await client.fetch_user(user_id)
                            await channel.send(f"⏰ <@{user_id}> Reminder: {text}")
                        user_reminders.remove(r)
                    except discord.HTTPException as e:
                        print(f"Error sending reminder: {e}")
            if not user_reminders:
                to_remove.append(user_id)

        for user_id in to_remove:
            del reminders[user_id]

        await asyncio.sleep(10)


async def set_reminder(user_id, time_str, text, channel_id, timezone=DEFAULT_TIMEZONE):
    try:
        reminder_time = timezone.localize(datetime.datetime.strptime(time_str, "%Y%m%d %H:%M"))

    except ValueError:
        return "Invalid date/time format. Use `YYYYMMDD HH:MM` (24-hour format)."
    except pytz.exceptions.UnknownTimeZoneError:
        return f"Unknown timezone. Using default timezone (IST)."


    now = datetime.datetime.now(pytz.utc)
    if reminder_time < now:
        return "You cannot set a reminder for the past!"

    if user_id not in reminders:
        reminders[user_id] = []

    reminders[user_id].append((reminder_time, text or "Reminder!", channel_id, timezone.zone))

    return f"Reminder set for {reminder_time.strftime('%Y-%m-%d %H:%M %Z')}!"


async def update_poll_embed(poll_id):
    poll_data = polls[poll_id]
    embed = discord.Embed(title=f"{poll_data['question']} (Poll ID: {poll_id})",
                          description="Poll ended!" if poll_data["closed"] else "Cast your vote!",
                          color=discord.Color.green() if poll_data["closed"] else discord.Color.blue())

    total_votes = sum(len(votes) for votes in poll_data["votes"].values())

    for i, option in enumerate(poll_data["options"]):
        votes = poll_data["votes"][option]
        percentage = (len(votes) / total_votes) * 100 if total_votes else 0
        embed.add_field(name=f"{i+1}. {option}", value=f"{len(votes)} votes ({percentage:.2f}%)", inline=False)

    try:
        if poll_data["closed"]:
            await poll_data["message"].edit(embed=embed, view=None)  # Remove buttons
        else:
            await poll_data["message"].edit(embed=embed)
    except discord.errors.NotFound:
        print(f"Message with ID {poll_data['message'].id} not found. Poll may have been deleted.")

@client.event
async def on_ready():
    client.loop.create_task(check_reminders())
    print("We have logged in as {0.user}".format(client))


@client.event
async def on_member_join(member):
    channel = member.guild.system_channel
    if channel:
        await channel.send(f"Welcome, {member.mention}, to the server!")


@client.event
async def on_message(message):
    if message.author == client.user:
        return
    elif message.content.startswith("!hello"):
        await message.channel.send("Hello!")
    elif message.content.startswith("!bye"):
        await message.channel.send("Goodbye have a nice day!")
    elif message.content.lower().startswith("!ask "):
        user_question = message.content[5:]
        if user_question.strip():
            try:
                response = model.generate_content(user_question)
                await message.channel.send(response.text)
            except Exception as e:
                await message.channel.send("Sorry, I couldn't process that request.")
                print(f"Error: {e}")
    elif message.content.startswith("!join"):
        if message.author.voice:
            channel = message.author.voice.channel
            try:
                if message.guild.id not in voice_clients:
                    voice_clients[message.guild.id] = await channel.connect()
                    await message.channel.send(f"Joined {channel.name}!")
                else:
                    await message.channel.send("Already connected to a voice channel!")
            except Exception as e:
                await message.channel.send("Failed to join the voice channel.")
                print(f"Error joining voice channel: {e}")
        else:
            await message.channel.send("You need to be in a voice channel!")
    elif message.content.startswith("!play "):
        if message.author.voice is None or message.guild.id not in voice_clients:
            await message.channel.send("Please join a voice channel and use the `!join` command first.")
            return

        song_name = message.content[6:].strip()
        if song_name:
            youtube_url = get_youtube_url(song_name)
            if youtube_url:
                if message.guild.id not in music_queues:
                    music_queues[message.guild.id] = []

                music_queues[message.guild.id].append(youtube_url)

                await message.channel.send(f"Added **{song_name}** to queue! 🎶")

                if message.guild.id in voice_clients and (voice_clients[message.guild.id] is None or not voice_clients[message.guild.id].is_playing()):
                    await play_next(message.guild)
            else:
                await message.channel.send("Couldn't find that song! Try another name.")

    elif message.content.startswith("!skip"):
        if message.guild.id in voice_clients and voice_clients[message.guild.id].is_playing():
            try:
                voice_clients[message.guild.id].stop()
                await message.channel.send("Skipped current song!")
                await play_next(message.guild)
            except Exception as e:
                await message.channel.send("Failed to skip song.")
                print(f"Error skipping song: {e}")
        else:
            await message.channel.send("No song is currently playing!")
    elif message.content.startswith("!stop"):
        if message.guild.id in voice_clients and voice_clients[message.guild.id].is_playing():
            try:
                voice_clients[message.guild.id].stop()
                music_queues[message.guild.id] = []
                await message.channel.send("Stopped playback and cleared queue!")
            except Exception as e:
                await message.channel.send("Failed to stop music.")
                print(f"Error stopping music: {e}")
        else:
            await message.channel.send("No song is currently playing!")

    elif message.content.startswith("!pause"):
        if message.guild.id in voice_clients and voice_clients[message.guild.id].is_playing():
            try:
                voice_clients[message.guild.id].pause()
                await message.channel.send("Paused music!")
            except Exception as e:
                await message.channel.send("Failed to pause music.")
                print(f"Error pausing music: {e}")

    elif message.content.startswith("!resume"):
        if message.guild.id in voice_clients and voice_clients[message.guild.id].is_paused():
            try:
                voice_clients[message.guild.id].resume()
                await message.channel.send("Resumed music!")
            except Exception as e:
                await message.channel.send("Failed to resume music.")
                print(f"Error resuming music: {e}")
        else:
            await message.channel.send("No song is currently paused!")

    elif message.content.startswith("!queue"):
        await display_queue(message.channel)

    elif message.content.startswith("!remind "):
        try:
            parts = message.content.split(" ", 1)
            if len(parts) < 2:
                await message.channel.send("Usage: `!remind YYYYMMDD HH:MM <reminder_text> [timezone]`")
                return

            reminder_text = parts[1]
            match = re.match(r"(\d{8} \d{2}:\d{2}) (.+?)(?: (\w+/\w+))?$", reminder_text)
            if not match:
                await message.channel.send("Invalid format. Use `YYYYMMDD HH:MM <reminder_text> [timezone]`")
                return

            time_str = match.group(1)
            text = match.group(2).strip()
            timezone_str = match.group(3)

            if timezone_str:
                try:
                    timezone = pytz.timezone(timezone_str)
                except pytz.UnknownTimeZoneError:
                    await message.channel.send("Invalid timezone specified, using IST.")
                    timezone = DEFAULT_TIMEZONE
            else:
                timezone = DEFAULT_TIMEZONE

            response = await set_reminder(message.author.id, time_str, text, message.channel.id, timezone)
            await message.channel.send(response)
        except Exception as e:
            print(f"Error in !remind: {e}")
            await message.channel.send("Failed to process the reminder command.")

    elif message.content.startswith("!reminders"):
        user_id = message.author.id
        if user_id in reminders and reminders[user_id]:
            print(reminders) # Print the reminders for debugging
            if user_id in reminders:
                reminder_list = "\n".join(
                    [f"{i + 1}. {r[0].strftime('%Y-%m-%d %H:%M %Z')} - {r[1]}" for i, r in enumerate(reminders[user_id])]
                )
                await message.channel.send(f"Your reminders:\n{reminder_list}")
            else:
                await message.channel.send("You have no reminders set.")
        else:
            await message.channel.send("You have no reminders set.")

    elif message.content.startswith("!delremind "):
        user_id = message.author.id
        parts = message.content.split(" ")
        if len(parts) != 2 or not parts[1].isdigit():
            await message.channel.send("Usage: `!delremind ID` (Get ID from `!reminders`)")
            return

        index = int(parts[1]) - 1
        if user_id in reminders and 0 <= index < len(reminders[user_id]):
            deleted = reminders[user_id].pop(index)
            await message.channel.send(f"Deleted reminder: {deleted[1]}")
        else:
            await message.channel.send("Invalid ID!")

    elif message.content.startswith("!poll "):

        try:
            poll_text = message.content[6:]
            options = poll_text.split(";")
            question = options[0].strip()
            options = [opt.strip() for opt in options[1:]]

            if not question or not options:
                raise ValueError

            poll_id = str(message.id)
            polls[poll_id] = {
                "question": question,
                "options": options,
                "votes": {option: [] for option in options},
                "creator": message.author.id,
                "closed": False,
                "message": None
            }

            embed = discord.Embed(title=f"{question} (Poll ID: {poll_id})",
                                  description="Cast your vote!", color=discord.Color.blue())
            for i, option in enumerate(options):
                embed.add_field(name=f"{i+1}. {option}", value="0 votes (0%)", inline=False)


            view = discord.ui.View()
            for i, option in enumerate(options):
                button = discord.ui.Button(style=discord.ButtonStyle.primary, label=str(i+1), row=i // 5)
                async def button_callback(interaction: discord.Interaction, opt=option, idx=i, poll_id=poll_id):
                    if polls[poll_id]["closed"]:
                        await interaction.response.send_message("This poll is closed.", ephemeral=True)
                        return

                    user_id = interaction.user.id
                    for op, voters in polls[poll_id]["votes"].items():
                        if user_id in voters:
                            voters.remove(user_id)
                            break

                    polls[poll_id]["votes"][opt].append(user_id)
                    await update_poll_embed(poll_id)
                    await interaction.response.send_message(f"You voted for: {opt}", ephemeral=True)

                button.callback = lambda interaction, opt=option, idx=i, poll_id=poll_id: button_callback(interaction, opt, idx, poll_id)
                view.add_item(button)

            poll_message = await message.channel.send(embed=embed, view=view)
            polls[poll_id]["message"] = poll_message



        except ValueError:
            await message.channel.send("Invalid poll format. Use `!poll Question;Option1;Option2;...`")
        except Exception as e:
            print(f"Error creating poll: {e}")
            await message.channel.send("Failed to create poll.")


    elif message.content.startswith("!closepoll "):

        try:
            poll_id = message.content[11:]

            if poll_id not in polls:
                await message.channel.send("Poll not found.")
                return

            poll_data = polls[poll_id]
            if message.author.id != poll_data["creator"] and not message.author.guild_permissions.administrator:
                await message.channel.send("You are not authorized to close this poll.")
                return


            poll_data["closed"] = True
            await update_poll_embed(poll_id)  # This call does the edit!

            await message.channel.send("Poll closed.")


        except Exception as e:
            print(f"Error closing poll: {e}")
            await message.channel.send("Failed to close poll.")

    elif message.content.startswith("!help"):
        help_text = (
            "**Music Commands:**\n"
            "`!join` - Bot joins your voice channel\n"
            "`!play <song_name>` - Adds a song to the queue\n"
            "`!pause` - Pauses the current song\n"
            "`!resume` - Resumes paused music\n"
            "`!skip` - Skips the current song\n"
            "`!stop` - Stops music and clears queue\n"
            "`!queue` - Shows the current music queue\n\n"
            "**Reminder Commands:**\n"
            "`!remind YYYYMMDD HH:MM <reminder_text> [timezone]` - Sets a reminder (24-hour format, e.g., `!remind 20240315 14:30 Meeting US/Eastern`)\n"
            "`!reminders` - Shows your reminders\n"
            "`!delremind ID` - Deletes a reminder by its ID\n\n"
            "**Poll Commands:**\n"
            "`!poll Question;Option1;Option2;...` - Creates a poll with options (Admin Only)\n"
            "`!closepoll <message_id>` - Closes a poll and freezes the results (Admin Only)\n\n"
            "**Other Commands:**\n"
            "`!hello` - Greets the user\n"
            "`!bye` - Says goodbye\n"
            "`!ask <question>` - Uses AI to answer your question"
        )
        await message.channel.send(help_text)

client.run(os.getenv("TOKEN"))
