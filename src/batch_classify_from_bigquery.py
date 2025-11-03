import asyncio
from google.cloud import bigquery
from telethon import TelegramClient
import os
import sys
from dotenv import load_dotenv
from datetime import datetime

# Add project root to the Python path to allow for absolute imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.classify_groups import get_and_classify_groups

# Load environment variables from .env file
load_dotenv()

# Read API credentials from environment variables
api_id = os.getenv('TELEGRAM_API_ID')
api_hash = os.getenv('TELEGRAM_API_HASH')

async def main():
    """
    Fetches keywords from BigQuery, runs the Telegram group classification,
    and saves the results to another BigQuery table.
    """
    # Initialize BigQuery client
    try:
        bq_client = bigquery.Client()
        print("Successfully connected to BigQuery.")
    except Exception as e:
        print(f"Could not connect to BigQuery. Please ensure you have authenticated. Error: {e}")
        return

    # --- 1. Fetch existing group IDs from the target table to avoid duplicates ---
    target_table_id = "pwcnext-sandbox01.telegram.groups"
    try:
        query = f"SELECT group_id FROM `{target_table_id}`"
        existing_group_ids = {row.group_id for row in bq_client.query(query).result()}
        print(f"Found {len(existing_group_ids)} existing groups in the target table.")
    except Exception as e:
        print(f"Could not fetch existing group IDs from {target_table_id}. Error: {e}")
        # Decide if you want to continue without this check. For safety, we'll exit.
        return

    # --- 2. Fetch keywords to process ---
    try:
        query = """
            SELECT DISTINCT keys_group
            FROM `pwcnext-sandbox01.telegram.keys`
            WHERE keys_group IS NOT NULL
        """
        print("Fetching keywords from BigQuery...")
        keywords = [row.keys_group for row in bq_client.query(query).result()]
        print(f"Found {len(keywords)} keywords to process.")
    except Exception as e:
        print(f"Failed to fetch keywords from BigQuery. Error: {e}")
        return

    if not keywords:
        print("No keywords found in the BigQuery table. Exiting.")
        return

    # --- 3. Process keywords and collect new group data ---
    all_new_groups = []
    if not api_id or not api_hash:
        raise ValueError("Please set the TELEGRAM_API_ID and TELEGRAM_API_HASH environment variables.")

    client = TelegramClient('anon', int(api_id), api_hash)
    async with client:
        for keyword in keywords:
            print(f"\n{'='*20} Processing keyword: {keyword} {'='*20}")
            classified_groups = await get_and_classify_groups(client, keyword)
            
            for group in classified_groups:
                if group['group_id'] not in existing_group_ids:
                    group['last_fetch_time'] = datetime.utcnow().isoformat()
                    all_new_groups.append(group)
                    existing_group_ids.add(group['group_id']) # Add to set to avoid duplicates in the same run
                    print(f"  New group found: {group['group_name']}. Queued for insertion.")
                else:
                    print(f"  Group '{group['group_name']}' already exists. Skipping.")
            
            await asyncio.sleep(5)

    # --- 4. Insert new groups into BigQuery ---
    if not all_new_groups:
        print("\nNo new groups to add to BigQuery.")
        return

    print(f"\nAttempting to insert {len(all_new_groups)} new groups into BigQuery...")
    try:
        errors = bq_client.insert_rows_json(target_table_id, all_new_groups)
        if not errors:
            print("Successfully inserted all new groups.")
        else:
            print("Encountered errors while inserting rows:")
            for error in errors:
                print(error)
    except Exception as e:
        print(f"An error occurred during BigQuery insertion: {e}")

if __name__ == "__main__":
    asyncio.run(main())
