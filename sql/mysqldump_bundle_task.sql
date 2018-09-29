-- MySQL dump 10.13  Distrib 5.7.19, for osx10.11 (x86_64)
--
-- Host: localhost    Database: mydatabase
-- ------------------------------------------------------
-- Server version	5.7.18

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `datacollector_bundle_task`
--

DROP TABLE IF EXISTS `datacollector_bundle_task`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `datacollector_bundle_task` (
  `bundle_task_id` int(11) NOT NULL AUTO_INCREMENT,
  `bundle_id` int(11) NOT NULL,
  `task_id` int(11) NOT NULL,
  `default_num_instances` int(11) DEFAULT NULL,
  PRIMARY KEY (`bundle_task_id`),
  KEY `bundle_id` (`bundle_id`),
  KEY `task_id` (`task_id`),
  CONSTRAINT `datacollector_bundle_task_ibfk_1` FOREIGN KEY (`bundle_id`) REFERENCES `datacollector_bundle` (`bundle_id`),
  CONSTRAINT `datacollector_bundle_task_ibfk_2` FOREIGN KEY (`task_id`) REFERENCES `datacollector_task` (`task_id`)
) ENGINE=InnoDB AUTO_INCREMENT=50 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `datacollector_bundle_task`
--

LOCK TABLES `datacollector_bundle_task` WRITE;
/*!40000 ALTER TABLE `datacollector_bundle_task` DISABLE KEYS */;
INSERT INTO `datacollector_bundle_task` VALUES (5,3,1,6),(6,3,7,1),(7,3,10,1),(8,3,11,5),(9,3,12,1),(10,3,13,NULL),(11,3,15,18),(12,4,1,6),(13,4,10,1),(14,4,11,5),(15,4,12,1),(16,4,13,NULL),(17,5,17,3),(19,5,16,10),(20,5,18,3),(22,5,20,2),(23,5,21,4),(24,5,22,5),(25,5,23,30),(38,6,1,6),(39,7,1,6),(40,6,7,1),(41,7,7,1),(42,6,10,1),(43,7,10,1),(44,6,11,5),(45,7,11,5),(46,6,12,1),(47,7,12,1),(48,6,13,NULL),(49,7,13,NULL);
/*!40000 ALTER TABLE `datacollector_bundle_task` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2018-09-29 15:40:52
