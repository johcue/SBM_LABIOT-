CREATE DATABASE `sbm` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
-- sbm.Beverage definition

CREATE TABLE `Beverage` (
  `Name` varchar(100) DEFAULT NULL,
  `LogDateTime` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
