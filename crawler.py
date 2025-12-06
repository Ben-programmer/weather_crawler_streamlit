import requests
import json
import sqlite3
from datetime import datetime
from pprint import pprint
import urllib3

# Disable SSL warnings (for Streamlit Cloud deployment)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def fetch_cwa_opendata():
    """
    Fetch weather data from CWA Open Data API.
    
    Note: SSL verification is disabled (verify=False) to handle certificate issues
    in some deployment environments like Streamlit Cloud.
    """
    url = (
        "https://opendata.cwa.gov.tw/fileapi/v1/opendataapi/F-A0010-001"
        "?Authorization=CWA-C9F8E7DB-1FAD-4DB2-BED6-54DD66994740"
        "&downloadType=WEB&format=JSON"
    )

    # Disable SSL verification to avoid certificate errors in cloud environments
    response = requests.get(url, timeout=30, verify=False)
    response.raise_for_status()
    return response.json()


def extract_temperature_table(data):
    """
    Extract daily MaxT and MinT for each location.
    Returns a list of dicts:
    [
      { "location": "北部地區", "date": "2025-12-05", "max": 22, "min": 15 },
      ...
    ]
    """
    forecasts = (
        data["cwaopendata"]["resources"]["resource"]["data"]
        ["agrWeatherForecasts"]["weatherForecasts"]["location"]
    )

    table = []

    for loc in forecasts:
        loc_name = loc["locationName"]
        maxT_list = loc["weatherElements"]["MaxT"]["daily"]
        minT_list = loc["weatherElements"]["MinT"]["daily"]

        # Loop by index (daily data is aligned by date)
        for i in range(len(maxT_list)):
            row = {
                "location": loc_name,
                "date": maxT_list[i]["dataDate"],
                "max_temp": int(maxT_list[i]["temperature"]),
                "min_temp": int(minT_list[i]["temperature"]),
            }
            table.append(row)

    return table


def print_table(table):
    print(f"{'Location':<10} {'Date':<12} {'MaxT':<6} {'MinT':<6}")
    print("-" * 40)
    for row in table:
        print(f"{row['location']:<10} {row['date']:<12} {row['max_temp']:<6} {row['min_temp']:<6}")


def init_database(db_name="sqlitedata.db"):
    """
    Create SQLite database and tables if they don't exist.
    
    Database Schema:
    - weather_forecast: stores temperature forecasts
    - fetch_log: logs when data was fetched
    """
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    # Create weather_forecast table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS weather_forecast (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            location TEXT NOT NULL,
            forecast_date DATE NOT NULL,
            max_temp INTEGER NOT NULL,
            min_temp INTEGER NOT NULL,
            fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(location, forecast_date, fetched_at)
        )
    """)
    
    # Create fetch_log table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fetch_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fetch_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            records_inserted INTEGER,
            status TEXT
        )
    """)
    
    conn.commit()
    conn.close()
    print(f"✓ Database '{db_name}' initialized successfully")


def save_to_database(table, db_name="sqlitedata.db"):
    """
    Save temperature forecast data to SQLite database.
    """
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    inserted_count = 0
    fetched_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    try:
        for row in table:
            cursor.execute("""
                INSERT INTO weather_forecast (location, forecast_date, max_temp, min_temp, fetched_at)
                VALUES (?, ?, ?, ?, ?)
            """, (row['location'], row['date'], row['max_temp'], row['min_temp'], fetched_time))
            inserted_count += 1
        
        # Log the fetch operation
        cursor.execute("""
            INSERT INTO fetch_log (records_inserted, status)
            VALUES (?, ?)
        """, (inserted_count, 'SUCCESS'))
        
        conn.commit()
        print(f"✓ Successfully saved {inserted_count} records to database")
        
    except sqlite3.IntegrityError as e:
        print(f"⚠ Some records already exist (duplicate): {e}")
        conn.rollback()
        
        # Try to log the failed operation
        cursor.execute("""
            INSERT INTO fetch_log (records_inserted, status)
            VALUES (?, ?)
        """, (0, f'FAILED: {str(e)}'))
        conn.commit()
        
    except Exception as e:
        print(f"✗ Error saving to database: {e}")
        conn.rollback()
        
        # Log the error
        cursor.execute("""
            INSERT INTO fetch_log (records_inserted, status)
            VALUES (?, ?)
        """, (0, f'ERROR: {str(e)}'))
        conn.commit()
        
    finally:
        conn.close()


def query_database(db_name="sqlitedata.db"):
    """
    Query and display some statistics from the database.
    """
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    # Get total records
    cursor.execute("SELECT COUNT(*) FROM weather_forecast")
    total = cursor.fetchone()[0]
    print(f"\n📊 Database Statistics:")
    print(f"   Total records: {total}")
    
    # Get latest fetch time
    cursor.execute("SELECT MAX(fetched_at) FROM weather_forecast")
    latest = cursor.fetchone()[0]
    print(f"   Latest fetch: {latest}")
    
    # Get locations
    cursor.execute("SELECT DISTINCT location FROM weather_forecast")
    locations = [row[0] for row in cursor.fetchall()]
    print(f"   Locations: {', '.join(locations)}")
    
    # Show recent records (limit 5)
    print(f"\n📋 Recent Records (Latest 5):")
    cursor.execute("""
        SELECT location, forecast_date, max_temp, min_temp, fetched_at
        FROM weather_forecast
        ORDER BY fetched_at DESC, forecast_date
        LIMIT 5
    """)
    
    print(f"{'Location':<10} {'Date':<12} {'MaxT':<6} {'MinT':<6} {'Fetched At':<20}")
    print("-" * 70)
    for row in cursor.fetchall():
        print(f"{row[0]:<10} {row[1]:<12} {row[2]:<6} {row[3]:<6} {row[4]:<20}")
    
    conn.close()


if __name__ == "__main__":
    DB_NAME = "sqlitedata.db"
    
    # 1. Initialize database
    init_database(DB_NAME)
    
    # 2. Fetch data from CWA API
    print("\n🌐 Fetching data from CWA API...")
    data = fetch_cwa_opendata()
    
    # 3. Extract temperature data
    temp_table = extract_temperature_table(data)
    print(f"✓ Extracted {len(temp_table)} records")
    
    # 4. Display table
    print("\n📊 Temperature Forecast:")
    print_table(temp_table)
    
    # 5. Save to database
    print(f"\n💾 Saving to database...")
    save_to_database(temp_table, DB_NAME)
    
    # 6. Query and show database statistics
    query_database(DB_NAME)
    
    print("\n✅ Process completed!")
