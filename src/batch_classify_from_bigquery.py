from google.cloud import bigquery, secretmanager
from telethon import TelegramClient
import os
import sys
from datetime import datetime
import google.generativeai as genai
import time
import asyncio

# Add project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.classify_groups import get_and_classify_groups
from src.config import BIGQUERY_KEYS_TABLE, BIGQUERY_GROUPS_TABLE, INSERT_ONLY_RELEVANT_GROUPS

# --- Secret Manager Helper ---
def get_secret(project_id, secret_id, version_id="latest"):
    """
    Retrieves a secret from Google Secret Manager.
    """
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")

# --- Main Application Logic ---
async def main():
    """
    Fetches keywords from BigQuery, runs classification, and saves results.
    """
    # --- 1. Load Configuration and Secrets ---
    project_id = os.environ.get('GCP_PROJECT_ID')
    if not project_id:
        raise ValueError("GCP_PROJECT_ID environment variable not set.")

    print("Fetching secrets from Secret Manager...")
    try:
        api_id = get_secret(project_id, "telegram-api-id")
        api_hash = get_secret(project_id, "telegram-api-hash")
        gemini_api_key = get_secret(project_id, "gemini-api-key")
    except Exception as e:
        print(f"Failed to fetch secrets. Ensure they are created and permissions are set. Error: {e}")
        return

    # Configure Gemini API
    genai.configure(api_key=gemini_api_key)

    # --- 2. Initialize BigQuery Client ---
    try:
        bq_client = bigquery.Client()
        print("Successfully connected to BigQuery.")
    except Exception as e:
        print(f"Could not connect to BigQuery. Error: {e}")
        return

    # --- 3. Fetch existing group IDs ---
    try:
        query = f"SELECT group_id FROM `{BIGQUERY_GROUPS_TABLE}`"
        existing_group_ids = {row.group_id for row in bq_client.query(query).result()}
        print(f"Found {len(existing_group_ids)} existing groups in the target table.")
    except Exception as e:
        print(f"Could not fetch existing group IDs. Error: {e}")
        return

    # --- 4. Fetch keywords to process ---
    try:
        query = f"SELECT DISTINCT keys_group FROM `{BIGQUERY_KEYS_TABLE}` WHERE keys_group IS NOT NULL"
        print("Fetching keywords from BigQuery...")
        keywords = [row.keys_group for row in bq_client.query(query).result()]
        print(f"Found {len(keywords)} keywords to process.")
    except Exception as e:
        print(f"Failed to fetch keywords from BigQuery. Error: {e}")
        return

    if not keywords:
        print("No keywords found. Exiting.")
        return

    # --- 5. Process keywords ---
    all_new_groups = []
    client = TelegramClient('anon', int(api_id), api_hash)
    
    async with client:
        for keyword in keywords:
            print(f"\n{'='*20} Processing keyword: {keyword} {'='*20}")
            classified_groups = await get_and_classify_groups(client, keyword)
            
            for group in classified_groups:
                if group['group_id'] not in existing_group_ids:
                    if INSERT_ONLY_RELEVANT_GROUPS and not group['is_relevant']:
                        print(f"  Group '{group['group_name']}' is not relevant. Skipping.")
                        continue
                    
                    group['last_fetch_time'] = datetime.utcnow().isoformat()
                    all_new_groups.append(group)
                    existing_group_ids.add(group['group_id'])
                    print(f"  New group found: {group['group_name']}. Queued for insertion.")
                else:
                    print(f"  Group '{group['group_name']}' already exists. Skipping.")
            
            await asyncio.sleep(5)

    # --- 6. Insert new groups into BigQuery ---
    if not all_new_groups:
        print("\nNo new groups to add to BigQuery.")
        return

    print(f"\nAttempting to insert {len(all_new_groups)} new groups into BigQuery...")
    try:
        errors = bq_client.insert_rows_json(BIGQUERY_GROUPS_TABLE, all_new_groups)
        if not errors:
            print("Successfully inserted all new groups.")
        else:
            print(f"Encountered errors while inserting rows: {errors}")
    except Exception as e:
        print(f"An error occurred during BigQuery insertion: {e}")

if __name__ == "__main__":
    # This allows running the script locally if you have `gcloud` authenticated
    # and the GCP_PROJECT_ID env var is set.
    asyncio.run(main())
