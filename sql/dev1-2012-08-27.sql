-- MySQL dump 10.13  Distrib 5.5.22, for debian-linux-gnu (x86_64)
--
-- Host: localhost    Database: dev1
-- ------------------------------------------------------
-- Server version	5.5.22-0ubuntu1

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
-- Table structure for table `admin_tools`
--

DROP TABLE IF EXISTS `admin_tools`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `admin_tools` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `admin_tools`
--

LOCK TABLES `admin_tools` WRITE;
/*!40000 ALTER TABLE `admin_tools` DISABLE KEYS */;
/*!40000 ALTER TABLE `admin_tools` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_contenttype`
--

DROP TABLE IF EXISTS `auth_contenttype`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_contenttype` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `image` varchar(100) NOT NULL,
  `model_name` varchar(50) NOT NULL,
  `module_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `auth_contenttype_f53ed95e` (`module_id`)
) ENGINE=MyISAM AUTO_INCREMENT=10 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_contenttype`
--

LOCK TABLES `auth_contenttype` WRITE;
/*!40000 ALTER TABLE `auth_contenttype` DISABLE KEYS */;
INSERT INTO `auth_contenttype` VALUES (1,'permission','','',1),(2,'group','icons/group.png','',1),(3,'user','icons/user.png','',1),(4,'property','icons/property.png','',2),(5,'log','icons/logging.png','',3),(6,'citizen','icons/citizen.png','',4),(9,'tax','icons/tax.png','',5);
/*!40000 ALTER TABLE `auth_contenttype` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_group`
--

DROP TABLE IF EXISTS `auth_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_group` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(80) NOT NULL,
  `i_status` varchar(10) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=MyISAM AUTO_INCREMENT=7 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group`
--

LOCK TABLES `auth_group` WRITE;
/*!40000 ALTER TABLE `auth_group` DISABLE KEYS */;
INSERT INTO `auth_group` VALUES (1,'testgroup','active'),(2,'dev','active');
/*!40000 ALTER TABLE `auth_group` ENABLE KEYS */;
UNLOCK TABLES;

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
  KEY `auth_group_permissions_bda51c3c` (`group_id`),
  KEY `auth_group_permissions_1e014c8f` (`permission_id`)
) ENGINE=MyISAM AUTO_INCREMENT=56 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group_permissions`
--

LOCK TABLES `auth_group_permissions` WRITE;
/*!40000 ALTER TABLE `auth_group_permissions` DISABLE KEYS */;
INSERT INTO `auth_group_permissions` VALUES (1,1,17),(2,1,1),(3,2,1),(4,2,2),(5,2,3),(6,2,4),(7,2,5),(8,2,6),(9,2,7),(10,2,8),(11,2,9),(12,2,10),(13,2,11),(14,2,12),(15,2,13),(16,2,14),(17,2,15),(18,2,16),(19,2,17),(20,2,18),(21,2,19),(22,2,20),(23,2,21),(24,2,22),(25,2,23),(26,2,24),(27,2,25),(28,2,26),(29,2,27),(30,2,28),(31,2,29),(32,2,30),(33,2,31),(34,2,32),(35,2,36),(36,2,35),(37,2,34),(38,2,33);
/*!40000 ALTER TABLE `auth_group_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_module`
--

DROP TABLE IF EXISTS `auth_module`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_module` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `image` varchar(100) NOT NULL,
  `description` varchar(200) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=6 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_module`
--

LOCK TABLES `auth_module` WRITE;
/*!40000 ALTER TABLE `auth_module` DISABLE KEYS */;
INSERT INTO `auth_module` VALUES (1,'auth','',''),(2,'property','',''),(3,'log','',''),(4,'citizen','',''),(5,'tax','','');
/*!40000 ALTER TABLE `auth_module` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_permission`
--

DROP TABLE IF EXISTS `auth_permission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_permission` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `codename` varchar(50) NOT NULL,
  `contenttype_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `auth_permission_a184c428` (`contenttype_id`)
) ENGINE=MyISAM AUTO_INCREMENT=37 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_permission`
--

LOCK TABLES `auth_permission` WRITE;
/*!40000 ALTER TABLE `auth_permission` DISABLE KEYS */;
INSERT INTO `auth_permission` VALUES (1,'Can view citizen','view_citizen',6),(2,'Can add citizen','add_citizen',6),(3,'Can change citizen','change_citizen',6),(4,'Can delete citizen','delete_citizen',6),(5,'Can view group','view_group',2),(6,'Can add group','add_group',2),(7,'Can change group','change_group',2),(8,'Can delete group','delete_group',2),(9,'Can view log','view_log',5),(10,'Can add log','add_log',5),(11,'Can change log','change_log',5),(12,'Can delete log','delete_log',5),(13,'Can view permission','view_permission',1),(14,'Can add permission','add_permission',1),(15,'Can change permission','change_permission',1),(16,'Can delete permission','delete_permission',1),(17,'Can view property','view_property',4),(18,'Can add property','add_property',4),(19,'Can change property','change_property',4),(20,'Can delete property','delete_property',4),(21,'Can view user','view_user',3),(22,'Can add user','add_user',3),(23,'Can change user','change_user',3),(24,'Can delete user','delete_user',3),(36,'Can delete tax','delete_tax',9),(35,'Can change tax','change_tax',9),(34,'Can add tax','add_tax',9),(33,'Can view tax','view_tax',9);
/*!40000 ALTER TABLE `auth_permission` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user`
--

DROP TABLE IF EXISTS `auth_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(30) NOT NULL,
  `firstname` varchar(30) NOT NULL,
  `lastname` varchar(30) NOT NULL,
  `contactnumber` varchar(30) NOT NULL,
  `email` varchar(75) NOT NULL,
  `password` varchar(128) NOT NULL,
  `active` tinyint(1) NOT NULL,
  `superuser` tinyint(1) NOT NULL,
  `lastlogin` datetime NOT NULL,
  `datejoined` datetime NOT NULL,
  `i_status` varchar(10) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=MyISAM AUTO_INCREMENT=10 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user`
--

LOCK TABLES `auth_user` WRITE;
/*!40000 ALTER TABLE `auth_user` DISABLE KEYS */;
INSERT INTO `auth_user` VALUES (1,'Kongluan Lin','Kongluan','Lin','','linkongluan@gmail.com','642841ac5168288de710c090272fdcba',1,1,'2012-08-21 04:59:17','2012-08-21 04:59:17','active'),(9,'PetersWang','Peters','Wang','','p@wang.com','83878c91171338902e0fe0fb97a8c47a',1,0,'2012-08-24 06:59:35','2012-08-24 06:59:35','active'),(3,'Shane Dale','Shane','Dale','','shane@propertymode.com.au','1e113fa10ad2e32cac8043b85e99a88d',1,1,'2012-08-21 04:59:17','2012-08-21 04:59:17','active'),(4,'Sandra Macnaughton','Sandra','Macnaughton','','sandra@propertymode.com.au','a921e09118e627ef733a8cc7f3ce835c',1,1,'2012-08-21 04:59:17','2012-08-21 04:59:17','active'),(5,'Justin Hopley','justin','Hopley','','justin@propertymode.com.au','09d914bbbd32fa8145d374c2e82ef7b5',1,1,'2012-08-21 04:59:17','2012-08-21 04:59:17','active'),(6,'peterpeter','peter','peter','','p@p.com','83878c91171338902e0fe0fb97a8c47a',1,1,'2012-08-21 06:20:21','2012-08-21 06:20:21','active'),(7,'adriandinc','adrian','dinc','','adrian@surrondpix.com.au','f22571ad0aacace295ee3f8940aa7ac5',1,1,'2012-08-23 05:43:38','2012-08-23 05:43:38','active');
/*!40000 ALTER TABLE `auth_user` ENABLE KEYS */;
UNLOCK TABLES;

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
  KEY `auth_user_groups_fbfc09f1` (`user_id`),
  KEY `auth_user_groups_bda51c3c` (`group_id`)
) ENGINE=MyISAM AUTO_INCREMENT=5 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user_groups`
--

LOCK TABLES `auth_user_groups` WRITE;
/*!40000 ALTER TABLE `auth_user_groups` DISABLE KEYS */;
INSERT INTO `auth_user_groups` VALUES (4,9,2),(3,7,2);
/*!40000 ALTER TABLE `auth_user_groups` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user_permissions`
--

DROP TABLE IF EXISTS `auth_user_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_user_permissions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`,`permission_id`),
  KEY `auth_user_permissions_fbfc09f1` (`user_id`),
  KEY `auth_user_permissions_1e014c8f` (`permission_id`)
) ENGINE=MyISAM AUTO_INCREMENT=3 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user_permissions`
--

LOCK TABLES `auth_user_permissions` WRITE;
/*!40000 ALTER TABLE `auth_user_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_user_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `citizen_citizen`
--

DROP TABLE IF EXISTS `citizen_citizen`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `citizen_citizen` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `firstname` varchar(50) NOT NULL,
  `lastname` varchar(50) NOT NULL,
  `citizenid` int(11) NOT NULL,
  `i_status` varchar(10) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `citizenid` (`citizenid`)
) ENGINE=MyISAM AUTO_INCREMENT=3 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `citizen_citizen`
--

LOCK TABLES `citizen_citizen` WRITE;
/*!40000 ALTER TABLE `citizen_citizen` DISABLE KEYS */;
INSERT INTO `citizen_citizen` VALUES (1,'Mark','Tong',12345,'active'),(2,'Paul','Kennardy',510134,'active');
/*!40000 ALTER TABLE `citizen_citizen` ENABLE KEYS */;
UNLOCK TABLES;

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
  KEY `django_session_c25c2c28` (`expire_date`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_session`
--

LOCK TABLES `django_session` WRITE;
/*!40000 ALTER TABLE `django_session` DISABLE KEYS */;
INSERT INTO `django_session` VALUES ('b41341d2bda060bea4b11ee95a598a92','OGU3M2RjOGNmNzNmOGVhMGZlY2QzNGQ0MTczMmE5YWRkMzkwOTMyOTqAAn1xAVUEdXNlcnECY2Nv\ncHlfcmVnCl9yZWNvbnN0cnVjdG9yCnEDY2F1dGgubW9kZWxzClVzZXIKcQRjX19idWlsdGluX18K\nb2JqZWN0CnEFTodScQZ9cQcoVQh1c2VybmFtZXEIWAwAAABLb25nbHVhbiBMaW5VCXN1cGVydXNl\ncnEJiFUJZmlyc3RuYW1lcQpYCAAAAEtvbmdsdWFuVQhsYXN0bmFtZXELWAMAAABMaW5VCGlfc3Rh\ndHVzcQxYBgAAAGFjdGl2ZVUGX3N0YXRlcQ1jZGphbmdvLmRiLm1vZGVscy5iYXNlCk1vZGVsU3Rh\ndGUKcQ4pgXEPfXEQKFUGYWRkaW5ncRGJVQJkYnESVQdkZWZhdWx0cRN1YlUKZGF0ZWpvaW5lZHEU\nY2RhdGV0aW1lCmRhdGV0aW1lCnEVVQoH3AgVBDsRAAAAY3B5dHoKX1VUQwpxFilScReGUnEYVQVl\nbWFpbHEZWBUAAABsaW5rb25nbHVhbkBnbWFpbC5jb21VDWNvbnRhY3RudW1iZXJxGlgAAAAAVQls\nYXN0bG9naW5xG2gVVQoH3AgVBDsRAAAAaBeGUnEcVQZhY3RpdmVxHYhVCHBhc3N3b3JkcR5YIAAA\nADY0Mjg0MWFjNTE2ODI4OGRlNzEwYzA5MDI3MmZkY2JhVQJpZHEfigEBdWJzLg==\n','2012-09-09 23:06:59'),('e32b211419a6c321e29ebe8e92c3775d','ZDM3NDVhOGEwOGViMWZiN2IzYzAzNjVhODBkYmNhNGQ1ZjliOGI5MzqAAn1xAVUEdXNlcnECY2Nv\ncHlfcmVnCl9yZWNvbnN0cnVjdG9yCnEDY2F1dGgubW9kZWxzClVzZXIKcQRjX19idWlsdGluX18K\nb2JqZWN0CnEFTodScQZ9cQcoVQh1c2VybmFtZXEIWA0AAABKdXN0aW4gSG9wbGV5VQlzdXBlcnVz\nZXJxCYhVCWZpcnN0bmFtZXEKWAYAAABqdXN0aW5VCGxhc3RuYW1lcQtYBgAAAEhvcGxleVUIaV9z\ndGF0dXNxDFgGAAAAYWN0aXZlVQZfc3RhdGVxDWNkamFuZ28uZGIubW9kZWxzLmJhc2UKTW9kZWxT\ndGF0ZQpxDimBcQ99cRAoVQZhZGRpbmdxEYlVAmRicRJVB2RlZmF1bHRxE3ViVQpkYXRlam9pbmVk\ncRRjZGF0ZXRpbWUKZGF0ZXRpbWUKcRVVCgfcCBUEOxEAAABjcHl0egpfVVRDCnEWKVJxF4ZScRhV\nBWVtYWlscRlYGgAAAGp1c3RpbkBwcm9wZXJ0eW1vZGUuY29tLmF1VQ1jb250YWN0bnVtYmVycRpY\nAAAAAFUJbGFzdGxvZ2lucRtoFVUKB9wIFQQ7EQAAAGgXhlJxHFUGYWN0aXZlcR2IVQhwYXNzd29y\nZHEeWCAAAAAwOWQ5MTRiYmJkMzJmYTgxNDVkMzc0YzJlODJlZjdiNVUCaWRxH4oBBXVicy4=\n','2012-09-06 05:38:49'),('63100f433db9ea8b046061bd8c84b20e','ZWM1ZDFmYWNlNWNmOGExMWI4YjVmYjM1NjRlMjYzMjdjMTExYzlmNTqAAn1xAVUEdXNlcnECY2Nv\ncHlfcmVnCl9yZWNvbnN0cnVjdG9yCnEDY2F1dGgubW9kZWxzClVzZXIKcQRjX19idWlsdGluX18K\nb2JqZWN0CnEFTodScQZ9cQcoVQh1c2VybmFtZXEIWAoAAABwZXRlcnBldGVyVQlzdXBlcnVzZXJx\nCYhVCWZpcnN0bmFtZXEKWAUAAABwZXRlclUIbGFzdG5hbWVxC1gFAAAAcGV0ZXJVCGlfc3RhdHVz\ncQxYBgAAAGFjdGl2ZVUGX3N0YXRlcQ1jZGphbmdvLmRiLm1vZGVscy5iYXNlCk1vZGVsU3RhdGUK\ncQ4pgXEPfXEQKFUGYWRkaW5ncRGJVQJkYnESVQdkZWZhdWx0cRN1YlUKZGF0ZWpvaW5lZHEUY2Rh\ndGV0aW1lCmRhdGV0aW1lCnEVVQoH3AgVBhQVAAAAY3B5dHoKX1VUQwpxFilScReGUnEYVQVlbWFp\nbHEZWAcAAABwQHAuY29tVQ1jb250YWN0bnVtYmVycRpYAAAAAFUJbGFzdGxvZ2lucRtoFVUKB9wI\nFQYUFQAAAGgXhlJxHFUGYWN0aXZlcR2IVQhwYXNzd29yZHEeWCAAAAA4Mzg3OGM5MTE3MTMzODkw\nMmUwZmUwZmI5N2E4YzQ3YVUCaWRxH4oBBnVicy4=\n','2012-09-04 06:22:56'),('3b4788ffdb40b2c0768ac8812a101ce1','OGVkNTA0Y2E1OWVjNDNmZTFhNDM4YWUxZWY2MDFmMTFkMGQyMTc2MjqAAn1xAS4=\n','2012-09-04 07:00:23'),('9c4309e5401a746ffde412be5f32719b','OGU3M2RjOGNmNzNmOGVhMGZlY2QzNGQ0MTczMmE5YWRkMzkwOTMyOTqAAn1xAVUEdXNlcnECY2Nv\ncHlfcmVnCl9yZWNvbnN0cnVjdG9yCnEDY2F1dGgubW9kZWxzClVzZXIKcQRjX19idWlsdGluX18K\nb2JqZWN0CnEFTodScQZ9cQcoVQh1c2VybmFtZXEIWAwAAABLb25nbHVhbiBMaW5VCXN1cGVydXNl\ncnEJiFUJZmlyc3RuYW1lcQpYCAAAAEtvbmdsdWFuVQhsYXN0bmFtZXELWAMAAABMaW5VCGlfc3Rh\ndHVzcQxYBgAAAGFjdGl2ZVUGX3N0YXRlcQ1jZGphbmdvLmRiLm1vZGVscy5iYXNlCk1vZGVsU3Rh\ndGUKcQ4pgXEPfXEQKFUGYWRkaW5ncRGJVQJkYnESVQdkZWZhdWx0cRN1YlUKZGF0ZWpvaW5lZHEU\nY2RhdGV0aW1lCmRhdGV0aW1lCnEVVQoH3AgVBDsRAAAAY3B5dHoKX1VUQwpxFilScReGUnEYVQVl\nbWFpbHEZWBUAAABsaW5rb25nbHVhbkBnbWFpbC5jb21VDWNvbnRhY3RudW1iZXJxGlgAAAAAVQls\nYXN0bG9naW5xG2gVVQoH3AgVBDsRAAAAaBeGUnEcVQZhY3RpdmVxHYhVCHBhc3N3b3JkcR5YIAAA\nADY0Mjg0MWFjNTE2ODI4OGRlNzEwYzA5MDI3MmZkY2JhVQJpZHEfigEBdWJzLg==\n','2012-09-06 01:44:45');
/*!40000 ALTER TABLE `django_session` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `jtax_assignedvalue`
--

DROP TABLE IF EXISTS `jtax_assignedvalue`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `jtax_assignedvalue` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `PlotId` int(11) NOT NULL,
  `AssignedValueAmount` int(11) NOT NULL,
  `AssignedValueDateTime` datetime NOT NULL,
  `AssignedValueAmountCurrencey` varchar(4) NOT NULL,
  `AssignedValueStaffId` int(11) NOT NULL,
  `AssignedValueCitizenId` int(11) NOT NULL,
  `AssignedValueValidUntil` datetime NOT NULL,
  `AssignedValueOnHold` varchar(4) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `jtax_assignedvalue`
--

LOCK TABLES `jtax_assignedvalue` WRITE;
/*!40000 ALTER TABLE `jtax_assignedvalue` DISABLE KEYS */;
/*!40000 ALTER TABLE `jtax_assignedvalue` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `jtax_declaredvalue`
--

DROP TABLE IF EXISTS `jtax_declaredvalue`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `jtax_declaredvalue` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `PlotId` int(11) NOT NULL,
  `DeclairedValueCitizenId` int(11) NOT NULL,
  `DeclairedValueAmount` int(11) NOT NULL,
  `DeclairedValueAmountCurrencey` varchar(4) NOT NULL,
  `DeclairedValueDateTime` datetime NOT NULL,
  `DeclairedValueStaffId` int(11) NOT NULL,
  `DeclairedValueAccepted` varchar(4) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `jtax_declaredvalue`
--

LOCK TABLES `jtax_declaredvalue` WRITE;
/*!40000 ALTER TABLE `jtax_declaredvalue` DISABLE KEYS */;
/*!40000 ALTER TABLE `jtax_declaredvalue` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `jtax_declaredvaluemedia`
--

DROP TABLE IF EXISTS `jtax_declaredvaluemedia`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `jtax_declaredvaluemedia` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `DeclaredValueId_id` int(11) NOT NULL,
  `DeclaredValueMediaType` varchar(4) NOT NULL,
  `DeclaredValueMediaFile` varchar(100) NOT NULL,
  `DelcaredValueMediaStaffId` int(11) NOT NULL,
  `DeclaredValueMediaDateTime` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `jtax_declaredvaluemedia_7a215869` (`DeclaredValueId_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `jtax_declaredvaluemedia`
--

LOCK TABLES `jtax_declaredvaluemedia` WRITE;
/*!40000 ALTER TABLE `jtax_declaredvaluemedia` DISABLE KEYS */;
/*!40000 ALTER TABLE `jtax_declaredvaluemedia` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `jtax_declaredvaluenotes`
--

DROP TABLE IF EXISTS `jtax_declaredvaluenotes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `jtax_declaredvaluenotes` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `DeclaredValueId_id` int(11) NOT NULL,
  `DeclaredValueNoteStaffId` int(11) NOT NULL,
  `DeclaredValueNote` longtext NOT NULL,
  `DeclaredValueNoteDateTime` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `jtax_declaredvaluenotes_7a215869` (`DeclaredValueId_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `jtax_declaredvaluenotes`
--

LOCK TABLES `jtax_declaredvaluenotes` WRITE;
/*!40000 ALTER TABLE `jtax_declaredvaluenotes` DISABLE KEYS */;
/*!40000 ALTER TABLE `jtax_declaredvaluenotes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `jtax_landrentaltax`
--

DROP TABLE IF EXISTS `jtax_landrentaltax`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `jtax_landrentaltax` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `PlotId` int(11) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `jtax_landrentaltax`
--

LOCK TABLES `jtax_landrentaltax` WRITE;
/*!40000 ALTER TABLE `jtax_landrentaltax` DISABLE KEYS */;
/*!40000 ALTER TABLE `jtax_landrentaltax` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `jtax_landrentaltaxmedia`
--

DROP TABLE IF EXISTS `jtax_landrentaltaxmedia`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `jtax_landrentaltaxmedia` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `LandRentalTaxId_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `jtax_landrentaltaxmedia_7ac1ad2c` (`LandRentalTaxId_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `jtax_landrentaltaxmedia`
--

LOCK TABLES `jtax_landrentaltaxmedia` WRITE;
/*!40000 ALTER TABLE `jtax_landrentaltaxmedia` DISABLE KEYS */;
/*!40000 ALTER TABLE `jtax_landrentaltaxmedia` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `jtax_landrentaltaxnotes`
--

DROP TABLE IF EXISTS `jtax_landrentaltaxnotes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `jtax_landrentaltaxnotes` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `LandRentalTaxId_id` int(11) NOT NULL,
  `LandRentalTaxNoteStaffId` int(11) NOT NULL,
  `LandRentalTaxNote` longtext NOT NULL,
  `LandRentalTaxNoteDateTime` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `jtax_landrentaltaxnotes_7ac1ad2c` (`LandRentalTaxId_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `jtax_landrentaltaxnotes`
--

LOCK TABLES `jtax_landrentaltaxnotes` WRITE;
/*!40000 ALTER TABLE `jtax_landrentaltaxnotes` DISABLE KEYS */;
/*!40000 ALTER TABLE `jtax_landrentaltaxnotes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `jtax_rentalincometax`
--

DROP TABLE IF EXISTS `jtax_rentalincometax`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `jtax_rentalincometax` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `PlotId` int(11) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `jtax_rentalincometax`
--

LOCK TABLES `jtax_rentalincometax` WRITE;
/*!40000 ALTER TABLE `jtax_rentalincometax` DISABLE KEYS */;
/*!40000 ALTER TABLE `jtax_rentalincometax` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `jtax_rentalincometaxnotes`
--

DROP TABLE IF EXISTS `jtax_rentalincometaxnotes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `jtax_rentalincometaxnotes` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `rentalIncomeTaxId_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `jtax_rentalincometaxnotes_9fd1f59c` (`rentalIncomeTaxId_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `jtax_rentalincometaxnotes`
--

LOCK TABLES `jtax_rentalincometaxnotes` WRITE;
/*!40000 ALTER TABLE `jtax_rentalincometaxnotes` DISABLE KEYS */;
/*!40000 ALTER TABLE `jtax_rentalincometaxnotes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `log_log`
--

DROP TABLE IF EXISTS `log_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `log_log` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `transactionid` int(11) NOT NULL,
  `userid` int(11) NOT NULL,
  `plotid` int(11) DEFAULT NULL,
  `tids` varchar(200) DEFAULT NULL,
  `username` varchar(100) NOT NULL,
  `table` varchar(100) DEFAULT NULL,
  `datetime` datetime NOT NULL,
  `olddata` varchar(1000) DEFAULT NULL,
  `newdata` varchar(1000) DEFAULT NULL,
  `message` varchar(1000) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=35 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `log_log`
--

LOCK TABLES `log_log` WRITE;
/*!40000 ALTER TABLE `log_log` DISABLE KEYS */;
INSERT INTO `log_log` VALUES (1,1,1,NULL,NULL,'Kongluan Lin','auth_user','2012-08-21 06:20:30','','','view User [peterpeter]'),(2,2,1,NULL,NULL,'Kongluan Lin','auth_user','2012-08-21 06:20:35','{\'username\': u\'peterpeter\', \'superuser\': False, \'groups\': [], \'firstname\': u\'peter\', \'lastname\': u\'peter\', \'i_status\': u\'active\', \'datejoined\': \'2012-08-21 06:20:21\', \'email\': u\'p@p.com\', \'contactnumber\': u\'\', \'lastlogin\': \'2012-08-21 06:20:21\', \'active\': True, \'password\': u\'020e36ec80045462f13c33d190eb7b6f\', \'id\': 6L, \'permissions\': []}','{\'username\': u\'peterpeter\', \'superuser\': False, \'groups\': [], \'firstname\': u\'peter\', \'lastname\': u\'peter\', \'i_status\': u\'active\', \'datejoined\': \'2012-08-21 06:20:21\', \'email\': u\'p@p.com\', \'contactnumber\': u\'\', \'lastlogin\': \'2012-08-21 06:20:21\', \'active\': True, \'password\': \'83878c91171338902e0fe0fb97a8c47a\', \'id\': 6L, \'permissions\': []}',' change password from \'020e36ec80045462f13c33d190eb7b6f\' to \'83878c91171338902e0fe0fb97a8c47a\' on User [peterpeter]'),(3,3,5,NULL,NULL,'justin Hopley','auth_user','2012-08-23 05:43:46','','','view User [adriandinc]'),(4,4,5,NULL,NULL,'justin Hopley','auth_user','2012-08-23 05:43:54','{\'username\': u\'adriandinc\', \'superuser\': False, \'groups\': [2L], \'firstname\': u\'adrian\', \'lastname\': u\'dinc\', \'i_status\': u\'active\', \'datejoined\': \'2012-08-23 05:43:38\', \'email\': u\'adrian@surrondpix.com.au\', \'contactnumber\': u\'\', \'lastlogin\': \'2012-08-23 05:43:38\', \'active\': True, \'password\': u\'66e5780a22508bad65b615ca6c4d709d\', \'id\': 7L, \'permissions\': []}','{\'username\': u\'adriandinc\', \'superuser\': True, \'groups\': [2L], \'firstname\': u\'adrian\', \'lastname\': u\'dinc\', \'i_status\': u\'active\', \'datejoined\': \'2012-08-23 05:43:38\', \'email\': u\'adrian@surrondpix.com.au\', \'contactnumber\': u\'\', \'lastlogin\': \'2012-08-23 05:43:38\', \'active\': True, \'password\': \'f22571ad0aacace295ee3f8940aa7ac5\', \'id\': 7L, \'permissions\': []}',' change superuser from \'False\' to \'True\', change password from \'66e5780a22508bad65b615ca6c4d709d\' to \'f22571ad0aacace295ee3f8940aa7ac5\' on User [adriandinc]'),(5,5,1,NULL,NULL,'Kongluan Lin','property_property','2012-08-23 07:13:52','','{\'i_status\': \'active\', \'citizens\': [], \'plotid\': 8221, \'suburb\': u\'Parramatta\', \'streetno\': 152, \'boundary\': 83L, \'id\': 83L, \'streetname\': u\'Little Street\'}','add Property [152 Little Street, Parramatta]'),(6,6,1,NULL,NULL,'Kongluan Lin','auth_group','2012-08-24 04:46:04','','','view Group [testgroup3]'),(7,7,1,NULL,NULL,'Kongluan Lin','auth_group','2012-08-24 04:46:11','{\'i_status\': u\'active\', \'permissions\': [19L, 20L, 21L], \'id\': 3L, \'name\': u\'testgroup3\'}','{\'i_status\': u\'active\', \'permissions\': [19L, 20L], \'id\': 3L, \'name\': u\'testgroup3\'}',' remove permissions [\'Can view user\'] on Group [testgroup3]'),(8,8,1,NULL,NULL,'Kongluan Lin','auth_user','2012-08-24 04:51:33','','','view User [WongLee]'),(9,9,1,NULL,NULL,'Kongluan Lin','auth_user','2012-08-24 04:52:10','{\'username\': u\'WongLee\', \'superuser\': False, \'groups\': [], \'firstname\': u\'Wong\', \'lastname\': u\'Lee\', \'i_status\': u\'active\', \'datejoined\': \'2012-08-24 04:50:23\', \'email\': u\'wlee@gmail.com\', \'contactnumber\': u\'\', \'lastlogin\': \'2012-08-24 04:50:23\', \'active\': True, \'password\': u\'c1ba3a655c3707af46e1d22daacd7a18\', \'id\': 8L, \'permissions\': []}','{\'username\': u\'WongLee\', \'superuser\': False, \'groups\': [], \'firstname\': u\'Wong\', \'lastname\': u\'Lee\', \'i_status\': u\'active\', \'datejoined\': \'2012-08-24 04:50:23\', \'email\': u\'wlee@gmail.com\', \'contactnumber\': u\'\', \'lastlogin\': \'2012-08-24 04:50:23\', \'active\': True, \'password\': \'76f5d947149185d77a1fa1a114b3fb30\', \'id\': 8L, \'permissions\': []}',' change password from \'c1ba3a655c3707af46e1d22daacd7a18\' to \'76f5d947149185d77a1fa1a114b3fb30\' on User [WongLee]'),(10,10,1,NULL,NULL,'Kongluan Lin','citizen_citizen','2012-08-24 04:59:01','','','view Citizen [Mark Tong]'),(11,11,1,NULL,NULL,'Kongluan Lin','citizen_citizen','2012-08-24 05:00:28','','','view Citizen [Mark Tong]'),(12,12,1,NULL,NULL,'Kongluan Lin','citizen_citizen','2012-08-24 05:02:36','','','view Citizen [Mark Tong]'),(13,13,1,NULL,NULL,'Kongluan Lin','citizen_citizen','2012-08-24 05:07:29','','','view Citizen [Mark Tong]'),(14,14,1,NULL,NULL,'Kongluan Lin','citizen_citizen','2012-08-24 05:08:55','','','view Citizen [Mark Tong]'),(15,15,1,NULL,NULL,'Kongluan Lin','citizen_citizen','2012-08-24 05:51:59','','','view Citizen [Mark Tong]'),(16,16,1,NULL,NULL,'Kongluan Lin','property_property','2012-08-24 05:58:13','','{\'i_status\': \'active\', \'citizens\': [], \'plotid\': 5555, \'suburb\': u\'Chatswood\', \'streetno\': 230, \'boundary\': 84L, \'id\': 84L, \'streetname\': u\'Auburn Road\'}','add Property [230 Auburn Road, Chatswood]'),(17,17,1,NULL,NULL,'Kongluan Lin','auth_group','2012-08-24 06:36:17','','','delete Group [test group 4]'),(18,18,1,NULL,NULL,'Kongluan Lin','auth_group','2012-08-24 06:38:03','','','User[Kongluan Lin] delete Group [test group 3]'),(19,19,1,NULL,NULL,'Kongluan Lin','auth_group','2012-08-24 06:39:12','','','User[Kongluan Lin] add Group [test group 3]'),(20,20,1,NULL,NULL,'Kongluan Lin','auth_group','2012-08-24 06:45:09','','','User[Kongluan Lin] view Group [test group 3]'),(21,21,1,NULL,NULL,'Kongluan Lin','auth_group','2012-08-24 06:45:37','{\'i_status\': u\'active\', \'permissions\': [9L, 10L, 11L], \'id\': 6L, \'name\': u\'test group 3\'}','{\'i_status\': u\'active\', \'permissions\': [9L, 10L], \'id\': 6L, \'name\': u\'test group 3\'}','User[Kongluan Lin]  remove permissions [\'Can change log\'] on Group [test group 3]'),(22,22,1,NULL,NULL,'Kongluan Lin','auth_group','2012-08-24 06:46:25','','','User[Kongluan Lin] delete Group [test group 3]'),(23,23,1,NULL,NULL,'Kongluan Lin','auth_user','2012-08-24 06:58:24','','','User[Kongluan Lin] delete User [Peter Wang]'),(24,24,1,NULL,NULL,'Kongluan Lin','auth_user','2012-08-24 06:59:35','','','User[Kongluan Lin] add User [PeterWang]'),(25,25,1,NULL,NULL,'Kongluan Lin','auth_user','2012-08-24 06:59:57','','','User[Kongluan Lin] view User [PeterWang]'),(26,26,1,NULL,NULL,'Kongluan Lin','auth_user','2012-08-24 07:00:27','{\'username\': u\'PeterWang\', \'superuser\': False, \'groups\': [], \'firstname\': u\'Peter\', \'lastname\': u\'Wang\', \'i_status\': u\'active\', \'datejoined\': \'2012-08-24 06:59:35\', \'email\': u\'p@wang.com\', \'contactnumber\': u\'\', \'lastlogin\': \'2012-08-24 06:59:35\', \'active\': True, \'password\': u\'aed285a479e32849b2d2c2a99b7d93d4\', \'id\': 9L, \'permissions\': []}','{\'username\': u\'PetersWang\', \'superuser\': False, \'groups\': [2L], \'firstname\': u\'Peters\', \'lastname\': u\'Wang\', \'i_status\': u\'active\', \'datejoined\': \'2012-08-24 06:59:35\', \'email\': u\'p@wang.com\', \'contactnumber\': u\'\', \'lastlogin\': \'2012-08-24 06:59:35\', \'active\': True, \'password\': \'83878c91171338902e0fe0fb97a8c47a\', \'id\': 9L, \'permissions\': []}','User[Kongluan Lin]  change username from \'PeterWang\' to \'PetersWang\', change firstname from \'Peter\' to \'Peters\', associate with groups [\'dev\'], change password from \'aed285a479e32849b2d2c2a99b7d93d4\' to \'83878c91171338902e0fe0fb97a8c47a\' on User [PetersWang]'),(27,27,1,NULL,NULL,'Kongluan Lin','citizen_citizen','2012-08-24 07:07:18','','','User[Kongluan Lin] add Citizen [Paul Kennardy]'),(28,28,1,NULL,NULL,'Kongluan Lin','citizen_citizen','2012-08-24 07:09:38','','','User[Kongluan Lin] view Citizen [Paul Kennardy]'),(29,29,1,NULL,NULL,'Kongluan Lin','citizen_citizen','2012-08-24 07:09:45','{\'lastname\': u\'Kennardy\', \'i_status\': u\'active\', \'citizenid\': 510132L, \'id\': 2L, \'firstname\': u\'Paul\'}','{\'lastname\': u\'Kennardy\', \'i_status\': u\'active\', \'citizenid\': 510134, \'id\': 2L, \'firstname\': u\'Paul\'}','User[Kongluan Lin]  change citizenid from \'510132\' to \'510134\' on Citizen [Paul Kennardy]'),(30,30,1,NULL,NULL,'Kongluan Lin','property_property','2012-08-24 07:16:04','','','User[Kongluan Lin] add Property [239 Auburn Road, Chatswood]'),(31,31,1,NULL,NULL,'Kongluan Lin','auth_user','2012-08-26 23:05:09','','','User[Kongluan Lin] '),(32,32,1,NULL,NULL,'Kongluan Lin','auth_user','2012-08-26 23:06:11','','','User[Kongluan Lin] '),(33,33,1,NULL,NULL,'Kongluan Lin','auth_user','2012-08-26 23:06:34','','','User[Kongluan Lin] logout'),(34,34,1,NULL,NULL,'Kongluan Lin','auth_user','2012-08-26 23:06:59','','','User[Kongluan Lin] login');
/*!40000 ALTER TABLE `log_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `property_boundary`
--

DROP TABLE IF EXISTS `property_boundary`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `property_boundary` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `polygon` polygon NOT NULL,
  `type` varchar(10) DEFAULT NULL,
  `i_status` varchar(10) NOT NULL,
  PRIMARY KEY (`id`),
  SPATIAL KEY `property_boundary_polygon_id` (`polygon`)
) ENGINE=MyISAM AUTO_INCREMENT=86 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `property_boundary`
--

LOCK TABLES `property_boundary` WRITE;
/*!40000 ALTER TABLE `property_boundary` DISABLE KEYS */;
INSERT INTO `property_boundary` VALUES (2,'\0\0\0\0\0\0\0\0\0\0\0\0\0$Dò¬áIAﬁŒ◊øQq\n¡@∑<e≠áIA}6©gp\n¡‰íô(µáIARzt¿o\n¡}àÿ∑áIA\ZMë áo\n¡G@&ÃáIA#±0˛up\n¡$Dò¬áIAﬁŒ◊øQq\n¡','manual','active'),(3,'\0\0\0\0\0\0\0\0\0\0\0\0\0G@&ÃáIA¸ç4plp\n¡!H\nπáIAÈnçÆêo\n¡Ú∆ì}√áIA§˘&Ön\n¡1rªÿáIA˛‰úvjo\n¡G@&ÃáIA¸ç4plp\n¡','manual','active'),(4,'\0\0\0\0\0\0\0\0\0\0	\0\0\0§4õ∞ÿáIAÔ∞¢!\\o\n¡¢˜!¯«áIA.Í^´n\n¡+® √áIAıÄ˝ò{n\n¡V¥‰¬áIAÍ≈ı¥én\n¡ö›§Õ¿áIA∂nˇ—vn\n¡l£@ÀáIAJûà°#m\n¡˜@ÜÓ‰áIA2!Ad‘m\n¡9å8BﬂáIA;Ö‡A√n\n¡§4õ∞ÿáIAÔ∞¢!\\o\n¡','manual','active'),(5,'\0\0\0\0\0\0\0\0\0\0\0\0\0óè§ÈáIA©ëmÉfm\n¡d9Æ9—áIAâß1◊l\n¡∞+M÷áIAU∞¯ãl\n¡G¿2óÌáIA\n‹∫kßl\n¡óè§ÈáIA©ëmÉfm\n¡','manual','active'),(6,'\0\0\0\0\0\0\0\0\0\0\0\0\0G¿2óÌáIA\n‹∫kßl\n¡d9Æ9—áIAÏ∆ﬁk\n¡¯êKÀ◊áIA’irì·j\n¡¢Ií‹áIAë√Ìj\n¡Ä°¢„ÌáIA™ÕÉî∂j\n¡ãH^£¯áIAnU<)k\n¡G¿2óÌáIA\n‹∫kßl\n¡','manual','active'),(7,'\0\0\0\0\0\0\0\0\0\0\r\0\0\0¢Ií‹áIAë√Ìj\n¡*X>Ì–áIA%TËk\n¡∞+M÷áIA=¡ˆRl\n¡\0˚ç“—áIAˇ ≥á∫l\n¡Z‚∑VπáIAKıß!l\n¡Z‚∑VπáIA˙5Ìk\n¡¯Q\rÁ´áIAVï¶ñ`j\n¡¸.Y¢áIA\n¶ÅKi\n¡¸.Y¢áIA¥1üi\n¡T\0	•áIAÊK=ıÎh\n¡å©™x≤áIAµm9Éıh\n¡^oˆÎºáIAae8i\n¡¢Ií‹áIAë√Ìj\n¡','manual','active'),(8,'\0\0\0\0\0\0\0\0\0\0\n\0\0\0!H\nπáIAKıß!l\n¡YíÚy∆áIA∏–ﬁrl\n¡Ú∆ì}√áIA˘ﬁùÔl\n¡2¬ÄÙ áIAbçä⁄m\n¡ ±Ç-∆áIAÛCùœm\n¡ÌÈèÕáIA6ö3’ım\n¡/5B_«áIA‡\nÓ–°n\n¡ö›§Õ¿áIA∂nˇ—vn\n¡¯Q\rÁ´áIA˛D÷ m\n¡!H\nπáIAKıß!l\n¡','manual','active'),(9,'\0\0\0\0\0\0\0\0\0\0\0\0\0ÏΩùKÉáIA≈¥\"1o\n¡™rÎ˜àáIAæ“ûØeo\n¡ßÂ¨bÖáIA∆Éë®o\n¡é—~áIAÔ∞¢!\\o\n¡y˚Ω≤ÇáIA≠%≤È5o\n¡ÏΩùKÉáIA≈¥\"1o\n¡','manual','active'),(10,'\0\0\0\0\0\0\0\0\0\0\0\0\0=*˛œ©áIAu¨1ú˙m\n¡a¸4Å¿áIA.Í^´n\n¡ZåJÆáIA«6>çTp\n¡&íıüáIA∆Éë®o\n¡ÜﬂÚ*ûáIA$ôto\n¡=*˛œ©áIAu¨1ú˙m\n¡','manual','active'),(11,'\0\0\0\0\0\0\0\0\0\0	\0\0\0áy#eáIA@ZIñm\n¡Év±náIA2!Ad‘m\n¡«ÎföláIAa6\"‘ n\n¡	7ÓfáIA(f9ÄÁm\n¡\\ì…fáIAa6\"‘ n\n¡”‚Á6jáIAº∞EBn\n¡QúHlháIAÏó¶n\n¡UyLﬁ^áIAº∞EBn\n¡áy#eáIA@ZIñm\n¡','manual','active'),(12,'\0\0\0\0\0\0\0\0\0\0\0\0\0Û\'‡R}áIA(Åãuïo\n¡[Û>OÄáIADÈ≤o\n¡†À/8~áIAµâQ«$p\n¡ö°ΩyáIAãÌb»˘o\n¡Öêm|áIAíâ<öo\n¡Û\'‡R}áIA(Åãuïo\n¡','manual','active'),(13,'\0\0\0\0\0\0\0\0\0\0\0\0\0ÀCK\Z\0àIAÛCùœm\n¡?VèÛáIA_ﬂπÕ\"o\n¡@ˆzIŸáIA[ÅRØp\n¡vJ¨\0÷áIA{b\0mÌp\n¡àÃg’áIAùµ°É◊q\n¡QgÓV¯áIAZEA_s\n¡íb€ÕˇáIAhy˝ïms\n¡⁄«\nLàIAv≠˜Í{s\n¡?8ëàIA	Ü¥*s\n¡P6XàIAhy˝ïms\n¡)˜ÒàIA™í3“Ár\n¡Ë˚°àIAQ·ccpr\n¡X1¶§àIAzòfÔq\n¡÷Í⁄\nàIA!Z»˜wq\n¡çÖ◊[	àIAîQ¶Ëp\n¡eG®	àIAáYb*n\n¡ÀCK\Z\0àIAÛCùœm\n¡','manual','active'),(14,'\0\0\0\0\0\0\0\0\0\0\0\0\0ö°ΩyáIAd f:o\n¡†À/8~áIAŒxS\0 p\n¡ú>Ò¢záIA#±0˛up\n¡®5r?xáIAI<TYp\n¡ö°ΩyáIA§‹dıo\n¡ö°ΩyáIAd f:o\n¡','manual','active'),(15,'\0\0\0\0\0\0\0\0\0\0\0\0\0»;,w_áIAô(Zn\n¡HµkáIAÓ>Ë%∞n\n¡ä}∏∏háIAûÒ∑î\'o\n¡JÇÀAaáIA1 ÿ]÷n\n¡Ûò‹ë^áIA¢j™Io\n¡óƒ˛1YáIAêΩΩ?o\n¡»;,w_áIAô(Zn\n¡','manual','active'),(16,'\0\0\0\0\0\0\0\0\0\0\0\0\0àÃg’áIA´ÈõÿÂq\n¡ãH^£¯áIAAVds\n¡íb€ÕˇáIA´ÓÕìs\n¡UÙ,Ï˚áIA∂Ω<t\n¡\nRÑµÈáIAZEA_s\n¡¢Ií‹áIA∆zq≤t\n¡àÃg’áIA´ÈõÿÂq\n¡','manual','active'),(17,'\0\0\0\0\0\0\0\0\0\0\0\0\0óƒ˛1YáIAûÒ∑î\'o\n¡UyLﬁ^áIA…ç¶ìRo\n¡4‰éÂXáIAZ_Vp\n¡K“êTáIAaQt…Œo\n¡óƒ˛1YáIAûÒ∑î\'o\n¡','manual','active'),(18,'\0\0\0\0\0\0\0\0\0\0\0\0\0›â£ˆtáIA◊‹Ú›q\n¡‰£ !|áIA¥2È¿&q\n¡ØOÔiáIA\n¬.≈zp\n¡®5r?xáIA¯BˇJp\n¡kCuáIA¢Ö¸˙ˆp\n¡›â£ˆtáIA◊‹Ú›q\n¡','manual','active'),(19,'\0\0\0\0\0\0\0\0\0\0\0\0\0\rﬂ¬JÌáIAoÜ4m^u\n¡é’ú8¸áIA•øut\n¡}dNÍáIAAVds\n¡}d)+›áIAá|™≠t\n¡\rﬂ¬JÌáIAoÜ4m^u\n¡','manual','active'),(20,'\0\0\0\0\0\0\0\0\0\0\0\0\0åCrNáIAÍ‡G™<p\n¡0WPPUáIA‰û27qp\n¡<N—ÏRáIAxÈ\r¸Àp\n¡®ˆ3[LáIA1Â*SÑp\n¡åCrNáIAÍ‡G™<p\n¡','manual','active'),(21,'\0\0\0\0\0\0\0\0\0\0\0\0\0kCuáIAò Ù\nq\n¡c]ÅVzáIA¬f„5q\n¡›â£ˆtáIAΩñàûr\n¡’UJoáIAπñ-Ùq\n¡kCuáIAò Ù\nq\n¡','manual','active'),(22,'\0\0\0\0\0\0\0\0\0\0\0\0\0ﬁ‘≠qáIA°.îÙ¯q\n¡Ü†¥FráIA‡@íª˝q\n¡X∂≈ñoáIA `Òyr\n¡c≠F3máIAämÄXr\n¡’UJoáIAÑ∆üJ‹q\n¡Z|páIAzòfÔq\n¡ﬁ‘≠qáIA°.îÙ¯q\n¡','manual','active'),(23,'\0\0\0\0\0\0\0\0\0\0\0\0\0àê›JáIA\'*#oóp\n¡ê™ÅRáIAjµßΩp\n¡Ø±ÖSáIAîQ¶Ëp\n¡´ÉrOáIA!Z»˜wq\n¡ÈAÊÆFáIA€UÂN0q\n¡ÈAÊÆFáIA€UÂN0q\n¡àê›JáIA\'*#oóp\n¡','manual','active'),(24,'\0\0\0\0\0\0\0\0\0\0\0\0\0÷o&ÃmáIAœeúkr\n¡®5r?xáIAˆD”ºr\n¡_–B¡váIA˜ÿ+Ó˙r\n¡ƒWÉjáIAY”HE≥r\n¡U)áláIA*æg’fr\n¡÷o&ÃmáIAœeúkr\n¡','manual','active'),(25,'\0\0\0\0\0\0\0\0\0\0\0\0\0vFáIAy·‹9q\n¡r¢§OáIA0é¬LÜq\n¡r¢§OáIAÑ∆üJ‹q\n¡D∏ÙLáIA«QêÇr\n¡9X4BáIAô<Ø∂q\n¡vFáIAy·‹9q\n¡','manual','active'),(26,'\0\0\0\0\0\0\0\0\0\0\0\0\0ç∫1qyáIAY”HE≥r\n¡0ñé4ÅáIA¥M;∂‘r\n¡ØOÔiáIA∫	9s\n¡&Ô“tváIA\r&C	s\n¡“í\"ZwáIAq¬J~Ær\n¡ç∫1qyáIAY”HE≥r\n¡','manual','active'),(27,'\0\0\0\0\0\0\0\0\0\0	\0\0\0j8¿úUáIAãµΩßq\n¡˚ôXáIAô<Ø∂q\n¡RÏ\rI[áIA–ö›jCq\n¡Ûò‹ë^áIA·’ÜVq\n¡ãÕ}ï[áIAùµ°É◊q\n¡èZº*_áIAzòfÔq\n¡íÁ˙øbáIA–ö›jCq\n¡	áﬁ YáIA∞πˆOq\n¡j8¿úUáIAãµΩßq\n¡','manual','active'),(28,'\0\0\0\0\0\0\0\0\0\0\0\0\0ÏΩùKÉáIAgCö¡r\n¡x´¯’èáIAñ{/s\n¡É¢yrçáIAù–ÛxÖs\n¡î‘ÆõÄáIA‚b&!s\n¡ÏΩùKÉáIAgCö¡r\n¡','manual','active'),(29,'\0\0\0\0\0\0\0\0\0\0\0\0\0x´¯’èáIA!u\ZÌ%s\n¡É¢yrçáIA‘.\"—s\n¡{87kìáIAämÄXr\n¡pA∂ŒïáIA\n›Ä∫(r\n¡ÀòáIAÁ2wù@r\n¡{87kìáIA˛ –=s\n¡ñgñáIAZEA_s\n¡(‹ÜPîáIA§¬ÿZ»s\n¡!¬	&çáIA^æı±Äs\n¡i\'9§éáIA‘.\"—s\n¡ˆdYéáIAA òs\n¡x´¯’èáIA!u\ZÌ%s\n¡','manual','active'),(30,'\0\0\0\0\0\0\0\0\0\0\0\0\0≤ùÔ\ZWáIAùµ°É◊q\n¡j8¿úUáIAÚÌ~Å-r\n¡≈ÆÌ·[áIAC≠ibr\n¡èZº*_áIA°.îÙ¯q\n¡≤ùÔ\ZWáIAùµ°É◊q\n¡','manual','active'),(31,'\0\0\0\0\0\0\0\0\0\0\0\0\0&íıüáIAœ^«YÛs\n¡ƒùfÈîáIApk‚w∞s\n¡7`FÇïáIA%Ó^Gs\n¡äºˆúîáIAÿßB4s\n¡ê‘¸ôáIAˆfqÚNr\n¡/ˆ{õáIAQ·ccpr\n¡ŒD\"©üáIAÁ2wù@r\n¡ƒŒQ®áIAC≠ibr\n¡ÇÔ∏ßáIA.7ZFàr\n¡LÆΩ´áIAq¬J~Ær\n¡@∑<e≠áIAõ^9}Ÿr\n¡øpùö´áIA˜ÿ+Ó˙r\n¡[2}3¨áIAÿßB4s\n¡=*˛œ©áIA^æı±Äs\n¡IéÉ©áIApk‚w∞s\n¡@ ßáIAÀÂ‘Ë—s\n¡∏V p§áIA¡*ÕÂs\n¡&íıüáIAœ^«YÛs\n¡','manual','active'),(32,'\0\0\0\0\0\0\0\0\0\0\0\0\0YãsbáIA¸®Üe\Zr\n¡\\ì…fáIA\0\"y÷;r\n¡M\n◊dáIAîlTõñr\n¡◊øÎ®`áIAQ·ccpr\n¡YãsbáIA¸®Üe\Zr\n¡','manual','active'),(33,'\0\0\0\0\0\0\0\0\0\0\0\0\0Á ﬂ±áIAÉo7Dﬁr\n¡–1÷ÑΩáIA´ÈõÿÂq\n¡K^¯$∏áIAü¿ãq\n¡Öè-N´áIA∞πˆOq\n¡9ùø:¶áIA˚6Ãinq\n¡‡[ì±áIA°.îÙ¯q\n¡øpùö´áIAcéP)†r\n¡ÕMµ™áIAmIX\rçr\n¡âl„ÆáIAŸ˛|H2r\n¡LÆΩ´áIAG&\\Ér\n¡Á ﬂ±áIAÉo7Dﬁr\n¡','manual','active'),(34,'\0\0\0\0\0\0\0\0\0\0\0\0\0U)áláIAùöOé)p\n¡MøD˙qáIA‡%@∆Op\n¡ÂÛÂ˝náIAm.ﬂp\n¡ƒ^(iáIAÇ§‡∏p\n¡U)áláIAùöOé)p\n¡','manual','active'),(35,'\0\0\0\0\0\0\0\0\0\0\n\0\0\0ëÜÆÍ®áIAqß¯à\0q\n¡&íıüáIA1Â*SÑp\n¡º3$‚öáIAQ∆n¬p\n¡Eî@◊£áIA–ö›jCq\n¡¸.Y¢áIA·’ÜVq\n¡≠Ød∞ôáIAqß¯à\0q\n¡ø¿bwûáIA#±0˛up\n¡ëÜÆÍ®áIA¢Ö¸˙ˆp\n¡ôÒ¢áIAÌ“`q\n¡ëÜÆÍ®áIAqß¯à\0q\n¡','manual','active'),(36,'\0\0\0\0\0\0\0\0\0\0\0\0\0“í\"ZwáIA¢j™Io\n¡Œ‰ƒsáIAÅ2[‰p\n¡ƒWÉjáIAd f:o\n¡Õ÷ÊláIAóÀxo\n¡QñnáIAxŒªo\n¡“í\"ZwáIA¢j™Io\n¡','manual','active'),(37,'\0\0\0\0\0\0\0\0\0\0\0\0\0íùáIA}6©gp\n¡Ó˙îáIA}πhsÎo\n¡È=èáIAI<TYp\n¡ê‘¸ôáIAÇ§‡∏p\n¡íùáIA}6©gp\n¡','manual','active'),(38,'\0\0\0\0\0\0\0\0\0\0\0\0\0íùáIA}6©gp\n¡Ó˙îáIA}πhsÎo\n¡È=èáIAI<TYp\n¡ê‘¸ôáIAÇ§‡∏p\n¡íùáIA}6©gp\n¡','manual','active'),(39,'\0\0\0\0\0\0\0\0\0\0\0\0\0BW«ìáIAãÌb»˘o\n¡0F…WéáIA6µÖ £o\n¡,πä¬äáIAŒxS\0 p\n¡x´¯’èáIAÓY:^p\n¡7∞_àáIA◊‹Ú›q\n¡!œÄáIA?%®íp\n¡%ü\ròÉáIAI<TYp\n¡õÓ+∆ááIA?%®íp\n¡;=JÙãáIA‹¨MU.p\n¡∏¶ÂLóáIA[ÅRØp\n¡˙Òó†ëáIAy·‹9q\n¡;=JÙãáIAîQ¶Ëp\n¡5ÀêâáIA€UÂN0q\n¡™rÎ˜àáIAò Ù\nq\n¡BW«ìáIAãÌb»˘o\n¡','manual','active'),(40,'\0\0\0\0\0\0\0\0\0\0\0\0\0MøD˙qáIA]Ω/cˇm\n¡Wf\0∫|áIAÍ≈ı¥én\n¡Wf\0∫|áIAb‰≥πn\n¡ö°ΩyáIAªY¨>Do\n¡Œ‰ƒsáIAxŒªo\n¡Ï\rc(váIA.Í^´n\n¡íó5„oáIAã“”Kn\n¡MøD˙qáIA]Ω/cˇm\n¡','manual','active'),(41,'\0\0\0\0\0\0\0\0\0\0\0\0\0È=èáIAV{\Z3n\n¡È=èáIA§˘&Ön\n¡3”ÌëáIA§˘&Ön\n¡BW«ìáIAtU…ï¸n\n¡≠Ød∞ôáIAf!œ@Ón\n¡©\"&ñáIAã“”Kn\n¡º3$‚öáIAV{\Z3n\n¡≈u\0óáIAí&Fn\n¡É¢yrçáIA†H õ%n\n¡ˆdYéáIAïç∑8n\n¡È=èáIAV{\Z3n\n¡','manual','active'),(42,'\0\0\0\0\0\0\0\0\0\0\0\0\0|˘¯ÜgáIA¥2È¿&q\n¡U)áláIAy·‹9q\n¡˝?òQiáIAví•ıÕq\n¡M\n◊dáIAdÂ∏/ûq\n¡|˘¯ÜgáIA¥2È¿&q\n¡','manual','active'),(43,'\0\0\0\0\0\0\0\0\0\0\0\0\0ø¿bwûáIAS(n\n¡H!lßáIA^òi˝l\n¡:ÌÑôáIAˇ ≥á∫l\n¡¶ïÁÖíáIA·aV◊üm\n¡IqDIöáIAgx7GÏm\n¡ø¿bwûáIAS(n\n¡','manual','active'),(44,'\0\0\0\0\0\0\0\0\0\0\n\0\0\0;˛`áIA Ë\r¸Àp\n¡Á°[ı`áIAÄRØp\n¡|˘¯ÜgáIAU?ﬂ„p\n¡ÓªÿháIACí¥p\n¡;˛`áIA\n¬.≈zp\n¡Fıå¨]áIAQ∆n¬p\n¡»;,w_áIA Ë\r¸Àp\n¡ú√_áIA Ë\r¸Àp\n¡ú√_áIA9◊5«p\n¡;˛`áIA Ë\r¸Àp\n¡','manual','active'),(45,'\0\0\0\0\0\0\0\0\0\0	\0\0\0äl1¿°áIA*Ω°ÜÂl\n¡¬˝€/ØáIAj\0p˚k\n¡@∑<e≠áIAy\n“nl\n¡IéÉ©áIAú¥€4Vl\n¡ŒÙ\\Ã¨áIAá>Ãl|l\n¡O;¸ñÆáIAz˛6\0l\n¡LÆΩ´áIA⁄T\0Øk\n¡ÉR¥ïöáIA\n‹∫kßl\n¡äl1¿°áIA*Ω°ÜÂl\n¡','manual','active'),(46,'\0\0\0\0\0\0\0\0\0\0\0\0\0÷o&ÃmáIAb‰≥πn\n¡\"bîﬂráIAJπ⁄ñ—n\n¡g:Ö»páIAî6∞∞:o\n¡U)áláIAêΩΩ?o\n¡÷o&ÃmáIAb‰≥πn\n¡','manual','active'),(47,'\0\0\0\0\0\0\0\0\0\0\0\0\0ä-Û€uáIA∞∏0Ñk\n¡™rÎ˜àáIA`PÆzMj\n¡;=JÙãáIA|∏¢$jj\n¡F‰¥ñáIAâz‚}Ãi\n¡IqDIöáIAë√Ìj\n¡ñgñáIAßTë#ïj\n¡ê‘¸ôáIA«5x>”j\n¡ê‘¸ôáIA˚ån!Îj\n¡ŒD\"©üáIAÄ1ïïãj\n¡ç˘oU•áIAnU<)k\n¡¸.Y¢áIAi¥MX<k\n¡’^ü”¶áIAó….»àk\n¡ƒùfÈîáIAıe´£Õl\n¡5ÀêâáIA3Ôn&l\n¡‰S[DâáIAñr∆¡äl\n¡|à¸GÜáIAñr∆¡äl\n¡y˚Ω≤ÇáIA3Ôn&l\n¡r·@à{áIA‡8’k\n¡ö°ΩyáIA‡8’k\n¡ä-Û€uáIA∞∏0Ñk\n¡','manual','active'),(48,'\0\0\0\0\0\0\0\0\0\0\0\0\0⁄¸daqáIAj\0p˚k\n¡I2enáIAk÷◊¬_l\n¡ä-Û€uáIA§¶¿ôl\n¡·‚ãxáIAA:È√4l\n¡⁄¸daqáIAj\0p˚k\n¡','manual','active'),(50,'\0\0\0\0\0\0\0\0\0\0\0\0\0¸≤ÉÜàIA˘Ûè¶p\n¡_È!–ÜàIAf~˙…q\n¡É|\ZùqàIA]ìmïq\n¡É|\ZùqàIA…mXÄp\n¡¸≤ÉÜàIA˘Ûè¶p\n¡','manual','active'),(51,'\0\0\0\0\0\0\0\0\0\0\0\0\0¸≤ÉÜàIA&\nÄ3≈q\n¡oÀëáàIAr˘I⁄r\n¡/ jÇràIAZ\nﬂr\n¡/ jÇràIA¸më4öq\n¡¸≤ÉÜàIA&\nÄ3≈q\n¡','manual','active'),(52,'\0\0\0\0\0\0\0\0\0\0\0\0\0Á∫:qàIAZ\nﬂr\n¡çqµáàIAô◊„r\n¡~OQNààIA¥-òzt\n¡ ú™PqàIAç\núÏ¯s\n¡Á∫:qàIAZ\nﬂr\n¡','manual','active'),(53,'\0\0\0\0\0\0\0\0\0\0\0\0\0çqµáàIA⁄Pît\n¡/ jÇràIAÃö≥˝s\n¡i⁄ŒràIAÒË-;	u\n¡çqµáàIAŸ˘+u\n¡çqµáàIA⁄Pît\n¡','manual','active'),(54,'\0\0\0\0\0\0\0\0\0\0\0\0\0º]äÈqàIAÒË-;	u\n¡®¨iáàIAŸ˘+u\n¡oÀëáàIAÊ÷ΩPv\n¡ˆ>˙5ràIAÊ÷ΩPv\n¡º]äÈqàIAÒË-;	u\n¡','manual','active'),(55,'\0\0\0\0\0\0\0\0\0\0\0\0\0oÀëáàIAë≈4v\n¡t¯ZkpàIAÅ«mv\n¡Á∫:qàIAç@@◊Tw\n¡®¨iáàIAtQ>ûYw\n¡oÀëáàIAë≈4v\n¡','manual','active'),(56,'\0\0\0\0\0\0\0\0\0\0\0\0\0ÿ6{“oàIA‘’w\n¡®¨iáàIA€6bﬂw\n¡Ò1ÁààIAwé\Z˛*z\n¡pW˘yàIA—ñRs†y\n¡i⁄ŒràIAE±\\∂x\n¡ÿ6{“oàIA‘’w\n¡','manual','active'),(57,'\0\0\0\0\0\0\0\0\0\0\0\0\0qk÷làIAùz¨RWq\n¡„-¸nmàIAÇi Ø8p\n¡√ËSZàIApº3Èp\n¡∏uÿUàIAùz¨RWq\n¡qk÷làIAùz¨RWq\n¡','manual','active'),(58,'\0\0\0\0\0\0\0\0\0\0\0\0\07ä¨âlàIA‹å™\\q\n¡{”ô±KàIAùz¨RWq\n¡ïyJLàIA(|:/qr\n¡„-¸nmàIA(|:/qr\n¡7ä¨âlàIA‹å™\\q\n¡','manual','active'),(59,'\0\0\0\0\0\0\0\0\0\0\0\0\0™Lå\"màIA˜ù6Ωzr\n¡µ¥	˛KàIAÈi<hlr\n¡˝9|MàIAÜ∑\n∂s\n¡qk÷làIAm)µ—∫s\n¡™Lå\"màIA˜ù6Ωzr\n¡','manual','active'),(60,'\0\0\0\0\0\0\0\0\0\0\0\0\0õ»ÃkàIAm)µ—∫s\n¡ƒ8…/MàIAÜ∑\n∂s\n¡˝9|MàIAvçTØ©t\n¡˙‹ø√<àIAù∞P=≥t\n¡ΩLFàIA˛≈øâv\n¡bÁ\\§kàIAë≈4v\n¡õ»ÃkàIAm)µ—∫s\n¡','manual','active'),(61,'\0\0\0\0\0\0\0\0\0\0\0\0\0Ô$}kàIAµ¡¬v\n¡ˆˇªQFàIAµ¡¬v\n¡äWY„LàIA*_gw\n¡Ô$}kàIA^Yºw\n¡Ô$}kàIAµ¡¬v\n¡','manual','active'),(62,'\0\0\0\0\0\0\0\0\0\0	\0\0\07ä¨âlàIA<ÅUJ w\n¡ïyJLàIA.M[ıw\n¡IßèRàIA…âúØw\n¡âîZàIAe∆€BMx\n¡)V≤4^àIAÖß¬]ãx\n¡0p/_eàIAÚŒ°î‹x\n¡—˛ßhàIA‰öß?Œx\n¡µC\røjàIA®QÃzsx\n¡7ä¨âlàIA<ÅUJ w\n¡','manual','active'),(63,'\0\0\0\0\0\0\0\0\0\0\0\0\0æ˙xËúàIA}ô≈7q\n¡êä8öàIAR˝÷8Óp\n¡oÀëáàIA>Ï´πp\n¡¸≤ÉÜàIAf~˙…q\n¡ €Ë4ùàIAÜ˝dr\n¡æ˙xËúàIA}ô≈7q\n¡','manual','active'),(64,'\0\0\0\0\0\0\0\0\0\0\0\0\0æ˙xËúàIAmc‹r\n¡çqµáàIA[av›q\n¡çqµáàIAZ\nﬂr\n¡ €Ë4ùàIAèaÛˆr\n¡æ˙xËúàIAmc‹r\n¡','manual','active'),(65,'\0\0\0\0\0\0\0\0\0\0\0\0\0 €Ë4ùàIAèaÛˆr\n¡®¨iáàIAZ\nﬂr\n¡®¨iáàIA⁄Pît\n¡ €Ë4ùàIA⁄Pît\n¡ €Ë4ùàIAèaÛˆr\n¡','manual','active'),(66,'\0\0\0\0\0\0\0\0\0\0\0\0\0Õ~8\ZûàIA–ïå$t\n¡oÀëáàIAÈÑé]\Zt\n¡çqµáàIAF!9_u\n¡`®fûàIA*πèBu\n¡Õ~8\ZûàIA–ïå$t\n¡','manual','active'),(67,'\0\0\0\0\0\0\0\0\0\0\0\0\0?A≥ûàIAfÚSùu\n¡¸≤ÉÜàIAó‡ı≈ìu\n¡çqµáàIA\ZI)‰w\n¡Õ~8\ZûàIA\ZI)‰w\n¡?A≥ûàIAfÚSùu\n¡','manual','active'),(68,'\0\0\0\0\0\0\0\0\0\0\0\0\0æ˙xËúàIA€6bﬂw\n¡6Í!–ÜàIA€6bﬂw\n¡®¨iáàIA\\}éZy\n¡æ˙xËúàIA+üäËy\n¡æ˙xËúàIA€6bﬂw\n¡','manual','active'),(69,'\0\0\0\0\0\0\0\0\0\0\0\0\0 €Ë4ùàIA\\}éZy\n¡¸≤ÉÜàIA5ZíÃy\n¡~OQNààIAè}7&z\n¡Åå ôàIA\0Óﬁòz\n¡ €Ë4ùàIA\\}éZy\n¡','manual','active'),(70,'\0\0\0\0\0\0\0\0\0\0\0\0\0ö∑E¯§àIA†CœTq\n¡v$M+∫àIA‰†¸sq\n¡ÈÊ,ƒ∫àIA:)\'ı†r\n¡q¶-£àIAûÏfNr\n¡ö∑E¯§àIA†CœTq\n¡','manual','active'),(71,'\0\0\0\0\0\0\0\0\0\0\0\0\0ØΩw∫àIA:)\'ı†r\n¡≈ˆ§àIAÜ˝dr\n¡ã3Ü∆£àIA\0÷öis\n¡ØΩw∫àIA\0÷öis\n¡ØΩw∫àIA:)\'ı†r\n¡','manual','active'),(72,'\0\0\0\0\0\0\0\0\0\0\0\0\0ØΩw∫àIA6–Ôws\n¡q¶-£àIA6–Ôws\n¡ﬂè6·¢àIAﬂgÈyt\n¡v$M+∫àIAﬂgÈyt\n¡ØΩw∫àIA6–Ôws\n¡','manual','active'),(73,'\0\0\0\0\0\0\0\0\0\0\0\0\0ØΩw∫àIA%Œi\"ut\n¡a÷’´§àIAﬂgÈyt\n¡q¶-£àIA•\Z¢u\n¡ØΩw∫àIA{xwu\n¡ØΩw∫àIA%Œi\"ut\n¡','manual','active'),(85,'\0\0\0\0\0\0\0\0\0\0\0\0\0>Ö1˚ÜIA¶‡U÷p\n¡~ÄˇßáIA`1—ç¸p\n¡º>sf˘ÜIAÛ$DLYr\n¡{CÜÔÒÜIA¢eYø$r\n¡>Ö1˚ÜIA¶‡U÷p\n¡','manual','active'),(75,'\0\0\0\0\0\0\0\0\0\0\0\0\0æâ|©ªàIA{xwu\n¡ã3Ü∆£àIAÒÛåòu\n¡a÷’´§àIAsﬂÉ¢≠v\n¡v$M+∫àIAsﬂÉ¢≠v\n¡æâ|©ªàIA{xwu\n¡','manual','active'),(76,'\0\0\0\0\0\0\0\0\0\0\0\0\0\"»úªàIAŸ~˜ªv\n¡≈ˆ§àIAsﬂÉ¢≠v\n¡\'ıe_§àIAé˛D˜w\n¡v$M+∫àIAÒµx\n¡\"»úªàIAŸ~˜ªv\n¡','manual','active'),(77,'\0\0\0\0\0\0\0\0\0\0\0\0\0$d{´áIA\ZI)‰w\n¡‚»ﬁΩáIAÊÒFÃw\n¡d£®øáIAÅ.–Ïix\n¡—ÀÛ´áIAÖß¬]ãx\n¡£‹C©áIAEÂÙ\'x\n¡^EÎZ´áIAEÂÙ\'x\n¡$d{´áIA\ZI)‰w\n¡','manual','active'),(78,'\0\0\0\0\0\0\0\0\0\0\0\0\0=C›ﬁπàIA¬¯ôx\n¡RRz£àIAÈj∑Ìw\n¡ã3Ü∆£àIA⁄ﬂü[·x\n¡v$M+∫àIANIî˛x\n¡=C›ﬁπàIA¬¯ôx\n¡','manual','active'),(79,'\0\0\0\0\0\0\0\0\0\0\0\0\0†Å˝EπàIA9”Ñ=$y\n¡≈ˆ§àIA@ö∞Ôx\n¡¶Æ∆î¢àIAZ&&Tz\n¡ª¸=∏àIAè}7&z\n¡†Å˝EπàIA9”Ñ=$y\n¡','manual','active'),(80,'\0\0\0\0\0\0\0\0\0\0\0\0\0XŒ«∑àIAiZ ©z\n¡ﬂè6·¢àIAs(ç	z\n¡$h\' †àIAÏßﬁøz\n¡q¶-£àIA|y«j¯z\n¡*2ﬂµàIA∆ˆúÑa{\n¡XŒ«∑àIAiZ ©z\n¡','manual','active'),(84,'\0\0\0\0\0\0\0\0\0\0\0\0\0!ÕX™ÎÜIA∑¿íPp\n¡Úí§ˆÜIA€\Z∞p\n¡,ƒŸFÈÜIAtPxOÿq\n¡≤Á|É·ÜIA“—¢5oq\n¡!ÕX™ÎÜIA∑¿íPp\n¡','manual','active');
/*!40000 ALTER TABLE `property_boundary` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `property_ownership`
--

DROP TABLE IF EXISTS `property_ownership`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `property_ownership` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `property_id` int(11) NOT NULL,
  `citizen_id` int(11) NOT NULL,
  `share` double NOT NULL,
  `startdate` date NOT NULL,
  `enddate` date DEFAULT NULL,
  `i_status` varchar(10) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `property_ownership_6a812853` (`property_id`),
  KEY `property_ownership_d00bbef7` (`citizen_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `property_ownership`
--

LOCK TABLES `property_ownership` WRITE;
/*!40000 ALTER TABLE `property_ownership` DISABLE KEYS */;
/*!40000 ALTER TABLE `property_ownership` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `property_property`
--

DROP TABLE IF EXISTS `property_property`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `property_property` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `plotid` int(11) NOT NULL,
  `streetno` int(11) DEFAULT NULL,
  `streetname` varchar(30) DEFAULT NULL,
  `suburb` varchar(50) NOT NULL,
  `boundary_id` int(11) NOT NULL,
  `i_status` varchar(10) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `property_property_2879d902` (`boundary_id`)
) ENGINE=MyISAM AUTO_INCREMENT=86 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `property_property`
--

LOCK TABLES `property_property` WRITE;
/*!40000 ALTER TABLE `property_property` DISABLE KEYS */;
INSERT INTO `property_property` VALUES (2,2000,1,'Stacey','Ashfield',2,'active'),(3,2001,2,'Stacey','Ashfield',3,'active'),(4,2002,3,'Stacey','Ashfield',4,'active'),(5,2003,4,'Stacey','Ashfield',5,'active'),(6,2004,5,'Stacey','Ashfield',6,'active'),(7,2005,6,'Stacey','Ashfield',7,'active'),(8,2006,7,'Stacey','Ashfield',8,'active'),(9,3000,12,'Myall','Cabramatta',9,'active'),(10,2007,8,'Stacey','Ashfield',10,'active'),(11,1000,52,'Phillip Steet','Parramatta',11,'active'),(12,3000,13,'Myall','Cabramatta',12,'active'),(13,2006,1,'paul st','Ashfield',13,'active'),(14,3002,14,'Myall','Cabramatta',14,'active'),(15,1001,54,'Phillip Steet','Parramatta',15,'active'),(16,2008,2,'paul st','Ashfield',16,'active'),(17,1003,56,'Phillip Steet','Parramatta',17,'active'),(18,3003,15,'Myall','Cabramatta',18,'active'),(19,2009,3,'paul st','Ashfield',19,'active'),(20,1004,58,'Phillip Steet','Parramatta',20,'active'),(21,3004,16,'Myall','Cabramatta',21,'active'),(22,3005,17,'Myall','Cabramatta',22,'active'),(23,1005,60,'Phillip Steet','Parramatta',23,'active'),(24,3006,18,'Myall','Cabramatta',24,'active'),(25,1006,62,'Phillip Steet','Parramatta',25,'active'),(26,3007,23,'John','Cabramatta',26,'active'),(27,1007,64,'Phillip Steet','Parramatta',27,'active'),(28,3008,24,'John','Cabramatta',28,'active'),(29,3009,25,'John','Cabramatta',29,'active'),(30,1008,5,'King Street','Parramatta',30,'active'),(31,3010,26,'John','Cabramatta',31,'active'),(32,1009,7,'King Street','Parramatta',32,'active'),(33,3011,112,'Bee','Cabramatta',33,'active'),(34,1010,101,'Wall Steet','Parramatta',34,'active'),(35,3012,122,'Bee','Cabramatta',35,'active'),(36,1011,103,'Wall Steet','Parramatta',36,'active'),(37,3013,121,'Bee','Cabramatta',37,'active'),(38,3013,121,'Bee','Cabramatta',38,'active'),(39,3014,119,'Bee','Cabramatta',39,'active'),(40,1012,111,'Wall Steet','Parramatta',40,'active'),(41,3015,32,'Goose','Cabramatta',41,'active'),(42,1015,99,'Wall Steet','Parramatta',42,'active'),(43,3016,33,'Goose','Cabramatta',43,'active'),(44,1019,15,'Wall Steet','Parramatta',44,'active'),(45,3017,34,'Goose','Cabramatta',45,'active'),(46,1025,45,'Wall Steet','Parramatta',46,'active'),(47,3018,236,'Hugh','Cabramatta',47,'active'),(48,3019,11,'Doom','Cabramatta',48,'active'),(50,9000,1,'Harold St','Glebe',50,'active'),(51,9001,2,'Harold St','Glebe',51,'active'),(52,9002,3,'Harold St','Glebe',52,'active'),(53,9003,4,'Harold St','Glebe',53,'active'),(54,9004,5,'Harold St','Glebe',54,'active'),(55,9005,6,'Harold St','Glebe',55,'active'),(56,9006,7,'Harold St','Glebe',56,'active'),(57,9006,7,'Harold St','Glebe',57,'active'),(58,9007,8,'Harold St','Glebe',58,'active'),(59,9008,9,'Harold St','Glebe',59,'active'),(60,9009,10,'Harold St','Glebe',60,'active'),(61,9010,11,'Harold St','Glebe',61,'active'),(62,9011,12,'Harold St','Glebe',62,'active'),(63,9012,1,'Paper St','Glebe',63,'active'),(64,9013,2,'Paper St','Glebe',64,'active'),(65,9014,3,'Paper St','Glebe',65,'active'),(66,9015,4,'Paper St','Glebe',66,'active'),(67,9016,5,'Paper St','Glebe',67,'active'),(68,9017,7,'Paper St','Glebe',68,'active'),(69,9018,8,'Paper St','Glebe',69,'active'),(70,9020,20,'Paper St','Glebe',70,'active'),(71,9021,21,'Paper St','Glebe',71,'active'),(72,9022,22,'Paper St','Glebe',72,'active'),(73,9023,23,'Paper St','glebe',73,'active'),(85,6666,239,'Auburn Road','Chatswood',85,'active'),(75,9024,24,'Paper St','Glebe',75,'active'),(76,9025,25,'Paper St','glebe',76,'active'),(77,8221,152,'Little Street','Parramatta',77,'active'),(78,9026,26,'Paper St','Glebe',78,'active'),(79,9027,27,'Paper St','Glebe',79,'active'),(80,9028,28,'Paper St','Glebe',80,'active'),(84,5555,230,'Auburn Road','Chatswood',84,'active');
/*!40000 ALTER TABLE `property_property` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2012-08-27 10:08:20
