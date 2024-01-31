LOAD DATA LOCAL INFILE '/tmp/input/stations.csv' 
INTO TABLE stations 
FIELDS TERMINATED BY ','
OPTIONALLY ENCLOSED BY '"' 
LINES TERMINATED BY '\r\n'
IGNORE 1 LINES
(id,name,FareZones,HubNaptanCode,Wifi,OutsideStationUniqueId,BlueBadgeCarParking,BlueBadgeCarParkSpaces,TaxiRanksOutsideStation,MainBusInterchange,PierInterchange,NationalRailInterchange,AirportInterchange,EmiratesAirLineInterchange,lat,lon,location)
;

LOAD DATA LOCAL INFILE '/tmp/input/users.csv' 
INTO TABLE users 
FIELDS TERMINATED BY ','
OPTIONALLY ENCLOSED BY '"' 
LINES TERMINATED BY '\r\n'
IGNORE 1 LINES
(name)
;