#!/usr/bin/env python3
from optparse import OptionError
import paho.mqtt.client as mqtt
from datetime import datetime
from MySQLdb import _mysql
from MySQLdb._exceptions import OperationalError
from os.path import exists
from os import remove
import random

try:
    db=_mysql.connect("10.37.129.3","martin","martin", "martin")
except OperationalError:
    db=_mysql.connect("10.37.129.3","martin","martin")
    db.query("CREATE DATABASE martin")
    db.query("USE martin")

# On se reconnecte automatiquement
db.ping(True)
db.query("""
CREATE TABLE IF NOT EXISTS martin.sensors (
    id INT NOT NULL AUTO_INCREMENT,
    macaddr VARCHAR(12) NOT NULL,
    piece VARCHAR(50) NOT NULL,
    emplacement VARCHAR(50),
    nom VARCHAR(50),
    UNIQUE (macaddr),
    PRIMARY KEY (id))
""")

db.query("""
CREATE TABLE IF NOT EXISTS martin.sensors_data (
    id INT NOT NULL AUTO_INCREMENT,
    sensor_id INT NOT NULL,
    CONSTRAINT sensorFK
        FOREIGN KEY (sensor_id)
        REFERENCES martin.sensors(id),
    datetime DATETIME NOT NULL,
    temp FLOAT NOT NULL,
    PRIMARY KEY (id))
""")

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("IUT/Colmar/SAE24/Maison1")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    # On vérifie un peu si qqun ne s'ammuse pas a envoyer n'importe quoi sur le brocker
    try:
        correct = len(str(msg.payload)[2:-1].split(",")) == 5
    except Exception:
        correct = False

    if correct:
        payload = str(msg.payload)[2:-1].split(",")

        mac_addr= payload[0].split("=")[1]
        piece= payload[1].split("=")[1]
        dt = datetime.strptime(payload[2].split("=")[1] + " " + payload[3].split("=")[1],
                            '%d/%m/%Y %H:%M:%S')
        temp= payload[4].split("=")[1]

        try:
            db.query(f"INSERT INTO sensors (macaddr, piece) VALUES ('{mac_addr}', '{piece}')")
        except Exception:
            pass

        db.query(f"SELECT id FROM sensors WHERE macaddr='{mac_addr}'")
        id = int(db.store_result().fetch_row()[0][0])

        sql_data = f"INSERT INTO sensors_data (sensor_id, datetime, martin) VALUES ({id}, '{dt.strftime('%Y-%m-%d %H:%M:%S')}', {temp})"
        print(sql_data)

        reachable = True
        try:
            db.query(sql_data)
            reachable = True
        except Exception:
            reachable = False
            bak = open("backup.sql", "a")
            bak.write(f"{sql_data}\n")
            bak.close()

        if exists("backup.sql") and reachable:
            with open('backup.sql') as f:
                for line in f:
                    db.query(line)
            remove('backup.sql')

client = mqtt.Client(client_id=f"client-grp13-{random.randint(1, 99999)}")
client.on_connect = on_connect
client.on_message = on_message

client.connect("test.mosquitto.org", port=1883, keepalive=60)

client.loop_forever()