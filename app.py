import os
import psycopg2
from datetime import datetime, timezone
from dotenv import load_dotenv
from flask import Flask, request

CREATE_ROOMS_TABLE = (
    "CREATE TABLE IF NOT EXISTS rooms (id SERIAL PRIMARY KEY, name TEXT)"
)

CREATE_TEMP_TABLE = """CREATE TABLE IF NOT EXISTS temperatures (room_id INTEGER, temperature REAL, date TIMESTAMP, FOREIGN KEY (room_id) REFERENCES rooms (id) ON DELETE CASCADE);"""

INSERT_ROOM_RETURN_ID = "INSERT INTO rooms (name) VALUES (%s) RETURNING id;"
INSERT_TEMP = (
    "INSERT INTO temperatures (room_id, temperature, date) VALUES (%s, %s, %s);"
)

GLOBAL_NUMBER_OF_DAYS = (
    """SELECT COUNT(DISTINCT DATE(date)) AS days FROM temperatures;"""
)

GLOBAL_AVG = (
    """SELECT AVG(temperature) AS average FROM temperatures;"""
)

app = Flask(__name__)
url = os.getenv("DATABASE_URL")
connection = psycopg2.connect(url)


@app.get("/")
def home():
    return {
        "data": "Hallo World!"
    }


@app.post("/api/room")
def create_room():
    data = request.get_json()
    name = data["name"]
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(CREATE_ROOMS_TABLE)
            cursor.execute(INSERT_ROOM_RETURN_ID, (name,))
            room_id = cursor.fetchone()[0]
    return {
        "id": room_id,
        "message": f"Room {name} created successfully"
    }, 201


@app.post("/api/temperature")
def add_temp():
    data = request.get_json()
    temperature = data["temperature"]
    room_id = data["room"]
    try:
        date = datetime.strptime(data["date"], "%m-%d-%Y %H:%M:%S")
    except KeyError:
        date = datetime.now(timezone.utc)

    with connection.cursor() as cursor:
        cursor.execute(CREATE_TEMP_TABLE)
        cursor.execute(INSERT_TEMP, (room_id, temperature, date))
    return {
        "message": "Temperature added successfully"
    }, 201


@app.get("/api/average")
def get_global_avg():
    with connection.cursor() as cursor:
        cursor.execute(GLOBAL_AVG)
        average = cursor.fetchone()[0]
        cursor.execute(GLOBAL_NUMBER_OF_DAYS)
        days = cursor.fetchone()[0]
    return {
        "average": round(average, 2),
        "days": days
    }, 201
