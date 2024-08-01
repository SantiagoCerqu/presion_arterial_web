import os
import psycopg2
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for
import psycopg2.extras
from datetime import datetime

# Load the global variables
load_dotenv()

app = Flask(__name__)
# Get the connection string and connect to the database
conn_string = os.getenv("DATABASE_INFO")
conn = psycopg2.connect(conn_string)

INSERT_USER = """
    INSERT INTO users (username, first_name, last_name, birthdate)
    VALUES (%s, %s, %s, %s) RETURNING id;
"""

INSERT_MEDICAL_RECORD = """
    INSERT INTO medical_records (user_id, event_date, event_time, systolic_pressure, diastolic_pressure, heart_rate, saturation, observations)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
"""

SELECT_ALL_USERS = """
    SELECT * FROM users;
"""

SELECT_USER = """
    SELECT * FROM users WHERE id = (%s);
"""

SELECT_RECORDS = """
    SELECT MR.* FROM medical_records AS MR 
    INNER JOIN users AS U ON MR.user_id = U.id
    WHERE U.id = (%s)
    ORDER BY MR.event_date DESC, MR.event_time DESC;
"""



@app.route("/")
def index():
    # Get and display all users
    with conn:
        # Create cursor as dictionary
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            cursor.execute(SELECT_ALL_USERS)
            users = cursor.fetchall()

    return render_template("index.html", users=users)

@app.route("/new_user", methods=["GET","POST"])
def new_user():
    if request.method == "POST":
        # Save the user data in variables, capitalize all user data
        username = request.form.get("username")
        first_name = request.form.get("f_name").title()
        last_name = request.form.get("l_name").title()
        birthdate = request.form.get("birthdate")

        # If user didnt put any information in the form
        if not username or not first_name or not last_name or not birthdate:
            return render_template("error.html", error_message="User not created, provide all user data")
        
        # Insert data in the database
        with conn:
            with conn.cursor() as cursor:
                cursor.execute(INSERT_USER, (username, first_name, last_name, birthdate,))
        return render_template("new_user.html", message=f"User {username} created successfully!!")
    
    # If request.method is GET
    return render_template("new_user.html")



@app.route("/view_records/<int:user_id>", methods=["GET","POST"])
def view_records(user_id):
    if request.method == "POST":
        # Store values
        event_date = request.form.get("event_date")
        event_time = request.form.get("event_time")
        systolic = request.form.get("systolic")
        diastolic = request.form.get("diastolic")
        heart_rate = request.form.get("heart_rate")
        saturation = request.form.get("saturation")
        observations = request.form.get("observations")

        if not event_date or not event_time or not systolic or not diastolic or not heart_rate or not saturation:
            return render_template("error.html", error_message="Record not created, provide all input data")
        
        # Date and Time Server validation
        try:
            event_date = datetime.strptime(event_date, "%Y-%m-%d").date()
            event_time = datetime.strptime(event_time, "%H:%M").time()
        except ValueError:
            return render_template("error.html", error_message="Incorrect Date or Time.")
        
        # Check if the values are integers
        try:
            systolic = int(systolic)
            diastolic = int(diastolic)
            heart_rate = int(heart_rate)
            saturation = int(saturation)
        except ValueError: 
            return render_template("error.html", error_message="Numbers must be integers.")
        
        # Insert data into the Database
        with conn:
            with conn.cursor() as cursor:
                cursor.execute(INSERT_MEDICAL_RECORD, (
                    user_id,
                    event_date,
                    event_time,
                    systolic,
                    diastolic,
                    heart_rate,
                    saturation,
                    observations,
                ))
        
        return redirect(url_for("view_records", user_id=user_id))

    
    # Get the user information and medical records for a single user
    with conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            # Get user info
            cursor.execute(SELECT_USER, (user_id,))
            user = cursor.fetchone()
            # Get all medical records 
            cursor.execute(SELECT_RECORDS, (user_id,))
            medical_records = cursor.fetchall()

    return render_template("view_records.html", user=user, medical_records=medical_records)



