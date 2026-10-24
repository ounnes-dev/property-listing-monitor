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
            last_seen TEXT NOT NULL,
            is_active INTEGER NOT NULL DEFAULT 1
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

    # Migration for existing databases
    cursor.execute("PRAGMA table_info(listings)")
    columns = [row[1] for row in cursor.fetchall()]

    if "is_active" not in columns:
        cursor.execute("""
            ALTER TABLE listings
            ADD COLUMN is_active INTEGER NOT NULL DEFAULT 1
        """)

    connection.commit()
    connection.close()


def save_listing(listing):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO listings (
            id,
            title,
            created_at,
            price,
            slug,
            city,
            transaction_type,
            last_seen,
            is_active
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)
        ON CONFLICT(id) DO UPDATE SET
            title = excluded.title,
            created_at = excluded.created_at,
            price = excluded.price,
            slug = excluded.slug,
            city = excluded.city,
            transaction_type = excluded.transaction_type,
            last_seen = excluded.last_seen,
            is_active = 1
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


def mark_listing_inactive(listing_id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE listings
        SET is_active = 0
        WHERE id = ?
    """, (listing_id,))

    connection.commit()
    connection.close()


def get_all_listings():

    connection = get_connection()
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM listings
        WHERE is_active = 1
    """)

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

    cursor.execute("""
        SELECT *
        FROM events
        ORDER BY timestamp
    """)

    rows = cursor.fetchall()

    connection.close()

    return [dict(row) for row in rows]


def get_events_for_listing(listing_id):

    connection = get_connection()
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM events
        WHERE listing_id = ?
        ORDER BY timestamp DESC, id DESC
    """, (listing_id,))

    rows = cursor.fetchall()

    connection.close()

    return [dict(row) for row in rows]


if __name__ == "__main__":
    create_tables()