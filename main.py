import asyncio
import os
import time

import discord
import requests
import yt_dlp as youtube_dl
from discord.ext import commands
from yt_dlp.utils import lowercase_escape

my_secret = os.environ['TOKEN']

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
# Set up the bot with a command prefix
bot = commands.Bot(command_prefix='*', intents=intents)


ffmpeg_path = 'ffmpeg'
# Path to the music folder
music_folder = './songs'
# List all audio files in the music folder (filter out non-audio files)
musicList = [file for file in os.listdir(music_folder) if file.endswith(('.mp3', '.wav', '.m4a'))]

@bot.event
async def on_message(message):
    # Don't let the bot respond to its own messages
    if message.author == bot.user:
        return
        
    # Print the content of the message in the console
    print(f"Message received from {message.author.name}: {message.content}")

    # Make sure to allow commands to work as well
    await bot.process_commands(message)
    
    # Respond to a specific message
    if message.content.lower() == "hello kusa":
        await message.channel.send('Hello, ' + message.author.display_name + '!')


@bot.event
async def on_member_join(member, ctx):
    target_channel = discord.utils.get(ctx.guild.text_channels, name="news")

    if target_channel:
        print(f"{member.name} has joined the server!")
    
@bot.event
async def on_member_remove(member, ctx):
    target_channel = discord.utils.get(ctx.guild.text_channels, name="news")

    if target_channel:
        print(f"{member.name} has left the server.")

@bot.event
async def on_reaction_add(reaction, user):
    if reaction.emoji == "👍":
        await reaction.message.channel.send(f"Thanks {user.name}!")
    if reaction.emoji == "👎":
        await reaction.message.channel.send(f"Sorry {user.name}! 🥺")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        # If the command is not found, inform the user
        await ctx.send("Invalid command. Please check the command and try again.")
    elif isinstance(error, commands.MissingRequiredArgument):
        # If a required argument is missing, inform the user
        await ctx.send("You are missing a required argument. Please provide it.")
    else:
        # For any other errors, you can log or provide a generic message
        await ctx.send("An error occurred while processing the command.")
        print(f"Error: {error}")


# Event for when the bot is ready
@bot.event
async def on_ready():
    print(f'Logged in as {"KUSA"}')

# Command to reply with a greeting
@bot.command()
async def hello(ctx):
    await ctx.send(f"Hello, {ctx.author.display_name}!")

@bot.command()
async def god(ctx):
    await ctx.send("God is good")

@bot.command()
@commands.has_permissions(administrator=True)
async def secret(ctx):
    await ctx.send("This is a secret message only for admins!")

@bot.command()
async def info(ctx):
    id = ctx.guild.id
    guild = ctx.guild.name 
    await ctx.send(f"The server name is {guild} and ID is {id}.")


@bot.command()
async def divide(ctx, num1: int, num2: int):
    try:
        result = num1 / num2
        await ctx.send(f"The result is {result}")
    except ZeroDivisionError:
        await ctx.send("Error: Cannot divide by zero!")
    except ValueError:
        await ctx.send("Error: Please provide valid numbers!")
        
@bot.command()
async def multiply(ctx, num1: int, num2: int):
    try:
        result = num1 * num2
        await ctx.send(f"The result is {result}")
    except ValueError:
        await ctx.send("Error: Please provide valid numbers!")

@bot.command()
async def greet(ctx):
    name = ctx.author.display_name
    
    if name:
        await ctx.send(f"Hello, {name}!")
    else:
        await ctx.send(f"Hello {name}, age not provided!")


@bot.command()
async def join(ctx):
    """Make the bot join the voice channel the user is in."""
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        await channel.connect()
        await ctx.send(f"Joined {channel.name}!")
    else:
        await ctx.send("You need to be in a voice channel for me to join!")

@bot.command()
async def leave(ctx):
    """Make the bot leave the current voice channel."""
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
    else:
        await ctx.send("I'm not in a voice channel!")

# Command to play music
@bot.command()
async def play(ctx, song_name=musicList[0]):   
    # Ensure user is in a voice channel
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        if ctx.voice_client:
            voice = ctx.voice_client
        else:
            voice = await channel.connect()
            await ctx.guild.change_voice_state(channel=channel, self_deaf=True)
        
        # Path to the song file
        song_path = f'./songs/{song_name}'  # Adjust the path if needed

        # Check if file exists
        import os
        if not os.path.exists(song_path):
            await ctx.send(f"Error: {song_name} not found.")
            return

        try:
            # Play audio using FFmpegOpusAudio
            audio_source = discord.FFmpegOpusAudio(song_path)
            voice.play(audio_source)
            await ctx.send(f'Now playing: {song_name}')
        except Exception as e:
            await ctx.send(f"An error occurred: {e}")
            print(f"Error playing audio: {e}")
    else:
        await ctx.send("You need to join a voice channel first.")

@bot.command()
async def listsongs(ctx):

    # List all files in the folder
    try:
        files = os.listdir(music_folder)

        # Filter only music files (e.g., mp3, wav, etc.)
        music_files = [f for f in files if f.endswith(('.mp3', '.m4a', '.ogg', '.flac'))]

        # Check if there are any music files
        if music_files:
            # Create a message with the list of songs
            song_list = "\n".join(music_files)
            await ctx.send(f"Available songs:\n{song_list}")
        else:
            await ctx.send("No songs found in the music folder.")

    except FileNotFoundError:
        await ctx.send(f"Error: The music folder '{music_folder}' was not found.")
    except Exception as e:
        await ctx.send(f"An error occurred: {e}")


# Command to play the next song
@bot.command()
async def next(ctx):
    if ctx.voice_client.is_playing():
        ctx.voice_client.stop()
    
    # Get all music files in the folder
    music_files = musicList

    # If there are no music files
    if not music_files:
        await ctx.send("No music files found.")
        return

    # Get the currently playing song (this assumes you store the last song played)
    current_song = getattr(ctx.voice_client, 'current_song', None)

    # Find the index of the current song
    if current_song:
        try:
            current_index = music_files.index(current_song)
            next_index = (current_index + 1) % len(music_files)  # Loop back to start if at the end
        except ValueError:
            next_index = 0  # Default to the first song if the current song isn't found
    else:
        next_index = 0  # If no song is playing, start with the first song

    # Get the next song
    next_song = music_files[next_index]

    # Check if the bot is already connected to a voice channel
    if not ctx.voice_client:
        if ctx.author.voice:
            channel = ctx.author.voice.channel
            await channel.connect()
        else:
            await ctx.send("You need to join a voice channel first.")
            return
    else:
        # If the bot is already connected, it won't join again
        voice = ctx.voice_client
    # Play the next song
    song_path = os.path.join(music_folder, next_song)
    audio_source = discord.FFmpegOpusAudio(song_path)

    # Play the song
    ctx.voice_client.play(audio_source)
    setattr(ctx.voice_client, 'current_song', next_song)  # Store the current song being played
    await ctx.send(f"Now playing: {next_song}")

@bot.command()
async def playAll(ctx):
    
    # Connect to the voice channel if not connected
    channel = ctx.author.voice.channel
    if not ctx.voice_client:
        voice = await channel.connect()
        await ctx.guild.change_voice_state(channel=channel, self_deaf=True)
        
    else:
        voice = ctx.voice_client
    
    music_files = musicList

    if not music_files:
        await ctx.send("No music files found.")
        return
        
    if ctx.voice_client.is_playing():
        ctx.voice_client.stop()

    
    # Function to play the next song in the list
    async def play_next_song():
        if music_files:
            song = music_files.pop(1)
            song_path = os.path.join(music_folder, song)

            # Play the song
            audio_source = discord.FFmpegOpusAudio(song_path)
            voice.play(audio_source, after=lambda e: bot.loop.create_task(play_next_song()))

            await ctx.send(f"Now playing: {song}")
        else:
            await ctx.voice_client.disconnect()
            await ctx.send("All songs have been played. Disconnecting.")

    # Start playing the first song
    await play_next_song()

  
@bot.command()
async def ping(ctx, member: discord.Member, repeat: int = 1):
    if(member.display_name == "Tsundere"):
        await ctx.send("You can't ping Tsundere!")
    else:
        if(member):
            for i in range(repeat):
                await ctx.send(f"Hello {member.mention}!")
        else:
            await ctx.send("Member invalid!")

@bot.command()
async def dm(ctx, memeber: discord.Member, *, message: str = ""):
    
    if(memeber.display_name != "Tsundere"):
        try:
            # Send a DM to the author of the command
            if(message):
                    await memeber.send(message)
            else:
                await memeber.send("Hello, this message form KUSA! 😘")
                
            await ctx.author.send(f"I sent {memeber.display_name} a DM! With {message}")
        except Exception as e:
            await ctx.send(f"Couldn't send a DM: {e}")
    else:
        await ctx.send("You can't DM Tsundere!")

@bot.command()
async def dmImage(ctx, memeber: discord.Member, url: str, *, message: str = "None"):

    if(memeber.display_name != "Tsundere"):
        try:
            # Send a DM to the author of the command
            if(url):
                await memeber.send(message)
                await memeber.send(url)
            else:
                await memeber.send("Hello, this message form KUSA! 😘")

            await ctx.author.send(f"I sent {memeber.display_name} a DM! With {message} with an image {url}")
        except Exception as e:
            await ctx.send(f"Couldn't send a DM: {e}")
    else:
        await ctx.send("You can't DM Tsundere!")


@bot.command()
async def dmRepeat(ctx, memeber: discord.Member, numbers = 1, *, message: str = ""):
    
    if(memeber.display_name != "Tsundere"):
        try:
            # Send a DM to the author of the command
            if(message):
                for i in range(numbers):
                    await memeber.send(message)
            else:
                await memeber.send("Hello, this message form KUSA! 😘")

            await ctx.author.send(f"I sent {memeber.display_name} a DM! With {message}")
        except Exception as e:
            await ctx.send(f"Couldn't send a DM: {e}")
    else:
        await ctx.send("You can't DM Tsundere!")

@bot.command()
async def playSC(ctx, url: str):
    if ctx.author.voice is None:
        await ctx.send("You need to join a voice channel first!")
        return

    if ctx.voice_client is None:
        channel = ctx.author.voice.channel
        await channel.connect()
        await ctx.guild.change_voice_state(channel=channel, self_deaf=True)
    
    # Additional options to force audio quality and format
    ydl_opts = {
        'format': 'bestaudio/best',  # Prefer the best audio quality available
        'quiet': True,
        'extractaudio': True,  # Only extract the audio
        'audioquality': 1,  # Set audio quality (1 is best)
        'audioformat': 'mp3',  # Ensure the audio format is compatible
    }

    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

            # Extract the audio URL
            audio_url = None
            if info and 'formats' in info:
                for format in info['formats']:
                    if 'url' in format and 'vcodec' in format and format['vcodec'] == 'none':
                        audio_url = format['url']
                        break

            if audio_url is None:
                await ctx.send("No valid audio stream found for this link.")
                return

            # Log the audio URL
            print(f"Audio URL: {audio_url}")

            # Play the audio using FFmpegOpusAudio
            source = discord.FFmpegOpusAudio(audio_url)
            ctx.voice_client.play(source, after=lambda e: print(f"Finished playing: {e}"))

            title = info.get('title', 'Unknown Title') if info else 'Unknown Title'
            await ctx.send(f"Now playing: {title}")

    except Exception as e:
        await ctx.send(f"An error occurred: {e}")
        print(f"Error: {e}")


@bot.command()
async def pause(ctx):
    """Pause the current audio."""
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.pause()
        await ctx.send("Paused the music!")
    else:
        await ctx.send("No music is currently playing!")

@bot.command()
async def resume(ctx):
    """Resume the paused audio."""
    if ctx.voice_client and ctx.voice_client.is_paused():
        ctx.voice_client.resume()
        await ctx.send("Resumed the music!")
    else:
        await ctx.send("No music is currently paused!")

@bot.command()
async def stop(ctx):
    if ctx.voice_client.connect():
        ctx.voice_client.stop()
        ctx.voice_client.disconnect()
        await ctx.send("Music stop.")
        
@bot.command() 
async def sendImage(ctx, url: str): 
    # Send an image using a URL 
    await ctx.send(url) 
    
@bot.command() 
async def sendGif(ctx, url: str): 
    # Send a gif using a URL 
    await ctx.send(url)

download_path = './downloads/'

@bot.command() 
async def download(ctx): 
    # Check if the message has attachments 
    if ctx.message.attachments: 
        for attachment in ctx.message.attachments: 
            file_name = os.path.join(download_path, attachment.filename) 
            # Download the file using requests (synchronous alternative)
            try:
                response = requests.get(attachment.url)
                if response.status_code == 200:
                    with open(file_name, 'wb') as f:
                        f.write(response.content)
                    await ctx.send(f"Downloaded {attachment.filename} to {file_name}")
                else:
                    await ctx.send(f"Failed to download {attachment.filename}")
            except Exception as e:
                await ctx.send(f"Error downloading {attachment.filename}: {e}")
    else: 
        await ctx.send("No attachments found in the message!")

    
# Run the bot with your token
bot.run(my_secret)

