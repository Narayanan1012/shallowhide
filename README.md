#Shallowhide
# Discord Bot with Music, Reminders, and AI Features

This Discord bot provides music playback, reminders, and AI-powered question answering. It utilizes `discord.py` for interacting with Discord, `yt-dlp` for fetching YouTube audio, and Google's Generative AI for answering questions. Below is an overview of the bot's features, the process followed to build it, and potential next steps for improvement.

## Features

### Music Commands
- `!join`: Joins the user's voice channel.
- `!play <song_name>`: Adds a song to the queue and starts playback.
- `!pause`: Pauses the current song.
- `!resume`: Resumes playback of a paused song.
- `!skip`: Skips the current song and plays the next in the queue.
- `!stop`: Stops playback and clears the queue.

### Reminder Commands
- `!remind YYYY-MM-DD HH:MM Your reminder`: Sets a reminder for a specific date and time.
- `!reminders`: Lists all active reminders for the user.
- `!delremind ID`: Deletes a reminder by its ID.

### AI Commands
- `!ask <question>`: Uses Google's Generative AI to answer questions.

### Other Commands
- `!hello`: Greets the user.
- `!bye`: Says goodbye.
- `!help`: Displays a list of available commands.

## Process

### 1. Setting Up the Bot
- Created a Discord bot application and obtained the bot token.
- Used `discord.py` to handle bot interactions and events.
- Configured intents to allow the bot to read message content.

### 2. Music Playback
- Integrated `yt-dlp` to fetch YouTube audio URLs based on song names.
- Implemented a queue system to manage playback of multiple songs.
- Used `discord.FFmpegPCMAudio` to stream audio to voice channels.
- Added commands for play, pause, resume, skip, and stop.

### 3. Reminders
- Created a reminder system using a dictionary to store reminders for each user.
- Used `datetime` to parse and compare reminder times.
- Implemented a background task (`check_reminders`) to check and trigger reminders periodically.

### 4. AI Integration
- Integrated Google's Generative AI (`gemini-1.5-pro`) to answer user questions.
- Added error handling for API requests.

### 5. Error Handling
- Added error handling for invalid inputs, API failures, and edge cases (e.g., past reminders, invalid URLs).

## Next Steps

### 1. Smooth Music Playback
- **Crossfade Between Songs**: Implement crossfading to ensure smooth transitions between songs.
- **Volume Control**: Add a command to adjust playback volume.
- **Playlist Support**: Allow users to add entire playlists to the queue.

### 2. Study Mode with Pomodoro
- **Pomodoro Timer**: Add commands to start a Pomodoro timer (e.g., `!pomodoro start`).
- **Study Mode**: Enable a study mode that plays relaxing music (e.g., lo-fi beats) and blocks distractions.
- **Break Reminders**: Notify users when it's time to take a break.

### 3. Advanced Reminders
- **Recurring Reminders**: Allow users to set recurring reminders (e.g., daily, weekly).
- **Snooze Option**: Add a snooze feature for reminders.

### 4. AI Enhancements
- **Contextual Memory**: Enable the AI to remember previous interactions with the user.
- **Custom Prompts**: Allow users to customize the AI's behavior with specific prompts.

### 5. User Preferences
- **Personalized Settings**: Allow users to set preferences (e.g., default volume, preferred music genre).
- **Save Playlists**: Let users save and load playlists.

### 6. Error Handling and Logging
- **Detailed Logs**: Implement logging to track errors and user interactions.
- **User Feedback**: Provide more informative error messages for users.

### 7. UI Improvements
- **Embed Messages**: Use Discord embeds for better-looking command responses.
- **Interactive Menus**: Add interactive menus for commands like `!help` and `!reminders`.

### 8. Deployment
- **Host the Bot**: Deploy the bot on a cloud platform (e.g., AWS, Heroku) for 24/7 availability.
- **Environment Variables**: Use `.env` files to manage sensitive data like API keys and tokens.

## How to Run the Bot

### Install Dependencies:
```bash
pip install discord.py python-dotenv google-generativeai yt-dlp
```

### Set Up Environment Variables:
Create a `.env` file with the following variables:
```plaintext
TOKEN=your_discord_bot_token
GEMINI_API_KEY=your_google_gemini_api_key
```

### Run the Bot:
```bash
python bot.py
```

## Conclusion
This bot is a versatile tool for Discord servers, offering music playback, reminders, and AI-powered features. With further development, it can become an even more powerful and user-friendly assistant. Feel free to contribute or suggest improvements!

