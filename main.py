#!/usr/bin/env python3
import sys
import time
import json
import time
import datetime
import sqlite3

from scapy.all import srp, Ether, ARP, conf

def get_network_devices():
    """ Returns devices connected in network"""

    conf.verb = 0
    ans, unans = srp(Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst=sys.argv[1]), timeout=2)
    return {"network_devices":ans, "timestamp":time.time()}

def get_connected_devices(network_devices):
    """ Returns formatted connected devices """

    devices = []
    date = datetime.datetime.fromtimestamp(network_devices["timestamp"]).strftime("%Y-%m-%d %H:%M:%S")

    for snd, rcv in network_devices["network_devices"]:
        #devices.append({"timestamp" : network_devices["timestamp"], "timestamp_str" : date, "mac" : rcv.sprintf(r"%Ether.src%"), "ip" : rcv.sprintf(r"%ARP.psrc%")})
        devices.append({"timestamp" : network_devices["timestamp"], "mac" : rcv.sprintf(r"%Ether.src%"), "ip" : rcv.sprintf(r"%ARP.psrc%")})

    return devices

def read_file(uri):
	"""Returns a file content as a string"""

	with open(uri, "r") as file_object:
		f = file_object.read()

	return f

def get_devices(date_now,devices_json):
    
    devices = []

    for device in devices_json:
        devices.append((date_now, device["mac"], device["alias"], device["comments"]))

    return devices

# http://www.cdotson.com/2014/06/generating-json-documents-from-sqlite-databases-in-python/
def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

<<<<<<< HEAD
def get_connection(db_filename):

    connection = sqlite3.connect(db_filename)
    connection.row_factory = dict_factory

    return connection

def get_cursor(connection):
    
    return connection.cursor()

=======
>>>>>>> initial files
def main():

    db_filename = "example.db"

    ### Queries
    create_table_devices = read_file("files/queries/create_table_devices.sql") 
    create_table_devices_connected = read_file("files/queries/create_table_devices_connected.sql")
    insert_into_devices  = read_file("files/queries/insert_into_devices.sql")
    insert_into_devices_connected = read_file("files/queries/insert_into_devices_connected.sql")
    get_results  = read_file("files/queries/get_results.sql")
    devices_json  = json.loads(read_file("files/devices.json"))

    if sys.argv[2]:
        t = int(sys.argv[2])

<<<<<<< HEAD
    connection = get_connection(db_filename)
    cursor = get_cursor(connection)

    cursor.execute(create_table_devices)
    cursor.execute(create_table_devices_connected)
=======
    conn = sqlite3.connect(db_filename)
    conn.row_factory = dict_factory

    c = conn.cursor()

    c.execute(create_table_devices)
>>>>>>> initial files

    date_now = time.time()

    devices = get_devices(date_now, devices_json)

<<<<<<< HEAD
    cursor.executemany(insert_into_devices, devices)

    # Save the changes
    connection.commit()
=======
    c.executemany(insert_into_devices, devices)

    # Save (commit) the changes
    conn.commit()

    # We can also close the connection if we are done with it.
    # Just be sure any changes have been committed or they will be lost.
    #conn.close()
>>>>>>> initial files

    while True:

        t = 5

        network_devices = get_network_devices()
        data = get_connected_devices(network_devices)
        data_list = list(map(lambda x: (x["timestamp"], x["mac"], x["ip"]), data))

<<<<<<< HEAD
        connection = get_connection(db_filename)

        cursor.executemany(insert_into_devices_connected, data_list)

        # Save (commit) the changes
        connection.commit()

        cursor.execute(get_results)
	    
        rows = cursor.fetchall()
=======
        conn = sqlite3.connect(db_filename)

        c.execute(create_table_devices_connected)

        c.executemany(insert_into_devices_connected, data_list)

        # Save (commit) the changes
        conn.commit()

        reader = c.execute(get_results)
	    
        rows = c.fetchall()
        #print("description: ", "\n", list(map(lambda x: x[0], reader.description)) )
>>>>>>> initial files

        print("\n", "results: ")

        for row in rows:
            print(row)

        # We can also close the connection if we are done with it.
        # Just be sure any changes have been committed or they will be lost.
<<<<<<< HEAD
        connection.close()
=======
        conn.close()
>>>>>>> initial files

        time.sleep(t)

if __name__ == "__main__":

    if len(sys.argv) < 2:

        help = read_file("files/doc/help.txt")

        print(help)

        sys.exit(1)

    main()
