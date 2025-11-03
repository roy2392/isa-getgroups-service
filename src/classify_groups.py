from telethon import TelegramClient
from telethon.tl import functions
import os
import argparse
from dotenv import load_dotenv
import google.generativeai as genai
import json

# Load environment variables from .env file
load_dotenv()

# Read API credentials from environment variables
api_id = os.getenv('TELEGRAM_API_ID')
api_hash = os.getenv('TELEGRAM_API_HASH')
gemini_api_key = os.getenv('GEMINI_API_KEY')

if not api_id or not api_hash:
    raise ValueError("Please set the TELEGRAM_API_ID and TELEGRAM_API_HASH environment variables.")

if not gemini_api_key:
    raise ValueError("Please set the GEMINI_API_KEY environment variable.")

# Initialize the Telegram client
client = TelegramClient('anon', int(api_id), api_hash)

# Configure the Gemini API
genai.configure(api_key=gemini_api_key)
model = genai.GenerativeModel('gemini-2.5-flash')

async def classify_group_relevance(keyword, messages):
    """
    Classifies if a group is relevant to a keyword based on its recent messages.
    """
    if not messages:
        return None, "No messages to analyze."

    message_texts = [msg.text for msg in messages if msg.text]
    if not message_texts:
        return None, "No text in recent messages."

    prompt = f"""
    Based on the following messages from a Telegram group, is the group relevant to the keyword '{keyword}'?
    Please provide your answer in JSON format with two keys: "is_relevant" (boolean) and "explanation" (a brief string).

    Messages:
    - {'\n- '.join(message_texts)}
    """

    try:
        response = model.generate_content(prompt)
        # Clean the response to ensure it's valid JSON
        cleaned_response = response.text.strip().replace('`', '').replace('json', '')
        result = json.loads(cleaned_response)
        return result.get('is_relevant'), result.get('explanation', 'No explanation provided.')
    except (json.JSONDecodeError, AttributeError, KeyError) as e:
        print(f"  Error parsing Gemini response: {e}")
        return None, "Could not determine relevance."
    except Exception as e:
        print(f"  Error classifying group: {e}")
        return None, "An unexpected error occurred during classification."


async def get_and_classify_groups(client, keyword):
    """
    Searches for public Telegram groups, fetches recent messages, and classifies them.
    """
    classified_groups = []
    result = await client(functions.contacts.SearchRequest(
        q=keyword,
        limit=10
    ))

    for chat in result.chats:
        group_title = getattr(chat, 'title', 'N/A')
        group_username = getattr(chat, 'username', 'N/A')
        print(f"\n--- Processing Group: {group_title} (@{group_username}) ---")

        try:
            entity = await client.get_entity(chat)
            messages = await client.get_messages(entity, limit=10)

            if not messages:
                print("  No recent messages found or history is hidden.")
                relevance, explanation = False, "No messages available for analysis."
            else:
                relevance, explanation = await classify_group_relevance(keyword, messages)

            group_data = {
                "group_id": str(chat.id),
                "group_name": group_title,
                "is_relevant": relevance,
                "why_relavent": explanation
            }
            classified_groups.append(group_data)
            print(f"  Relevant to '{keyword}': {relevance}")
            print(f"  Explanation: {explanation}")

        except Exception as e:
            print(f"  Could not process group. Reason: {e}")
    
    return classified_groups

async def main():
    """
    Main function to connect to the client and perform the search and classification.
    """
    parser = argparse.ArgumentParser(description="Search and classify Telegram groups.")
    parser.add_argument("keyword", type=str, help="The keyword to search for.")
    args = parser.parse_args()

    async with client:
        print(f"Searching and classifying groups with keyword: {args.keyword}")
        results = await get_and_classify_groups(client, args.keyword)
        print("\n--- Classification Results ---")
        print(json.dumps(results, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
