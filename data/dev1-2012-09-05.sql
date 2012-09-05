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
) ENGINE=MyISAM AUTO_INCREMENT=8 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group`
--

LOCK TABLES `auth_group` WRITE;
/*!40000 ALTER TABLE `auth_group` DISABLE KEYS */;
INSERT INTO `auth_group` VALUES (1,'testgroup','active'),(7,'dev1','active');
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
) ENGINE=MyISAM AUTO_INCREMENT=84 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group_permissions`
--

LOCK TABLES `auth_group_permissions` WRITE;
/*!40000 ALTER TABLE `auth_group_permissions` DISABLE KEYS */;
INSERT INTO `auth_group_permissions` VALUES (1,1,17),(2,1,1),(83,7,33),(82,7,34),(81,7,35),(80,7,36),(79,7,24),(78,7,23),(77,7,22),(76,7,21),(75,7,20),(74,7,19),(73,7,18),(72,7,17),(71,7,16),(70,7,15),(69,7,14),(68,7,13),(67,7,12),(66,7,11),(65,7,10),(64,7,9),(63,7,8),(62,7,7),(61,7,6),(60,7,5),(59,7,4),(58,7,3),(57,7,2),(56,7,1);
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
INSERT INTO `auth_user` VALUES (1,'Kongluan Lin','Kongluan','Lin','','linkongluan@gmail.com','642841ac5168288de710c090272fdcba',1,1,'2012-08-21 04:59:17','2012-08-21 04:59:17','active'),(3,'Shane Dale','Shane','Dale','','shane@propertymode.com.au','1e113fa10ad2e32cac8043b85e99a88d',1,1,'2012-08-21 04:59:17','2012-08-21 04:59:17','active'),(4,'Sandra Macnaughton','Sandra','Macnaughton','','sandra@propertymode.com.au','a921e09118e627ef733a8cc7f3ce835c',1,1,'2012-08-21 04:59:17','2012-08-21 04:59:17','active'),(5,'Justin Hopley','justin','Hopley','','justin@propertymode.com.au','09d914bbbd32fa8145d374c2e82ef7b5',1,1,'2012-08-21 04:59:17','2012-08-21 04:59:17','active'),(6,'peterpeter','peter','peter','','p@p.com','83878c91171338902e0fe0fb97a8c47a',1,1,'2012-08-21 06:20:21','2012-08-21 06:20:21','active'),(7,'adriandinc','adrian','dinc','','adrian@surrondpix.com.au','f22571ad0aacace295ee3f8940aa7ac5',1,1,'2012-08-23 05:43:38','2012-08-23 05:43:38','active');
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
) ENGINE=MyISAM AUTO_INCREMENT=6 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `citizen_citizen`
--

LOCK TABLES `citizen_citizen` WRITE;
/*!40000 ALTER TABLE `citizen_citizen` DISABLE KEYS */;
INSERT INTO `citizen_citizen` VALUES (1,'Mark','Young',12345,'active'),(2,'Paul','Kennardy',510134,'active'),(3,'Bob','Smith',1001,'active'),(5,'Michael','Kay',30032,'active');
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
INSERT INTO `django_session` VALUES ('b41341d2bda060bea4b11ee95a598a92','OGU3M2RjOGNmNzNmOGVhMGZlY2QzNGQ0MTczMmE5YWRkMzkwOTMyOTqAAn1xAVUEdXNlcnECY2Nv\ncHlfcmVnCl9yZWNvbnN0cnVjdG9yCnEDY2F1dGgubW9kZWxzClVzZXIKcQRjX19idWlsdGluX18K\nb2JqZWN0CnEFTodScQZ9cQcoVQh1c2VybmFtZXEIWAwAAABLb25nbHVhbiBMaW5VCXN1cGVydXNl\ncnEJiFUJZmlyc3RuYW1lcQpYCAAAAEtvbmdsdWFuVQhsYXN0bmFtZXELWAMAAABMaW5VCGlfc3Rh\ndHVzcQxYBgAAAGFjdGl2ZVUGX3N0YXRlcQ1jZGphbmdvLmRiLm1vZGVscy5iYXNlCk1vZGVsU3Rh\ndGUKcQ4pgXEPfXEQKFUGYWRkaW5ncRGJVQJkYnESVQdkZWZhdWx0cRN1YlUKZGF0ZWpvaW5lZHEU\nY2RhdGV0aW1lCmRhdGV0aW1lCnEVVQoH3AgVBDsRAAAAY3B5dHoKX1VUQwpxFilScReGUnEYVQVl\nbWFpbHEZWBUAAABsaW5rb25nbHVhbkBnbWFpbC5jb21VDWNvbnRhY3RudW1iZXJxGlgAAAAAVQls\nYXN0bG9naW5xG2gVVQoH3AgVBDsRAAAAaBeGUnEcVQZhY3RpdmVxHYhVCHBhc3N3b3JkcR5YIAAA\nADY0Mjg0MWFjNTE2ODI4OGRlNzEwYzA5MDI3MmZkY2JhVQJpZHEfigEBdWJzLg==\n','2012-09-18 23:04:10'),('e32b211419a6c321e29ebe8e92c3775d','ZDM3NDVhOGEwOGViMWZiN2IzYzAzNjVhODBkYmNhNGQ1ZjliOGI5MzqAAn1xAVUEdXNlcnECY2Nv\ncHlfcmVnCl9yZWNvbnN0cnVjdG9yCnEDY2F1dGgubW9kZWxzClVzZXIKcQRjX19idWlsdGluX18K\nb2JqZWN0CnEFTodScQZ9cQcoVQh1c2VybmFtZXEIWA0AAABKdXN0aW4gSG9wbGV5VQlzdXBlcnVz\nZXJxCYhVCWZpcnN0bmFtZXEKWAYAAABqdXN0aW5VCGxhc3RuYW1lcQtYBgAAAEhvcGxleVUIaV9z\ndGF0dXNxDFgGAAAAYWN0aXZlVQZfc3RhdGVxDWNkamFuZ28uZGIubW9kZWxzLmJhc2UKTW9kZWxT\ndGF0ZQpxDimBcQ99cRAoVQZhZGRpbmdxEYlVAmRicRJVB2RlZmF1bHRxE3ViVQpkYXRlam9pbmVk\ncRRjZGF0ZXRpbWUKZGF0ZXRpbWUKcRVVCgfcCBUEOxEAAABjcHl0egpfVVRDCnEWKVJxF4ZScRhV\nBWVtYWlscRlYGgAAAGp1c3RpbkBwcm9wZXJ0eW1vZGUuY29tLmF1VQ1jb250YWN0bnVtYmVycRpY\nAAAAAFUJbGFzdGxvZ2lucRtoFVUKB9wIFQQ7EQAAAGgXhlJxHFUGYWN0aXZlcR2IVQhwYXNzd29y\nZHEeWCAAAAAwOWQ5MTRiYmJkMzJmYTgxNDVkMzc0YzJlODJlZjdiNVUCaWRxH4oBBXVicy4=\n','2012-09-18 22:51:29'),('63100f433db9ea8b046061bd8c84b20e','ZWM1ZDFmYWNlNWNmOGExMWI4YjVmYjM1NjRlMjYzMjdjMTExYzlmNTqAAn1xAVUEdXNlcnECY2Nv\ncHlfcmVnCl9yZWNvbnN0cnVjdG9yCnEDY2F1dGgubW9kZWxzClVzZXIKcQRjX19idWlsdGluX18K\nb2JqZWN0CnEFTodScQZ9cQcoVQh1c2VybmFtZXEIWAoAAABwZXRlcnBldGVyVQlzdXBlcnVzZXJx\nCYhVCWZpcnN0bmFtZXEKWAUAAABwZXRlclUIbGFzdG5hbWVxC1gFAAAAcGV0ZXJVCGlfc3RhdHVz\ncQxYBgAAAGFjdGl2ZVUGX3N0YXRlcQ1jZGphbmdvLmRiLm1vZGVscy5iYXNlCk1vZGVsU3RhdGUK\ncQ4pgXEPfXEQKFUGYWRkaW5ncRGJVQJkYnESVQdkZWZhdWx0cRN1YlUKZGF0ZWpvaW5lZHEUY2Rh\ndGV0aW1lCmRhdGV0aW1lCnEVVQoH3AgVBhQVAAAAY3B5dHoKX1VUQwpxFilScReGUnEYVQVlbWFp\nbHEZWAcAAABwQHAuY29tVQ1jb250YWN0bnVtYmVycRpYAAAAAFUJbGFzdGxvZ2lucRtoFVUKB9wI\nFQYUFQAAAGgXhlJxHFUGYWN0aXZlcR2IVQhwYXNzd29yZHEeWCAAAAA4Mzg3OGM5MTE3MTMzODkw\nMmUwZmUwZmI5N2E4YzQ3YVUCaWRxH4oBBnVicy4=\n','2012-09-04 06:22:56'),('3b4788ffdb40b2c0768ac8812a101ce1','OGVkNTA0Y2E1OWVjNDNmZTFhNDM4YWUxZWY2MDFmMTFkMGQyMTc2MjqAAn1xAS4=\n','2012-09-04 07:00:23'),('9c4309e5401a746ffde412be5f32719b','OGU3M2RjOGNmNzNmOGVhMGZlY2QzNGQ0MTczMmE5YWRkMzkwOTMyOTqAAn1xAVUEdXNlcnECY2Nv\ncHlfcmVnCl9yZWNvbnN0cnVjdG9yCnEDY2F1dGgubW9kZWxzClVzZXIKcQRjX19idWlsdGluX18K\nb2JqZWN0CnEFTodScQZ9cQcoVQh1c2VybmFtZXEIWAwAAABLb25nbHVhbiBMaW5VCXN1cGVydXNl\ncnEJiFUJZmlyc3RuYW1lcQpYCAAAAEtvbmdsdWFuVQhsYXN0bmFtZXELWAMAAABMaW5VCGlfc3Rh\ndHVzcQxYBgAAAGFjdGl2ZVUGX3N0YXRlcQ1jZGphbmdvLmRiLm1vZGVscy5iYXNlCk1vZGVsU3Rh\ndGUKcQ4pgXEPfXEQKFUGYWRkaW5ncRGJVQJkYnESVQdkZWZhdWx0cRN1YlUKZGF0ZWpvaW5lZHEU\nY2RhdGV0aW1lCmRhdGV0aW1lCnEVVQoH3AgVBDsRAAAAY3B5dHoKX1VUQwpxFilScReGUnEYVQVl\nbWFpbHEZWBUAAABsaW5rb25nbHVhbkBnbWFpbC5jb21VDWNvbnRhY3RudW1iZXJxGlgAAAAAVQls\nYXN0bG9naW5xG2gVVQoH3AgVBDsRAAAAaBeGUnEcVQZhY3RpdmVxHYhVCHBhc3N3b3JkcR5YIAAA\nADY0Mjg0MWFjNTE2ODI4OGRlNzEwYzA5MDI3MmZkY2JhVQJpZHEfigEBdWJzLg==\n','2012-09-06 01:44:45');
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
) ENGINE=MyISAM AUTO_INCREMENT=6 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `jtax_declaredvalue`
--

LOCK TABLES `jtax_declaredvalue` WRITE;
/*!40000 ALTER TABLE `jtax_declaredvalue` DISABLE KEYS */;
INSERT INTO `jtax_declaredvalue` VALUES (1,2000,1,400000,'$AUS','2000-01-02 10:30:00',152,'true'),(2,2000,2,550000,'$AUS','2005-05-09 12:10:30',185,'true'),(3,3000,1,750000,'$AUS','2007-12-22 15:50:28',202,'true'),(4,1010,2,360000,'$AUS','2009-08-25 20:32:45',235,'true'),(5,1001,1,860000,'$AUS','2011-05-30 15:20:15',521,'true');
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
) ENGINE=MyISAM AUTO_INCREMENT=190 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `log_log`
--

LOCK TABLES `log_log` WRITE;
/*!40000 ALTER TABLE `log_log` DISABLE KEYS */;
INSERT INTO `log_log` VALUES (1,1,1,NULL,NULL,'Kongluan Lin','auth_user','2012-08-21 06:20:30','','','view User [peterpeter]'),(2,2,1,NULL,NULL,'Kongluan Lin','auth_user','2012-08-21 06:20:35','{\'username\': u\'peterpeter\', \'superuser\': False, \'groups\': [], \'firstname\': u\'peter\', \'lastname\': u\'peter\', \'i_status\': u\'active\', \'datejoined\': \'2012-08-21 06:20:21\', \'email\': u\'p@p.com\', \'contactnumber\': u\'\', \'lastlogin\': \'2012-08-21 06:20:21\', \'active\': True, \'password\': u\'020e36ec80045462f13c33d190eb7b6f\', \'id\': 6L, \'permissions\': []}','{\'username\': u\'peterpeter\', \'superuser\': False, \'groups\': [], \'firstname\': u\'peter\', \'lastname\': u\'peter\', \'i_status\': u\'active\', \'datejoined\': \'2012-08-21 06:20:21\', \'email\': u\'p@p.com\', \'contactnumber\': u\'\', \'lastlogin\': \'2012-08-21 06:20:21\', \'active\': True, \'password\': \'83878c91171338902e0fe0fb97a8c47a\', \'id\': 6L, \'permissions\': []}',' change password from \'020e36ec80045462f13c33d190eb7b6f\' to \'83878c91171338902e0fe0fb97a8c47a\' on User [peterpeter]'),(3,3,5,NULL,NULL,'justin Hopley','auth_user','2012-08-23 05:43:46','','','view User [adriandinc]'),(4,4,5,NULL,NULL,'justin Hopley','auth_user','2012-08-23 05:43:54','{\'username\': u\'adriandinc\', \'superuser\': False, \'groups\': [2L], \'firstname\': u\'adrian\', \'lastname\': u\'dinc\', \'i_status\': u\'active\', \'datejoined\': \'2012-08-23 05:43:38\', \'email\': u\'adrian@surrondpix.com.au\', \'contactnumber\': u\'\', \'lastlogin\': \'2012-08-23 05:43:38\', \'active\': True, \'password\': u\'66e5780a22508bad65b615ca6c4d709d\', \'id\': 7L, \'permissions\': []}','{\'username\': u\'adriandinc\', \'superuser\': True, \'groups\': [2L], \'firstname\': u\'adrian\', \'lastname\': u\'dinc\', \'i_status\': u\'active\', \'datejoined\': \'2012-08-23 05:43:38\', \'email\': u\'adrian@surrondpix.com.au\', \'contactnumber\': u\'\', \'lastlogin\': \'2012-08-23 05:43:38\', \'active\': True, \'password\': \'f22571ad0aacace295ee3f8940aa7ac5\', \'id\': 7L, \'permissions\': []}',' change superuser from \'False\' to \'True\', change password from \'66e5780a22508bad65b615ca6c4d709d\' to \'f22571ad0aacace295ee3f8940aa7ac5\' on User [adriandinc]'),(5,5,1,NULL,NULL,'Kongluan Lin','property_property','2012-08-23 07:13:52','','{\'i_status\': \'active\', \'citizens\': [], \'plotid\': 8221, \'suburb\': u\'Parramatta\', \'streetno\': 152, \'boundary\': 83L, \'id\': 83L, \'streetname\': u\'Little Street\'}','add Property [152 Little Street, Parramatta]'),(6,6,1,NULL,NULL,'Kongluan Lin','auth_group','2012-08-24 04:46:04','','','view Group [testgroup3]'),(7,7,1,NULL,NULL,'Kongluan Lin','auth_group','2012-08-24 04:46:11','{\'i_status\': u\'active\', \'permissions\': [19L, 20L, 21L], \'id\': 3L, \'name\': u\'testgroup3\'}','{\'i_status\': u\'active\', \'permissions\': [19L, 20L], \'id\': 3L, \'name\': u\'testgroup3\'}',' remove permissions [\'Can view user\'] on Group [testgroup3]'),(8,8,1,NULL,NULL,'Kongluan Lin','auth_user','2012-08-24 04:51:33','','','view User [WongLee]'),(9,9,1,NULL,NULL,'Kongluan Lin','auth_user','2012-08-24 04:52:10','{\'username\': u\'WongLee\', \'superuser\': False, \'groups\': [], \'firstname\': u\'Wong\', \'lastname\': u\'Lee\', \'i_status\': u\'active\', \'datejoined\': \'2012-08-24 04:50:23\', \'email\': u\'wlee@gmail.com\', \'contactnumber\': u\'\', \'lastlogin\': \'2012-08-24 04:50:23\', \'active\': True, \'password\': u\'c1ba3a655c3707af46e1d22daacd7a18\', \'id\': 8L, \'permissions\': []}','{\'username\': u\'WongLee\', \'superuser\': False, \'groups\': [], \'firstname\': u\'Wong\', \'lastname\': u\'Lee\', \'i_status\': u\'active\', \'datejoined\': \'2012-08-24 04:50:23\', \'email\': u\'wlee@gmail.com\', \'contactnumber\': u\'\', \'lastlogin\': \'2012-08-24 04:50:23\', \'active\': True, \'password\': \'76f5d947149185d77a1fa1a114b3fb30\', \'id\': 8L, \'permissions\': []}',' change password from \'c1ba3a655c3707af46e1d22daacd7a18\' to \'76f5d947149185d77a1fa1a114b3fb30\' on User [WongLee]'),(10,10,1,NULL,NULL,'Kongluan Lin','citizen_citizen','2012-08-24 04:59:01','','','view Citizen [Mark Tong]'),(11,11,1,NULL,NULL,'Kongluan Lin','citizen_citizen','2012-08-24 05:00:28','','','view Citizen [Mark Tong]'),(12,12,1,NULL,NULL,'Kongluan Lin','citizen_citizen','2012-08-24 05:02:36','','','view Citizen [Mark Tong]'),(13,13,1,NULL,NULL,'Kongluan Lin','citizen_citizen','2012-08-24 05:07:29','','','view Citizen [Mark Tong]'),(14,14,1,NULL,NULL,'Kongluan Lin','citizen_citizen','2012-08-24 05:08:55','','','view Citizen [Mark Tong]'),(15,15,1,NULL,NULL,'Kongluan Lin','citizen_citizen','2012-08-24 05:51:59','','','view Citizen [Mark Tong]'),(16,16,1,NULL,NULL,'Kongluan Lin','property_property','2012-08-24 05:58:13','','{\'i_status\': \'active\', \'citizens\': [], \'plotid\': 5555, \'suburb\': u\'Chatswood\', \'streetno\': 230, \'boundary\': 84L, \'id\': 84L, \'streetname\': u\'Auburn Road\'}','add Property [230 Auburn Road, Chatswood]'),(17,17,1,NULL,NULL,'Kongluan Lin','auth_group','2012-08-24 06:36:17','','','delete Group [test group 4]'),(18,18,1,NULL,NULL,'Kongluan Lin','auth_group','2012-08-24 06:38:03','','','User[Kongluan Lin] delete Group [test group 3]'),(19,19,1,NULL,NULL,'Kongluan Lin','auth_group','2012-08-24 06:39:12','','','User[Kongluan Lin] add Group [test group 3]'),(20,20,1,NULL,NULL,'Kongluan Lin','auth_group','2012-08-24 06:45:09','','','User[Kongluan Lin] view Group [test group 3]'),(21,21,1,NULL,NULL,'Kongluan Lin','auth_group','2012-08-24 06:45:37','{\'i_status\': u\'active\', \'permissions\': [9L, 10L, 11L], \'id\': 6L, \'name\': u\'test group 3\'}','{\'i_status\': u\'active\', \'permissions\': [9L, 10L], \'id\': 6L, \'name\': u\'test group 3\'}','User[Kongluan Lin]  remove permissions [\'Can change log\'] on Group [test group 3]'),(22,22,1,NULL,NULL,'Kongluan Lin','auth_group','2012-08-24 06:46:25','','','User[Kongluan Lin] delete Group [test group 3]'),(23,23,1,NULL,NULL,'Kongluan Lin','auth_user','2012-08-24 06:58:24','','','User[Kongluan Lin] delete User [Peter Wang]'),(24,24,1,NULL,NULL,'Kongluan Lin','auth_user','2012-08-24 06:59:35','','','User[Kongluan Lin] add User [PeterWang]'),(25,25,1,NULL,NULL,'Kongluan Lin','auth_user','2012-08-24 06:59:57','','','User[Kongluan Lin] view User [PeterWang]'),(26,26,1,NULL,NULL,'Kongluan Lin','auth_user','2012-08-24 07:00:27','{\'username\': u\'PeterWang\', \'superuser\': False, \'groups\': [], \'firstname\': u\'Peter\', \'lastname\': u\'Wang\', \'i_status\': u\'active\', \'datejoined\': \'2012-08-24 06:59:35\', \'email\': u\'p@wang.com\', \'contactnumber\': u\'\', \'lastlogin\': \'2012-08-24 06:59:35\', \'active\': True, \'password\': u\'aed285a479e32849b2d2c2a99b7d93d4\', \'id\': 9L, \'permissions\': []}','{\'username\': u\'PetersWang\', \'superuser\': False, \'groups\': [2L], \'firstname\': u\'Peters\', \'lastname\': u\'Wang\', \'i_status\': u\'active\', \'datejoined\': \'2012-08-24 06:59:35\', \'email\': u\'p@wang.com\', \'contactnumber\': u\'\', \'lastlogin\': \'2012-08-24 06:59:35\', \'active\': True, \'password\': \'83878c91171338902e0fe0fb97a8c47a\', \'id\': 9L, \'permissions\': []}','User[Kongluan Lin]  change username from \'PeterWang\' to \'PetersWang\', change firstname from \'Peter\' to \'Peters\', associate with groups [\'dev\'], change password from \'aed285a479e32849b2d2c2a99b7d93d4\' to \'83878c91171338902e0fe0fb97a8c47a\' on User [PetersWang]'),(27,27,1,NULL,NULL,'Kongluan Lin','citizen_citizen','2012-08-24 07:07:18','','','User[Kongluan Lin] add Citizen [Paul Kennardy]'),(28,28,1,NULL,NULL,'Kongluan Lin','citizen_citizen','2012-08-24 07:09:38','','','User[Kongluan Lin] view Citizen [Paul Kennardy]'),(29,29,1,NULL,NULL,'Kongluan Lin','citizen_citizen','2012-08-24 07:09:45','{\'lastname\': u\'Kennardy\', \'i_status\': u\'active\', \'citizenid\': 510132L, \'id\': 2L, \'firstname\': u\'Paul\'}','{\'lastname\': u\'Kennardy\', \'i_status\': u\'active\', \'citizenid\': 510134, \'id\': 2L, \'firstname\': u\'Paul\'}','User[Kongluan Lin]  change citizenid from \'510132\' to \'510134\' on Citizen [Paul Kennardy]'),(30,30,1,NULL,NULL,'Kongluan Lin','property_property','2012-08-24 07:16:04','','','User[Kongluan Lin] add Property [239 Auburn Road, Chatswood]'),(31,31,1,NULL,NULL,'Kongluan Lin','auth_user','2012-08-26 23:05:09','','','User[Kongluan Lin] '),(32,32,1,NULL,NULL,'Kongluan Lin','auth_user','2012-08-26 23:06:11','','','User[Kongluan Lin] '),(33,33,1,NULL,NULL,'Kongluan Lin','auth_user','2012-08-26 23:06:34','','','User[Kongluan Lin] logout'),(34,34,1,NULL,NULL,'Kongluan Lin','auth_user','2012-08-26 23:06:59','','','User[Kongluan Lin] login'),(35,35,1,NULL,NULL,'Kongluan Lin','auth_user','2012-08-27 07:17:50','','','User[Kongluan Lin] logout'),(36,36,1,NULL,NULL,'Kongluan Lin','auth_user','2012-08-27 22:44:26','','','User[Kongluan Lin] login'),(37,37,5,NULL,NULL,'justin Hopley','auth_user','2012-08-28 04:03:17','','','User[justin Hopley] login'),(38,38,1,NULL,NULL,'Kongluan Lin','citizen_citizen','2012-08-28 04:35:39','','','User[Kongluan Lin] view Citizen [Mark Tong]'),(39,39,1,NULL,NULL,'Kongluan Lin','citizen_citizen','2012-08-28 04:35:45','','','User[Kongluan Lin] view Citizen [Mark Tong]'),(40,40,1,NULL,NULL,'Kongluan Lin','auth_group','2012-08-28 04:39:01','','','User[Kongluan Lin] view Group [dev]'),(41,41,1,NULL,NULL,'Kongluan Lin','auth_group','2012-08-28 04:40:16','','','User[Kongluan Lin] view Group [dev]'),(42,42,1,NULL,NULL,'Kongluan Lin','auth_group','2012-08-28 04:40:23','','','User[Kongluan Lin] view Group [dev]'),(43,43,1,NULL,NULL,'Kongluan Lin','auth_group','2012-08-28 04:42:00','','','User[Kongluan Lin] delete Group [dev]'),(44,44,1,NULL,NULL,'Kongluan Lin','auth_group','2012-08-28 04:43:00','','','User[Kongluan Lin] view Group [testgroup]'),(45,45,1,NULL,NULL,'Kongluan Lin','auth_group','2012-08-28 04:49:29','','','User[Kongluan Lin] add Group [dev1]'),(46,46,1,NULL,NULL,'Kongluan Lin','auth_user','2012-08-28 04:53:26','','','User[Kongluan Lin] view User [PetersWang]'),(47,47,1,NULL,NULL,'Kongluan Lin','auth_user','2012-08-28 04:53:36','','','User[Kongluan Lin] view User [PetersWang]'),(48,48,1,NULL,NULL,'Kongluan Lin','auth_user','2012-08-28 04:53:47','','','User[Kongluan Lin] view User [PetersWang]'),(49,49,1,NULL,NULL,'Kongluan Lin','auth_user','2012-08-28 04:54:41','','','User[Kongluan Lin] delete User [PetersWang]'),(50,50,1,NULL,NULL,'Kongluan Lin','auth_user','2012-08-28 05:04:46','','','User[Kongluan Lin] logout'),(51,51,1,NULL,NULL,'Kongluan Lin','auth_user','2012-08-28 05:04:57','','','User[Kongluan Lin] login'),(52,52,5,NULL,NULL,'justin Hopley','auth_user','2012-08-29 06:52:45','','','User[justin Hopley] logout'),(53,53,5,NULL,NULL,'justin Hopley','auth_user','2012-08-29 06:57:46','','','User[justin Hopley] login'),(54,54,1,NULL,NULL,'Kongluan Lin','auth_user','2012-09-02 22:55:59','','','User[Kongluan Lin] logout'),(55,55,1,NULL,NULL,'Kongluan Lin','auth_user','2012-09-02 22:56:13','','','User[Kongluan Lin] login'),(56,56,1,NULL,NULL,'Kongluan Lin','auth_user','2012-09-02 23:40:45','','','User[Kongluan Lin] logout'),(57,57,1,NULL,NULL,'Kongluan Lin','auth_user','2012-09-02 23:43:06','','','User[Kongluan Lin] login'),(58,58,1,NULL,NULL,'Kongluan Lin','auth_user','2012-09-02 23:43:35','','','User[Kongluan Lin] logout'),(59,59,1,NULL,NULL,'Kongluan Lin','auth_user','2012-09-02 23:46:20','','','User[Kongluan Lin] login'),(60,60,1,NULL,NULL,'Kongluan Lin','auth_user','2012-09-02 23:46:34','','','User[Kongluan Lin] logout'),(61,61,1,NULL,NULL,'Kongluan Lin','auth_user','2012-09-02 23:52:09','','','User[Kongluan Lin] login'),(62,62,1,NULL,NULL,'Kongluan Lin','auth_user','2012-09-03 07:21:08','','','User[Kongluan Lin] logout'),(63,63,1,NULL,NULL,'Kongluan Lin','auth_user','2012-09-03 23:46:26','','','User[Kongluan Lin] login'),(64,64,1,NULL,NULL,'Kongluan Lin','property_property','2012-09-03 23:51:32','','','User[Kongluan Lin] add Property [135 Little Street, Parramatta]'),(65,65,1,NULL,NULL,'Kongluan Lin','property_property','2012-09-03 23:53:44','','','User[Kongluan Lin] add Property [137 Little Street, Parramatta]'),(66,66,1,NULL,NULL,'Kongluan Lin','property_property','2012-09-03 23:54:53','','','User[Kongluan Lin] add Property [139 Little Street, Parramatta]'),(67,67,1,NULL,NULL,'Kongluan Lin','property_property','2012-09-03 23:55:36','','','User[Kongluan Lin] add Property [141 Little Street, Parramatta]'),(68,68,1,NULL,NULL,'Kongluan Lin','property_property','2012-09-03 23:57:36','','','User[Kongluan Lin] add Property [143 Little Street, Parramatta]'),(69,69,1,NULL,NULL,'Kongluan Lin','property_property','2012-09-03 23:58:32','','','User[Kongluan Lin] add Property [145 Little Street, Parramatta]'),(70,70,1,NULL,NULL,'Kongluan Lin','property_property','2012-09-04 00:01:46','','','User[Kongluan Lin] add Property [1 Eagle Street, Parramatta]'),(71,71,1,NULL,NULL,'Kongluan Lin','property_property','2012-09-04 00:02:28','','','User[Kongluan Lin] add Property [2 Eagle Street, Parramatta]'),(72,72,1,NULL,NULL,'Kongluan Lin','property_property','2012-09-04 00:04:14','','','User[Kongluan Lin] add Property [3 Eagle Street, Parramatta]'),(73,73,1,NULL,NULL,'Kongluan Lin','property_property','2012-09-04 00:05:29','','','User[Kongluan Lin] add Property [4 Eagle Street, Parramatta]'),(74,74,1,NULL,NULL,'Kongluan Lin','property_property','2012-09-04 00:06:07','','','User[Kongluan Lin] add Property [5 Eagle Street, Parramatta]'),(75,75,1,NULL,NULL,'Kongluan Lin','property_property','2012-09-04 00:06:56','','','User[Kongluan Lin] add Property [6 Eagle Street, Parramatta]'),(76,76,1,NULL,NULL,'Kongluan Lin','property_property','2012-09-04 00:07:46','','','User[Kongluan Lin] add Property [7 Eagle Street, Parramatta]'),(77,77,1,NULL,NULL,'Kongluan Lin','property_property','2012-09-04 00:13:20','','','User[Kongluan Lin] add Property [9 Eagle Street, Parramatta]'),(78,78,1,NULL,NULL,'Kongluan Lin','property_property','2012-09-04 00:14:15','','','User[Kongluan Lin] add Property [11 Eagle Street, Parramatta]'),(79,79,1,NULL,NULL,'Kongluan Lin','property_property','2012-09-04 00:14:54','','','User[Kongluan Lin] add Property [13 Eagle Street, Parramatta]'),(80,80,1,NULL,NULL,'Kongluan Lin','property_property','2012-09-04 00:15:44','','','User[Kongluan Lin] add Property [14 Eagle Street, Parramatta]'),(81,81,1,NULL,NULL,'Kongluan Lin','property_property','2012-09-04 00:18:12','','','User[Kongluan Lin] add Property [15 Eagle Street, Parramatta]'),(82,82,1,NULL,NULL,'Kongluan Lin','property_property','2012-09-04 00:18:56','','','User[Kongluan Lin] add Property [16 Eagle Street, Parramatta]'),(83,83,1,NULL,NULL,'Kongluan Lin','property_property','2012-09-04 00:20:48','','','User[Kongluan Lin] add Property [147 Little Street, Parramatta]'),(84,84,1,NULL,NULL,'Kongluan Lin','property_property','2012-09-04 00:21:46','','','User[Kongluan Lin] add Property [148 Little Street, Parramatta]'),(85,85,1,NULL,NULL,'Kongluan Lin','property_property','2012-09-04 00:22:43','','','User[Kongluan Lin] add Property [149 Little Street, Parramatta]'),(86,86,1,NULL,NULL,'Kongluan Lin','property_property','2012-09-04 00:23:44','','','User[Kongluan Lin] add Property [153 Little Street, Parramatta]'),(87,87,1,NULL,NULL,'Kongluan Lin','property_property','2012-09-04 00:27:19','','','User[Kongluan Lin] add Property [1 Dixon Street, Parramatta]'),(88,88,1,NULL,NULL,'Kongluan Lin','property_property','2012-09-04 00:28:49','','','User[Kongluan Lin] add Property [2 Dixon Street, Glebe]'),(89,89,1,NULL,NULL,'Kongluan Lin','property_property','2012-09-04 00:29:40','','','User[Kongluan Lin] add Property [3 Dixon Street, Parramatta]'),(90,90,1,NULL,NULL,'Kongluan Lin','property_property','2012-09-04 00:30:25','','','User[Kongluan Lin] add Property [4 Dixon Street, Glebe]'),(91,91,1,NULL,NULL,'Kongluan Lin','property_property','2012-09-04 00:31:35','','','User[Kongluan Lin] add Property [5 Dixon Street, Glebe]'),(92,92,1,NULL,NULL,'Kongluan Lin','property_property','2012-09-04 00:36:13','','','User[Kongluan Lin] add Property [6 Dixon Street, Glebe]'),(93,93,1,NULL,NULL,'Kongluan Lin','property_property','2012-09-04 00:40:50','','','User[Kongluan Lin] add Property [10 York Street, Petersham]'),(94,94,1,NULL,NULL,'Kongluan Lin','property_property','2012-09-04 00:42:02','','','User[Kongluan Lin] add Property [12 York Street, Petersham]'),(95,95,1,NULL,NULL,'Kongluan Lin','property_property','2012-09-04 00:43:10','','','User[Kongluan Lin] add Property [13 York Street, Petersham]'),(96,96,1,NULL,NULL,'Kongluan Lin','property_property','2012-09-04 00:48:23','','','User[Kongluan Lin] add Property [13 Harold Street, Glebe]'),(97,97,1,NULL,NULL,'Kongluan Lin','property_property','2012-09-04 00:49:02','','','User[Kongluan Lin] add Property [14 Harold Street, Glebe]'),(98,98,1,NULL,NULL,'Kongluan Lin','property_property','2012-09-04 00:51:51','','','User[Kongluan Lin] add Property [4 Paul Street, Ashfield]'),(99,99,1,NULL,NULL,'Kongluan Lin','property_property','2012-09-04 01:07:06','','','User[Kongluan Lin] add Property [1 Church Street, Atarmon]'),(100,100,1,NULL,NULL,'Kongluan Lin','property_property','2012-09-04 01:08:00','','','User[Kongluan Lin] add Property [2 Church Street, Atarmon]'),(101,101,1,NULL,NULL,'Kongluan Lin','property_property','2012-09-04 01:08:31','','','User[Kongluan Lin] add Property [3 Church Street, Atarmon]'),(102,102,1,NULL,NULL,'Kongluan Lin','property_property','2012-09-04 01:09:13','','','User[Kongluan Lin] add Property [4 Church Street, Atarmon]'),(103,103,1,NULL,NULL,'Kongluan Lin','property_property','2012-09-04 01:10:53','','','User[Kongluan Lin] add Property [5 Church Street, Atarmon]'),(104,104,1,NULL,NULL,'Kongluan Lin','property_property','2012-09-04 01:11:19','','','User[Kongluan Lin] add Property [6 Church Street, Atarmon]'),(105,105,1,NULL,NULL,'Kongluan Lin','property_property','2012-09-04 01:11:53','','','User[Kongluan Lin] add Property [7 Church Street, Atarmon]'),(106,106,1,NULL,NULL,'Kongluan Lin','property_property','2012-09-04 01:12:36','','','User[Kongluan Lin] add Property [8 Church Street, Atarmon]'),(107,107,1,NULL,NULL,'Kongluan Lin','property_property','2012-09-04 01:15:33','','','User[Kongluan Lin] add Property [50 Croydon Road, Atarmon]'),(108,108,1,NULL,NULL,'Kongluan Lin','property_property','2012-09-04 01:16:11','','','User[Kongluan Lin] add Property [51 Croydon Road, Atarmon]'),(109,109,1,NULL,NULL,'Kongluan Lin','property_property','2012-09-04 01:16:48','','','User[Kongluan Lin] add Property [15 Croydon Road, Atarmon]'),(110,110,1,NULL,NULL,'Kongluan Lin','property_property','2012-09-04 01:30:46','','','User[Kongluan Lin] add Property [7 Dixon Street, Glebe]'),(111,111,5,NULL,NULL,'justin Hopley','citizen_citizen','2012-09-04 01:32:17','','','User[justin Hopley] add Citizen [Bob Smith]'),(112,112,1,NULL,NULL,'Kongluan Lin','property_property','2012-09-04 01:33:22','','','User[Kongluan Lin] add Property [8 Dixon Street, Glebe]'),(113,113,1,NULL,NULL,'Kongluan Lin','property_property','2012-09-04 01:34:34','','','User[Kongluan Lin] add Property [9 Dixon Street, Glebe]'),(114,114,1,NULL,NULL,'Kongluan Lin','property_property','2012-09-04 01:35:14','','','User[Kongluan Lin] add Property [9 Dixon Street, Glebe]'),(115,115,1,NULL,NULL,'Kongluan Lin','property_property','2012-09-04 01:36:24','','','User[Kongluan Lin] add Property [11 Dixon Street, Glebe]'),(116,116,1,NULL,NULL,'Kongluan Lin','property_property','2012-09-04 01:37:03','','','User[Kongluan Lin] add Property [12 Dixon Street, Glebe]'),(117,117,1,NULL,NULL,'Kongluan Lin','property_property','2012-09-04 01:38:49','','','User[Kongluan Lin] add Property [1 Gordon Avenue, Glebe]'),(118,118,1,NULL,NULL,'Kongluan Lin','property_property','2012-09-04 01:39:18','','','User[Kongluan Lin] add Property [2 Gordon Avenue, Glebe]'),(119,119,1,NULL,NULL,'Kongluan Lin','property_property','2012-09-04 01:39:54','','','User[Kongluan Lin] add Property [3 Gordon Avenue, Glebe]'),(120,120,1,NULL,NULL,'Kongluan Lin','property_property','2012-09-04 01:41:43','','','User[Kongluan Lin] add Property [4 Gordon Avenue, Glebe]'),(121,121,1,NULL,NULL,'Kongluan Lin','property_property','2012-09-04 01:42:35','','','User[Kongluan Lin] add Property [5 Gordon Avenue, Glebe]'),(122,122,1,NULL,NULL,'Kongluan Lin','property_property','2012-09-04 01:43:04','','','User[Kongluan Lin] add Property [6 Gordon Avenue, Glebe]'),(123,123,1,NULL,NULL,'Kongluan Lin','property_property','2012-09-04 01:44:04','','','User[Kongluan Lin] add Property [7 Gordon Avenue, Glebe]'),(124,124,1,NULL,NULL,'Kongluan Lin','property_property','2012-09-04 01:44:45','','','User[Kongluan Lin] add Property [8 Gordon Avenue, Glebe]'),(125,125,1,NULL,NULL,'Kongluan Lin','property_property','2012-09-04 01:45:08','','','User[Kongluan Lin] add Property [9 Gordon Avenue, Glebe]'),(126,126,1,NULL,NULL,'Kongluan Lin','property_property','2012-09-04 01:46:03','','','User[Kongluan Lin] add Property [10 Gordon Avenue, Glebe]'),(127,127,1,NULL,NULL,'Kongluan Lin','property_property','2012-09-04 01:46:32','','','User[Kongluan Lin] add Property [11 Gordon Avenue, Glebe]'),(128,128,1,NULL,NULL,'Kongluan Lin','property_property','2012-09-04 01:47:07','','','User[Kongluan Lin] add Property [11 Gordon Avenue, Glebe]'),(129,129,1,NULL,NULL,'Kongluan Lin','property_property','2012-09-04 01:48:15','','','User[Kongluan Lin] add Property [13 Gordon Avenue, Glebe]'),(130,130,1,NULL,NULL,'Kongluan Lin','property_property','2012-09-04 01:48:38','','','User[Kongluan Lin] add Property [14 Gordon Avenue, Glebe]'),(131,131,1,NULL,NULL,'Kongluan Lin','property_property','2012-09-04 01:49:08','','','User[Kongluan Lin] add Property [15 Gordon Avenue, Glebe]'),(132,132,1,NULL,NULL,'Kongluan Lin','property_property','2012-09-04 01:51:01','','','User[Kongluan Lin] add Property [1 Elezebeth Street, Glebe]'),(133,133,1,NULL,NULL,'Kongluan Lin','property_property','2012-09-04 01:51:22','','','User[Kongluan Lin] add Property [2 Elezebeth Street, Glebe]'),(134,134,1,NULL,NULL,'Kongluan Lin','property_property','2012-09-04 01:51:44','','','User[Kongluan Lin] add Property [3 Elezebeth Street, Glebe]'),(135,135,1,NULL,NULL,'Kongluan Lin','property_property','2012-09-04 01:52:26','','','User[Kongluan Lin] add Property [4 Elezebeth Street, Glebe]'),(136,136,1,NULL,NULL,'Kongluan Lin','property_property','2012-09-04 01:53:00','','','User[Kongluan Lin] add Property [5 Elezebeth Street, Glebe]'),(137,137,1,NULL,NULL,'Kongluan Lin','property_property','2012-09-04 01:53:26','','','User[Kongluan Lin] add Property [6 Elezebeth Street, Glebe]'),(138,138,1,NULL,NULL,'Kongluan Lin','property_property','2012-09-04 01:53:51','','','User[Kongluan Lin] add Property [7 Elezebeth Street, Glebe]'),(139,139,1,NULL,NULL,'Kongluan Lin','property_property','2012-09-04 01:54:15','','','User[Kongluan Lin] add Property [8 Elezebeth Street, Glebe]'),(140,140,1,NULL,NULL,'Kongluan Lin','property_property','2012-09-04 01:57:39','','','User[Kongluan Lin] add Property [14 York Street, Petersham]'),(141,141,1,NULL,NULL,'Kongluan Lin','property_property','2012-09-04 01:58:20','','','User[Kongluan Lin] add Property [15 York Street, Petersham]'),(142,142,1,NULL,NULL,'Kongluan Lin','property_property','2012-09-04 01:59:21','','','User[Kongluan Lin] add Property [16 York Street, Petersham]'),(143,143,1,NULL,NULL,'Kongluan Lin','property_property','2012-09-04 02:00:08','','','User[Kongluan Lin] add Property [16 York Street, Petersham]'),(144,144,1,NULL,NULL,'Kongluan Lin','property_property','2012-09-04 02:00:42','','','User[Kongluan Lin] add Property [17 York Street, Petersham]'),(145,145,1,NULL,NULL,'Kongluan Lin','property_property','2012-09-04 02:01:28','','','User[Kongluan Lin] add Property [18 York Street, Petersham]'),(146,146,1,NULL,NULL,'Kongluan Lin','property_property','2012-09-04 02:02:27','','','User[Kongluan Lin] add Property [1 Swan Avenue, Petersham]'),(147,147,1,NULL,NULL,'Kongluan Lin','property_property','2012-09-04 02:03:07','','','User[Kongluan Lin] add Property [2 Swan Avenue, Petersham]'),(148,148,1,NULL,NULL,'Kongluan Lin','property_property','2012-09-04 02:03:39','','','User[Kongluan Lin] add Property [3 Swan Avenue, Petersham]'),(149,149,1,NULL,NULL,'Kongluan Lin','property_property','2012-09-04 02:04:22','','','User[Kongluan Lin] add Property [4 York Street, Petersham]'),(150,150,1,NULL,NULL,'Kongluan Lin','property_property','2012-09-04 02:04:59','','','User[Kongluan Lin] add Property [5 Swan Avenue, Petersham]'),(151,151,1,NULL,NULL,'Kongluan Lin','property_property','2012-09-04 02:06:12','','','User[Kongluan Lin] add Property [6 Swan Avenue, Petersham]'),(152,152,1,NULL,NULL,'Kongluan Lin','property_property','2012-09-04 02:06:47','','','User[Kongluan Lin] add Property [7 Swan Avenue, Petersham]'),(153,153,1,NULL,NULL,'Kongluan Lin','property_property','2012-09-04 02:07:34','','','User[Kongluan Lin] add Property [8 Swan Avenue, Petersham]'),(154,154,1,NULL,NULL,'Kongluan Lin','property_property','2012-09-04 02:08:08','','','User[Kongluan Lin] add Property [9 Swan Avenue, Petersham]'),(155,155,1,NULL,NULL,'Kongluan Lin','property_property','2012-09-04 02:08:49','','','User[Kongluan Lin] add Property [10 Swan Avenue, Petersham]'),(156,156,1,NULL,NULL,'Kongluan Lin','property_property','2012-09-04 02:09:26','','','User[Kongluan Lin] add Property [11 Swan Avenue, Petersham]'),(157,157,1,NULL,NULL,'Kongluan Lin','property_property','2012-09-04 02:09:53','','','User[Kongluan Lin] add Property [12 Swan Avenue, Petersham]'),(158,158,1,NULL,NULL,'Kongluan Lin','property_property','2012-09-04 02:12:20','','','User[Kongluan Lin] add Property [101 Cleveland Steet, Petersham]'),(159,159,1,NULL,NULL,'Kongluan Lin','property_property','2012-09-04 02:12:54','','','User[Kongluan Lin] add Property [102 Cleveland Steet, Petersham]'),(160,160,1,NULL,NULL,'Kongluan Lin','property_property','2012-09-04 02:13:27','','','User[Kongluan Lin] add Property [103 Cleveland Steet, Petersham]'),(161,161,1,NULL,NULL,'Kongluan Lin','property_property','2012-09-04 02:14:04','','','User[Kongluan Lin] add Property [104 Cleveland Steet, Petersham]'),(162,162,1,NULL,NULL,'Kongluan Lin','property_property','2012-09-04 02:14:44','','','User[Kongluan Lin] add Property [105 Cleveland Steet, Petersham]'),(163,163,1,NULL,NULL,'Kongluan Lin','property_property','2012-09-04 02:18:56','','','User[Kongluan Lin] add Property [106 Cleveland Steet, Petersham]'),(164,164,1,NULL,NULL,'Kongluan Lin','property_property','2012-09-04 02:19:27','','','User[Kongluan Lin] add Property [107 Cleveland Steet, Petersham]'),(165,165,1,NULL,NULL,'Kongluan Lin','property_property','2012-09-04 02:20:02','','','User[Kongluan Lin] add Property [108 Cleveland Steet, Petersham]'),(166,166,1,NULL,NULL,'Kongluan Lin','property_property','2012-09-04 03:55:19','','','User[Kongluan Lin] add Property [109 Cleveland Steet, Petersham]'),(167,167,1,NULL,NULL,'Kongluan Lin','property_property','2012-09-04 03:57:39','','','User[Kongluan Lin] add Property [110 Cooper Street, Petersham]'),(168,168,1,NULL,NULL,'Kongluan Lin','property_property','2012-09-04 03:58:43','','','User[Kongluan Lin] add Property [111 Cooper Street, Petersham]'),(169,169,1,NULL,NULL,'Kongluan Lin','property_property','2012-09-04 04:00:25','','','User[Kongluan Lin] add Property [112 Cooper Street, Petersham]'),(170,170,1,NULL,NULL,'Kongluan Lin','citizen_citizen','2012-09-04 04:33:45','','','User[Kongluan Lin] add Citizen [Mary Roman]'),(171,171,1,NULL,NULL,'Kongluan Lin','citizen_citizen','2012-09-04 04:42:12','','','User[Kongluan Lin] view Citizen [Paul Kennardy]'),(172,172,1,NULL,NULL,'Kongluan Lin','citizen_citizen','2012-09-04 04:43:56','','','User[Kongluan Lin] view Citizen [Paul Kennardy]'),(173,173,1,NULL,NULL,'Kongluan Lin','citizen_citizen','2012-09-04 04:44:47','','','User[Kongluan Lin] view Citizen [Paul Kennardy]'),(174,174,1,NULL,NULL,'Kongluan Lin','citizen_citizen','2012-09-04 04:45:21','','','User[Kongluan Lin] view Citizen [Paul Kennardy]'),(175,175,1,NULL,NULL,'Kongluan Lin','citizen_citizen','2012-09-04 04:45:56','','','User[Kongluan Lin] view Citizen [Paul Kennardy]'),(176,176,1,NULL,NULL,'Kongluan Lin','citizen_citizen','2012-09-04 04:49:08','','','User[Kongluan Lin] view Citizen [Mark Tong]'),(177,177,1,NULL,NULL,'Kongluan Lin','citizen_citizen','2012-09-04 04:49:30','','','User[Kongluan Lin] view Citizen [Mark Yong]'),(178,178,1,NULL,NULL,'Kongluan Lin','citizen_citizen','2012-09-04 04:49:43','','','User[Kongluan Lin] view Citizen [Mark Young]'),(179,179,1,NULL,NULL,'Kongluan Lin','citizen_citizen','2012-09-04 04:58:54','','','User[Kongluan Lin] delete Citizen [Mary Roman]'),(180,180,1,NULL,NULL,'Kongluan Lin','citizen_citizen','2012-09-04 04:59:59','','','User[Kongluan Lin] view Citizen [Bob Smith]'),(181,181,1,NULL,NULL,'Kongluan Lin','citizen_citizen','2012-09-04 05:00:34','','','User[Kongluan Lin] view Citizen [Bob Smith]'),(182,182,5,NULL,NULL,'justin Hopley','citizen_citizen','2012-09-04 22:49:36','','','User[justin Hopley] add Citizen [Michael Kay]'),(183,183,5,NULL,NULL,'justin Hopley','auth_user','2012-09-04 22:50:58','','','User[justin Hopley] logout'),(184,184,5,NULL,NULL,'justin Hopley','auth_user','2012-09-04 22:51:29','','','User[justin Hopley] login'),(185,185,5,NULL,NULL,'justin Hopley','auth_group','2012-09-04 22:53:16','','','User[justin Hopley] view Group [dev1]'),(186,186,1,NULL,NULL,'Kongluan Lin','auth_user','2012-09-04 22:55:02','','','User[Kongluan Lin] logout'),(187,187,1,NULL,NULL,'Kongluan Lin','auth_user','2012-09-04 23:04:10','','','User[Kongluan Lin] login'),(188,188,5,NULL,NULL,'justin Hopley','property_property','2012-09-04 23:13:10','','','User[justin Hopley] add Property [9 Elezebeth Street, Glebe]'),(189,189,5,NULL,NULL,'justin Hopley','property_property','2012-09-04 23:13:42','','','User[justin Hopley] add Property [10 Elezebeth Street, Glebe]');
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
) ENGINE=MyISAM AUTO_INCREMENT=193 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `property_boundary`
--

LOCK TABLES `property_boundary` WRITE;
/*!40000 ALTER TABLE `property_boundary` DISABLE KEYS */;
INSERT INTO `property_boundary` VALUES (88,'\0\0\0\0\0\0\0\0\0\0\0\0\0‡ª‹©áIAƒπ¿$êx\n¡^EÎZ´áIA|^uuJy\n¡hú·=√áIA9”Ñ=$y\n¡7≤ø¡áIAi?Œ≥nx\n¡‡ª‹©áIAƒπ¿$êx\n¡','manual','active'),(2,'\0\0\0\0\0\0\0\0\0\0\0\0\0$Dò¬áIAﬁŒ◊øQq\n¡@∑<e≠áIA}6©gp\n¡‰íô(µáIARzt¿o\n¡}àÿ∑áIA\ZMë áo\n¡G@&ÃáIA#±0˛up\n¡$Dò¬áIAﬁŒ◊øQq\n¡','manual','active'),(3,'\0\0\0\0\0\0\0\0\0\0\0\0\0G@&ÃáIA¸ç4plp\n¡!H\nπáIAÈnçÆêo\n¡Ú∆ì}√áIA§˘&Ön\n¡1rªÿáIA˛‰úvjo\n¡G@&ÃáIA¸ç4plp\n¡','manual','active'),(4,'\0\0\0\0\0\0\0\0\0\0	\0\0\0§4õ∞ÿáIAÔ∞¢!\\o\n¡¢˜!¯«áIA.Í^´n\n¡+® √áIAıÄ˝ò{n\n¡V¥‰¬áIAÍ≈ı¥én\n¡ö›§Õ¿áIA∂nˇ—vn\n¡l£@ÀáIAJûà°#m\n¡˜@ÜÓ‰áIA2!Ad‘m\n¡9å8BﬂáIA;Ö‡A√n\n¡§4õ∞ÿáIAÔ∞¢!\\o\n¡','manual','active'),(5,'\0\0\0\0\0\0\0\0\0\0\0\0\0óè§ÈáIA©ëmÉfm\n¡d9Æ9—áIAâß1◊l\n¡∞+M÷áIAU∞¯ãl\n¡G¿2óÌáIA\n‹∫kßl\n¡óè§ÈáIA©ëmÉfm\n¡','manual','active'),(6,'\0\0\0\0\0\0\0\0\0\0\0\0\0G¿2óÌáIA\n‹∫kßl\n¡d9Æ9—áIAÏ∆ﬁk\n¡¯êKÀ◊áIA’irì·j\n¡¢Ií‹áIAë√Ìj\n¡Ä°¢„ÌáIA™ÕÉî∂j\n¡ãH^£¯áIAnU<)k\n¡G¿2óÌáIA\n‹∫kßl\n¡','manual','active'),(7,'\0\0\0\0\0\0\0\0\0\0\r\0\0\0¢Ií‹áIAë√Ìj\n¡*X>Ì–áIA%TËk\n¡∞+M÷áIA=¡ˆRl\n¡\0˚ç“—áIAˇ ≥á∫l\n¡Z‚∑VπáIAKıß!l\n¡Z‚∑VπáIA˙5Ìk\n¡¯Q\rÁ´áIAVï¶ñ`j\n¡¸.Y¢áIA\n¶ÅKi\n¡¸.Y¢áIA¥1üi\n¡T\0	•áIAÊK=ıÎh\n¡å©™x≤áIAµm9Éıh\n¡^oˆÎºáIAae8i\n¡¢Ií‹áIAë√Ìj\n¡','manual','active'),(8,'\0\0\0\0\0\0\0\0\0\0\n\0\0\0!H\nπáIAKıß!l\n¡YíÚy∆áIA∏–ﬁrl\n¡Ú∆ì}√áIA˘ﬁùÔl\n¡2¬ÄÙ áIAbçä⁄m\n¡ ±Ç-∆áIAÛCùœm\n¡ÌÈèÕáIA6ö3’ım\n¡/5B_«áIA‡\nÓ–°n\n¡ö›§Õ¿áIA∂nˇ—vn\n¡¯Q\rÁ´áIA˛D÷ m\n¡!H\nπáIAKıß!l\n¡','manual','active'),(9,'\0\0\0\0\0\0\0\0\0\0\0\0\0ÏΩùKÉáIA≈¥\"1o\n¡™rÎ˜àáIAæ“ûØeo\n¡ßÂ¨bÖáIA∆Éë®o\n¡é—~áIAÔ∞¢!\\o\n¡y˚Ω≤ÇáIA≠%≤È5o\n¡ÏΩùKÉáIA≈¥\"1o\n¡','manual','active'),(10,'\0\0\0\0\0\0\0\0\0\0\0\0\0=*˛œ©áIAu¨1ú˙m\n¡a¸4Å¿áIA.Í^´n\n¡ZåJÆáIA«6>çTp\n¡&íıüáIA∆Éë®o\n¡ÜﬂÚ*ûáIA$ôto\n¡=*˛œ©áIAu¨1ú˙m\n¡','manual','active'),(11,'\0\0\0\0\0\0\0\0\0\0	\0\0\0áy#eáIA@ZIñm\n¡Év±náIA2!Ad‘m\n¡«ÎföláIAa6\"‘ n\n¡	7ÓfáIA(f9ÄÁm\n¡\\ì…fáIAa6\"‘ n\n¡”‚Á6jáIAº∞EBn\n¡QúHlháIAÏó¶n\n¡UyLﬁ^áIAº∞EBn\n¡áy#eáIA@ZIñm\n¡','manual','active'),(12,'\0\0\0\0\0\0\0\0\0\0\0\0\0Û\'‡R}áIA(Åãuïo\n¡[Û>OÄáIADÈ≤o\n¡†À/8~áIAµâQ«$p\n¡ö°ΩyáIAãÌb»˘o\n¡Öêm|áIAíâ<öo\n¡Û\'‡R}áIA(Åãuïo\n¡','manual','active'),(13,'\0\0\0\0\0\0\0\0\0\0\0\0\0ÀCK\Z\0àIAÛCùœm\n¡?VèÛáIA_ﬂπÕ\"o\n¡@ˆzIŸáIA[ÅRØp\n¡vJ¨\0÷áIA{b\0mÌp\n¡àÃg’áIAùµ°É◊q\n¡QgÓV¯áIAZEA_s\n¡íb€ÕˇáIAhy˝ïms\n¡⁄«\nLàIAv≠˜Í{s\n¡?8ëàIA	Ü¥*s\n¡P6XàIAhy˝ïms\n¡)˜ÒàIA™í3“Ár\n¡Ë˚°àIAQ·ccpr\n¡X1¶§àIAzòfÔq\n¡÷Í⁄\nàIA!Z»˜wq\n¡çÖ◊[	àIAîQ¶Ëp\n¡eG®	àIAáYb*n\n¡ÀCK\Z\0àIAÛCùœm\n¡','manual','active'),(14,'\0\0\0\0\0\0\0\0\0\0\0\0\0ö°ΩyáIAd f:o\n¡†À/8~áIAŒxS\0 p\n¡ú>Ò¢záIA#±0˛up\n¡®5r?xáIAI<TYp\n¡ö°ΩyáIA§‹dıo\n¡ö°ΩyáIAd f:o\n¡','manual','active'),(15,'\0\0\0\0\0\0\0\0\0\0\0\0\0»;,w_áIAô(Zn\n¡HµkáIAÓ>Ë%∞n\n¡ä}∏∏háIAûÒ∑î\'o\n¡JÇÀAaáIA1 ÿ]÷n\n¡Ûò‹ë^áIA¢j™Io\n¡óƒ˛1YáIAêΩΩ?o\n¡»;,w_áIAô(Zn\n¡','manual','active'),(16,'\0\0\0\0\0\0\0\0\0\0\0\0\0àÃg’áIA´ÈõÿÂq\n¡ãH^£¯áIAAVds\n¡íb€ÕˇáIA´ÓÕìs\n¡UÙ,Ï˚áIA∂Ω<t\n¡\nRÑµÈáIAZEA_s\n¡¢Ií‹áIA∆zq≤t\n¡àÃg’áIA´ÈõÿÂq\n¡','manual','active'),(17,'\0\0\0\0\0\0\0\0\0\0\0\0\0óƒ˛1YáIAûÒ∑î\'o\n¡UyLﬁ^áIA…ç¶ìRo\n¡4‰éÂXáIAZ_Vp\n¡K“êTáIAaQt…Œo\n¡óƒ˛1YáIAûÒ∑î\'o\n¡','manual','active'),(18,'\0\0\0\0\0\0\0\0\0\0\0\0\0›â£ˆtáIA◊‹Ú›q\n¡‰£ !|áIA¥2È¿&q\n¡ØOÔiáIA\n¬.≈zp\n¡®5r?xáIA¯BˇJp\n¡kCuáIA¢Ö¸˙ˆp\n¡›â£ˆtáIA◊‹Ú›q\n¡','manual','active'),(19,'\0\0\0\0\0\0\0\0\0\0\0\0\0\rﬂ¬JÌáIAoÜ4m^u\n¡é’ú8¸áIA•øut\n¡}dNÍáIAAVds\n¡}d)+›áIAá|™≠t\n¡\rﬂ¬JÌáIAoÜ4m^u\n¡','manual','active'),(20,'\0\0\0\0\0\0\0\0\0\0\0\0\0åCrNáIAÍ‡G™<p\n¡0WPPUáIA‰û27qp\n¡<N—ÏRáIAxÈ\r¸Àp\n¡®ˆ3[LáIA1Â*SÑp\n¡åCrNáIAÍ‡G™<p\n¡','manual','active'),(21,'\0\0\0\0\0\0\0\0\0\0\0\0\0kCuáIAò Ù\nq\n¡c]ÅVzáIA¬f„5q\n¡›â£ˆtáIAΩñàûr\n¡’UJoáIAπñ-Ùq\n¡kCuáIAò Ù\nq\n¡','manual','active'),(22,'\0\0\0\0\0\0\0\0\0\0\0\0\0ﬁ‘≠qáIA°.îÙ¯q\n¡Ü†¥FráIA‡@íª˝q\n¡X∂≈ñoáIA `Òyr\n¡c≠F3máIAämÄXr\n¡’UJoáIAÑ∆üJ‹q\n¡Z|páIAzòfÔq\n¡ﬁ‘≠qáIA°.îÙ¯q\n¡','manual','active'),(23,'\0\0\0\0\0\0\0\0\0\0\0\0\0àê›JáIA\'*#oóp\n¡ê™ÅRáIAjµßΩp\n¡Ø±ÖSáIAîQ¶Ëp\n¡´ÉrOáIA!Z»˜wq\n¡ÈAÊÆFáIA€UÂN0q\n¡ÈAÊÆFáIA€UÂN0q\n¡àê›JáIA\'*#oóp\n¡','manual','active'),(24,'\0\0\0\0\0\0\0\0\0\0\0\0\0÷o&ÃmáIAœeúkr\n¡®5r?xáIAˆD”ºr\n¡_–B¡váIA˜ÿ+Ó˙r\n¡ƒWÉjáIAY”HE≥r\n¡U)áláIA*æg’fr\n¡÷o&ÃmáIAœeúkr\n¡','manual','active'),(25,'\0\0\0\0\0\0\0\0\0\0\0\0\0vFáIAy·‹9q\n¡r¢§OáIA0é¬LÜq\n¡r¢§OáIAÑ∆üJ‹q\n¡D∏ÙLáIA«QêÇr\n¡9X4BáIAô<Ø∂q\n¡vFáIAy·‹9q\n¡','manual','active'),(26,'\0\0\0\0\0\0\0\0\0\0\0\0\0ç∫1qyáIAY”HE≥r\n¡0ñé4ÅáIA¥M;∂‘r\n¡ØOÔiáIA∫	9s\n¡&Ô“tváIA\r&C	s\n¡“í\"ZwáIAq¬J~Ær\n¡ç∫1qyáIAY”HE≥r\n¡','manual','active'),(27,'\0\0\0\0\0\0\0\0\0\0	\0\0\0j8¿úUáIAãµΩßq\n¡˚ôXáIAô<Ø∂q\n¡RÏ\rI[áIA–ö›jCq\n¡Ûò‹ë^áIA·’ÜVq\n¡ãÕ}ï[áIAùµ°É◊q\n¡èZº*_áIAzòfÔq\n¡íÁ˙øbáIA–ö›jCq\n¡	áﬁ YáIA∞πˆOq\n¡j8¿úUáIAãµΩßq\n¡','manual','active'),(28,'\0\0\0\0\0\0\0\0\0\0\0\0\0ÏΩùKÉáIAgCö¡r\n¡x´¯’èáIAñ{/s\n¡É¢yrçáIAù–ÛxÖs\n¡î‘ÆõÄáIA‚b&!s\n¡ÏΩùKÉáIAgCö¡r\n¡','manual','active'),(29,'\0\0\0\0\0\0\0\0\0\0\0\0\0x´¯’èáIA!u\ZÌ%s\n¡É¢yrçáIA‘.\"—s\n¡{87kìáIAämÄXr\n¡pA∂ŒïáIA\n›Ä∫(r\n¡ÀòáIAÁ2wù@r\n¡{87kìáIA˛ –=s\n¡ñgñáIAZEA_s\n¡(‹ÜPîáIA§¬ÿZ»s\n¡!¬	&çáIA^æı±Äs\n¡i\'9§éáIA‘.\"—s\n¡ˆdYéáIAA òs\n¡x´¯’èáIA!u\ZÌ%s\n¡','manual','active'),(30,'\0\0\0\0\0\0\0\0\0\0\0\0\0≤ùÔ\ZWáIAùµ°É◊q\n¡j8¿úUáIAÚÌ~Å-r\n¡≈ÆÌ·[áIAC≠ibr\n¡èZº*_áIA°.îÙ¯q\n¡≤ùÔ\ZWáIAùµ°É◊q\n¡','manual','active'),(31,'\0\0\0\0\0\0\0\0\0\0\0\0\0&íıüáIAœ^«YÛs\n¡ƒùfÈîáIApk‚w∞s\n¡7`FÇïáIA%Ó^Gs\n¡äºˆúîáIAÿßB4s\n¡ê‘¸ôáIAˆfqÚNr\n¡/ˆ{õáIAQ·ccpr\n¡ŒD\"©üáIAÁ2wù@r\n¡ƒŒQ®áIAC≠ibr\n¡ÇÔ∏ßáIA.7ZFàr\n¡LÆΩ´áIAq¬J~Ær\n¡@∑<e≠áIAõ^9}Ÿr\n¡øpùö´áIA˜ÿ+Ó˙r\n¡[2}3¨áIAÿßB4s\n¡=*˛œ©áIA^æı±Äs\n¡IéÉ©áIApk‚w∞s\n¡@ ßáIAÀÂ‘Ë—s\n¡∏V p§áIA¡*ÕÂs\n¡&íıüáIAœ^«YÛs\n¡','manual','active'),(32,'\0\0\0\0\0\0\0\0\0\0\0\0\0YãsbáIA¸®Üe\Zr\n¡\\ì…fáIA\0\"y÷;r\n¡M\n◊dáIAîlTõñr\n¡◊øÎ®`áIAQ·ccpr\n¡YãsbáIA¸®Üe\Zr\n¡','manual','active'),(33,'\0\0\0\0\0\0\0\0\0\0\0\0\0Á ﬂ±áIAÉo7Dﬁr\n¡–1÷ÑΩáIA´ÈõÿÂq\n¡K^¯$∏áIAü¿ãq\n¡Öè-N´áIA∞πˆOq\n¡9ùø:¶áIA˚6Ãinq\n¡‡[ì±áIA°.îÙ¯q\n¡øpùö´áIAcéP)†r\n¡ÕMµ™áIAmIX\rçr\n¡âl„ÆáIAŸ˛|H2r\n¡LÆΩ´áIAG&\\Ér\n¡Á ﬂ±áIAÉo7Dﬁr\n¡','manual','active'),(34,'\0\0\0\0\0\0\0\0\0\0\0\0\0U)áláIAùöOé)p\n¡MøD˙qáIA‡%@∆Op\n¡ÂÛÂ˝náIAm.ﬂp\n¡ƒ^(iáIAÇ§‡∏p\n¡U)áláIAùöOé)p\n¡','manual','active'),(35,'\0\0\0\0\0\0\0\0\0\0\n\0\0\0ëÜÆÍ®áIAqß¯à\0q\n¡&íıüáIA1Â*SÑp\n¡º3$‚öáIAQ∆n¬p\n¡Eî@◊£áIA–ö›jCq\n¡¸.Y¢áIA·’ÜVq\n¡≠Ød∞ôáIAqß¯à\0q\n¡ø¿bwûáIA#±0˛up\n¡ëÜÆÍ®áIA¢Ö¸˙ˆp\n¡ôÒ¢áIAÌ“`q\n¡ëÜÆÍ®áIAqß¯à\0q\n¡','manual','active'),(36,'\0\0\0\0\0\0\0\0\0\0\0\0\0“í\"ZwáIA¢j™Io\n¡Œ‰ƒsáIAÅ2[‰p\n¡ƒWÉjáIAd f:o\n¡Õ÷ÊláIAóÀxo\n¡QñnáIAxŒªo\n¡“í\"ZwáIA¢j™Io\n¡','manual','active'),(37,'\0\0\0\0\0\0\0\0\0\0\0\0\0íùáIA}6©gp\n¡Ó˙îáIA}πhsÎo\n¡È=èáIAI<TYp\n¡ê‘¸ôáIAÇ§‡∏p\n¡íùáIA}6©gp\n¡','manual','active'),(38,'\0\0\0\0\0\0\0\0\0\0\0\0\0íùáIA}6©gp\n¡Ó˙îáIA}πhsÎo\n¡È=èáIAI<TYp\n¡ê‘¸ôáIAÇ§‡∏p\n¡íùáIA}6©gp\n¡','manual','active'),(39,'\0\0\0\0\0\0\0\0\0\0\0\0\0BW«ìáIAãÌb»˘o\n¡0F…WéáIA6µÖ £o\n¡,πä¬äáIAŒxS\0 p\n¡x´¯’èáIAÓY:^p\n¡7∞_àáIA◊‹Ú›q\n¡!œÄáIA?%®íp\n¡%ü\ròÉáIAI<TYp\n¡õÓ+∆ááIA?%®íp\n¡;=JÙãáIA‹¨MU.p\n¡∏¶ÂLóáIA[ÅRØp\n¡˙Òó†ëáIAy·‹9q\n¡;=JÙãáIAîQ¶Ëp\n¡5ÀêâáIA€UÂN0q\n¡™rÎ˜àáIAò Ù\nq\n¡BW«ìáIAãÌb»˘o\n¡','manual','active'),(40,'\0\0\0\0\0\0\0\0\0\0\0\0\0MøD˙qáIA]Ω/cˇm\n¡Wf\0∫|áIAÍ≈ı¥én\n¡Wf\0∫|áIAb‰≥πn\n¡ö°ΩyáIAªY¨>Do\n¡Œ‰ƒsáIAxŒªo\n¡Ï\rc(váIA.Í^´n\n¡íó5„oáIAã“”Kn\n¡MøD˙qáIA]Ω/cˇm\n¡','manual','active'),(41,'\0\0\0\0\0\0\0\0\0\0\0\0\0È=èáIAV{\Z3n\n¡È=èáIA§˘&Ön\n¡3”ÌëáIA§˘&Ön\n¡BW«ìáIAtU…ï¸n\n¡≠Ød∞ôáIAf!œ@Ón\n¡©\"&ñáIAã“”Kn\n¡º3$‚öáIAV{\Z3n\n¡≈u\0óáIAí&Fn\n¡É¢yrçáIA†H õ%n\n¡ˆdYéáIAïç∑8n\n¡È=èáIAV{\Z3n\n¡','manual','active'),(42,'\0\0\0\0\0\0\0\0\0\0\0\0\0|˘¯ÜgáIA¥2È¿&q\n¡U)áláIAy·‹9q\n¡˝?òQiáIAví•ıÕq\n¡M\n◊dáIAdÂ∏/ûq\n¡|˘¯ÜgáIA¥2È¿&q\n¡','manual','active'),(43,'\0\0\0\0\0\0\0\0\0\0\0\0\0ø¿bwûáIAS(n\n¡H!lßáIA^òi˝l\n¡:ÌÑôáIAˇ ≥á∫l\n¡¶ïÁÖíáIA·aV◊üm\n¡IqDIöáIAgx7GÏm\n¡ø¿bwûáIAS(n\n¡','manual','active'),(44,'\0\0\0\0\0\0\0\0\0\0\n\0\0\0;˛`áIA Ë\r¸Àp\n¡Á°[ı`áIAÄRØp\n¡|˘¯ÜgáIAU?ﬂ„p\n¡ÓªÿháIACí¥p\n¡;˛`áIA\n¬.≈zp\n¡Fıå¨]áIAQ∆n¬p\n¡»;,w_áIA Ë\r¸Àp\n¡ú√_áIA Ë\r¸Àp\n¡ú√_áIA9◊5«p\n¡;˛`áIA Ë\r¸Àp\n¡','manual','active'),(45,'\0\0\0\0\0\0\0\0\0\0	\0\0\0äl1¿°áIA*Ω°ÜÂl\n¡¬˝€/ØáIAj\0p˚k\n¡@∑<e≠áIAy\n“nl\n¡IéÉ©áIAú¥€4Vl\n¡ŒÙ\\Ã¨áIAá>Ãl|l\n¡O;¸ñÆáIAz˛6\0l\n¡LÆΩ´áIA⁄T\0Øk\n¡ÉR¥ïöáIA\n‹∫kßl\n¡äl1¿°áIA*Ω°ÜÂl\n¡','manual','active'),(46,'\0\0\0\0\0\0\0\0\0\0\0\0\0÷o&ÃmáIAb‰≥πn\n¡\"bîﬂráIAJπ⁄ñ—n\n¡g:Ö»páIAî6∞∞:o\n¡U)áláIAêΩΩ?o\n¡÷o&ÃmáIAb‰≥πn\n¡','manual','active'),(47,'\0\0\0\0\0\0\0\0\0\0\0\0\0ä-Û€uáIA∞∏0Ñk\n¡™rÎ˜àáIA`PÆzMj\n¡;=JÙãáIA|∏¢$jj\n¡F‰¥ñáIAâz‚}Ãi\n¡IqDIöáIAë√Ìj\n¡ñgñáIAßTë#ïj\n¡ê‘¸ôáIA«5x>”j\n¡ê‘¸ôáIA˚ån!Îj\n¡ŒD\"©üáIAÄ1ïïãj\n¡ç˘oU•áIAnU<)k\n¡¸.Y¢áIAi¥MX<k\n¡’^ü”¶áIAó….»àk\n¡ƒùfÈîáIAıe´£Õl\n¡5ÀêâáIA3Ôn&l\n¡‰S[DâáIAñr∆¡äl\n¡|à¸GÜáIAñr∆¡äl\n¡y˚Ω≤ÇáIA3Ôn&l\n¡r·@à{áIA‡8’k\n¡ö°ΩyáIA‡8’k\n¡ä-Û€uáIA∞∏0Ñk\n¡','manual','active'),(48,'\0\0\0\0\0\0\0\0\0\0\0\0\0⁄¸daqáIAj\0p˚k\n¡I2enáIAk÷◊¬_l\n¡ä-Û€uáIA§¶¿ôl\n¡·‚ãxáIAA:È√4l\n¡⁄¸daqáIAj\0p˚k\n¡','manual','active'),(50,'\0\0\0\0\0\0\0\0\0\0\0\0\0¸≤ÉÜàIA˘Ûè¶p\n¡_È!–ÜàIAf~˙…q\n¡É|\ZùqàIA]ìmïq\n¡É|\ZùqàIA…mXÄp\n¡¸≤ÉÜàIA˘Ûè¶p\n¡','manual','active'),(51,'\0\0\0\0\0\0\0\0\0\0\0\0\0¸≤ÉÜàIA&\nÄ3≈q\n¡oÀëáàIAr˘I⁄r\n¡/ jÇràIAZ\nﬂr\n¡/ jÇràIA¸më4öq\n¡¸≤ÉÜàIA&\nÄ3≈q\n¡','manual','active'),(52,'\0\0\0\0\0\0\0\0\0\0\0\0\0Á∫:qàIAZ\nﬂr\n¡çqµáàIAô◊„r\n¡~OQNààIA¥-òzt\n¡ ú™PqàIAç\núÏ¯s\n¡Á∫:qàIAZ\nﬂr\n¡','manual','active'),(53,'\0\0\0\0\0\0\0\0\0\0\0\0\0çqµáàIA⁄Pît\n¡/ jÇràIAÃö≥˝s\n¡i⁄ŒràIAÒË-;	u\n¡çqµáàIAŸ˘+u\n¡çqµáàIA⁄Pît\n¡','manual','active'),(54,'\0\0\0\0\0\0\0\0\0\0\0\0\0º]äÈqàIAÒË-;	u\n¡®¨iáàIAŸ˘+u\n¡oÀëáàIAÊ÷ΩPv\n¡ˆ>˙5ràIAÊ÷ΩPv\n¡º]äÈqàIAÒË-;	u\n¡','manual','active'),(55,'\0\0\0\0\0\0\0\0\0\0\0\0\0oÀëáàIAë≈4v\n¡t¯ZkpàIAÅ«mv\n¡Á∫:qàIAç@@◊Tw\n¡®¨iáàIAtQ>ûYw\n¡oÀëáàIAë≈4v\n¡','manual','active'),(56,'\0\0\0\0\0\0\0\0\0\0\0\0\0ÿ6{“oàIA‘’w\n¡®¨iáàIA€6bﬂw\n¡Ò1ÁààIAwé\Z˛*z\n¡pW˘yàIA—ñRs†y\n¡i⁄ŒràIAE±\\∂x\n¡ÿ6{“oàIA‘’w\n¡','manual','active'),(57,'\0\0\0\0\0\0\0\0\0\0\0\0\0qk÷làIAùz¨RWq\n¡„-¸nmàIAÇi Ø8p\n¡√ËSZàIApº3Èp\n¡∏uÿUàIAùz¨RWq\n¡qk÷làIAùz¨RWq\n¡','manual','active'),(58,'\0\0\0\0\0\0\0\0\0\0\0\0\07ä¨âlàIA‹å™\\q\n¡{”ô±KàIAùz¨RWq\n¡ïyJLàIA(|:/qr\n¡„-¸nmàIA(|:/qr\n¡7ä¨âlàIA‹å™\\q\n¡','manual','active'),(59,'\0\0\0\0\0\0\0\0\0\0\0\0\0™Lå\"màIA˜ù6Ωzr\n¡µ¥	˛KàIAÈi<hlr\n¡˝9|MàIAÜ∑\n∂s\n¡qk÷làIAm)µ—∫s\n¡™Lå\"màIA˜ù6Ωzr\n¡','manual','active'),(60,'\0\0\0\0\0\0\0\0\0\0\0\0\0õ»ÃkàIAm)µ—∫s\n¡ƒ8…/MàIAÜ∑\n∂s\n¡˝9|MàIAvçTØ©t\n¡˙‹ø√<àIAù∞P=≥t\n¡ΩLFàIA˛≈øâv\n¡bÁ\\§kàIAë≈4v\n¡õ»ÃkàIAm)µ—∫s\n¡','manual','active'),(61,'\0\0\0\0\0\0\0\0\0\0\0\0\0Ô$}kàIAµ¡¬v\n¡ˆˇªQFàIAµ¡¬v\n¡äWY„LàIA*_gw\n¡Ô$}kàIA^Yºw\n¡Ô$}kàIAµ¡¬v\n¡','manual','active'),(62,'\0\0\0\0\0\0\0\0\0\0	\0\0\07ä¨âlàIA<ÅUJ w\n¡ïyJLàIA.M[ıw\n¡IßèRàIA…âúØw\n¡âîZàIAe∆€BMx\n¡)V≤4^àIAÖß¬]ãx\n¡0p/_eàIAÚŒ°î‹x\n¡—˛ßhàIA‰öß?Œx\n¡µC\røjàIA®QÃzsx\n¡7ä¨âlàIA<ÅUJ w\n¡','manual','active'),(63,'\0\0\0\0\0\0\0\0\0\0\0\0\0æ˙xËúàIA}ô≈7q\n¡êä8öàIAR˝÷8Óp\n¡oÀëáàIA>Ï´πp\n¡¸≤ÉÜàIAf~˙…q\n¡ €Ë4ùàIAÜ˝dr\n¡æ˙xËúàIA}ô≈7q\n¡','manual','active'),(64,'\0\0\0\0\0\0\0\0\0\0\0\0\0æ˙xËúàIAmc‹r\n¡çqµáàIA[av›q\n¡çqµáàIAZ\nﬂr\n¡ €Ë4ùàIAèaÛˆr\n¡æ˙xËúàIAmc‹r\n¡','manual','active'),(65,'\0\0\0\0\0\0\0\0\0\0\0\0\0 €Ë4ùàIAèaÛˆr\n¡®¨iáàIAZ\nﬂr\n¡®¨iáàIA⁄Pît\n¡ €Ë4ùàIA⁄Pît\n¡ €Ë4ùàIAèaÛˆr\n¡','manual','active'),(66,'\0\0\0\0\0\0\0\0\0\0\0\0\0Õ~8\ZûàIA–ïå$t\n¡oÀëáàIAÈÑé]\Zt\n¡çqµáàIAF!9_u\n¡`®fûàIA*πèBu\n¡Õ~8\ZûàIA–ïå$t\n¡','manual','active'),(67,'\0\0\0\0\0\0\0\0\0\0\0\0\0?A≥ûàIAfÚSùu\n¡¸≤ÉÜàIAó‡ı≈ìu\n¡çqµáàIA\ZI)‰w\n¡Õ~8\ZûàIA\ZI)‰w\n¡?A≥ûàIAfÚSùu\n¡','manual','active'),(68,'\0\0\0\0\0\0\0\0\0\0\0\0\0æ˙xËúàIA€6bﬂw\n¡6Í!–ÜàIA€6bﬂw\n¡®¨iáàIA\\}éZy\n¡æ˙xËúàIA+üäËy\n¡æ˙xËúàIA€6bﬂw\n¡','manual','active'),(69,'\0\0\0\0\0\0\0\0\0\0\0\0\0 €Ë4ùàIA\\}éZy\n¡¸≤ÉÜàIA5ZíÃy\n¡~OQNààIAè}7&z\n¡Åå ôàIA\0Óﬁòz\n¡ €Ë4ùàIA\\}éZy\n¡','manual','active'),(70,'\0\0\0\0\0\0\0\0\0\0\0\0\0ö∑E¯§àIA†CœTq\n¡v$M+∫àIA‰†¸sq\n¡ÈÊ,ƒ∫àIA:)\'ı†r\n¡q¶-£àIAûÏfNr\n¡ö∑E¯§àIA†CœTq\n¡','manual','active'),(71,'\0\0\0\0\0\0\0\0\0\0\0\0\0ØΩw∫àIA:)\'ı†r\n¡≈ˆ§àIAÜ˝dr\n¡ã3Ü∆£àIA\0÷öis\n¡ØΩw∫àIA\0÷öis\n¡ØΩw∫àIA:)\'ı†r\n¡','manual','active'),(72,'\0\0\0\0\0\0\0\0\0\0\0\0\0ØΩw∫àIA6–Ôws\n¡q¶-£àIA6–Ôws\n¡ﬂè6·¢àIAﬂgÈyt\n¡v$M+∫àIAﬂgÈyt\n¡ØΩw∫àIA6–Ôws\n¡','manual','active'),(73,'\0\0\0\0\0\0\0\0\0\0\0\0\0ØΩw∫àIA%Œi\"ut\n¡a÷’´§àIAﬂgÈyt\n¡q¶-£àIA•\Z¢u\n¡ØΩw∫àIA{xwu\n¡ØΩw∫àIA%Œi\"ut\n¡','manual','active'),(85,'\0\0\0\0\0\0\0\0\0\0\0\0\0>Ö1˚ÜIA¶‡U÷p\n¡~ÄˇßáIA`1—ç¸p\n¡º>sf˘ÜIAÛ$DLYr\n¡{CÜÔÒÜIA¢eYø$r\n¡>Ö1˚ÜIA¶‡U÷p\n¡','manual','active'),(75,'\0\0\0\0\0\0\0\0\0\0\0\0\0æâ|©ªàIA{xwu\n¡ã3Ü∆£àIAÒÛåòu\n¡a÷’´§àIAsﬂÉ¢≠v\n¡v$M+∫àIAsﬂÉ¢≠v\n¡æâ|©ªàIA{xwu\n¡','manual','active'),(76,'\0\0\0\0\0\0\0\0\0\0\0\0\0\"»úªàIAŸ~˜ªv\n¡≈ˆ§àIAsﬂÉ¢≠v\n¡\'ıe_§àIAé˛D˜w\n¡v$M+∫àIAÒµx\n¡\"»úªàIAŸ~˜ªv\n¡','manual','active'),(77,'\0\0\0\0\0\0\0\0\0\0\0\0\0$d{´áIA\ZI)‰w\n¡‚»ﬁΩáIAÊÒFÃw\n¡d£®øáIAÅ.–Ïix\n¡—ÀÛ´áIAÖß¬]ãx\n¡£‹C©áIAEÂÙ\'x\n¡^EÎZ´áIAEÂÙ\'x\n¡$d{´áIA\ZI)‰w\n¡','manual','active'),(78,'\0\0\0\0\0\0\0\0\0\0\0\0\0=C›ﬁπàIA¬¯ôx\n¡RRz£àIAÈj∑Ìw\n¡ã3Ü∆£àIA⁄ﬂü[·x\n¡v$M+∫àIANIî˛x\n¡=C›ﬁπàIA¬¯ôx\n¡','manual','active'),(79,'\0\0\0\0\0\0\0\0\0\0\0\0\0†Å˝EπàIA9”Ñ=$y\n¡≈ˆ§àIA@ö∞Ôx\n¡¶Æ∆î¢àIAZ&&Tz\n¡ª¸=∏àIAè}7&z\n¡†Å˝EπàIA9”Ñ=$y\n¡','manual','active'),(80,'\0\0\0\0\0\0\0\0\0\0\0\0\0XŒ«∑àIAiZ ©z\n¡ﬂè6·¢àIAs(ç	z\n¡$h\' †àIAÏßﬁøz\n¡q¶-£àIA|y«j¯z\n¡*2ﬂµàIA∆ˆúÑa{\n¡XŒ«∑àIAiZ ©z\n¡','manual','active'),(87,'\0\0\0\0\0\0\0\0\0\0	\0\0\0$∂1∏áIAàUìjáv\n¡~:öÀáIAÑ‹†˘ev\n¡∆üMÕáIAJµOü.w\n¡lyÂØπáIA\'FÇFw\n¡lyÂØπáIA˝nWÉw\n¡êˆˇ∂áIA.M[ıw\n¡€ÆÜ≥∂áIA¿%|æ¿v\n¡–∑πáIAŸ~˜ªv\n¡$∂1∏áIAàUìjáv\n¡','manual','active'),(86,'\0\0\0\0\0\0\0\0\0\0	\0\0\0™7Yn∞áIA´‰Jí¡t\n¡.ªqÒ¬áIAhYZZõt\n¡=?1#ƒáIA VGu\n¡∆üMÕáIAñ\Z9u\n¡HÊÏ‚ŒáIAÏ”√Èu\n¡J˛„£áIA)bÆàDv\n¡’‰Œe¢áIAXŒ˜˛éu\n¡ÚúàÏ±áIA{xwu\n¡™7Yn∞áIA´‰Jí¡t\n¡','manual','active'),(84,'\0\0\0\0\0\0\0\0\0\0\0\0\0!ÕX™ÎÜIA∑¿íPp\n¡Úí§ˆÜIA€\Z∞p\n¡,ƒŸFÈÜIAtPxOÿq\n¡≤Á|É·ÜIA“—¢5oq\n¡!ÕX™ÎÜIA∑¿íPp\n¡','manual','active'),(89,'\0\0\0\0\0\0\0\0\0\0\0\0\0øÖ–Ì≈áIA“Ì∫yûx\n¡Ï˙¿’áIAws»}x\n¡¬¬I¶÷áIA\'&òwÙx\n¡k) ”∆áIACéå!y\n¡k) ”∆áIACéå!y\n¡2H∞Ü∆áIANIî˛x\n¡øÖ–Ì≈áIA“Ì∫yûx\n¡','manual','active'),(90,'\0\0\0\0\0\0\0\0\0\0\0\0\0îô®áIAÕ`y\n¡Õzå^®áIAs(ç	z\n¡^EÎZ´áIAz\roLz\n¡\\¸™®áIAQ›ÿkÕz\n¡õ≥ô<ØáIAcä≈1˝z\n¡e_hÖ≤áIAó‡O∫z\n¡–∑πáIAÄÚπ€{\n¡¥ﬁ.ªáIAÏßﬁøz\n¡ûıøáIAË.Ï•ùz\n¡ﬁÎˇk«áIAâ;ƒZz\n¡2H∞Ü∆áIAW≠3„Ïy\n¡øÖ–Ì≈áIA˜πN™y\n¡\n(y$ÿáIA¥.^…Éy\n¡ånÔŸáIALÚ+ˇˇy\n¡…‹∆–›áIAe·-8˚y\n¡Gñ\'‹áIAxÂÇ)y\n¡È‚Ä≈áIAäío Xy\n¡∞ºƒáIAüí2y\n¡îô®áIAÕ`y\n¡','manual','active'),(91,'\0\0\0\0\0\0\0\0\0\0	\0\0\0^EÎZ´áIApgWÄ\r|\n¡pVÈ!∞áIA¨ÀÑ:~\n¡ÓøÑzªáIAi@î}\n¡aÇdºáIA‘ºØã}\n¡=?1#ƒáIAJÃwe}\n¡€^¡÷√áIA£gÂ\\\'}\n¡O\0j\r÷áIAáˇ≤\n}\n¡1¯Í©”áIABRv¡{\n¡^EÎZ´áIApgWÄ\r|\n¡','manual','active'),(92,'\0\0\0\0\0\0\0\0\0\0\0\0\0ÿ`ÜﬂáIAF!9_u\n¡¨cK.˙áIAz!ôyv\n¡àÓjÚáIA£Qÿ)w\n¡R=„≈ÊáIAñâçøïv\n¡˜∆µÄ‡áIAı|r°ÿv\n¡˜∆µÄ‡áIA∂jt⁄”v\n¡ÿ`ÜﬂáIAF!9_u\n¡','manual','active'),(93,'\0\0\0\0\0\0\0\0\0\0\0\0\0y\rUK‚áIAJµOü.w\n¡J”†æÏáIA a†w\n¡Ã@âÓáIA€6bﬂw\n¡N∞§0„áIA(}\0~Úw\n¡y\rUK‚áIAJµOü.w\n¡','manual','active'),(94,'\0\0\0\0\0\0\0\0\0\0\0\0\0˙SÙ‰áIAI^Áò0x\n¡Øâ√˝áIA(}\0~Úw\n¡&@®ÒàIA±µkXby\n¡Îv:àIA ˇ‘˘÷z\n¡äŒç5ÙáIAÄÚπ€{\n¡nq@ÎáIAUVÀ‹Óz\n¡FFb)ÈáIAQ›ÿkÕz\n¡˙SÙ‰áIAI^Áò0x\n¡','manual','active'),(95,'\0\0\0\0\0\0\0\0\0\0\0\0\0jô⁄ˇáIA<ÅUJ w\n¡Îs»àIA◊ΩÒΩw\n¡<ﬁ‰M\nàIA,ˆÚÓx\n¡≥}»XàIA±öc¥w\n¡jô⁄ˇáIA<ÅUJ w\n¡','manual','active'),(96,'\0\0\0\0\0\0\0\0\0\0\0\0\0bÆV”àIA:*ÌC\"x\n¡ß6ÇﬂàIA¬¯ôx\n¡(}!™àIA9”Ñ=$y\n¡‰ÙıùàIAÜ}Y7y\n¡bÆV”àIA:*ÌC\"x\n¡','manual','active'),(97,'\0\0\0\0\0\0\0\0\0\0\0\0\0ßÜGºàIAéb;zy\n¡ÛxµœàIAøÈe≠py\n¡!c§àIA∫6Qz\n¡)ÕÊÜàIA»Mã_z\n¡ßÜGºàIAéb;zy\n¡','manual','active'),(98,'\0\0\0\0\0\0\0\0\0\0\0\0\00Ác±àIAò∆igy\n¡^—RaàIAË.Ï•ùz\n¡B®úõàIAÚÈÛâäz\n¡˘BmàIAﬂ L»Æy\n¡≠Ø$àIA¶˙ctuy\n¡πGÄ¶àIAîMwÆEy\n¡0Ác±àIAò∆igy\n¡','manual','active'),(99,'\0\0\0\0\0\0\0\0\0\0\0\0\0Æ¡%ÏáIA\"qèıÇ{\n¡T*ó°àIA—±§hN{\n¡Ö°ƒÊ\nàIA%‘[R}\n¡±ûˇ∫ÔáIA-˜∏=ï}\n¡Æ¡%ÏáIA\"qèıÇ{\n¡','manual','active'),(100,'\0\0\0\0\0\0\0\0\0\0\0\0\0YW`ÌáIAEÊ∫vê}\n¡‡Ú+àIA‚y„#,}\n¡7·€àIADèRpí~\n¡áAO†áIAãì5⁄~\n¡YW`ÌáIAEÊ∫vê}\n¡','manual','active'),(101,'\0\0\0\0\0\0\0\0\0\0\0\0\0œ¶~ÚáIA)ô¬!\n¡xLì/àIA±∂1ß„~\n¡|Ÿ—ƒàIA˜c¨I-Ä\n¡`q›\ZıáIA`ô]Ä\n¡œ¶~ÚáIA)ô¬!\n¡','manual','active'),(102,'\0\0\0\0\0\0\0\0\0\0\0\0\0oıúLˆáIArøÖ’åÄ\n¡b^ëˆàIA:ÔúÅSÄ\n¡Ú(ÚàIA:#»Å\n¡ëË\n`˚áIA!Ì=Ç\n¡ôÏ1˜áIAn\0x÷Å\n¡kh^∑ÚáIAÄÛ*õÄ\n¡oıúLˆáIArøÖ’åÄ\n¡','manual','active'),(103,'\0\0\0\0\0\0\0\0\0\0\0\0\0´ÜQàIA¥I∞æ1{\n¡6±ˇ àIA|y«j¯z\n¡·©y%àIA≤2Eh|\n¡∫óEÉàIA.N!Dì|\n¡÷eÍàIAb3]+ˇ{\n¡´ÜQàIA¥I∞æ1{\n¡','manual','active'),(104,'\0\0\0\0\0\0\0\0\0\0\0\0\0xLì/àIAü	E·≥~\n¡:>Zî$àIA8\\çz~\n¡Ü0»ß)àIA+ª¢,EÄ\n¡Ôõ±]àIAïièÚtÄ\n¡xLì/àIAü	E·≥~\n¡','manual','active'),(105,'\0\0\0\0\0\0\0\0\0\0\0\0\01¯Í©”áIA7ón,‘{\n¡Yß%Õ‡áIAZAxIº{\n¡R=„≈ÊáIAz=±Y®}\n¡øÖ–Ì≈áIAåÍùÿ}\n¡€^¡÷√áIAÿæ€??}\n¡à·ŸY÷áIA∆Ôy}\n¡1¯Í©”áIA7ón,‘{\n¡','manual','active'),(106,'\0\0\0\0\0\0\0\0\0\0\0\0\0õ≥ô<ØáIAÎ›Ç~\n¡˙SÙ‰áIAT\ZµÀû}\n¡ãSÁáIAdp9ã–~\n¡ÚúàÏ±áIAÓˇl>\n¡ÚúàÏ±áIAÓˇl>\n¡õ≥ô<ØáIAÎ›Ç~\n¡','manual','active'),(107,'\0\0\0\0\0\0\0\0\0\0\0\0\0˙8±áIA‡À0\n¡Ò¸˝2ÃáIAøÍ+¸Ò~\n¡@|™€‘áIA]d»aÇ\n¡ñ÷ï ∏áIA«µ»êÇ\n¡˙8±áIA‡À0\n¡','manual','active'),(108,'\0\0\0\0\0\0\0\0\0\0\0\0\0Å«\\/œáIA√cm\n¡˛‡2´ÁáIAãì5⁄~\n¡ñ≈“ÒáIA,ÎÇ\n¡õ:è‘áIAYÎ’ë?Ç\n¡rCù˝ÕáIA?ø˜¯r\n¡Å«\\/œáIA√cm\n¡','manual','active'),(109,'\0\0\0\0\0\0\0\0\0\0\0\0\0Œ`ùªàIA‡ùä}q\n¡(áyŒàIAp◊Öﬁ∂q\n¡qÏ4˜œàIAÍ€ˆcs\n¡Œ`ùªàIAk+gór\n¡Œ`ùªàIA‡ùä}q\n¡','manual','active'),(110,'\0\0\0\0\0\0\0\0\0\0\0\0\0ï-ƒ∫àIA/n¥r\n¡’*U^œàIA°Ò∏&s\n¡WqÙ(—àIA‹Ñ@2t\n¡ï-ƒ∫àIA˜∏à≤(t\n¡ï-ƒ∫àIA/n¥r\n¡','manual','active'),(111,'\0\0\0\0\0\0\0\0\0\0\0\0\0\\ûΩw∫àIA‹Ñ@2t\n¡qÏ4˜œàIA+ï@t\n¡™Õ§C–àIAF!9_u\n¡Pß<€ºàIA.2	\0du\n¡\\ûΩw∫àIA‹Ñ@2t\n¡','manual','active'),(112,'\0\0\0\0\0\0\0\0\0\0\0\0\0A#}©ªàIAF!9_u\n¡Ô•ï,ŒàIAF!9_u\n¡bhu≈ŒàIAöÄ0∑v\n¡A#}©ªàIA≤ÒÅi≤v\n¡A#}©ªàIAF!9_u\n¡','manual','active'),(113,'\0\0\0\0\0\0\0\0\0\0\0\0\0Ü˚míπàIA¿%|æ¿v\n¡å≈%‡ÕàIAöÄ0∑v\n¡bhu≈ŒàIA¬¯ôx\n¡⁄W≠∏àIA»2≥ï±x\n¡Ü˚míπàIA¿%|æ¿v\n¡','manual','active'),(114,'\0\0\0\0\0\0\0\0\0\0\0\0\0M\Z˛EπàIA»2≥ï±x\n¡å≈%‡ÕàIAé˛D˜w\n¡j“∑Ã»àIApgWÄ\r|\n¡«F Ê≥àIA	õKf{\n¡M\Z˛EπàIA»2≥ï±x\n¡','manual','active'),(115,'\0\0\0\0\0\0\0\0\0\0\0\0\0√ûvâ-àIAKõ√¯{\n¡ì˝EàIAó‡O∫z\n¡Í˝ÎœGàIA4|ª≤{\n¡·¶ıÏ/àIAb3]+ˇ{\n¡√ûvâ-àIAKõ√¯{\n¡','manual','active'),(116,'\0\0\0\0\0\0\0\0\0\0\0\0\0˚&§,àIAöF8|\n¡\'lö±KàIAÖ›fHÁ{\n¡/Ü‹RàIAû≤‹⁄µ\n¡„„n•@àIA(B∞ª#Ä\n¡HrTÈ2àIAÙA\"ﬂ	\n¡˚&§,àIAöF8|\n¡','manual','active'),(117,'\0\0\0\0\0\0\0\0\0\0	\0\0\08›\røjàIAìˆ®Gz\n¡å9æŸiàIA°E[Ú|\n¡CÑ…~uàIAåÍùÿ}\n¡np}ZìàIA%‘[R}\n¡uä˙ÑöàIA‘*óŸo{\n¡ó‡yôtàIA>æ1™Òy\n¡ó‡yôtàIA>æ1™Òy\n¡ó‡yôtàIA>æ1™Òy\n¡8›\røjàIAìˆ®Gz\n¡','manual','active'),(118,'\0\0\0\0\0\0\0\0\0\0\0\0\0J  ‡$àIAÄ-\nûËr\n¡ª44Ç3àIA≈ÙÁ^p\n¡´`Øs?àIA+πFøn\n¡Ê·©y%àIAÖ„m\n¡CM∂àIAZ{Ω	n\n¡üÃ?ÿàIA•¯◊÷rn\n¡·€àIAºêq	po\n¡}7ÇﬂàIA”(<mp\n¡∆ú±]àIAõQÇq\n¡‹:Óπ\ZàIA¡2KÑr\n¡„Tk‰!àIAµÑ\0Å\0s\n¡J  ‡$àIAÄ-\nûËr\n¡','manual','active'),(119,'\0\0\0\0\0\0\0\0\0\0\0\0\0ü[Cô5àIA˝H\\‘o\n¡\0ú(,PàIA[F$!/p\n¡6Y„LàIAi∞¬`ôs\n¡Œï˜%+àIA8“æÓ¢s\n¡÷ˇ9-%àIAèaÛˆr\n¡ü[Cô5àIA˝H\\‘o\n¡','manual','active'),(120,'\0\0\0\0\0\0\0\0\0\0\n\0\0\0ºËø\0àIA{»ãs\n¡°ºènÔáIA*πèBu\n¡A¿?àIAƒπ¿$êx\n¡\n¥‡*<àIAöÄ0∑v\n¡Ÿ<≥Â5àIAÁ-&Wu\n¡ıei´&àIAm)µ—∫s\n¡eÎœãàIAL÷ª–r\n¡‡Ú+àIAıFŒ∂|s\n¡mUìàIACç∆“ès\n¡ºËø\0àIA{»ãs\n¡','manual','active'),(121,'\0\0\0\0\0\0\0\0\0\0\0\0\0º;◊´>áIA$A]1r\n¡û3XH<áIA|Ú,†ír\n¡ØÙê2NáIAÇ\0Å\0s\n¡@øÔ.QáIA`ä8ˆur\n¡@øÔ.QáIA`ä8ˆur\n¡@øÔ.QáIA`ä8ˆur\n¡º;◊´>áIA$A]1r\n¡','manual','active'),(122,'\0\0\0\0\0\0\0\0\0\0\0\0\0∑PË˚;áIAÏ‚.Ÿçr\n¡Ûn—\0MáIAµÑ\0Å\0s\n¡–î§DáIAöoÕft\n¡g—;S3áIA¶˘ù%Ùs\n¡∑PË˚;áIAÏ‚.Ÿçr\n¡','manual','active'),(123,'\0\0\0\0\0\0\0\0\0\0\0\0\0°≤´ü3áIAç\núÏ¯s\n¡9ÁL£0áIALÒe∞~t\n¡ØÊ•ÙAáIAΩë7XÒt\n¡ÕÓ$XDáIA/âqbt\n¡°≤´ü3áIAç\núÏ¯s\n¡','manual','active'),(124,'\0\0\0\0\0\0\0\0\0\0\0\0\0ù%m\n0áIArb>àt\n¡o;~Z-áIAΩë7XÒt\n¡U¿=å.áIAŸ˘+u\n¡´Yg_>áIATUému\n¡K®ÖçBáIAΩë7XÒt\n¡ù%m\n0áIArb>àt\n¡','manual','active'),(125,'\0\0\0\0\0\0\0\0\0\0\0\0\0Y‹‚PáIA“0âr\n¡è0±ôMáIA√∏˙’s\n¡0\nÎ^áIACç∆“ès\n¡ΩHÄbáIAßP,Úr\n¡Y‹‚PáIA“0âr\n¡','manual','active'),(126,'\0\0\0\0\0\0\0\0\0\0\0\0\0VOAMMáIAπ˝ÚÒ!s\n¡≈Ñ‚PJáIAFπC±s\n¡◊E;\\áIA∏¶äÎ#t\n¡0\nÎ^áIA*ûƒôîs\n¡ÀNöû^áIA*ûƒôîs\n¡0\nÎ^áIA*ûƒôîs\n¡VOAMMáIAπ˝ÚÒ!s\n¡','manual','active'),(127,'\0\0\0\0\0\0\0\0\0\0\0\0\0å£rJáIAU:≥òøs\n¡˚ÿGáIA	fuxXt\n¡ÕÓ$XDáIA§¢5ˆt\n¡ﬁØ]BVáIAñ\Z9u\n¡dÉ;¢[áIA¬aíœt\n¡å£rJáIAU:≥òøs\n¡','manual','active'),(128,'\0\0\0\0\0\0\0\0\0\0\0\0\0K®ÖçBáIA’Ä9ëÏt\n¡HG¯>áIATUému\n¡Äœ«QáIA˙LÕ¯u\n¡	\r]UáIA8Ì‰Pu\n¡	\r]UáIA8Ì‰Pu\n¡K®ÖçBáIA’Ä9ëÏt\n¡','manual','active'),(129,'\0\0\0\0\0\0\0\0\0\0\0\0\0÷ıU^iáIA‹ß¸\ns\n¡ΩHÄbáIA‹Ñ@2t\n¡?czáIA¯*CÆ‘t\n¡Ë∂éH{áIAd‡gÈyt\n¡˛TÀ§ÉáIAù∞P=≥t\n¡¢éÿÇäáIA·í©{◊s\n¡¢éÿÇäáIA·í©{◊s\n¡÷ıU^iáIA‹ß¸\ns\n¡','manual','active'),(130,'\0\0\0\0\0\0\0\0\0\0\0\0\0ΩYﬁ-|áIAÄH\\ìñt\n¡p´=ÑáIA´‰Jí¡t\n¡¡Ê√áIA…n…¶v\n¡\'ãá\\áIAÖ:4u\n¡\\˘öaáIA˜∏à≤(t\n¡üQ_ yáIAaEÁœt\n¡ΩYﬁ-|áIAÄH\\ìñt\n¡','manual','active'),(131,'\0\0\0\0\0\0\0\0\0\0\0\0\0®gÆfáIAXŒ˜˛éu\n¡œ€ÿ3báIA7ñ®›Rv\n¡Zyn·{áIA““hÑv\n¡^≠váIAë≈4v\n¡$%=*áIAë≈4v\n¡®gÆfáIAXŒ˜˛éu\n¡','manual','active'),(132,'\0\0\0\0\0\0\0\0\0\0\0\0\0O≤!◊àIAËπl˘Ùq\n¡≥E“à÷àIATä„)Hs\n¡‚ä÷ÍàIAbæ›~Vs\n¡˘\"ÎàIANü6Ωzr\n¡O≤!◊àIAËπl˘Ùq\n¡','manual','active'),(133,'\0\0\0\0\0\0\0\0\0\0\0\0\0ìﬂ¢\n’àIAÚÕ€E[s\n¡√®ZXÈàIAŸﬁŸ`s\n¡ä«ÍÈàIA˙1{#Jt\n¡ìﬂ¢\n’àIA!}\\Et\n¡ìﬂ¢\n’àIAÚÕ€E[s\n¡','manual','active'),(134,'\0\0\0\0\0\0\0\0\0\0\0\0\0x≤!◊àIA=Ωk[pt\n¡©-\ZäÍàIA%Œi\"ut\n¡6k:ÒÈàIA<fUru\n¡¢cb<÷àIA.2	\0du\n¡¢cb<÷àIA.2	\0du\n¡iÇÚÔ’àIA\rrZu\n¡x≤!◊àIA=Ωk[pt\n¡','manual','active'),(135,'\0\0\0\0\0\0\0\0\0\0\0\0\0¢cb<÷àIAC«hu\n¡©-\ZäÍàIA.2	\0du\n¡oL™=ÍàIA≤ÒÅi≤v\n¡&B’÷àIAñâçøïv\n¡¢cb<÷àIAC«hu\n¡','manual','active'),(136,'\0\0\0\0\0\0\0\0\0\0\0\0\0‹D“à÷àIA≤ÒÅi≤v\n¡√®ZXÈàIAöÄ0∑v\n¡\'ÁzøËàIA\"C´∆y\n¡ìﬂ¢\n’àIAﬂ L»Æy\n¡‹D“à÷àIA≤ÒÅi≤v\n¡','manual','active'),(137,'\0\0\0\0\0\0\0\0\0\0\0\0\0ô@”àIA0ä7U„y\n¡AbªçÁàIAs(ç	z\n¡ÍxÃ›‰àIA›é6∑^|\n¡0°Ç£’àIA›é6∑^|\n¡≈™œàIAàVYπ|\n¡qÏ4˜œàIA/zÇ∑{\n¡ô@”àIA0ä7U„y\n¡','manual','active'),(138,'\0\0\0\0\0\0\0\0\0\0\0\0\0~–ioÎàIA	õKf{\n¡ŒOÙàIAíü¶°I{\n¡œ¬¿¸àIA∏¬¢/S{\n¡H,s€˚àIA@˚\r\n√|\n¡ådƒ˘àIAuRÌ⁄|\n¡ä«ÍÈàIA˝o“ú|\n¡√®ZXÈàIA˝o“ú|\n¡~–ioÎàIA	õKf{\n¡','manual','active'),(139,'\0\0\0\0\0\0\0\0\0\0\0\0\0oL™=ÍàIA´Â·Bz\n¡<5Ú>˛àIAz\roLz\n¡TÇÚ˝àIA¬}™@{\n¡≥‘’IıàIAé&¥0({\n¡Ç]®ÔàIAÌôk{\n¡oL™=ÍàIA	õKf{\n¡oL™=ÍàIA´Â·Bz\n¡','manual','active'),(140,'\0\0\0\0\0\0\0\0\0\0\0\0\0\'ÁzøËàIAè}7&z\n¡Kπ±pˇàIAìˆ®Gz\n¡ì·Ó\0âIAj±àØ\Zy\n¡¯¨∆2ÛàIANIî˛x\n¡ÖÍÊôÚàIAäío Xy\n¡6k:ÒÈàIAäío Xy\n¡\'ÁzøËàIAè}7&z\n¡','manual','active'),(141,'\0\0\0\0\0\0\0\0\0\0\0\0\0¯¨∆2ÛàIAkêìy\n¡Z=q¢\0âIAQ¬Üvy\n¡‹ÉmâIA”ˆ`\nx\n¡6k:ÒÈàIAé˛D˜w\n¡√®ZXÈàIAws»}x\n¡în¶ÀÛàIA\\}éZy\n¡¯¨∆2ÛàIAkêìy\n¡','manual','active'),(142,'\0\0\0\0\0\0\0\0\0\0	\0\0\06k:ÒÈàIA‡cŸ˛v\n¡6k:ÒÈàIAøŒ∏¬w\n¡ıàùÔàIA˜û¸¸w\n¡eÄπâIA”ˆ`\nx\n¡à\'`RâIA<ÅUJ w\n¡ÿˆ—◊˛àIAÔ:].\rw\n¡S#Ùw˘àIA a†w\n¡}Ä§í¯àIA±lˆÊv\n¡6k:ÒÈàIA‡cŸ˛v\n¡','manual','active'),(143,'\0\0\0\0\0\0\0\0\0\0\0\0\0oL™=ÍàIAÙ\n∏•,v\n¡©-\ZäÍàIA±lˆÊv\n¡‹ÉmâIA*_gw\n¡¡–ûâIA∆ı÷5‡u\n¡≥‘’IıàIA©ç‚ã√u\n¡oL™=ÍàIAÙ\n∏•,v\n¡','manual','active'),(144,'\0\0\0\0\0\0\0\0\0\0\0\0\0*tπTÏàIAl“LÀºt\n¡@¬0‘âIAÑ¡N∏t\n¡eÄπâIAﬁ‰ÿn€u\n¡@ˆ∞ÙàIAëû‡R»u\n¡ª>QÔàIAfÚSùu\n¡çT)°ÏàIAXŒ˜˛éu\n¡*tπTÏàIAl“LÀºt\n¡','manual','active'),(145,'\0\0\0\0\0\0\0\0\0\0\0\0\0ÒíIÏàIAl“LÀºt\n¡‹ÉmâIA´‰Jí¡t\n¡@¬0‘âIAÜ∑\n∂s\n¡@ˆ∞ÙàIAw‰ºµßs\n¡©-\ZäÍàIAÒ◊”ds\n¡ÒíIÏàIAl“LÀºt\n¡','manual','active'),(146,'\0\0\0\0\0\0\0\0\0\0\0\0\0ä÷ÍàIAﬁÆ4Ñr\n¡æ{ë	\0âIAÑ¶¸\ns\n¡‹ÉmâIA¢Ä´¥“s\n¡=Ö∑ÒàIA{»ãs\n¡\'ÁzøËàIA¸à„)Hs\n¡ä÷ÍàIAﬁÆ4Ñr\n¡','manual','active'),(147,'\0\0\0\0\0\0\0\0\0\0\0\0\0ó´ÑâIA¥I∞æ1{\n¡à\'`RâIAë∫¯ñ˜|\n¡Ò—áÏâIA7≤¿!Ç}\n¡¨˘ñ\ZâIA¬}™@{\n¡¨˘ñ\ZâIA¬}™@{\n¡`)âIA™é®⁄D{\n¡ó´ÑâIA¥I∞æ1{\n¡','manual','active'),(148,'\0\0\0\0\0\0\0\0\0\0\0\0\0\nnˇâIA„C?9–y\n¡Ê⁄P\ZâIA\"V=\0’y\n¡¨˘ñ\ZâIA¥I∞æ1{\n¡–åè–âIAò·ª{\n¡\nnˇâIA„C?9–y\n¡','manual','active'),(149,'\0\0\0\0\0\0\0\0\0\0\0\0\0ö8^âIA˘∑®x\n¡¨˘ñ\ZâIA‡!µŒ¨x\n¡s\'∑âIA’E‰¡y\n¡˛v~ÄâIAﬂ L»Æy\n¡ö8^âIA˘∑®x\n¡','manual','active'),(150,'\0\0\0\0\0\0\0\0\0\0\0\0\0\r˚=≤âIA@˙GªAw\n¡\\*%~âIAç@@◊Tw\n¡≈ıˇâIAÖß¬]ãx\n¡ö8^âIAws»}x\n¡‘ŒeâIAws»}x\n¡aWÓÃâIAws»}x\n¡\r˚=≤âIA@˙GªAw\n¡','manual','active'),(151,'\0\0\0\0\0\0\0\0\0\0\0\0\0aWÓÃâIAOÖ™Nv\n¡\\*%~âIA]π§k\\v\n¡#Iµ1âIA◊K-8w\n¡˛v~ÄâIAfDIKw\n¡aWÓÃâIAOÖ™Nv\n¡','manual','active'),(152,'\0\0\0\0\0\0\0\0\0\0\0\0\0ö8^âIAaEÁœt\n¡kÆ‰ØâIA8Ì‰Pu\n¡ÌÙÉz!âIA]π§k\\v\n¡‘ŒeâIAs¨OIv\n¡ö8^âIAaEÁœt\n¡','manual','active'),(153,'\0\0\0\0\0\0\0\0\0\0\0\0\0cD¢®%âIAÃö≥˝s\n¡ˆKz]9âIA=Ωk[pt\n¡ÆÊJﬂ7âIA≠’¸‰u\n¡ÈgEÂâIA.2	\0du\n¡cD¢®%âIAÃö≥˝s\n¡','manual','active'),(154,'\0\0\0\0\0\0\0\0\0\0\0\0\0≈ıˇâIAcâˇ‚{u\n¡\r:|ñ4âIAﬁ‰ÿn€u\n¡\r:|ñ4âIAŒYvœv\n¡kÆ‰ØâIAöÄ0∑v\n¡≈ıˇâIAcâˇ‚{u\n¡','manual','active'),(155,'\0\0\0\0\0\0\0\0\0\0\0\0\0ïï âIAŒYvœv\n¡ãÛ‹À2âIA‡cŸ˛v\n¡˛µºd3âIA7±˙“\0x\n¡¯ÎâIA˛‡«w\n¡ïï âIAŒYvœv\n¡','manual','active'),(156,'\0\0\0\0\0\0\0\0\0\0\0\0\0∞Ü’òâIA€6bﬂw\n¡ãÛ‹À2âIA7±˙“\0x\n¡\n≠=1âIA5ZíÃy\n¡≈ıˇâIA\0úÈÍx\n¡∞Ü’òâIA€6bﬂw\n¡','manual','active'),(157,'\0\0\0\0\0\0\0\0\0\0\0\0\0°gâIA7ñ>˘x\n¡}oö1âIA+üäËy\n¡nÎ]h0âIAHy9éﬁy\n¡ı^∆ÅâIA˚2ArÀy\n¡°gâIA7ñ>˘x\n¡','manual','active'),(158,'\0\0\0\0\0\0\0\0\0\0\0\0\0.@6ŒâIAiZ ©z\n¡nÎ]h0âIAìˆ®Gz\n¡àfû6/âIAúZÆÖ6{\n¡ı^∆ÅâIAg∏¢{\n¡.@6ŒâIAiZ ©z\n¡','manual','active'),(159,'\0\0\0\0\0\0\0\0\0\0\0\0\0ı^∆ÅâIAé&¥0({\n¡%Ü.Í.âIAíü¶°I{\n¡≤√NQ.âIA.N!Dì|\n¡¨˘ñ\ZâIA˙ˆ*a{|\n¡ı^∆ÅâIAé&¥0({\n¡','manual','active'),(160,'\0\0\0\0\0\0\0\0\0\0\0\0\0ùu◊—âIA_ò|\n¡/8âIA)~∆Ãs}\n¡ËÄ+âIA[ö≠·}\n¡§?è-âIAc•\'´|\n¡ùu◊—âIA_ò|\n¡','manual','active'),(161,'\0\0\0\0\0\0\0\0\0\0\0\0\0|T≤“ÆàIAlÓdÏ{\n¡ß( †àIA\"qèıÇ{\n¡0≤	úúàIAyÀˆ]¸|\n¡3ÔÇT≠àIA˝o“ú|\n¡”=°Ç±àIAËI>õK|\n¡|T≤“ÆàIAlÓdÏ{\n¡','manual','active'),(162,'\0\0\0\0\0\0\0\0\0\0\0\0\0˜–ôOúàIAyÀˆ]¸|\n¡œ±àIAÔ;#}é|\n¡ı0ñ∂àIAºVÁï\"}\n¡Ã#$X™àIA)~∆Ãs}\n¡,’*¶àIAÆ\"Ì@}\n¡Økj—öàIAÿæ€??}\n¡˜–ôOúàIAyÀˆ]¸|\n¡','manual','active'),(163,'\0\0\0\0\0\0\0\0\0\0\0\0\0†Á™üôàIAT\ZµÀû}\n¡ÛÛï›•àIAÊÚ’îM}\n¡Ωüd&©àIAûóäÂ~\n¡´ﬁ+<óàIAøiY~\n¡†Á™üôàIAT\ZµÀû}\n¡','manual','active'),(164,'\0\0\0\0\0\0\0\0\0\0\0\0\0ÂøõàóàIA@`ˇp~\n¡Ã#$X™àIA≈∫Üs~\n¡¿,£ª¨àIAÿŸ-5Ì~\n¡∂%ïàIAÔ•9\n¡ÂøõàóàIA@`ˇp~\n¡','manual','active'),(165,'\0\0\0\0\0\0\0\0\0\0\0\0\0∂%ïàIA‡À0\n¡§ƒÆêàIA!\0õHXÄ\n¡Ωüd&©àIA!\0õHXÄ\n¡±®„â´àIA‡À0\n¡∂%ïàIA‡À0\n¡','manual','active'),(166,'\0\0\0\0\0\0\0\0\0\0\0\0\0\\_ìéàIAïièÚtÄ\n¡Ò–±äàIAóã]òÅ\n¡Èúü˙çàIAﬁè¸‡Å\n¡,’*¶àIAvS ;\\Ç\n¡ã(7·¢àIA`ô]Ä\n¡\\_ìéàIAïièÚtÄ\n¡','manual','active'),(167,'\0\0\0\0\0\0\0\0\0\0\0\0\0Ωüd&©àIA[B>ò=Å\n¡FPF¯§àIA]d»aÇ\n¡wwÆ`∏àIAˇ‚ù Ç\n¡{ÌıªàIAT\0)%rÅ\n¡Ωüd&©àIA[B>ò=Å\n¡','manual','active'),(168,'\0\0\0\0\0\0\0\0\0\0\0\0\0iC¥™àIA!\0õHXÄ\n¡“Ì€•æàIA:ÔúÅSÄ\n¡{ÌıªàIAmÔ*^mÅ\n¡¸A®àIA[B>ò=Å\n¡iC¥™àIA!\0õHXÄ\n¡','manual','active'),(169,'\0\0\0\0\0\0\0\0\0\0\0\0\0?ÊÒ™àIA‡À0\n¡\\äá¬àIA‹R ¶\n¡~ë+ãøàIA!\0õHXÄ\n¡Æ•ÙßàIA˜c¨I-Ä\n¡?ÊÒ™àIA‡À0\n¡','manual','active'),(170,'\0\0\0\0\0\0\0\0\0\0\0\0\0íÚÓ.∑àIA%‘[R}\n¡W¡πƒàIAøiY~\n¡Çj √àIAÙA\"ﬂ	\n¡¿,£ª¨àIAv4\n¡î§™àIAFw´7~\n¡J›Ñç®àIA-˜∏=ï}\n¡íÚÓ.∑àIA%‘[R}\n¡','manual','active'),(171,'\0\0\0\0\0\0\0\0\0\0\0\0\0Ú£–\0≥àIAz\"_d˙{\n¡7|¡È∞àIA \Z\'ÔÑ|\n¡ë¢)RƒàIAzq\0F~\n¡j“∑Ã»àIA˙ˆ*a{|\n¡ÚGÄ»àIA˙ˆ*a{|\n¡Ú£–\0≥àIAz\"_d˙{\n¡','manual','active'),(172,'\0\0\0\0\0\0\0\0\0\0\0\0\0S‰µìÕàIAÔ;#}é|\n¡¢ù_„àIAuRÌ⁄|\n¡ıoMz‚àIA¯ü¬Z}}\n¡v≤…àIAàq´Æ∂}\n¡S‰µìÕàIAÔ;#}é|\n¡','manual','active'),(173,'\0\0\0\0\0\0\0\0\0\0\0\0\0ÏWó àIAbNØ ≠}\n¡≠\n¸‡àIA¯ü¬Z}}\n¡ıoMz‚àIA˘}V)~\n¡$™ÿàIA˝äo«J~\n¡ÚGÄ»àIAzq\0F~\n¡ÏWó àIAbNØ ≠}\n¡','manual','active'),(174,'\0\0\0\0\0\0\0\0\0\0\0\0\0j“∑Ã»àIAøiY~\n¡Ö´®µ∆àIA™â&\n¡{C+⁄ÁàIAøÍ+¸Ò~\n¡±ó\\ë‰àIA”ÓÄ»~\n¡±Á!n◊àIAzq\0F~\n¡j“∑Ã»àIAøiY~\n¡','manual','active'),(175,'\0\0\0\0\0\0\0\0\0\0\0\0\0Ëã«àIAÓˇl>\n¡†&ÈÉ≈àIA˝•¡º¯\n¡µt`€àIAÔq«gÍ\n¡˙LQÏÿàIA√cm\n¡Ëã«àIAÓˇl>\n¡','manual','active'),(176,'\0\0\0\0\0\0\0\0\0\0\0\0\0e	ÎƒàIAÂ∂øÉ˝\n¡÷z\Z;¬àIA—≤j∑œÄ\n¡Á;S%‘àIAv8xFÆÄ\n¡ìﬂ¢\n’àIA¢+œK◊\n¡e	ÎƒàIAÂ∂øÉ˝\n¡','manual','active'),(177,'\0\0\0\0\0\0\0\0\0\0\0\0\0\0ÿ U¡àIAw™2BZÅ\n¡&B’÷àIA*d:&GÅ\n¡3.¡8ŸàIA¢˙Ã‰Å\n¡ˆøW’àIAH>ÈÀÇ\n¡·qõ◊øàIAÄ“IÇ\n¡\0ÿ U¡àIAw™2BZÅ\n¡','manual','active'),(178,'\0\0\0\0\0\0\0\0\0\0\0\0\0“Ì€•æàIAh–ÊMÇ\n¡ˆøW’àIA,ÎÇ\n¡ól·üÿàIA≥`¸bÉ\n¡‹D“à÷àIAﬁ™N˚çÉ\n¡¸Jå¿ΩàIAêä‚˘Ç\n¡“Ì€•æàIAh–ÊMÇ\n¡','manual','active'),(179,'\0\0\0\0\0\0\0\0\0\0\0\0\0#Z<*ÂàIAúu\0{‰|\n¡H,s€˚àIAÿæ€??}\n¡ŒOÙàIAŒ&Q\0\n¡gŒ‡àIAô«/nË~\n¡#Z<*ÂàIAúu\0{‰|\n¡','manual','active'),(180,'\0\0\0\0\0\0\0\0\0\0\0\0\0¶†—ŸàIAÍÜ\Z˚\n¡{ì∂⁄àIAÃ«ΩJÄ\n¡§GœàIA»NÀŸ‡\n¡ŒOÙàIA£Ç7R’~\n¡¶†—ŸàIAÍÜ\Z˚\n¡','manual','active'),(181,'\0\0\0\0\0\0\0\0\0\0\0\0\0tyså”àIA+ª¢,EÄ\n¡™Õ§C–àIAv8xFÆÄ\n¡ˆøW’àIABS<_BÅ\n¡.¯ÈÔàIA\"rUDÅ\n¡=Ö∑ÒàIA»NÀŸ‡\n¡tyså”àIA+ª¢,EÄ\n¡','manual','active'),(182,'\0\0\0\0\0\0\0\0\0\0\0\0\0ˆøW’àIAêô4{UÅ\n¡.¯ÈÔàIA\naöÁÄ\n¡ÒíIÏàIAíªæÂxÇ\n¡&B’÷àIAñ4±VöÇ\n¡‹D“à÷àIAñ4±VöÇ\n¡&B’÷àIAñ4±VöÇ\n¡&B’÷àIAÆ#≥èïÇ\n¡ˆøW’àIAêô4{UÅ\n¡','manual','active'),(183,'\0\0\0\0\0\0\0\0\0\0\0\0\0x≤!◊àIA„z©r≠Ç\n¡ıoMz‚àIAà\0∑åÇ\n¡©-\ZäÍàIA\nû•\0∑Ç\n¡ø√ÂàIA(($˜É\n¡iÇÚÔ’àIAﬁ™N˚çÉ\n¡x≤!◊àIA„z©r≠Ç\n¡','manual','active'),(184,'\0\0\0\0\0\0\0\0\0\0\0\0\0õ»kÓàIA“üU≈Ç\n¡–åè–âIAñ4±VöÇ\n¡û≈úÆâIAüòP4âÉ\n¡∫ÓRt¸àIAãî˚g[Ñ\n¡~–ioÎàIA]\Z¯Ñ\n¡õ»kÓàIA“üU≈Ç\n¡','manual','active'),(185,'\0\0\0\0\0\0\0\0\0\0\0\0\0@ˆ∞ÙàIA?⁄IÓ Å\n¡˝„	âIA\nÉS	Å\n¡YÌ´≈\râIAzÃº¨}Ç\n¡ıàùÔàIA«µ»êÇ\n¡@ˆ∞ÙàIA?⁄IÓ Å\n¡','manual','active'),(186,'\0\0\0\0\0\0\0\0\0\0\0\0\05u˜àIAî˜‘ˆ»\n¡JiÏìâIA\"WOV\n¡`)âIA«˜b”‚Ä\n¡1ÜdÙàIA¸E|*Å\n¡5u˜àIAî˜‘ˆ»\n¡','manual','active'),(187,'\0\0\0\0\0\0\0\0\0\0\0\0\0H,s€˚àIAÒ≠›x:}\n¡.@6ŒâIA~∂£ …}\n¡V`m0\nâIAøÍ+¸Ò~\n¡≥‘’IıàIA-3C\n¡H,s€˚àIAÒ≠›x:}\n¡','manual','active'),(188,'\0\0\0\0\0\0\0\0\0\0\0\0\0j^”,âIANJZT~\n¡.@6ŒâIAûóäÂ~\n¡èA›|\nâIAÊ\r(ä˚~\n¡–< ÛâIAÍ°l Ä\n¡ˇÇA&âIArøÖ’åÄ\n¡j^”,âIANJZT~\n¡','manual','active'),(189,'\0\0\0\0\0\0\0\0\0\0\0\0\0ö8^âIA\0»K\'Å\n¡∞Ü’òâIAß|∏§Ä\n¡ﬂr*$âIA0@—8Å\n¡\\*%~âIA]d»aÇ\n¡€3KêâIAÆ#≥èïÇ\n¡ö8^âIA\0»K\'Å\n¡','manual','active'),(190,'\0\0\0\0\0\0\0\0\0\0\0\0\0ó´ÑâIA\nû•\0∑Ç\n¡\\*%~âIAπﬁ∫sÇÇ\n¡/8âIA#X…ù◊Ñ\n¡<5Ú>˛àIA¿ÎÒJsÑ\n¡ö8^âIAEﬁ•É\n¡ó´ÑâIA\nû•\0∑Ç\n¡','manual','active'),(191,'\0\0\0\0\0\0\0\0\0\0\0\0\0ª«„˛GâIA∂jt⁄”v\n¡Y79è:âIA}öãÜöv\n¡hª¯¿;âIA ˛´Uu\n¡Ò∂DâIA›rs/u\n¡Ê$îGâIAÿ¢√˚v\n¡ª«„˛GâIA∂jt⁄”v\n¡','manual','active'),(192,'\0\0\0\0\0\0\0\0\0\0\0\0\0 V…B:âIAofë1åv\n¡e.∫+8âIAs˙’ó[x\n¡#ìB˚JâIAÓUØ#ªx\n¡ª«„˛GâIAŸ~˜ªv\n¡ V…B:âIAofë1åv\n¡','manual','active');
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
) ENGINE=MyISAM AUTO_INCREMENT=193 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `property_property`
--

LOCK TABLES `property_property` WRITE;
/*!40000 ALTER TABLE `property_property` DISABLE KEYS */;
INSERT INTO `property_property` VALUES (88,8002,139,'Little Street','Parramatta',88,'active'),(2,2000,1,'Stacey','Ashfield',2,'active'),(3,2001,2,'Stacey','Ashfield',3,'active'),(4,2002,3,'Stacey','Ashfield',4,'active'),(5,2003,4,'Stacey','Ashfield',5,'active'),(6,2004,5,'Stacey','Ashfield',6,'active'),(7,2005,6,'Stacey','Ashfield',7,'active'),(8,2006,7,'Stacey','Ashfield',8,'active'),(9,3000,12,'Myall','Cabramatta',9,'active'),(10,2007,8,'Stacey','Ashfield',10,'active'),(11,1000,52,'Phillip Steet','Parramatta',11,'active'),(12,3078,13,'Myall','Cabramatta',12,'active'),(13,2006,1,'paul st','Ashfield',13,'active'),(14,3002,14,'Myall','Cabramatta',14,'active'),(15,1001,54,'Phillip Steet','Parramatta',15,'active'),(16,2008,2,'paul st','Ashfield',16,'active'),(17,1003,56,'Phillip Steet','Parramatta',17,'active'),(18,3003,15,'Myall','Cabramatta',18,'active'),(19,2009,3,'paul st','Ashfield',19,'active'),(20,1004,58,'Phillip Steet','Parramatta',20,'active'),(21,3004,16,'Myall','Cabramatta',21,'active'),(22,3005,17,'Myall','Cabramatta',22,'active'),(23,1005,60,'Phillip Steet','Parramatta',23,'active'),(24,3006,18,'Myall','Cabramatta',24,'active'),(25,1006,62,'Phillip Steet','Parramatta',25,'active'),(26,3007,23,'John','Cabramatta',26,'active'),(27,1007,64,'Phillip Steet','Parramatta',27,'active'),(28,3008,24,'John','Cabramatta',28,'active'),(29,3009,25,'John','Cabramatta',29,'active'),(30,1008,5,'King Street','Parramatta',30,'active'),(31,3010,26,'John','Cabramatta',31,'active'),(32,1009,7,'King Street','Parramatta',32,'active'),(33,3011,112,'Bee','Cabramatta',33,'active'),(34,1010,101,'Wall Steet','Parramatta',34,'active'),(35,3012,122,'Bee','Cabramatta',35,'active'),(36,1011,103,'Wall Steet','Parramatta',36,'active'),(37,3013,121,'Bee','Cabramatta',37,'active'),(38,3013,121,'Bee','Cabramatta',38,'active'),(39,3014,119,'Bee','Cabramatta',39,'active'),(40,1012,111,'Wall Steet','Parramatta',40,'active'),(41,3015,32,'Goose','Cabramatta',41,'active'),(42,1015,99,'Wall Steet','Parramatta',42,'active'),(43,3016,33,'Goose','Cabramatta',43,'active'),(44,1019,15,'Wall Steet','Parramatta',44,'active'),(45,3017,34,'Goose','Cabramatta',45,'active'),(46,1025,45,'Wall Steet','Parramatta',46,'active'),(47,3018,236,'Hugh','Cabramatta',47,'active'),(48,3019,11,'Doom','Cabramatta',48,'active'),(50,9000,1,'Harold St','Glebe',50,'active'),(51,9001,2,'Harold St','Glebe',51,'active'),(52,9002,3,'Harold St','Glebe',52,'active'),(53,9003,4,'Harold St','Glebe',53,'active'),(54,9004,5,'Harold St','Glebe',54,'active'),(55,9005,6,'Harold St','Glebe',55,'active'),(56,9006,7,'Harold St','Glebe',56,'active'),(57,9006,7,'Harold St','Glebe',57,'active'),(58,9007,8,'Harold St','Glebe',58,'active'),(59,9008,9,'Harold St','Glebe',59,'active'),(60,9009,10,'Harold St','Glebe',60,'active'),(61,9010,11,'Harold St','Glebe',61,'active'),(62,9011,12,'Harold St','Glebe',62,'active'),(63,9012,1,'Paper St','Glebe',63,'active'),(64,9013,2,'Paper St','Glebe',64,'active'),(65,9014,3,'Paper St','Glebe',65,'active'),(66,9015,4,'Paper St','Glebe',66,'active'),(67,9016,5,'Paper St','Glebe',67,'active'),(68,9017,7,'Paper St','Glebe',68,'active'),(69,9018,8,'Paper St','Glebe',69,'active'),(70,9020,20,'Paper St','Glebe',70,'active'),(71,9021,21,'Paper St','Glebe',71,'active'),(72,9022,22,'Paper St','Glebe',72,'active'),(73,9023,23,'Paper St','glebe',73,'active'),(85,6666,239,'Auburn Road','Chatswood',85,'active'),(75,9024,24,'Paper St','Glebe',75,'active'),(76,9025,25,'Paper St','glebe',76,'active'),(77,8221,152,'Little Street','Parramatta',77,'active'),(78,9026,26,'Paper St','Glebe',78,'active'),(79,9027,27,'Paper St','Glebe',79,'active'),(80,9028,28,'Paper St','Glebe',80,'active'),(87,8001,137,'Little Street','Parramatta',87,'active'),(86,8000,135,'Little Street','Parramatta',86,'active'),(84,5555,230,'Auburn Road','Chatswood',84,'active'),(89,8003,141,'Little Street','Parramatta',89,'active'),(90,8004,143,'Little Street','Parramatta',90,'active'),(91,8005,145,'Little Street','Parramatta',91,'active'),(92,8010,1,'Eagle Street','Parramatta',92,'active'),(93,8011,2,'Eagle Street','Parramatta',93,'active'),(94,8012,3,'Eagle Street','Parramatta',94,'active'),(95,8013,4,'Eagle Street','Parramatta',95,'active'),(96,8014,5,'Eagle Street','Parramatta',96,'active'),(97,8015,6,'Eagle Street','Parramatta',97,'active'),(98,8016,7,'Eagle Street','Parramatta',98,'active'),(99,8017,9,'Eagle Street','Parramatta',99,'active'),(100,8018,11,'Eagle Street','Parramatta',100,'active'),(101,8019,13,'Eagle Street','Parramatta',101,'active'),(102,8020,14,'Eagle Street','Parramatta',102,'active'),(103,8021,15,'Eagle Street','Parramatta',103,'active'),(104,8022,16,'Eagle Street','Parramatta',104,'active'),(105,8006,147,'Little Street','Parramatta',105,'active'),(106,8007,148,'Little Street','Parramatta',106,'active'),(107,8008,149,'Little Street','Parramatta',107,'active'),(108,8009,153,'Little Street','Parramatta',108,'active'),(109,9029,1,'Dixon Street','Glebe',109,'active'),(110,9030,2,'Dixon Street','Glebe',110,'active'),(111,9031,3,'Dixon Street','Glebe',111,'active'),(112,9032,4,'Dixon Street','Glebe',112,'active'),(113,9033,5,'Dixon Street','Glebe',113,'active'),(114,9034,6,'Dixon Street','Glebe',114,'active'),(115,9035,10,'York Street','Petersham',115,'active'),(116,9037,12,'York Street','Petersham',116,'active'),(117,9038,13,'York Street','Petersham',117,'active'),(118,9100,13,'Harold Street','Glebe',118,'active'),(119,9101,14,'Harold Street','Glebe',119,'active'),(120,2010,4,'Paul Street','Ashfield',120,'active'),(121,1500,1,'Church Street','Atarmon',121,'active'),(122,1501,2,'Church Street','Atarmon',122,'active'),(123,1502,3,'Church Street','Atarmon',123,'active'),(124,1503,4,'Church Street','Atarmon',124,'active'),(125,1504,5,'Church Street','Atarmon',125,'active'),(126,1505,6,'Church Street','Atarmon',126,'active'),(127,1506,7,'Church Street','Atarmon',127,'active'),(128,1507,8,'Church Street','Atarmon',128,'active'),(129,1508,50,'Croydon Road','Atarmon',129,'active'),(130,1509,51,'Croydon Road','Atarmon',130,'active'),(131,1510,15,'Croydon Road','Atarmon',131,'active'),(132,9036,7,'Dixon Street','Glebe',132,'active'),(133,9040,8,'Dixon Street','Glebe',133,'active'),(134,9041,9,'Dixon Street','Glebe',134,'active'),(135,9042,10,'Dixon Street','Glebe',135,'active'),(136,9043,11,'Dixon Street','Glebe',136,'active'),(137,9044,12,'Dixon Street','Glebe',137,'active'),(138,9045,1,'Gordon Avenue','Glebe',138,'active'),(139,9046,2,'Gordon Avenue','Glebe',139,'active'),(140,9047,3,'Gordon Avenue','Glebe',140,'active'),(141,9048,4,'Gordon Avenue','Glebe',141,'active'),(142,9049,5,'Gordon Avenue','Glebe',142,'active'),(143,9050,6,'Gordon Avenue','Glebe',143,'active'),(144,9051,7,'Gordon Avenue','Glebe',144,'active'),(145,9052,8,'Gordon Avenue','Glebe',145,'active'),(146,9053,9,'Gordon Avenue','Glebe',146,'active'),(147,9054,10,'Gordon Avenue','Glebe',147,'active'),(148,9055,11,'Gordon Avenue','Glebe',148,'active'),(149,9056,12,'Gordon Avenue','Glebe',149,'active'),(150,9057,13,'Gordon Avenue','Glebe',150,'active'),(151,9058,14,'Gordon Avenue','Glebe',151,'active'),(152,9059,15,'Gordon Avenue','Glebe',152,'active'),(153,9060,1,'Elezebeth Street','Glebe',153,'active'),(154,9061,2,'Elezebeth Street','Glebe',154,'active'),(155,9062,3,'Elezebeth Street','Glebe',155,'active'),(156,9063,4,'Elezebeth Street','Glebe',156,'active'),(157,9064,5,'Elezebeth Street','Glebe',157,'active'),(158,9065,6,'Elezebeth Street','Glebe',158,'active'),(159,9066,7,'Elezebeth Street','Glebe',159,'active'),(160,9067,8,'Elezebeth Street','Glebe',160,'active'),(161,9068,14,'York Street','Petersham',161,'active'),(162,9069,15,'York Street','Petersham',162,'active'),(163,9070,16,'York Street','Petersham',163,'active'),(164,9071,16,'York Street','Petersham',164,'active'),(165,9072,17,'York Street','Petersham',165,'active'),(166,9073,18,'York Street','Petersham',166,'active'),(167,9074,1,'Swan Avenue','Petersham',167,'active'),(168,9075,2,'Swan Avenue','Petersham',168,'active'),(169,9076,3,'Swan Avenue','Petersham',169,'active'),(170,9077,4,'Swan Avenue','Petersham',170,'active'),(171,9078,5,'Swan Avenue','Petersham',171,'active'),(172,9079,6,'Swan Avenue','Petersham',172,'active'),(173,9080,7,'Swan Avenue','Petersham',173,'active'),(174,9081,8,'Swan Avenue','Petersham',174,'active'),(175,9082,9,'Swan Avenue','Petersham',175,'active'),(176,9083,10,'Swan Avenue','Petersham',176,'active'),(177,9084,11,'Swan Avenue','Petersham',177,'active'),(178,9085,12,'Swan Avenue','Petersham',178,'active'),(179,9086,101,'Cleveland Steet','Petersham',179,'active'),(180,9087,102,'Cleveland Steet','Petersham',180,'active'),(181,9088,103,'Cleveland Steet','Petersham',181,'active'),(182,9089,104,'Cleveland Steet','Petersham',182,'active'),(183,9090,105,'Cleveland Steet','Petersham',183,'active'),(184,9091,106,'Cleveland Steet','Petersham',184,'active'),(185,9092,107,'Cleveland Steet','Petersham',185,'active'),(186,9093,108,'Cleveland Steet','Petersham',186,'active'),(187,9094,109,'Cleveland Steet','Petersham',187,'active'),(188,9095,110,'Cooper Street','Petersham',188,'active'),(189,9096,111,'Cooper Street','Petersham',189,'active'),(190,9097,112,'Cooper Street','Petersham',190,'active'),(191,9200,9,'Elezebeth Street','Glebe',191,'active'),(192,9201,10,'Elezebeth Street','Glebe',192,'active');
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

-- Dump completed on 2012-09-05 10:08:17
