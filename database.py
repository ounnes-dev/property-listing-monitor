import sqlite3


DATABASE_NAME = "property_monitor.db"


def get_connection():
    return sqlite3.connect(DATABASE_NAME)


def create_tables():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS listings (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            created_at TEXT,
            price REAL,
            slug TEXT,
            city TEXT,
            transaction_type TEXT,
            last_seen TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            event_type TEXT NOT NULL,
            listing_id TEXT NOT NULL,
            title TEXT NOT NULL,
            old_price REAL,
            new_price REAL,
            city TEXT
        )
    """)

    connection.commit()
    connection.close()

def save_listing(listing):
    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        INSERT OR REPLACE INTO listings (
            id,
            title,
            created_at,
            price,
            slug,
            city,
            transaction_type,
            last_seen
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        listing["id"],
        listing["title"],
        listing["created_at"],
        listing["price"],
        listing["slug"],
        listing["city"],
        listing["transaction_type"],
        listing["last_seen"]
    ))

    connection.commit()
    connection.close()

def get_all_listings():

    connection = get_connection()

    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    cursor.execute("SELECT * FROM listings")

    rows = cursor.fetchall()

    connection.close()

    return [dict(row) for row in rows]

def get_listing_by_id(listing_id):
    connection = get_connection()
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM listings WHERE id = ?",
        (listing_id,)
    )

    row = cursor.fetchone()

    connection.close()

    if row is None:
        return None

    return dict(row)

def save_event(event_type, listing_id, title, old_price, new_price, city, timestamp):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO events (
            timestamp,
            event_type,
            listing_id,
            title,
            old_price,
            new_price,
            city
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        timestamp,
        event_type,
        listing_id,
        title,
        old_price,
        new_price,
        city
    ))

    connection.commit()
    connection.close()

def get_events():
    connection = get_connection()
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM events ORDER BY timestamp")

    rows = cursor.fetchall()

    connection.close()

    return [dict(row) for row in rows]    

if __name__ == "__main__":
    create_tables()