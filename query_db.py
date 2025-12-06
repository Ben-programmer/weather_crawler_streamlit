"""
Query script for SQLite database - View weather forecast data
"""
import sqlite3
import sys

DB_NAME = "sqlitedata.db"


def show_all_records():
    """Display all records in the database"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT location, forecast_date, max_temp, min_temp, fetched_at
        FROM weather_forecast
        ORDER BY fetched_at DESC, location, forecast_date
    """)
    
    print(f"\n{'ID':<5} {'Location':<12} {'Date':<12} {'MaxT':<6} {'MinT':<6} {'Fetched At':<20}")
    print("=" * 80)
    
    for idx, row in enumerate(cursor.fetchall(), 1):
        print(f"{idx:<5} {row[0]:<12} {row[1]:<12} {row[2]:<6} {row[3]:<6} {row[4]:<20}")
    
    conn.close()


def show_by_location(location):
    """Display records for a specific location"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT forecast_date, max_temp, min_temp, fetched_at
        FROM weather_forecast
        WHERE location = ?
        ORDER BY forecast_date
    """, (location,))
    
    results = cursor.fetchall()
    
    if results:
        print(f"\n📍 Weather Forecast for: {location}")
        print(f"{'Date':<12} {'MaxT':<6} {'MinT':<6} {'Fetched At':<20}")
        print("-" * 60)
        
        for row in results:
            print(f"{row[0]:<12} {row[1]:<6} {row[2]:<6} {row[3]:<20}")
    else:
        print(f"⚠ No records found for location: {location}")
    
    conn.close()


def show_statistics():
    """Display database statistics"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Total records
    cursor.execute("SELECT COUNT(*) FROM weather_forecast")
    total = cursor.fetchone()[0]
    
    # Locations
    cursor.execute("SELECT DISTINCT location FROM weather_forecast")
    locations = [row[0] for row in cursor.fetchall()]
    
    # Date range
    cursor.execute("SELECT MIN(forecast_date), MAX(forecast_date) FROM weather_forecast")
    date_range = cursor.fetchone()
    
    # Fetch history
    cursor.execute("SELECT COUNT(*), MIN(fetch_time), MAX(fetch_time) FROM fetch_log")
    fetch_info = cursor.fetchone()
    
    print("\n" + "=" * 80)
    print("📊 DATABASE STATISTICS")
    print("=" * 80)
    print(f"Total Records: {total}")
    print(f"Locations: {len(locations)}")
    print(f"  - {', '.join(locations)}")
    print(f"Forecast Date Range: {date_range[0]} to {date_range[1]}")
    print(f"Total Fetches: {fetch_info[0]}")
    print(f"First Fetch: {fetch_info[1]}")
    print(f"Latest Fetch: {fetch_info[2]}")
    
    # Average temperatures by location
    print(f"\n📈 Average Temperatures by Location:")
    cursor.execute("""
        SELECT location, 
               ROUND(AVG(max_temp), 1) as avg_max,
               ROUND(AVG(min_temp), 1) as avg_min
        FROM weather_forecast
        GROUP BY location
        ORDER BY avg_max DESC
    """)
    
    print(f"{'Location':<12} {'Avg MaxT':<10} {'Avg MinT':<10}")
    print("-" * 40)
    for row in cursor.fetchall():
        print(f"{row[0]:<12} {row[1]:<10} {row[2]:<10}")
    
    conn.close()


def show_fetch_log():
    """Display fetch log history"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, fetch_time, records_inserted, status
        FROM fetch_log
        ORDER BY fetch_time DESC
    """)
    
    print(f"\n📝 FETCH LOG HISTORY")
    print(f"{'ID':<5} {'Fetch Time':<20} {'Records':<10} {'Status':<20}")
    print("-" * 70)
    
    for row in cursor.fetchall():
        print(f"{row[0]:<5} {row[1]:<20} {row[2]:<10} {row[3]:<20}")
    
    conn.close()


def main():
    """Main menu"""
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "all":
            show_all_records()
        elif command == "stats":
            show_statistics()
        elif command == "log":
            show_fetch_log()
        elif command == "location" and len(sys.argv) > 2:
            location = sys.argv[2]
            show_by_location(location)
        else:
            print("Invalid command!")
            print_usage()
    else:
        # Default: show statistics
        show_statistics()


def print_usage():
    """Print usage instructions"""
    print("\n" + "=" * 80)
    print("📖 USAGE:")
    print("=" * 80)
    print("python query_db.py              - Show statistics (default)")
    print("python query_db.py stats        - Show statistics")
    print("python query_db.py all          - Show all records")
    print("python query_db.py log          - Show fetch log")
    print("python query_db.py location <name> - Show records for specific location")
    print("\nExample locations: 北部地區, 中部地區, 南部地區, 東北部地區, 東部地區, 東南部地區")
    print("=" * 80)


if __name__ == "__main__":
    try:
        main()
        if len(sys.argv) == 1:
            print_usage()
    except sqlite3.OperationalError as e:
        print(f"✗ Database error: {e}")
        print(f"⚠ Make sure '{DB_NAME}' exists. Run crawler.py first to create it.")
    except Exception as e:
        print(f"✗ Error: {e}")
