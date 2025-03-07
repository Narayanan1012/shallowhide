# Shallowhide
# Discord Bot with Music, Reminders, Polls, and AI Features

This Discord bot provides music playback, reminders, polls, and AI-powered question answering. It uses the `discord.py` library for interacting with Discord, `yt-dlp` for fetching YouTube audio, and Google's Generative AI for answering questions. Below is an overview of the bot's features, setup instructions, and potential next steps for improvement.

## Features

### Music
Allows users to play music from YouTube in a voice channel. The bot manages a queue system and provides basic playback controls.

### Reminders
Enables users to set reminders for specific dates and times. The bot periodically checks and notifies users of their reminders.

### Polls
Allows users to create polls with multiple options. Users can vote using reactions, and results can be retrieved later.

### AI Integration
Uses Google's Generative AI to answer user questions, making the bot an interactive assistant.

### General Commands
Includes utility and fun commands such as greetings and a help menu.

## Commands

### Music Commands
- `!join` - Joins the user's voice channel.
- `!play <song_name>` - Adds a song to the queue and starts playback.
- `!pause` - Pauses the current song.
- `!resume` - Resumes playback of a paused song.
- `!skip` - Skips the current song and plays the next in the queue.
- `!stop` - Stops playback and clears the queue.

### Reminder Commands
- `!remind YYYY-MM-DD HH:MM Your reminder` - Sets a reminder for a specific date and time.
- `!reminders` - Lists all active reminders for the user.
- `!delremind ID` - Deletes a reminder by its ID.

### Poll Commands
- `!poll "Question" Option1 Option2 [Option3 ...]` - Starts a poll with the given question and options.
- `!vote <option_number>` - Casts a vote for the specified option in an active poll.
- `!pollresult` - Displays the results of the latest poll.

### AI Commands
- `!ask <question>` - Uses Google's Generative AI to answer questions.

### Other Commands
- `!hello` - Greets the user.
- `!bye` - Says goodbye.
- `!help` - Displays a list of available commands.

## Setup Instructions

### Create a Discord Bot Application
1. Go to the [Discord Developer Portal](https://discord.com/developers/applications).
2. Click "New Application" and give it a name.
3. Navigate to "Bot" in the left menu and click "Add Bot."
4. Enable the necessary permissions under the "OAuth2" and "Bot" sections.
5. Copy the bot token from the "Bot" section for later use.

### Prerequisites
Ensure you have the following installed:
- Python 3.8+
- `ffmpeg` for music streaming
- `pip` for installing dependencies

### Install Dependencies
Run the following command to install required libraries:
```sh
pip install discord.py python-dotenv google-generativeai yt-dlp asyncio datetime pytz
```

### Setting Up `ffmpeg`
The bot requires `ffmpeg` for music playback. Follow these steps to set it up:
1. Download `ffmpeg` from [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html).
2. Extract the contents and locate the `bin` folder.
3. Copy the full path to `ffmpeg.exe` inside the `bin` folder.
4. Add the path to the system environment variables:
   - Open "System Properties" and go to the "Advanced" tab.
   - Click "Environment Variables."
   - Under "System Variables," find "Path" and click "Edit."
   - Click "New" and paste the full path to the `bin` folder.
   - Click "OK" to save and exit.
5. Restart your system for the changes to take effect.
6. Verify installation by running:
   ```sh
   ffmpeg -version
   ```
   If installed correctly, this command should display version details.

### Set Up Environment Variables
Create a `.env` file in the project directory and add the following:
```sh
TOKEN=your_discord_bot_token
GEMINI_API_KEY=your_google_gemini_api_key
```

### Running the Bot
Execute the following command to start the bot:
```sh
python main.py
```

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

### 4. Polls
- Added a poll system allowing users to create and vote on polls.
- Used reactions to collect votes on poll options.
- Implemented commands to cast votes and retrieve poll results.

### 5. AI Integration
- Integrated Google's Generative AI (`gemini-1.5-pro`) to answer user questions.
- Added error handling for API requests.

### 6. Error Handling
- Added error handling for invalid inputs, API failures, and edge cases (e.g., past reminders, invalid URLs).

## Required Discord Bot Permissions
The bot requires the following permissions for proper functionality:
- **Read Messages** - Allows the bot to read commands.
- **Send Messages** - Allows the bot to respond to users.
- **Connect & Speak** - Required for joining and streaming audio in voice channels.
- **Embed Links** - Allows the bot to send enhanced messages.
- **Add Reactions** - Needed for poll voting.

## Next Steps

### 1. Improved Music Features
- Implement crossfading between songs for smooth transitions.
- Add volume control commands.
- Support adding full playlists to the queue.

### 2. Study Mode with Pomodoro
- Add commands to start a Pomodoro timer (e.g., `!pomodoro start`).
- Enable a study mode that plays relaxing music (e.g., lo-fi beats).
- Implement break reminders.

### 3. Advanced Reminders
- Allow users to set recurring reminders (e.g., daily, weekly).
- Implement a snooze option for reminders.

### 4. AI Enhancements
- Enable contextual memory for more interactive conversations.
- Allow users to customize the AI's behavior with specific prompts.

### 5. User Preferences
- Implement personalized settings (e.g., default volume, preferred music genre).
- Add support for saving and loading playlists.

### 6. Error Handling and Logging
- Implement detailed logs for tracking errors and user interactions.
- Provide more informative error messages for users.

### 7. UI Improvements
- Use Discord embeds for better-looking command responses.
- Implement interactive menus for commands like `!help`, `!reminders`, and `!polls`.

### 8. Deployment
- Host the bot on a cloud platform (e.g., AWS, Heroku) for 24/7 availability.
- Ensure environment variables are securely managed.

## Conclusion
This bot provides a versatile solution for Discord servers, offering music playback, reminders, polls, and AI-powered features. With further development, it can become a more powerful and user-friendly assistant. Suggestions and contributions are welcome.

