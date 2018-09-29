-- MySQL dump 10.13  Distrib 5.7.23, for Linux (x86_64)
--
-- Host: localhost    Database: csc2518
-- ------------------------------------------------------
-- Server version	5.7.22-0ubuntu0.16.04.1

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
-- Table structure for table `auth_group`
--

DROP TABLE IF EXISTS `auth_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_group` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(80) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `auth_group_permissions`
--

DROP TABLE IF EXISTS `auth_group_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_group_permissions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `group_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `group_id` (`group_id`,`permission_id`),
  KEY `auth_group_permissions_425ae3c4` (`group_id`),
  KEY `auth_group_permissions_1e014c8f` (`permission_id`),
  CONSTRAINT `group_id_refs_id_3cea63fe` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `permission_id_refs_id_5886d21f` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `auth_message`
--

DROP TABLE IF EXISTS `auth_message`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_message` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `message` longtext NOT NULL,
  PRIMARY KEY (`id`),
  KEY `auth_message_403f60f` (`user_id`),
  CONSTRAINT `user_id_refs_id_650f49a6` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `auth_permission`
--

DROP TABLE IF EXISTS `auth_permission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_permission` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `content_type_id` int(11) NOT NULL,
  `codename` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `content_type_id` (`content_type_id`,`codename`),
  KEY `auth_permission_1bb8f392` (`content_type_id`),
  CONSTRAINT `content_type_id_refs_id_728de91f` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=148 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `auth_user`
--

DROP TABLE IF EXISTS `auth_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(30) NOT NULL,
  `first_name` varchar(30) NOT NULL,
  `last_name` varchar(30) NOT NULL,
  `email` varchar(254) NOT NULL,
  `password` varchar(128) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `date_joined` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=1002 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `auth_user_groups`
--

DROP TABLE IF EXISTS `auth_user_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_user_groups` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `group_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`,`group_id`),
  KEY `auth_user_groups_403f60f` (`user_id`),
  KEY `auth_user_groups_425ae3c4` (`group_id`),
  CONSTRAINT `group_id_refs_id_f116770` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `user_id_refs_id_7ceef80f` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `auth_user_user_permissions`
--

DROP TABLE IF EXISTS `auth_user_user_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_user_user_permissions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`,`permission_id`),
  KEY `auth_user_user_permissions_403f60f` (`user_id`),
  KEY `auth_user_user_permissions_1e014c8f` (`permission_id`),
  CONSTRAINT `permission_id_refs_id_67e79cb` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `user_id_refs_id_dfbab7d` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

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
) ENGINE=InnoDB AUTO_INCREMENT=36 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `datacollector_bundle_task_field_value`
--

DROP TABLE IF EXISTS `datacollector_bundle_task_field_value`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `datacollector_bundle_task_field_value` (
  `bundle_task_field_value_id` int(11) NOT NULL AUTO_INCREMENT,
  `bundle_task_id` int(11) NOT NULL,
  `task_field_value_id` int(11) NOT NULL,
  PRIMARY KEY (`bundle_task_field_value_id`),
  KEY `D0ec1e62f7717741d6ab39be72d6844b` (`bundle_task_id`),
  KEY `a90850a9e3891af0793e6346a0ec4c76` (`task_field_value_id`),
  CONSTRAINT `D0ec1e62f7717741d6ab39be72d6844b` FOREIGN KEY (`bundle_task_id`) REFERENCES `datacollector_bundle_task` (`bundle_task_id`),
  CONSTRAINT `a90850a9e3891af0793e6346a0ec4c76` FOREIGN KEY (`task_field_value_id`) REFERENCES `datacollector_task_field_value` (`task_field_value_id`)
) ENGINE=InnoDB AUTO_INCREMENT=901 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `datacollector_client`
--

DROP TABLE IF EXISTS `datacollector_client`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `datacollector_client` (
  `client_id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `secret` varchar(1000) NOT NULL,
  `secret_expirydate` datetime(6) DEFAULT NULL,
  `clienttype_id` int(11) NOT NULL,
  `datetime_created` datetime(6) DEFAULT NULL,
  PRIMARY KEY (`client_id`),
  KEY `D7c5eb60c3abe2c267e14a4df4346aa0` (`clienttype_id`),
  CONSTRAINT `D7c5eb60c3abe2c267e14a4df4346aa0` FOREIGN KEY (`clienttype_id`) REFERENCES `datacollector_clienttype` (`clienttype_id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `datacollector_clienttype`
--

DROP TABLE IF EXISTS `datacollector_clienttype`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `datacollector_clienttype` (
  `clienttype_id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  PRIMARY KEY (`clienttype_id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `datacollector_country`
--

DROP TABLE IF EXISTS `datacollector_country`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `datacollector_country` (
  `country_id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(200) NOT NULL,
  `iso_code` varchar(2) NOT NULL,
  PRIMARY KEY (`country_id`)
) ENGINE=InnoDB AUTO_INCREMENT=250 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `datacollector_country_province`
--

DROP TABLE IF EXISTS `datacollector_country_province`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `datacollector_country_province` (
  `country_province_id` int(11) NOT NULL AUTO_INCREMENT,
  `country_id` int(11) NOT NULL,
  `name` varchar(200) NOT NULL,
  `iso_code` varchar(10) NOT NULL,
  `type_name` varchar(50) NOT NULL,
  PRIMARY KEY (`country_province_id`),
  KEY `datacollector_country_province_534dd89` (`country_id`),
  CONSTRAINT `country_id_refs_country_id_3ab8af71` FOREIGN KEY (`country_id`) REFERENCES `datacollector_country` (`country_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `datacollector_dementia_type`
--

DROP TABLE IF EXISTS `datacollector_dementia_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `datacollector_dementia_type` (
  `dementia_type_id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(200) NOT NULL,
  `ranking` int(11) DEFAULT NULL,
  `requires_detail` int(1) DEFAULT NULL,
  PRIMARY KEY (`dementia_type_id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `datacollector_demographics_oise`
--

DROP TABLE IF EXISTS `datacollector_demographics_oise`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `datacollector_demographics_oise` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `subject_id` int(11) DEFAULT NULL,
  `name` varchar(100) DEFAULT NULL,
  `gender_id` varchar(1) DEFAULT NULL,
  `age` int(11) DEFAULT NULL,
  `grade` int(11) DEFAULT NULL,
  `identity` tinyint(1) DEFAULT NULL,
  `canada` tinyint(1) DEFAULT NULL,
  `english_ability` tinyint(1) DEFAULT NULL,
  `other_languages` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `subject_id` (`subject_id`),
  CONSTRAINT `datacollector_demographics_oise_ibfk_1` FOREIGN KEY (`subject_id`) REFERENCES `datacollector_subject` (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=257 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `datacollector_education_level`
--

DROP TABLE IF EXISTS `datacollector_education_level`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `datacollector_education_level` (
  `education_level_id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(200) NOT NULL,
  `ranking` int(11) DEFAULT NULL,
  PRIMARY KEY (`education_level_id`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `datacollector_ethnicity`
--

DROP TABLE IF EXISTS `datacollector_ethnicity`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `datacollector_ethnicity` (
  `ethnicity_id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(200) NOT NULL,
  `ranking` int(11) DEFAULT NULL,
  PRIMARY KEY (`ethnicity_id`)
) ENGINE=InnoDB AUTO_INCREMENT=14 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `datacollector_field_data_type`
--

DROP TABLE IF EXISTS `datacollector_field_data_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `datacollector_field_data_type` (
  `field_data_type_id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  PRIMARY KEY (`field_data_type_id`)
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `datacollector_field_type`
--

DROP TABLE IF EXISTS `datacollector_field_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `datacollector_field_type` (
  `field_type_id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  PRIMARY KEY (`field_type_id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `datacollector_gender`
--

DROP TABLE IF EXISTS `datacollector_gender`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `datacollector_gender` (
  `gender_id` varchar(1) NOT NULL,
  `name` varchar(20) NOT NULL,
  `ranking` int(11) DEFAULT NULL,
  `requires_detail` int(1) DEFAULT NULL,
  PRIMARY KEY (`gender_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `datacollector_language`
--

DROP TABLE IF EXISTS `datacollector_language`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `datacollector_language` (
  `language_id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(200) NOT NULL,
  `iso_code` varchar(2) NOT NULL,
  `is_official` int(1) DEFAULT NULL,
  PRIMARY KEY (`language_id`)
) ENGINE=InnoDB AUTO_INCREMENT=185 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `datacollector_language_level`
--

DROP TABLE IF EXISTS `datacollector_language_level`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `datacollector_language_level` (
  `language_level_id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `ranking` int(11) DEFAULT NULL,
  PRIMARY KEY (`language_level_id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `datacollector_notification`
--

DROP TABLE IF EXISTS `datacollector_notification`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `datacollector_notification` (
  `notification_id` varchar(50) NOT NULL,
  `notification_name` varchar(200) NOT NULL,
  `notification_text` longtext NOT NULL,
  `notification_trigger` varchar(50) DEFAULT NULL,
  `icon_filename` varchar(100) NOT NULL,
  `notification_target` varchar(200) DEFAULT NULL,
  PRIMARY KEY (`notification_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `datacollector_prize`
--

DROP TABLE IF EXISTS `datacollector_prize`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `datacollector_prize` (
  `prize_id` varchar(50) NOT NULL,
  `prize_name` varchar(200) NOT NULL,
  `prize_value` decimal(6,2) NOT NULL,
  PRIMARY KEY (`prize_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `datacollector_questionnaire_oise`
--

DROP TABLE IF EXISTS `datacollector_questionnaire_oise`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `datacollector_questionnaire_oise` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `session_id` int(11) DEFAULT NULL,
  `enjoy_reading` tinyint(1) DEFAULT NULL,
  `fun_reading` tinyint(1) DEFAULT NULL,
  `good_reader` tinyint(1) DEFAULT NULL,
  `ease_reading` tinyint(1) DEFAULT NULL,
  `long_reading` tinyint(1) DEFAULT NULL,
  `challenging_reading` tinyint(1) DEFAULT NULL,
  `iep` tinyint(1) DEFAULT NULL,
  `esl` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `session_id` (`session_id`),
  CONSTRAINT `datacollector_questionnaire_oise_ibfk_1` FOREIGN KEY (`session_id`) REFERENCES `datacollector_session` (`session_id`)
) ENGINE=InnoDB AUTO_INCREMENT=219 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `datacollector_session`
--

DROP TABLE IF EXISTS `datacollector_session`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `datacollector_session` (
  `session_id` int(11) NOT NULL AUTO_INCREMENT,
  `subject_id` int(11) NOT NULL,
  `start_date` datetime NOT NULL,
  `end_date` datetime DEFAULT NULL,
  `session_type_id` tinyint(3) unsigned DEFAULT NULL,
  PRIMARY KEY (`session_id`),
  KEY `datacollector_session_638462f1` (`subject_id`),
  CONSTRAINT `subject_id_refs_user_id_171a3b69` FOREIGN KEY (`subject_id`) REFERENCES `datacollector_subject` (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=3306 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `datacollector_session_phone_duration`
--

DROP TABLE IF EXISTS `datacollector_session_phone_duration`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `datacollector_session_phone_duration` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `session_id` int(11) NOT NULL,
  `duration` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `session_id` (`session_id`),
  CONSTRAINT `datacollector_session_phone_duration_ibfk_1` FOREIGN KEY (`session_id`) REFERENCES `datacollector_session` (`session_id`)
) ENGINE=InnoDB AUTO_INCREMENT=131 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `datacollector_session_response`
--

DROP TABLE IF EXISTS `datacollector_session_response`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `datacollector_session_response` (
  `session_response_id` int(11) NOT NULL AUTO_INCREMENT,
  `session_task_instance_id` int(11) NOT NULL,
  `date_completed` date DEFAULT NULL,
  `value_text` longtext,
  `value_audio` varchar(100) DEFAULT NULL,
  `value_multiselect` varchar(100) DEFAULT NULL,
  `value_expected` longtext,
  `num_repeats` int(11) DEFAULT NULL,
  `value_image` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`session_response_id`),
  KEY `datacollector_session_response_1580a68b` (`session_task_instance_id`),
  CONSTRAINT `session_task_instance_id_refs_session_task_instance_id_275d9174` FOREIGN KEY (`session_task_instance_id`) REFERENCES `datacollector_session_task_instance` (`session_task_instance_id`)
) ENGINE=InnoDB AUTO_INCREMENT=138489 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `datacollector_session_task`
--

DROP TABLE IF EXISTS `datacollector_session_task`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `datacollector_session_task` (
  `session_task_id` int(11) NOT NULL AUTO_INCREMENT,
  `session_id` int(11) NOT NULL,
  `task_id` int(11) NOT NULL,
  `order` int(11) NOT NULL,
  `delay` int(11) NOT NULL,
  `embedded_delay` int(11) NOT NULL,
  `instruction_viewed` int(11) NOT NULL,
  `date_completed` date DEFAULT NULL,
  `total_time` bigint(20) DEFAULT NULL,
  PRIMARY KEY (`session_task_id`),
  KEY `datacollector_session_task_6b4dc4c3` (`session_id`),
  KEY `datacollector_session_task_3ff01bab` (`task_id`),
  CONSTRAINT `session_id_refs_session_id_33945942` FOREIGN KEY (`session_id`) REFERENCES `datacollector_session` (`session_id`),
  CONSTRAINT `task_id_refs_task_id_d4ece4a` FOREIGN KEY (`task_id`) REFERENCES `datacollector_task` (`task_id`)
) ENGINE=InnoDB AUTO_INCREMENT=26407 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `datacollector_session_task_instance`
--

DROP TABLE IF EXISTS `datacollector_session_task_instance`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `datacollector_session_task_instance` (
  `session_task_instance_id` int(11) NOT NULL AUTO_INCREMENT,
  `session_task_id` int(11) NOT NULL,
  PRIMARY KEY (`session_task_instance_id`),
  KEY `datacollector_session_task_instance_5df83440` (`session_task_id`),
  CONSTRAINT `session_task_id_refs_session_task_id_145d3494` FOREIGN KEY (`session_task_id`) REFERENCES `datacollector_session_task` (`session_task_id`)
) ENGINE=InnoDB AUTO_INCREMENT=138490 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `datacollector_session_task_instance_value`
--

DROP TABLE IF EXISTS `datacollector_session_task_instance_value`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `datacollector_session_task_instance_value` (
  `session_task_instance_value_id` int(11) NOT NULL AUTO_INCREMENT,
  `session_task_instance_id` int(11) NOT NULL,
  `task_field_id` int(11) NOT NULL,
  `value` longtext NOT NULL,
  `value_display` longtext,
  `difficulty_id` int(11) NOT NULL,
  PRIMARY KEY (`session_task_instance_value_id`),
  KEY `datacollector_session_task_instance_value_1580a68b` (`session_task_instance_id`),
  KEY `datacollector_session_task_instance_value_7f083cdc` (`task_field_id`),
  KEY `datacollector_session_task_instance_value_269a6dbd` (`difficulty_id`),
  CONSTRAINT `difficulty_id_refs_value_difficulty_id_4e2617bf` FOREIGN KEY (`difficulty_id`) REFERENCES `datacollector_value_difficulty` (`value_difficulty_id`),
  CONSTRAINT `session_task_instance_id_refs_session_task_instance_id_103baf3d` FOREIGN KEY (`session_task_instance_id`) REFERENCES `datacollector_session_task_instance` (`session_task_instance_id`),
  CONSTRAINT `task_field_id_refs_task_field_id_4993d500` FOREIGN KEY (`task_field_id`) REFERENCES `datacollector_task_field` (`task_field_id`)
) ENGINE=InnoDB AUTO_INCREMENT=204974 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `datacollector_session_type`
--

DROP TABLE IF EXISTS `datacollector_session_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `datacollector_session_type` (
  `session_type_id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `text_only` int(11) NOT NULL,
  PRIMARY KEY (`session_type_id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `datacollector_settings`
--

DROP TABLE IF EXISTS `datacollector_settings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `datacollector_settings` (
  `setting_name` varchar(50) NOT NULL,
  `setting_value` varchar(50) NOT NULL,
  PRIMARY KEY (`setting_name`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `datacollector_subject`
--

DROP TABLE IF EXISTS `datacollector_subject`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `datacollector_subject` (
  `user_id` int(11) NOT NULL,
  `date_created` date DEFAULT NULL,
  `date_consent_submitted` date DEFAULT NULL,
  `date_demographics_submitted` date DEFAULT NULL,
  `date_last_session_access` date DEFAULT NULL,
  `consent_alternate` int(11) DEFAULT NULL,
  `email_validated` int(1) DEFAULT NULL,
  `email_token` varchar(1000) DEFAULT NULL,
  `preference_email_reminders` int(11) DEFAULT NULL,
  `preference_email_reminders_freq` int(11) DEFAULT NULL,
  `email_reminders` varchar(100) DEFAULT NULL,
  `preference_email_updates` int(11) NOT NULL,
  `email_updates` varchar(100) DEFAULT NULL,
  `preference_public_release` int(11) NOT NULL,
  `preference_prizes` int(11) DEFAULT NULL,
  `email_prizes` varchar(100) DEFAULT NULL,
  `gender_id` varchar(1) DEFAULT NULL,
  `dob` date DEFAULT NULL,
  `origin_country_id` int(11) DEFAULT NULL,
  `origin_country_province_id` int(11) DEFAULT NULL,
  `residence_country_id` int(11) DEFAULT NULL,
  `education_level_id` int(11) DEFAULT NULL,
  `dementia_med` int(1) DEFAULT NULL,
  `smoker_recent` int(1) DEFAULT NULL,
  `auth_token` varchar(1000) DEFAULT NULL,
  `auth_token_expirydate` datetime DEFAULT NULL,
  `phone_pin` varchar(4) DEFAULT NULL,
  PRIMARY KEY (`user_id`),
  KEY `datacollector_subject_115dbd13` (`gender_id`),
  KEY `datacollector_subject_1eca0e1b` (`origin_country_id`),
  KEY `datacollector_subject_72c23619` (`origin_country_province_id`),
  KEY `datacollector_subject_3a2c1672` (`education_level_id`),
  CONSTRAINT `education_level_id_refs_education_level_id_154875c6` FOREIGN KEY (`education_level_id`) REFERENCES `datacollector_education_level` (`education_level_id`),
  CONSTRAINT `gender_id_refs_gender_id_2b74fe21` FOREIGN KEY (`gender_id`) REFERENCES `datacollector_gender` (`gender_id`),
  CONSTRAINT `origin_country_id_refs_country_id_50d69a0f` FOREIGN KEY (`origin_country_id`) REFERENCES `datacollector_country` (`country_id`),
  CONSTRAINT `origin_country_province_id_refs_country_province_id_6e53308b` FOREIGN KEY (`origin_country_province_id`) REFERENCES `datacollector_country_province` (`country_province_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `datacollector_subject_bundle`
--

DROP TABLE IF EXISTS `datacollector_subject_bundle`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `datacollector_subject_bundle` (
  `subject_bundle_id` int(11) NOT NULL AUTO_INCREMENT,
  `subject_id` int(11) NOT NULL,
  `bundle_id` int(11) NOT NULL,
  `active_startdate` date NOT NULL,
  `active_enddate` date DEFAULT NULL,
  `completion_token` varchar(1000) DEFAULT NULL,
  `completion_token_usedate` date DEFAULT NULL,
  `completion_req_sessions` int(11) DEFAULT NULL,
  PRIMARY KEY (`subject_bundle_id`),
  KEY `subject_id` (`subject_id`),
  KEY `bundle_id` (`bundle_id`),
  CONSTRAINT `datacollector_subject_bundle_ibfk_1` FOREIGN KEY (`subject_id`) REFERENCES `datacollector_subject` (`user_id`),
  CONSTRAINT `datacollector_subject_bundle_ibfk_2` FOREIGN KEY (`bundle_id`) REFERENCES `datacollector_bundle` (`bundle_id`)
) ENGINE=InnoDB AUTO_INCREMENT=476 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `datacollector_subject_dementia_type`
--

DROP TABLE IF EXISTS `datacollector_subject_dementia_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `datacollector_subject_dementia_type` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `subject_id` int(11) NOT NULL,
  `dementia_type_id` int(11) DEFAULT NULL,
  `dementia_type_name` varchar(200) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `datacollector_subject_dementia_type_638462f1` (`subject_id`),
  CONSTRAINT `subject_id_refs_user_id_66d3890` FOREIGN KEY (`subject_id`) REFERENCES `datacollector_subject` (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=69 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `datacollector_subject_emails`
--

DROP TABLE IF EXISTS `datacollector_subject_emails`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `datacollector_subject_emails` (
  `email_id` int(11) NOT NULL AUTO_INCREMENT,
  `date_sent` date NOT NULL,
  `subject_id` int(11) NOT NULL,
  `email_from` varchar(100) NOT NULL,
  `email_to` varchar(100) NOT NULL,
  `email_type` varchar(50) NOT NULL,
  `prize_amt` decimal(6,2) DEFAULT NULL,
  PRIMARY KEY (`email_id`),
  KEY `subject_id` (`subject_id`),
  CONSTRAINT `datacollector_subject_emails_ibfk_1` FOREIGN KEY (`subject_id`) REFERENCES `datacollector_subject` (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=3758 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `datacollector_subject_ethnicity`
--

DROP TABLE IF EXISTS `datacollector_subject_ethnicity`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `datacollector_subject_ethnicity` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `subject_id` int(11) NOT NULL,
  `ethnicity_id` int(11) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=556 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `datacollector_subject_gender`
--

DROP TABLE IF EXISTS `datacollector_subject_gender`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `datacollector_subject_gender` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `subject_id` int(11) NOT NULL,
  `gender_id` varchar(1) NOT NULL,
  `gender_name` varchar(200) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `subject_id` (`subject_id`),
  CONSTRAINT `datacollector_subject_gender_ibfk_1` FOREIGN KEY (`subject_id`) REFERENCES `datacollector_subject` (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=149 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `datacollector_subject_language`
--

DROP TABLE IF EXISTS `datacollector_subject_language`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `datacollector_subject_language` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `subject_id` int(11) NOT NULL,
  `language_id` int(11) NOT NULL,
  `level_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `datacollector_subject_language_638462f1` (`subject_id`),
  KEY `datacollector_subject_language_7ab48146` (`language_id`),
  KEY `datacollector_subject_language_340bd28f` (`level_id`),
  CONSTRAINT `language_id_refs_language_id_6b807774` FOREIGN KEY (`language_id`) REFERENCES `datacollector_language` (`language_id`),
  CONSTRAINT `level_id_refs_language_level_id_8ca0f91` FOREIGN KEY (`level_id`) REFERENCES `datacollector_language_level` (`language_level_id`),
  CONSTRAINT `subject_id_refs_user_id_23e6f48b` FOREIGN KEY (`subject_id`) REFERENCES `datacollector_subject` (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1124 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `datacollector_subject_language_oise`
--

DROP TABLE IF EXISTS `datacollector_subject_language_oise`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `datacollector_subject_language_oise` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) DEFAULT NULL,
  `level` tinyint(1) DEFAULT NULL,
  `demographics_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `demographics_id` (`demographics_id`),
  CONSTRAINT `datacollector_subject_language_oise_ibfk_1` FOREIGN KEY (`demographics_id`) REFERENCES `datacollector_demographics_oise` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=310 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `datacollector_subject_notifications`
--

DROP TABLE IF EXISTS `datacollector_subject_notifications`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `datacollector_subject_notifications` (
  `subject_notification_id` int(11) NOT NULL AUTO_INCREMENT,
  `subject_id` int(11) NOT NULL,
  `notification_id` varchar(50) NOT NULL,
  `date_start` date NOT NULL,
  `date_end` date DEFAULT NULL,
  `dismissed` int(11) NOT NULL,
  PRIMARY KEY (`subject_notification_id`),
  KEY `subject_id` (`subject_id`),
  KEY `notification_id` (`notification_id`),
  CONSTRAINT `datacollector_subject_notifications_ibfk_1` FOREIGN KEY (`subject_id`) REFERENCES `datacollector_subject` (`user_id`),
  CONSTRAINT `datacollector_subject_notifications_ibfk_2` FOREIGN KEY (`notification_id`) REFERENCES `datacollector_notification` (`notification_id`)
) ENGINE=InnoDB AUTO_INCREMENT=869 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `datacollector_subject_prizes`
--

DROP TABLE IF EXISTS `datacollector_subject_prizes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `datacollector_subject_prizes` (
  `subject_prize_id` int(11) NOT NULL AUTO_INCREMENT,
  `subject_id` int(11) NOT NULL,
  `prize_id` varchar(50) NOT NULL,
  `date_received` datetime NOT NULL,
  `filename` varchar(200) DEFAULT NULL,
  PRIMARY KEY (`subject_prize_id`),
  KEY `subject_id` (`subject_id`),
  KEY `prize_id` (`prize_id`),
  CONSTRAINT `datacollector_subject_prizes_ibfk_1` FOREIGN KEY (`subject_id`) REFERENCES `datacollector_subject` (`user_id`),
  CONSTRAINT `datacollector_subject_prizes_ibfk_2` FOREIGN KEY (`prize_id`) REFERENCES `datacollector_prize` (`prize_id`)
) ENGINE=InnoDB AUTO_INCREMENT=142 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `datacollector_subject_usabilitysurvey`
--

DROP TABLE IF EXISTS `datacollector_subject_usabilitysurvey`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `datacollector_subject_usabilitysurvey` (
  `subjectsurvey_id` int(11) NOT NULL AUTO_INCREMENT,
  `subject_id` int(11) NOT NULL,
  `question_id` varchar(50) NOT NULL,
  `question` text NOT NULL,
  `question_type` varchar(50) NOT NULL,
  `question_order` int(11) DEFAULT NULL,
  `response_id` longtext,
  `response` text,
  `date_completed` date NOT NULL,
  `usabilitysurvey_type_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`subjectsurvey_id`),
  KEY `subject_id` (`subject_id`),
  CONSTRAINT `datacollector_subject_usabilitysurvey_ibfk_1` FOREIGN KEY (`subject_id`) REFERENCES `datacollector_subject` (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1567 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `datacollector_subject_usabilitysurvey_type`
--

DROP TABLE IF EXISTS `datacollector_subject_usabilitysurvey_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `datacollector_subject_usabilitysurvey_type` (
  `usabilitysurvey_type_id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  PRIMARY KEY (`usabilitysurvey_type_id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `datacollector_task`
--

DROP TABLE IF EXISTS `datacollector_task`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `datacollector_task` (
  `task_id` int(11) NOT NULL AUTO_INCREMENT,
  `name_id` varchar(50) NOT NULL,
  `name` varchar(50) NOT NULL,
  `instruction` longtext NOT NULL,
  `instruction_phone` longtext,
  `default_num_instances` int(11) DEFAULT NULL,
  `default_order` int(11) NOT NULL,
  `is_order_fixed` int(11) NOT NULL,
  `default_delay` int(11) NOT NULL,
  `default_embedded_delay` int(11) NOT NULL,
  `is_active` int(11) NOT NULL,
  PRIMARY KEY (`task_id`)
) ENGINE=InnoDB AUTO_INCREMENT=23 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `datacollector_task_field`
--

DROP TABLE IF EXISTS `datacollector_task_field`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `datacollector_task_field` (
  `task_field_id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `task_id` int(11) NOT NULL,
  `field_type_id` int(11) NOT NULL,
  `field_data_type_id` int(11) NOT NULL,
  `embedded_response` int(11) NOT NULL,
  `keep_visible` int(1) DEFAULT NULL,
  `generate_value` int(1) DEFAULT NULL,
  `assoc_id` int(11) DEFAULT NULL,
  `default_num_instances` int(11) DEFAULT NULL,
  `preserve_order` int(11) DEFAULT NULL,
  PRIMARY KEY (`task_field_id`),
  KEY `datacollector_task_field_3ff01bab` (`task_id`),
  KEY `datacollector_task_field_66db44d3` (`field_type_id`),
  KEY `datacollector_task_field_4ec7af17` (`field_data_type_id`),
  CONSTRAINT `field_data_type_id_refs_field_data_type_id_248e52b8` FOREIGN KEY (`field_data_type_id`) REFERENCES `datacollector_field_data_type` (`field_data_type_id`),
  CONSTRAINT `field_type_id_refs_field_type_id_2256a370` FOREIGN KEY (`field_type_id`) REFERENCES `datacollector_field_type` (`field_type_id`),
  CONSTRAINT `task_id_refs_task_id_2ecd30be` FOREIGN KEY (`task_id`) REFERENCES `datacollector_task` (`task_id`)
) ENGINE=InnoDB AUTO_INCREMENT=62 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `datacollector_task_field_data_attribute`
--

DROP TABLE IF EXISTS `datacollector_task_field_data_attribute`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `datacollector_task_field_data_attribute` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `task_field_id` int(11) NOT NULL,
  `name` varchar(200) NOT NULL,
  `value` varchar(200) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `datacollector_task_field_data_attribute_7f083cdc` (`task_field_id`),
  CONSTRAINT `task_field_id_refs_task_field_id_1870c6c2` FOREIGN KEY (`task_field_id`) REFERENCES `datacollector_task_field` (`task_field_id`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `datacollector_task_field_value`
--

DROP TABLE IF EXISTS `datacollector_task_field_value`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `datacollector_task_field_value` (
  `task_field_value_id` int(11) NOT NULL AUTO_INCREMENT,
  `task_field_id` int(11) NOT NULL,
  `value` longtext NOT NULL,
  `value_display` longtext,
  `difficulty_id` int(11) NOT NULL,
  `assoc_id` int(11) DEFAULT NULL,
  `response_expected` longtext,
  PRIMARY KEY (`task_field_value_id`),
  KEY `datacollector_task_field_value_7f083cdc` (`task_field_id`),
  KEY `datacollector_task_field_value_269a6dbd` (`difficulty_id`),
  CONSTRAINT `difficulty_id_refs_value_difficulty_id_2dbee21c` FOREIGN KEY (`difficulty_id`) REFERENCES `datacollector_value_difficulty` (`value_difficulty_id`),
  CONSTRAINT `task_field_id_refs_task_field_id_463b49dd` FOREIGN KEY (`task_field_id`) REFERENCES `datacollector_task_field` (`task_field_id`)
) ENGINE=InnoDB AUTO_INCREMENT=5493 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `datacollector_value_difficulty`
--

DROP TABLE IF EXISTS `datacollector_value_difficulty`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `datacollector_value_difficulty` (
  `value_difficulty_id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  PRIMARY KEY (`value_difficulty_id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `django_admin_log`
--

DROP TABLE IF EXISTS `django_admin_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_admin_log` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `action_time` datetime NOT NULL,
  `user_id` int(11) NOT NULL,
  `content_type_id` int(11) DEFAULT NULL,
  `object_id` longtext,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint(5) unsigned NOT NULL,
  `change_message` longtext NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin_log_403f60f` (`user_id`),
  KEY `django_admin_log_1bb8f392` (`content_type_id`),
  CONSTRAINT `content_type_id_refs_id_288599e6` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `user_id_refs_id_c8665aa` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=78 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `django_content_type`
--

DROP TABLE IF EXISTS `django_content_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_content_type` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `app_label` (`app_label`,`model`)
) ENGINE=InnoDB AUTO_INCREMENT=50 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `django_migrations`
--

DROP TABLE IF EXISTS `django_migrations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_migrations` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `django_session`
--

DROP TABLE IF EXISTS `django_session`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_3da3d3d8` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `django_site`
--

DROP TABLE IF EXISTS `django_site`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_site` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `domain` varchar(100) NOT NULL,
  `name` varchar(50) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2018-09-23  0:32:49
