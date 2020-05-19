SELECT report.*, devices_last.alias 
FROM (SELECT * FROM devices WHERE "timestamp" = (SELECT MAX("timestamp") from devices)) as devices_last
INNER JOIN 
(
	SELECT *,
	       CASE 
		       WHEN connected_last = "true" AND connected_penultimate = "true" THEN 'Keep connected'
		       WHEN connected_last = "true" AND connected_penultimate = "false" THEN 'New connected'
		       WHEN connected_last = "false" AND connected_penultimate = "true" THEN 'Disconnected'
	       END AS status
	FROM 
	(
	                --------------------------------------------------------------------------------------------------
	                -- Still connected devices (connected in the last scan and also in the penultimate scan)
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
	)
) as report
ON report.mac = devices_last.mac