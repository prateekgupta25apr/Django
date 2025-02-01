create schema sample_project_1;
create schema sample_project_2;

CREATE TABLE `table_1` (
  `primary_key` int NOT NULL AUTO_INCREMENT,
  `col_1` varchar(500) DEFAULT NULL,
  `col_2` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`primary_key`)
)