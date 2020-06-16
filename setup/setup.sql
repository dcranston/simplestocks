CREATE DATABASE simplestocks;

CREATE USER 'simplestocks'@'localhost' IDENTIFIED BY 'qhfqe91FWI9204hfk2kasfp30n2mNbb4';
CREATE USER 'simplestocks'@'%' IDENTIFIED BY 'qhfqe91FWI9204hfk2kasfp30n2mNbb4';

DROP TABLE IF EXISTS quotes;
CREATE TABLE quotes (
  id int PRIMARY KEY AUTO_INCREMENT,
  symbol varchar(12) NOT NULL,
  timestamp timestamp NOT NULL,
  value float NOT NULL);

DROP TABLE IF EXISTS config;
CREATE TABLE config (
  id int PRIMARY KEY AUTO_INCREMENT,
  auth_token varchar(64) NULL,
  refresh_token varchar(64)) NULL;


GRANT ALL ON simplestocks.* TO 'simplestocks'@'localhost';
GRANT ALL ON simplestocks.* TO 'simplestocks'@'%';