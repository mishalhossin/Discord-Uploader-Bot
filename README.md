
# Discord Uploader Bot

<p align="center">
    <img src="https://github.com/mishalhossin/Discord-Uploader-Bot/assets/91066601/f1df760f-690a-4144-8f2c-fb28b18e399c" alt="File Folder">
</p>

This is a Discord bot that allows users to upload files to file hosting service directly from Discord. The bot is written in Python and uses the Discord.py and aiohttp libraries.

## Installation

1. Clone the repository:

   ```
   git clone https://github.com/mishalhossin/Anonfiles-discord-bot.git
   ```

2. Install the required dependencies:

   ```
   pip install -r requirements.txt
   ```


3. Create a `.env` file in the root directory of the project and add your Discord bot token:

   ```
   DISCORD_TOKEN=<your-discord-bot-token>
   ```

4. Run the bot:

   ```
   python bot.py
   ```

## Usage

The bot is triggered by `/upload` slash command command and a file attachment. 

![image](https://github.com/mishalhossin/Discord-Uploader-Bot/assets/91066601/929afe45-908d-428c-b157-51aa1e0f6fbe)

The bot will respond with a message indicating that it is processing the file and will then upload it to Anonfiles. Once the upload is complete, the bot will post a message with the file's URL and other information.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue if you have any suggestions or bug reports.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
