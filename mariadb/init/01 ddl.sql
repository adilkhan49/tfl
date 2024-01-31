CREATE TABLE stations 
(
    id VARCHAR(255) UNIQUE,
    name VARCHAR(255) PRIMARY KEY,
    FareZones VARCHAR(255),
    HubNaptanCode VARCHAR(255),
    Wifi BOOLEAN,
    OutsideStationUniqueId VARCHAR(255),
    BlueBadgeCarParking BOOLEAN,
    BlueBadgeCarParkSpaces INT,
    TaxiRanksOutsideStation BOOLEAN,
    MainBusInterchange VARCHAR(255),
    PierInterchange VARCHAR(255),
    NationalRailInterchange VARCHAR(255),
    AirportInterchange VARCHAR(255),
    EmiratesAirLineInterchange VARCHAR(255),
    lat VARCHAR(255),
    lon VARCHAR(255),
    location VARCHAR(255),
    created_date DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    modified_date DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP NOT NULL
);

CREATE TABLE users 
(
    name VARCHAR(255) PRIMARY KEY,
    email_address VARCHAR(255),
    created_date DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    modified_date DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP NOT NULL
);