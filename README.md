# KUSA — Discord Bot

An asynchronous Python Discord bot built with `discord.py`, featuring voice-channel integration, local music playback, media URL playback, and server utilities.

## Features

- Event-driven commands and message/reaction handlers
- Voice channel connection and disconnection
- Local audio playback with FFmpeg, song listing, pause and resume
- Audio stream extraction with yt-dlp for permitted media sources
- Server information, arithmetic commands, and administrator-only command example
- Attachment handling and command error reporting

## Setup

Install Python 3, FFmpeg (available on PATH), and the Python dependencies:

```sh
python -m pip install -r requirements.txt
```

Create a bot in the [Discord Developer Portal](https://discord.com/developers/applications). Configure its message-content intent and grant only the permissions needed for your test server. Set the `TOKEN` environment variable locally using your shell; never commit the actual token. The `.env.example` is a configuration reference only; the original script does not automatically load dotenv files.

Create `songs/` and `downloads/` locally. The original script requires at least one supported local audio file in `songs/` at startup. Use audio you have permission to play.

## Development status

This repository preserves the original learning project. Syntax was checked, but the bot has not been connected to Discord or tested end-to-end. Before deployment, review member-event signatures, empty-library startup, playback state, blocking network calls, attachment path handling, message logging, and unrestricted direct-message/mention commands. Disable or restrict potentially disruptive commands and apply rate limits and consent controls. Do not deploy the original script unchanged on a public server.

## Engineering concepts

Asynchronous programming, API integration, event handlers, dependency management, media processing, error handling, environment-based configuration, and access control.
