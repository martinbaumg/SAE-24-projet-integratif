#!/usr/bin/env python3

from optparse import OptionError
import paho.mqtt.client as mqtt
from datetime import datetime
from MySQLdb import _mysql
from MySQLdb._exceptions import OperationalError
from os.path import exists
from os import remove

try:
    db=_mysql.connect("172.17.0.2","root","toto", "temp")
except OperationalError:
    db=_mysql.connect("172.17.0.2","root","toto")
    db.query("CREATE DATABASE temp")
    db.query("USE temp")

# On se reconnecte automatiquement
db.ping(True)
db.query("""
CREATE TABLE IF NOT EXISTS temp.sensors (
    id INT NOT NULL AUTO_INCREMENT,
    sensor_id VARCHAR(12) NOT NULL,
    piece VARCHAR(50) NOT NULL,
    nom VARCHAR(50),
    PRIMARY KEY (id))
""")

db.query("""
CREATE TABLE IF NOT EXISTS temp.sensors_data (
    id INT NOT NULL AUTO_INCREMENT,
    sensor_id VARCHAR(12) NOT NULL,
    CONSTRAINT sensor_id
        FOREIGN KEY (`IdCompagnie`)
        REFERENCES `sae_23`.`compagnie` (`IdCompagnie`)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
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
    try:
        correct = len(str(msg.payload)[2:-1].split(",")) == 5
    except Exception:
        correct = False

    if correct:
        payload = str(msg.payload)[2:-1].split(",")

        id= payload[0].split("=")[1]
        piece= payload[1].split("=")[1]
        dt = datetime.strptime(payload[2].split("=")[1] + " " + payload[3].split("=")[1],
                            '%d/%m/%Y %H:%M:%S')
        temp= payload[4].split("=")[1]

        sql = f"INSERT INTO sensors_data (sensor_id, piece, datetime, temp) VALUES ('{id}', '{piece}', '{dt.strftime('%Y-%m-%d %H:%M:%S')}', {temp})"
        print(sql)

        reachable = True
        try:
            db.query(sql)
            reachable = True
        except Exception:
            reachable = False
            bak = open("backup.sql", "a")
            bak.write(f"{sql}\n")
            bak.close()

        if exists("backup.sql") and reachable:
            with open('backup.sql') as f:
                for line in f:
                    db.query(line)
            remove('backup.sql')

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("test.mosquitto.org", port=1883, keepalive=60)

client.loop_forever()