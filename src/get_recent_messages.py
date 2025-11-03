from telethon import TelegramClient
from telethon.tl import functions, types
import os
import argparse
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Read API credentials from environment variables
api_id = os.getenv('TELEGRAM_API_ID')
api_hash = os.getenv('TELEGRAM_API_HASH')

if not api_id or not api_hash:
    raise ValueError("Please set the TELEGRAM_API_ID and TELEGRAM_API_HASH environment variables.")

# Initialize the client
client = TelegramClient('anon', int(api_id), api_hash)

async def get_recent_messages(keyword):
    """
    Searches for public Telegram groups and fetches the 10 most recent messages from each.
    """
    result = await client(functions.contacts.SearchRequest(
        q=keyword,
        limit=10  # Limit the number of groups to avoid being too spammy
    ))

    for chat in result.chats:
        print(f"\n--- Group: {getattr(chat, 'title', 'N/A')} (@{getattr(chat, 'username', 'N/A')}) ---")
        
        try:
            # Get the input entity for the chat to fetch messages
            entity = await client.get_entity(chat)
            messages = await client.get_messages(entity, limit=10)
            
            if not messages:
                print("No recent messages found or history is hidden.")
                continue

            for message in messages:
                sender = await message.get_sender()
                sender_name = getattr(sender, 'username', 'N/A') or getattr(sender, 'first_name', 'N/A')
                print(f"  [{message.date.strftime('%Y-%m-%d %H:%M')}] {sender_name}: {message.text}")

        except Exception as e:
            print(f"Could not retrieve messages for this group. Reason: {e}")

async def main():
    """
    Main function to connect to the client and perform the search.
    """
    parser = argparse.ArgumentParser(description="Search for Telegram groups and get recent messages.")
    parser.add_argument("keyword", type=str, help="The keyword to search for.")
    args = parser.parse_args()

    async with client:
        print(f"Searching for groups with keyword: {args.keyword}")
        await get_recent_messages(args.keyword)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
