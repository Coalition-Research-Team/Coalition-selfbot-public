import os
from src.discord_bot import CoalitionBot


# Clear console screen
def clear_terminal():
    os.system("cls" if os.name == "nt" else "clear")




prefixes = ['!']

def main():
    from dotenv import load_dotenv
    load_dotenv('.env')
    
    token = os.environ.get("DISCORD_TOKEN")
    if not token:
        print("No token found in environment variables.")
        return
    
    bot = CoalitionBot(prefixes=prefixes, self_bot=True)
    # Add more commands here as needed...
    print(token)
    # asyncio.create_task(run_gui())        
    bot.run(token)


if __name__ == "__main__":
    main()
