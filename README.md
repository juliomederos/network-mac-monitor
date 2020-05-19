# Network mac and ip monitor

Script to monitor mac and ip addresses events of devices in network.

The monitorization consists in:

1. Detecting connecting and disconnecting "mac" addresses in network based on a previous scan.
2. Detecting changes on the ip assigned to "mac" addresses in network
3. Detecting more than one adapter connected to the network with the same mac (mac spoofing)

# Use

``` bash
sudo python3 main.py 192.168.0.0/24
```

# Specs

The code will perform a scan on the network retrieving connected macs and the corresponing ip.
Data model example:

{'timestamp': '2020-03-17 20:42:37', 'devices': [{'mac': 'xx:xx:xx:xx:xx:x1', 'ip': '192.168.0.1'}, {'mac': 'xx:xx:xx:xx:xx:x2', 'ip': '192.168.0.254'}, {'mac': 'xx:xx:xx:xx:xx:x3', 'ip': '192.168.0.14'}, {'mac': 'xx:xx:xx:xx:xx:x4', 'ip': '192.168.0.18'}, {'mac': 'xx:xx:xx:xx:xx:x5', 'ip': '192.168.0.20'}]}

After this the script filters the "devices" structure to extract mac addresses:

NEW Devices:  ['xx:xx:xx:xx:xx:x1', 'xx:xx:xx:xx:xx:x2', 'xx:xx:xx:xx:xx:x3', 'xx:xx:xx:xx:xx:x4', 'xx:xx:xx:xx:xx:x5']


1. Having the connected devices they will be compared with the previous scan and have the next output:

NEW LIST {'disconnected': ['xx:xx:xx:xx:xx:x6', 'xx:xx:xx:xx:xx:x7'], 'connected': []}

{'timestamp': '2020-03-17 20:42:37', 'mac': 'xx:xx:xx:xx:xx:x6', 'ip': '192.168.0.1', 'event_type' : "disconnect" }

# Dependencies

pip3 install -r requirements.txt 

# Data structure

In order to register and persist events ocurring in the network some data structures will be created.

devices : stores the list of devices and the common identification of them
''' sql
CREATE TABLE devices (timestamp REAL, mac TEXT, alias TEXT, comments text)
'''

devices_connected : 
''' sql
CREATE TABLE devices_connected (timestamp REAL, mac TEXT, ip TEXT)
'''



``` sql


--------------------------------------------------------------------------------------------------
-- Rows from the last scan
SELECT * FROM devices_connected WHERE "timestamp" = (SELECT MAX("timestamp") from devices_connected)

--------------------------------------------------------------------------------------------------
-- Rows from the penultimate scan
SELECT * FROM devices_connected WHERE "timestamp" = (SELECT "timestamp" from devices_connected ORDER BY "timestamp" ASC LIMIT 1)

--------------------------------------------------------------------------------------------------
-- Still connected devices (connected in the last scan and in the penultimate scan)
SELECT tbl_last.mac, "true" as connected_last, "true" as connected_penultimate 
FROM 
	(SELECT * FROM devices_connected WHERE "timestamp" = (SELECT MAX("timestamp") from devices_connected)) as tbl_last	
WHERE tbl_last.mac IN (SELECT mac FROM devices_connected WHERE "timestamp" = (SELECT "timestamp" from devices_connected ORDER BY "timestamp" ASC LIMIT 1))
ORDER BY mac ASC
;

--------------------------------------------------------------------------------------------------
-- New connected devices (connected in the last scan but not in the penultimate scan)
SELECT tbl_last.mac, "true" as connected_last, "false" as connected_penultimate 
FROM 
	(SELECT * FROM devices_connected WHERE "timestamp" = (SELECT MAX("timestamp") from devices_connected)) as tbl_last	
WHERE tbl_last.mac NOT IN (SELECT mac FROM devices_connected WHERE "timestamp" = (SELECT "timestamp" from devices_connected ORDER BY "timestamp" ASC LIMIT 1))
ORDER BY mac ASC
;

--------------------------------------------------------------------------------------------------
-- Disconnected devices (not connected in the last scan but connected in the penultimate scan)
-- Rows from the penultimate scan
SELECT tbl_penultimate.mac
FROM (SELECT mac FROM devices_connected WHERE "timestamp" = (SELECT "timestamp" from devices_connected ORDER BY "timestamp" ASC LIMIT 1)) tbl_penultimate
WHERE tbl_penultimate.mac NOT IN
(
-- Still connected devices (connected in the last scan and in the penultimate scan)
--SELECT tbl_last.mac, "true" as connected_last, "true" as connected_penultimate 
SELECT tbl_last.mac
FROM 
	(SELECT * FROM devices_connected WHERE "timestamp" = (SELECT MAX("timestamp") from devices_connected)) as tbl_last	
WHERE tbl_last.mac IN (SELECT mac FROM devices_connected WHERE "timestamp" = (SELECT "timestamp" from devices_connected ORDER BY "timestamp" ASC LIMIT 1))

UNION ALL
-- New connected devices (connected in the last scan but not in the penultimate scan)
--SELECT tbl_last.mac, "true" as connected_last, "false" as connected_penultimate 
SELECT tbl_last.mac
FROM 
	(SELECT * FROM devices_connected WHERE "timestamp" = (SELECT MAX("timestamp") from devices_connected)) as tbl_last	
WHERE tbl_last.mac NOT IN (SELECT mac FROM devices_connected WHERE "timestamp" = (SELECT "timestamp" from devices_connected ORDER BY "timestamp" ASC LIMIT 1))
)


--------------------------------------------------------------------------------------------------



--------------------------------------------------------------------------------------------------
-- Still connected devices (connected in the last scan and in the penultimate scan)
SELECT tbl_last.mac, "true" as connected_last, "true" as connected_penultimate 
FROM 
	(SELECT * FROM devices_connected WHERE "timestamp" = (SELECT MAX("timestamp") from devices_connected)) as tbl_last	
WHERE tbl_last.mac IN (SELECT mac FROM devices_connected WHERE "timestamp" = (SELECT "timestamp" from devices_connected ORDER BY "timestamp" ASC LIMIT 1))

UNION ALL
-- New connected devices (connected in the last scan but not in the penultimate scan)
SELECT tbl_last.mac, "true" as connected_last, "false" as connected_penultimate 
FROM 
	(SELECT * FROM devices_connected WHERE "timestamp" = (SELECT MAX("timestamp") from devices_connected)) as tbl_last	
WHERE tbl_last.mac NOT IN (SELECT mac FROM devices_connected WHERE "timestamp" = (SELECT "timestamp" from devices_connected ORDER BY "timestamp" ASC LIMIT 1))

UNION ALL

-- Disconnected devices (not connected in the last scan but connected in the penultimate scan)
-- Rows from the penultimate scan
SELECT tbl_penultimate.mac, "false" as connected_last, "true" as connected_penultimate 
FROM (SELECT mac FROM devices_connected WHERE "timestamp" = (SELECT "timestamp" from devices_connected ORDER BY "timestamp" ASC LIMIT 1)) tbl_penultimate
WHERE tbl_penultimate.mac NOT IN
(
-- Still connected devices (connected in the last scan and in the penultimate scan)
--SELECT tbl_last.mac, "true" as connected_last, "true" as connected_penultimate 
SELECT tbl_last.mac
FROM 
	(SELECT * FROM devices_connected WHERE "timestamp" = (SELECT MAX("timestamp") from devices_connected)) as tbl_last	
WHERE tbl_last.mac IN (SELECT mac FROM devices_connected WHERE "timestamp" = (SELECT "timestamp" from devices_connected ORDER BY "timestamp" ASC LIMIT 1))

UNION ALL
-- New connected devices (connected in the last scan but not in the penultimate scan)
--SELECT tbl_last.mac, "true" as connected_last, "false" as connected_penultimate 
SELECT tbl_last.mac
FROM 
	(SELECT * FROM devices_connected WHERE "timestamp" = (SELECT MAX("timestamp") from devices_connected)) as tbl_last	
WHERE tbl_last.mac NOT IN (SELECT mac FROM devices_connected WHERE "timestamp" = (SELECT "timestamp" from devices_connected ORDER BY "timestamp" ASC LIMIT 1))
)

--------------------------------------------------------------------------------------------------
--Mac spoofing (mac appears more than one time)
SELECT mac
FROM (
--Grouping to find repeated mac's addresses in network
SELECT mac, count(*) AS total
FROM devices_connected WHERE "timestamp" = (SELECT MAX("timestamp") from devices_connected)
GROUP BY mac
)
WHERE total > 1

--------------------------------------------------------------------------------------------------
--Getting names with the report, example : 

SELECT tbl_last.*, devices_last.alias 
FROM (SELECT * FROM devices WHERE "timestamp" = (SELECT MAX("timestamp") from devices)) as devices_last
INNER JOIN (SELECT * FROM devices_connected WHERE "timestamp" = (SELECT MAX("timestamp") from devices_connected)) as tbl_last
ON tbl_last.mac = devices_last.mac
;

--------------------------------------------------------------------------------------------------
```


| mac               | connected_last  | connected_penultimate    | status         |
| :---------------- | :-------------: | :----------------------: | :------------- |
| fc:xx:xx:xx:xx:xx | true            | true                     | Keep connected |
| 7c:xx:xx:xx:xx:xx | true            | false                    | New connected  |
| b8:xx:xx:xx:xx:xx | false           | true                     | Disconnected   |



