# ![Twason - The KISS Twitch bot](logo.svg)

Twason is an opinionated Twitch chatbot created with the [KISS principle](https://en.wikipedia.org/wiki/KISS_principle) in mind.
It is based on the [IRC](https://en.wikipedia.org/wiki/Internet_Relay_Chat) protocol and is configurable in just one JSON file.

## What the hell is that name!?

Twason is a portmanteau based on two words: _Twitch_ (the platform the bot is designed for) and _Jason_ (as the JSON file that you use to wonfigure it).

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
You can have an interface to create and validate your config file ![here](https://json-editor.github.io/json-editor/?data=N4Ig9gDgLglmB2BnEAuUMDGCA2MBGqIAZglAIYDuApomALZUCsIANOHgFZUZQD62ZAJ5gArlELwwAJzplsrEIgwALKrNSgAJEtXqUIZVCgREKAPRmOteAFodasgDppAczMATKWSJQzAJgAGQJsARj8ze3U2TRh3QkNjUwt3KhEVSSl3RyIpMygKMmtHSKcrBAVYKGwqQgAVAusFFKUpGGg4eEIAQQACLHgiGBceweqR6R6oVUmKGCgVHrwwKB76wvK2KEEIGv0wTm5xNggpSCopWBoNEHhMAGt4MgZr5oxW9vL9WunbjAenqg9MBEHrCERSRbLCrbXaKKCteAuEAAXzYKjI8HgVHkaBAr3esE+IG+gMeDCBILBEPRmOx0J2hEQ8JgiJRaPosng7l4JyogwAHi8aG82oTOvoAApSPkwfl9DkY9wU0GiFZLI4gLYM/RMhFI1EGbEQIUtUUdQgAYQxKpEPTIPBgADcyFBAVNAapsBB5XROUqAPz02FLMDVDFskBYX2K5C4/FmokAGRgTOVVJ9fqDhDIUi8ggUczUsdAWth+y4PAUJzOFxgV1xZN2oHjH3FIAAcgDle6M4qszrmayDXIYIV683hQTzfourmhMqR4VxtSFVz+yAc3mC666MXNTDGYP9QaGIhEGQXE28ZOE22ALI0c+X5VRzObA8DvUog3SgCOIhgaU4hQABtG4AQURdECuNhTyfGoAF0DREW5/yoABJHdY01KQRBqA1YAYKQTRFVtuncJVpQwDBwSoeAVkVO0xHoF1MB6OCLxqd9tXYCsNWrHZa3HEA8CofIqDo65S0IctDirU5BMuPdCKvaT9HgEQ6FE4i2CofkMGwERECdKg7xZGA6E01AAhPR9OOUj8QBZV1Lx0kA9IMoyTLM25LLoazkR/Kh/0AqhgLAlSFA4y9kCQthdRdKgXHzOMbzI/QAFVoKBLEegSlzBEmMAehOZz2LsmL111FkkV0jT/NAkBThQ9wbFOPAWQURBlBEIgiGqEA4pACAwFDEipyTFMVmBG0V2jNduNhTchG3IspMc2TK2OBTziU65G3G29CE7ckZp7V8+0Ww8v2HXAxz3FsxW6OdCpmqDl17Bb9x45b8zYQtd3WnjqqHWyz04w70pAB9wefGaLq+tS4RuoKQqA1AwIOtgoJgkBosQ5DULwzC1v0eE8O/Ng/wA9HGtE8TJPi+FEuSqtRvkJDUZpsKMZue4scjZQMSxeR2Xm7leQFBRPWNIburACheHOU4pGw5zzntJ7Nl0YNRqgBKIAAFm/IA=). 

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
  }
}
```
