from telethon import TelegramClient
from telethon.tl import functions
import os
import argparse

# Read API credentials from environment variables
api_id = os.getenv('TELEGRAM_API_ID')
api_hash = os.getenv('TELEGRAM_API_HASH')

if not api_id or not api_hash:
    raise ValueError("Please set the TELEGRAM_API_ID and TELEGRAM_API_HASH environment variables.")

# Initialize the client
client = TelegramClient('anon', int(api_id), api_hash)

async def search_public_groups(keyword):
    """
    Searches for public Telegram groups and channels based on a keyword.
    """
    result = await client(functions.contacts.SearchRequest(
        q=keyword,
        limit=100  # Maximum number of results
    ))

    for chat in result.chats:
        print(f"ID: {chat.id}, Title: {getattr(chat, 'title', None)}, Username: @{getattr(chat, 'username', None)}")

async def main():
    """
    Main function to connect to the client and perform the search.
    """
    parser = argparse.ArgumentParser(description="Search for Telegram groups by keyword.")
    parser.add_argument("keyword", type=str, help="The keyword to search for.")
    args = parser.parse_args()

    async with client:
        print(f"Searching for groups with keyword: {args.keyword}")
        await search_public_groups(args.keyword)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
