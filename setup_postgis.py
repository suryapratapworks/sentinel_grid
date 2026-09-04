import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

db_url = os.getenv("DATABASE_URL")

try:
    if db_url:
        conn = psycopg2.connect(db_url)
    else:
        conn = psycopg2.connect(
            dbname=os.getenv("POSTGRES_DB", "sentinel_grid"),
            user=os.getenv("POSTGRES_USER", "postgres"),
            password=os.getenv("POSTGRES_PASSWORD", "postgres"),
            host=os.getenv("POSTGRES_HOST", "localhost"),
            port=int(os.getenv("POSTGRES_PORT", 5432))
        )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    
    # Try enabling postgis
    try:
        cur.execute("CREATE EXTENSION IF NOT EXISTS postgis;")
        cur.execute("SELECT PostGIS_Version();")
        version = cur.fetchone()[0]
        print(f"SUCCESS: PostGIS extension enabled! Version: {version}")
    except Exception as ext_err:
        print(f"PostGIS Extension Note: {ext_err}")
        print("Testing spatial queries using native PostgreSQL geometric / trigonometric spatial math...")
    
    # Verify spatial geometry calculations (e.g. ST_Distance or Haversine function)
    cur.execute("""
        -- Create a custom spatial distance function if PostGIS isn't installed in the PostgreSQL distribution
        CREATE OR REPLACE FUNCTION calculate_distance_km(
            lat1 double precision, lon1 double precision,
            lat2 double precision, lon2 double precision
        ) RETURNS double precision AS $$
        DECLARE
            r double precision := 6371; -- Earth radius in km
            dlat double precision := radians(lat2 - lat1);
            dlon double precision := radians(lon2 - lon1);
            a double precision;
            c double precision;
        BEGIN
            a := sin(dlat/2)^2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)^2;
            c := 2 * atan2(sqrt(a), sqrt(1-a));
            RETURN r * c;
        END;
        $$ LANGUAGE plpgsql IMMUTABLE;
    """)
    print("Spatial calculation function calculate_distance_km(lat1, lon1, lat2, lon2) created successfully!")
    
    # Test spatial distance between Delhi coordinates
    cur.execute("SELECT calculate_distance_km(28.6139, 77.2090, 28.6328, 77.2195);")
    dist = cur.fetchone()[0]
    print(f"Spatial Test Distance: {dist:.3f} km")
    
    cur.close()
    conn.close()
except Exception as e:
    print("Database connection error:", e)