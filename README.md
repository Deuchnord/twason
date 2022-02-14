# ![Twason - The KISS Twitch bot](logo.svg)

Twason is an opinionated Twitch chatbot created with the [KISS principle](https://en.wikipedia.org/wiki/KISS_principle) in mind.
It is based on the [IRC](https://en.wikipedia.org/wiki/Internet_Relay_Chat) protocol and is configurable in just one JSON file.

## What the hell is that name!?

Twason is a portmanteau based on two words: _Twitch_ (the platform the bot is designed for) and _Jason_ (as the JSON file that you use to configure it).

## What features does it provide?

Currently, Twason has the following features:

- **Commands:** automatically answer to messages that start with a given command
    - Customizable commands prefix (useful if you're using multiple bots)
    - Mention the user who invoked the command in the answer
    - Help command auto-generation
- **Timer:** automatically send pre-defined messages
    - Only one timer to keep the bot from spamming in the chat
    - Configurable time and number of messages between each automatic message
    - Two strategies available:
        - _round-robin_: send the messages in the same order they have been set in the configuration file
        - _shuffle_: send the messages in a random order

More features will be available in the future.

## How do I use it?

Twason is currently in development and may contain bugs, but it is globally usable. Actually, I'm using it on [my Twitch channel](https://twitch.tv/jdeuchnord).
The simplest (and safest) way to use it is to use the Docker image: [`deuchnord/twason`](https://hub.docker.com/r/deuchnord/twason).
A Docker-Compose file is also available for facility.

### About the Twitch token

To enable the bot to connect to Twitch chat, you will need to generate a token. Head to the [Twitch Chat OAuth Password Generator](https://twitchapps.com/tmi/) and follow the instructions to generate it.
Then, you will need to give it to the bot through the `TWITCH_TOKEN` environment variable.

### The JSON configuration file

To configure the bot, you will need to create a JSON file in `config/config.json` as defined in the `docker-compose.yml` file.
You can find a minimal configuration in the `config.json.dist` file in this repository.

Below is the complete configuration reference:

```json5
{
  "nickname": "yourbot",                        // the Twitch name of your bot
  "channel": "yourchannel",                     // the channel the bot must follow
  "command_prefix": "!",                        // the prefix the commands will have (defaults to '!')
  "help": true,                                 // if true, a help command will be automatically generated (defaults to true)
  "commands": [                                 // a list of commands that your bot will recognize and respond to (empty by default)
    {
      "name": "ping",                           // the command name - spaces are not recommended here (even though they are technically accepted)
      "aliases": ["pong"],
      "message": "Pong @{author} Kappa"         // the message the bot must send when someone invokes this command ('{author}' will be replaced with the user who invoked the command)
    }
  ],
  "timer": {                                    // the configuration of the automatically sent messages
    "between": {
      "time": 10,                               // the minimum time that must have passed between two messages (defaults to 10)
      "messages": 10                            // the minimum number of messages that the chat members must have sent between two messages (defaults to 10)
    },
    "strategy": "round-robin",                  // the strategy used to send the messages: "round-robin" or "shuffle" (defaults to "round-robin")
                                                // the messages are actually commands with the same options as above
    "pool": [                                   // a list of commands to send (empty by default)
      {
        "name": "hello",
        "aliases": ["hi"],
        "message": "Hello World! HeyGuys"
      }
    ]
  },
  "moderator": {
    // The configuration of the moderator (see bellow for more information)
  }
}
```

### The Moderator

Twason has features to help you moderate your chat automatically against most of the nuisance that streamers may face to.
Any moderation feature has to be activated in the configuration in the `moderator` section of the `config.json` file, and have the same options:

```json5
{
  "moderation-feature": { // replace the name with the moderation feature name
    "activate": false, // set this to true to activate the feature
    "decision": "delete", // the action to take: "delete" or "timeout"
    "duration": 5, // if decision is timeout, the duration of the ban, in seconds
    "message": "Calm down, {author}" // this message will be sent in the chat when a member becomes a pain in the ass
  }
}
```

Some moderation features may include more options. In this case, they have to be included in the same way.

The available moderation features are the following:

- `caps-lock`: moderate the messages written in CAPS LOCK
  Additional options:
  - `min-size`: the minimum size of the message to moderate
  - `threshold`: the percentage of capital letters that will trigger the moderation
- `flood`: prevent the members of the chat to flood in your chat
  Additional options:
  - `max-word-length`: the maximum length of a word
  - `ignore-hashtags`: if `true`, don't moderate the hashtags (defaults to `false`)
  - to moderate the unwanted repetition of messages, you will need to add these two options:
    - `max-msg-occurrences`: the number of times a message can be repeated before it gets moderated 
    - `min-time-between-occurrence`: the time in which a message is counted, in seconds
    a member will be moderated if they send `max-msg-occurrences` in `min-time-between-occurrence` seconds
  - `raid-cooldown`: when a raid happens, the time in minutes of cooldown in which the flood is authorized
