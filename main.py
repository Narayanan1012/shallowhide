import discord
import os
from dotenv import load_dotenv
import google.generativeai as genai
import yt_dlp
import asyncio
import datetime
import re

FFMPEG_PATH = r"C:\ffmpeg\bin"
discord.FFmpegPCMAudio.executable = FFMPEG_PATH
ffmpeg_options = {
    'options': '-vn'
}
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-pro")
intents = discord.Intents.default()
intents.message_content = True 
client = discord.Client(intents=intents)
voice_clients = {}  
music_queues = {}
reminders = {}

def get_youtube_url(song_name):
    search_query = f"ytsearch:{song_name}"
    ydl_opts = {
        "format": "bestaudio/best",
        "noplaylist": True,
        "quiet": True,
        "default_search": "ytsearch",
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(search_query, download=False)
        if "entries" in info and info["entries"]:
            return info["entries"][0]["url"]
        return None

async def play_next(guild):
    guild_id = guild.id
    if guild_id not in music_queues or not music_queues[guild_id]:
        return

    next_song = music_queues[guild_id].pop(0)
    voice_client = voice_clients.get(guild_id)

    if voice_client and voice_client.is_connected():
        voice_client.play(discord.FFmpegPCMAudio(next_song), after=lambda e: asyncio.run_coroutine_threadsafe(play_next(guild), client.loop))

async def check_reminders():
    while True:
        now = datetime.datetime.now()
        to_remove = []
        for user_id, user_reminders in reminders.items():
            for r in user_reminders[:]:
                remind_time, text, channel_id = r
                if now >= remind_time:
                    user = await client.fetch_user(user_id)
                    channel = client.get_channel(channel_id)
                    if channel:
                        await channel.send(f"⏰ <@{user_id}> Reminder: {text}")
                    user_reminders.remove(r)
            if not user_reminders:
                to_remove.append(user_id)
        for user_id in to_remove:
            del reminders[user_id]
        await asyncio.sleep(60)

async def set_reminder(user_id, time_str, text, channel_id):
    time_str = time_str.strip()
    match = re.match(r"(\d{4}-\d{2}-\d{2}) (\d{2}:\d{2})", time_str)
    if not match:
        return "Invalid format! Use `YYYY-MM-DD HH:MM`"

    date_part, time_part = match.groups()
    try:
        remind_time = datetime.datetime.strptime(f"{date_part} {time_part}", "%Y-%m-%d %H:%M")
        if remind_time < datetime.datetime.now():
            return "You cannot set a reminder for the past!"

        if user_id not in reminders:
            reminders[user_id] = []
        reminders[user_id].append((remind_time, text, channel_id))
        return f"Reminder set for {remind_time.strftime('%Y-%m-%d %H:%M')}!"
    except ValueError:
        return "Invalid date or time!"

if __name__ == "__main__":
    @client.event
    async def on_ready():
        print("We have logged in as {0.user}".format(client))
        client.loop.create_task(check_reminders())

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
                if message.guild.id not in voice_clients:  
                    voice_clients[message.guild.id] = await channel.connect()
                    await message.channel.send(f"Joined {channel.name}!")
                else:
                    await message.channel.send("Already connected to a voice channel!")
            else:
                await message.channel.send("You need to be in a voice channel!")
        elif message.content.startswith("!play "):
            song_name = message.content[6:].strip()
            if song_name:
                youtube_url = get_youtube_url(song_name)
                if youtube_url:
                    if message.guild.id not in music_queues:
                        music_queues[message.guild.id] = []
                    
                    music_queues[message.guild.id].append(youtube_url)
                    
                    await message.channel.send(f"Added **{song_name}** to queue! 🎶")

                    if not voice_clients[message.guild.id].is_playing():
                        await play_next(message.guild)
                else:
                    await message.channel.send("Couldn't find that song! Try another name.")

        elif message.content.startswith("!skip"):
            if message.guild.id in voice_clients and voice_clients[message.guild.id].is_playing():
                voice_clients[message.guild.id].stop()
                await message.channel.send("Skipped current song!")
                await play_next(message.guild)
            else:
                await message.channel.send("No song is currently playing!")
        elif message.content.startswith("!stop"):
            if message.guild.id in voice_clients and voice_clients[message.guild.id].is_playing():
                voice_clients[message.guild.id].stop()
                music_queues[message.guild.id] = []
                await message.channel.send("Stopped playback and cleared queue!")
            else:
                await message.channel.send("No song is currently playing!")
        elif message.content.startswith("!pause"):
            if message.guild.id in voice_clients and voice_clients[message.guild.id].is_playing():
                voice_clients[message.guild.id].pause()
                await message.channel.send("Paused music!")
            else:
                await message.channel.send("No song is currently playing!")

        elif message.content.startswith("!resume"):
            if message.guild.id in voice_clients and voice_clients[message.guild.id].is_paused():
                voice_clients[message.guild.id].resume()
                await message.channel.send("Resumed music!")
            else:
                await message.channel.send("No song is currently paused!")
        elif message.content.startswith("!remind "):
            parts = message.content.split(" ", 2)
            if len(parts) < 3:
                await message.channel.send("Usage: `!remind YYYY-MM-DD HH:MM Your reminder`")
            else:
                response = await set_reminder(message.author.id, parts[1], parts[2], message.channel.id)
                await message.channel.send(response)

        elif message.content.startswith("!reminders"):
            user_id = message.author.id
            if user_id in reminders and reminders[user_id]:
                reminder_list = "\n".join(
                    [f"{i+1}. {r[0].strftime('%Y-%m-%d %H:%M')} - {r[1]}" for i, r in enumerate(reminders[user_id])]
                )
                await message.channel.send(f"Your reminders:\n{reminder_list}")
            else:
                await message.channel.send("You have no reminders set.")

        elif message.content.startswith("!delremind "):
            user_id = message.author.id
            parts = message.content.split(" ")
            if len(parts) != 2 or not parts[1].isdigit():
                await message.channel.send("Usage: `!delremind ID` (Get ID from `!reminders`)")
            else:
                index = int(parts[1]) - 1
                if user_id in reminders and 0 <= index < len(reminders[user_id]):
                    deleted = reminders[user_id].pop(index)
                    await message.channel.send(f"Deleted reminder: {deleted[1]}")
                else:
                    await message.channel.send("Invalid ID!")
        elif message.content.startswith("!help"):
            help_text = (
                "**Music Commands:**\n"
                "`!join` - Bot joins your voice channel\n"
                "`!play <song_name>` - Adds a song to the queue\n"
                "`!pause` - Pauses the current song\n"
                "`!resume` - Resumes paused music\n"
                "`!skip` - Skips the current song\n"
                "`!stop` - Stops music and leaves channel\n\n"
                "**Reminder Commands:**\n"
                "`!remind YYYY-MM-DD HH:MM Your reminder` - Sets a reminder\n"
                "`!reminders` - Shows your reminders\n"
                "`!delremind ID` - Deletes a reminder\n\n"
                "**Other Commands:**\n"
                "`!hello` - Greets the user\n"
                "`!bye` - Says goodbye\n"
                "`!ask <question>` - Uses AI to answer your question"
            )
            await message.channel.send(help_text)

    client.run(os.getenv("TOKEN"))