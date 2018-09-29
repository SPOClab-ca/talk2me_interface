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
-- Table structure for table `datacollector_bundle`
--

DROP TABLE IF EXISTS `datacollector_bundle`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `datacollector_bundle` (
  `bundle_id` int(11) NOT NULL AUTO_INCREMENT,
  `name_id` varchar(50) NOT NULL,
  `description` text,
  `bundle_token` varchar(1000) NOT NULL,
  `completion_req_sessions` int(11) DEFAULT NULL,
  `active_enddate` date DEFAULT NULL,
  PRIMARY KEY (`bundle_id`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `datacollector_bundle`
--

LOCK TABLES `datacollector_bundle` WRITE;
/*!40000 ALTER TABLE `datacollector_bundle` DISABLE KEYS */;
INSERT INTO `datacollector_bundle` VALUES (1,'picturedesc_normative','For participants in the normative data collection effort who will only be responding to the picture description task','137fbdcd7e5d8ad66148a80b048cfd34f92c9f377a8d3164e9ba381a0bfb033b6859473d4a103968d15d8521acb216ee6c18e99ee807d21c2128cac170aff7d3',10,'2015-10-13'),(2,'SCHC','For participants in the Scarborough Centre for Healthy Communities study - define the same pictures to be used by all participants','2d3cec2616f60287975a62e6e8b236c6b033c5f0d0895ad1594e5d79a8e7477deea932a9fdcb152e5675c2b0e8fafc76e102f85b676680d101f5c8e73c5784c6',4,NULL),(3,'uhn_web','For participants in the UHN study at Toronto Rehabilitation Institute (web). Only a subset of the Talk2Me tasks are used.','5d41c50802e08b384ea5f0295c7045464ff8001dcbdc8e20484c5d403b4e7d65cf299a4c65cd65c617c1984da562062045f9d54fe93a3f3e1d78ea7a094ee866',NULL,NULL),(4,'uhn_phone','For participants in the UHN study at Toronto Rehabilitation Institute (phone). Only a subset of the Talk2Me tasks are used.','4728acc6cd6b43d5c27a0af1c6b32a05f513c1bde4a6137737e0377192d4b96445bd9790d88db815e5cb2e5214b21722292beef653264632babbdbb4a9e14e21',NULL,NULL),(5,'oise','For participants in the OISE project','paugiuq1qb97j0l2gn7ks1pqzx3xidw5nkdor0wkpgzwcp3h4zh76flqexy9w9iqc29w87o1hoosu7goxmcg5dw71bwmkh7xxnsf53zq58rgsddrmyr7xky16viibupc',NULL,NULL),(6,'wch_web','For participants in the study at WCH (web). Only a subset of the Talk2Me tasks are used.','ejjog1qtp586445gah0qlw37byyryanhrcfow42avtcnefvbjxbffn0yr7zol3bpre96ekl8so8lqhg1wxghs133bli9hhzim6qu6yqr14g4t76vl7acxcwc7448lfjj',NULL,NULL),(7,'wch_phone','For participants in the UHN study at WCH (phone). Only a subset of the Talk2Me tasks are used.','nqy6vnmif5l0vk963rhd3ro1j6i8qqnfsq7zy1gs7uspq6xlhqzdkt2n246fejerv028ld3cl2q376hzxd0zug6htb5f693q161vdiy80m766jv7a31y4g3wpk3tch73',NULL,NULL);
/*!40000 ALTER TABLE `datacollector_bundle` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2018-09-29 15:38:36
