import psycopg2
"""

paciente (nombres, apellido, fecha de nacimiento)
registro (fecha, hora, presion_sistolica, presion_diastolica, pulsaciones, saturacion)
"""

# Create connection object
conn_string = "dbname='presion_arterial' user='postgres' host='localhost'  port='5432'"
conn = psycopg2.connect(conn_string)

# Create cursor object
cursor = conn.cursor()

# Create patients and medical_records tables
cursor.execute("""
    
    -- Drop tables if exist
    -- DROP TABLE users CASCADE;
    -- DROP TABLE medical_records CASCADE;
    
    
    -- Create tables
    CREATE TABLE IF NOT EXISTS users(
        id serial PRIMARY KEY,
        username VARCHAR(50) NOT NULL UNIQUE,
        first_name VARCHAR(50) NOT NULL,
        last_name VARCHAR(50) NOT NULL,
        birthdate DATE NOT NULL
    );
               
    CREATE TABLE IF NOT EXISTS medical_records(
        id serial PRIMARY KEY,
        user_id INT,
        event_date DATE UNIQUE,
        event_time TIME CHECK (event_time >= '00:00:00' AND event_time <= '23:59:59'),
        systolic_pressure INTEGER,
        diastolic_pressure INTEGER,
        heart_rate INTEGER,
        saturation INTEGER,
        observations VARCHAR(100),
        FOREIGN KEY(user_id) REFERENCES users(id)
    );
""")




# Commit changes
conn.commit()

# Close cursor and connection
cursor.close()
conn.close()




