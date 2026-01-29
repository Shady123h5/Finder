# Discord Message Forwarder Bot

## Overview

This is a Discord bot that monitors a specific channel and forwards all messages to a webhook destination. The bot captures message content, author information, embeds, and attachments, then relays them via Discord webhook to another channel or server.

The primary use case is cross-server or cross-channel message mirroring, allowing messages from one Discord channel to appear in another location automatically.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Bot Framework
- **Technology**: Python with discord.py library
- **Pattern**: Event-driven architecture using Discord gateway events
- **Rationale**: discord.py provides a clean async interface for Discord's API, making it straightforward to listen for and react to messages

### Message Handling
- **Approach**: Single-channel monitoring with webhook forwarding
- **Flow**: Bot receives message event → filters by channel ID → constructs webhook payload → sends via HTTP POST
- **Message Components Handled**:
  - Text content
  - Author name and avatar
  - Embedded content (preserves Discord embed structure)
  - File attachments (converted to URL links)

### Configuration
- **Current State**: Hardcoded values in source file
- **Recommendation**: Should migrate to environment variables for security (TOKEN, WEBHOOK_URL, CHANNEL_ID contain sensitive data)

### Project Structure Note
The repository contains both Python and Node.js configuration files, but only the Python bot (`main.py`) contains actual application logic. The `index.js` is empty and `package.json` only has TypeScript type definitions - these appear to be remnants or placeholders and are not part of the functional application.

## External Dependencies

### Discord API
- **Discord Gateway**: Used for real-time message events via discord.py client
- **Discord Webhooks**: HTTP endpoint for forwarding messages to destination channel
- **Authentication**: Bot token required for gateway connection

### Python Libraries
- **discord.py**: Discord API wrapper for Python (not in requirements file - needs to be installed)
- **requests**: HTTP library for webhook POST requests (not in requirements file - needs to be installed)

### Missing Configuration
A `requirements.txt` file should be created with:
```
discord.py
requests
```

### Security Concern
The bot token and webhook URL are currently exposed in the source code. These should be moved to environment variables using `os.environ.get()` or a `.env` file with python-dotenv.