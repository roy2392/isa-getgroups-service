"""
Backfill script to populate group_link for existing groups in BigQuery.
Fetches username from Telegram API and updates the table.
"""
from google.cloud import bigquery, secretmanager
from telethon import TelegramClient
from telethon.tl import functions
import os
import asyncio

from src.config import BIGQUERY_GROUPS_TABLE

# Get the project root directory for session file
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SESSION_PATH = os.path.join(PROJECT_ROOT, 'anon')


def get_secret(project_id, secret_id, version_id="latest"):
    """Retrieves a secret from Google Secret Manager."""
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")


async def backfill_group_links():
    """Fetch group usernames from Telegram and update BigQuery."""

    project_id = os.environ.get('GCP_PROJECT_ID')
    if not project_id:
        raise ValueError("GCP_PROJECT_ID environment variable not set.")

    print("Fetching secrets...")
    api_id = get_secret(project_id, "telegram-api-id")
    api_hash = get_secret(project_id, "telegram-api-hash")

    bq_client = bigquery.Client()

    # Fetch groups without group_link
    query = f"""
        SELECT group_id, group_name
        FROM `{BIGQUERY_GROUPS_TABLE}`
        WHERE group_link IS NULL
    """
    print("Fetching groups without group_link...")
    rows = list(bq_client.query(query).result())
    print(f"Found {len(rows)} groups to update.")

    if not rows:
        print("No groups need updating.")
        return

    client = TelegramClient(SESSION_PATH, int(api_id), api_hash)

    await client.connect()
    if not await client.is_user_authorized():
        print("ERROR: Telegram session not authorized. Please run the app interactively first.")
        return

    try:
        for row in rows:
            group_id = row.group_id
            group_name = row.group_name

            try:
                # Search for the group by name to find its username
                result = await client(functions.contacts.SearchRequest(
                    q=group_name,
                    limit=10
                ))

                # Find matching chat by ID
                username = None
                for chat in result.chats:
                    if str(chat.id) == group_id:
                        username = getattr(chat, 'username', None)
                        break

                if username:
                    group_link = f"https://t.me/{username}"
                    update_query = f"""
                        UPDATE `{BIGQUERY_GROUPS_TABLE}`
                        SET group_link = '{group_link}'
                        WHERE group_id = '{group_id}'
                    """
                    bq_client.query(update_query).result()
                    print(f"✓ Updated '{group_name}' -> {group_link}")
                else:
                    print(f"✗ No username found for '{group_name}' (ID: {group_id})")

                await asyncio.sleep(1)  # Rate limiting

            except Exception as e:
                print(f"✗ Error processing '{group_name}' (ID: {group_id}): {e}")
    finally:
        await client.disconnect()


if __name__ == "__main__":
    asyncio.run(backfill_group_links())
