SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";

CREATE TABLE `Dagelijkse_Samenvatting` (
  `Samenvatting_ID` int(11) NOT NULL AUTO_INCREMENT,
  `DeviceID` int(11) DEFAULT NULL,
  `Datum` date DEFAULT NULL,
  `Aantal_Cola` int(11) DEFAULT NULL,
  `Aantal_Water` int(11) DEFAULT NULL,
  `Volume_Cola` float DEFAULT NULL,
  `Volume_Water` float DEFAULT NULL,
  `Temperatuur` int(11) DEFAULT NULL,
  `Vochtigheid` int(11) DEFAULT NULL,
  PRIMARY KEY (`Samenvatting_ID`),
  KEY `FK3_DeviceID_idx` (`DeviceID`),
  CONSTRAINT `FK2_DeviceID` FOREIGN KEY (`DeviceID`) REFERENCES `Device` (`DeviceID`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `Device` (
  `DeviceID` int(11) NOT NULL,
  `Beschrijving` varchar(45) DEFAULT NULL,
  `Actief_Sinds` datetime DEFAULT NULL,
  `Is_Actief` tinyint(1) DEFAULT NULL,
  `GebruikerID` int(11) DEFAULT NULL,
  PRIMARY KEY (`DeviceID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `Gebruiker` (
  `GebruikerID` int(11) NOT NULL,
  `Email` varchar(100) DEFAULT NULL,
  `Naam` int(11) DEFAULT NULL,
  PRIMARY KEY (`GebruikerID`),
  CONSTRAINT `FK_GebruikerID` FOREIGN KEY (`GebruikerID`) REFERENCES `Device` (`DeviceID`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `Historiek` (
  `HistoriekID` int(11) NOT NULL AUTO_INCREMENT,
  `DeviceID` int(11) DEFAULT NULL,
  `DrankType` varchar(10) DEFAULT NULL,
  `Tijdsstip` datetime DEFAULT NULL,
  `Volume_Cola` float DEFAULT NULL,
  `Volume_Water` float DEFAULT NULL,
  `Temperatuur` float DEFAULT NULL,
  `Vochtigheid` float DEFAULT NULL,
  PRIMARY KEY (`HistoriekID`),
  KEY `FK4_DeviceID_idx` (`DeviceID`),
  CONSTRAINT `FK4_DeviceID` FOREIGN KEY (`DeviceID`) REFERENCES `Device` (`DeviceID`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
