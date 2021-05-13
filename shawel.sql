-- MariaDB dump 10.19  Distrib 10.5.9-MariaDB, for Linux (aarch64)
--
-- Host: localhost    Database: shawel
-- ------------------------------------------------------
-- Server version	10.5.9-MariaDB

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `api`
--

DROP TABLE IF EXISTS `api`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `api` (
  `key_` varchar(256) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`key_`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `api`
--

LOCK TABLES `api` WRITE;
/*!40000 ALTER TABLE `api` DISABLE KEYS */;
INSERT INTO `api` VALUES ('d87174bf4cc2936c48a04a1ecac481975314c6877fe16b07768146523647104b');
/*!40000 ALTER TABLE `api` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `chats`
--

DROP TABLE IF EXISTS `chats`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `chats` (
  `id` int(11) NOT NULL,
  `raspisanie` int(11) NOT NULL DEFAULT 0,
  `game-cmds` int(11) NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `chats`
--

LOCK TABLES `chats` WRITE;
/*!40000 ALTER TABLE `chats` DISABLE KEYS */;
INSERT INTO `chats` VALUES (2000000002,0,0),(2000000015,0,1),(2000000016,1,0),(2000000017,0,0),(2000000018,0,0),(2000000019,0,0);
/*!40000 ALTER TABLE `chats` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `imgs`
--

DROP TABLE IF EXISTS `imgs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `imgs` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `image` blob NOT NULL,
  `type` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL,
  `size` int(11) NOT NULL,
  `mark` varchar(128) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `mark` (`mark`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `imgs`
--

LOCK TABLES `imgs` WRITE;
/*!40000 ALTER TABLE `imgs` DISABLE KEYS */;
/*!40000 ALTER TABLE `imgs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `mute`
--

DROP TABLE IF EXISTS `mute`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `mute` (
  `chatid` int(11) NOT NULL,
  `vkid` int(11) NOT NULL,
  `date` int(11) NOT NULL,
  `warn` int(11) NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `mute`
--

LOCK TABLES `mute` WRITE;
/*!40000 ALTER TABLE `mute` DISABLE KEYS */;
/*!40000 ALTER TABLE `mute` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `uptime`
--

DROP TABLE IF EXISTS `uptime`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `uptime` (
  `id` int(11) NOT NULL,
  `friendly_name` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL,
  `status` int(11) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `uptime`
--

LOCK TABLES `uptime` WRITE;
/*!40000 ALTER TABLE `uptime` DISABLE KEYS */;
INSERT INTO `uptime` VALUES (786116008,'1. node1 [HTTPS]',2),(786815135,'2. node1 [PING]',2),(787219709,'6. node3 [PING]',2),(787368511,'5. node3 [HTTPS]',2),(787783921,'4. node2 [PING]',2),(787783931,'3. node2 [HTTPS]',2);
/*!40000 ALTER TABLE `uptime` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `users` (
  `vkid` int(30) NOT NULL,
  `dostup` int(11) NOT NULL DEFAULT 0,
  `EXP` int(11) NOT NULL DEFAULT 0,
  `raspisanie` int(11) NOT NULL DEFAULT 0,
  PRIMARY KEY (`vkid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (228167601,0,2,1),(250700830,0,0,0),(252489312,0,0,0),(257842723,0,0,0),(277746917,0,0,0),(277988184,0,0,0),(279508220,0,0,0),(290137168,0,0,0),(301023575,0,0,0),(304126093,0,0,0),(305371382,0,0,0),(314544195,0,0,0),(319307323,0,0,0),(320809408,0,0,0),(324977194,0,0,0),(331465308,2,5,1),(332756622,0,0,0),(337744844,0,0,0),(339444055,0,0,0),(344493265,0,0,0),(356535517,0,1,1),(364911251,0,0,0),(381992762,0,107,0),(399941524,0,160,1),(406387825,0,0,0),(417079484,0,0,0),(445248149,0,0,0),(453268079,0,29,1),(487070830,0,0,0),(500136993,2,0,0),(524573062,0,5,0),(524876015,0,0,0),(539432007,0,0,0),(560289436,0,0,0),(564191377,0,0,0),(572689805,0,0,0),(574214420,0,4,1),(586788717,0,0,0),(587379423,0,0,0);
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `vk`
--

DROP TABLE IF EXISTS `vk`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `vk` (
  `rasp` varchar(200) NOT NULL,
  `zvonki` varchar(200) NOT NULL,
  `rasp-updated` varchar(64) NOT NULL,
  `rasp-checked` varchar(64) NOT NULL,
  `vlaga` int(11) DEFAULT NULL,
  `time-poliv` int(11) DEFAULT NULL,
  `autopoliv` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `vk`
--

LOCK TABLES `vk` WRITE;
/*!40000 ALTER TABLE `vk` DISABLE KEYS */;
INSERT INTO `vk` VALUES ('photo331465308_457248903_5025b52e2db77f6c24,photo331465308_457248904_f21b200fb651cb36d4','photo331465308_457248905_a54bbd7a94f77110b6,photo331465308_457248906_2e99be46af2e418254','18:30:00 12.05.2021','13:30:00 13.05.2021',0,1617731100,1603791912);
/*!40000 ALTER TABLE `vk` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2021-05-13 13:40:21
