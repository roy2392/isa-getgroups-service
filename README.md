# Telegram Group and Message Retrieval Service

This project provides Python scripts to interact with the Telegram API for searching public groups and retrieving recent messages from them.

## Setup

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/your-username/isa-getgroups-service.git
    cd isa-getgroups-service
    ```

2.  **Create and configure the `.env` file:**

    Copy the `.env.example` file to `.env` and fill in your Telegram API credentials.

    ```bash
    cp .env.example .env
    ```

    Open the newly created `.env` file and replace `YOUR_API_ID` and `YOUR_API_HASH` with your actual Telegram API credentials. You can obtain these from [my.telegram.org/apps](https://my.telegram.org/apps). You will also need to add your `GEMINI_API_KEY`.

    ```
    TELEGRAM_API_ID=21722549
    TELEGRAM_API_HASH=YOUR_API_HASH
    GEMINI_API_KEY=YOUR_GEMINI_API_KEY
    ```

3.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

## Usage

### 1. Search for Telegram Groups by Keyword

This script searches for public Telegram groups and channels based on a provided keyword.

```bash
python src/search_telegram_groups.py "your_keyword"
```

Replace `"your_keyword"` with the term you want to search for (e.g., "מניות").

### 2. Get Recent Messages from Groups by Keyword

This script first searches for public Telegram groups based on a keyword and then retrieves the 10 most recent messages from each found group.

```bash
python src/get_recent_messages.py "your_keyword"
```

Replace `"your_keyword"` with the term you want to search for.

### 3. Classify Group Relevance with Gemini

This script uses the Gemini API to classify whether a group is relevant to a given keyword based on its recent messages.

```bash
python src/classify_groups.py "your_keyword"
```

Replace `"your_keyword"` with the term you want to search for.