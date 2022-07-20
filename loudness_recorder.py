import pyaudio
import audioop
import psycopg2
from datetime import datetime


CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
RECORD_SECONDS = 20
WAVE_OUTPUT_FILENAME = "output.wav"

database_name = 'loudness'
database_user = 'postgres'
database_user_password = 'put password here'
table_name = 'historical_loudness'


def update_table(database_name, database_user, database_user_password, table_name, microphone1_value, microphone2_value, timestamp_value):

    # Setup connection to database
    connection = psycopg2.connect(user=database_user,
                                  password=database_user_password,
                                  host="127.0.0.1",
                                  port="5432",
                                  database=database_name)

    # Create a cursor object to execute queries against the database
    cursor = connection.cursor()

    try:
        # SQL Statement to insert a new row into the table
        sql = f"INSERT INTO {table_name} (ts, microphone1, microphone2) VALUES (%s, %s, %s)"

        # Values for the row to be inserted
        val = (timestamp_value,
                microphone1_value,
                microphone2_value)

        # Execute the SQL statement
        cursor.execute(sql, val)

        # Commit the changes to the database
        connection.commit()

        # Print the number of rows inserted
        count = cursor.rowcount
        # print("- ", count, "Record(s) inserted successfully ")

    except (Exception, psycopg2.Error) as error:
        print("Error in update operation", error)

    finally:
        # Close communication with the database
        if connection:
            cursor.close()
            connection.close()
            # print("Connection closed")


# ~~~ MAIN ~~~ #


p = pyaudio.PyAudio()

stream = p.open(format=FORMAT,
                input_device_index=1,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

stream2 = p.open(format=FORMAT,
                input_device_index=2,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)


while True:
    data1 = stream.read(CHUNK, exception_on_overflow = False)
    data2 = stream2.read(CHUNK, exception_on_overflow = False)
    rms1 = audioop.rms(data1, 2)  # here's where you calculate the volume
    rms2 = audioop.rms(data2, 2)  # here's where you calculate the volume
    print(rms1, rms2)
    ts = datetime.now()
    
    update_table(database_name=database_name, database_user=database_user, database_user_password=database_user_password, table_name=table_name, microphone1_value=rms1, microphone2_value=rms2, timestamp_value=ts)

stream.stop_stream()
stream.close()
p.terminate()

