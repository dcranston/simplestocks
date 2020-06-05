CREATE DATABASE simplestocks;

CREATE USER 'simplestocks'@'localhost' IDENTIFIED BY 'qhfqe91FWI9204hfk2kasfp30n2mNbb4';
CREATE USER 'simplestocks'@'%' IDENTIFIED BY 'qhfqe91FWI9204hfk2kasfp30n2mNbb4';

DROP TABLE IF EXISTS quotes;
CREATE TABLE quotes (
  id int PRIMARY KEY AUTO_INCREMENT,
  symbol varchar(12) NOT NULL,
  timestamp timestamp NOT NULL,
  value float NOT NULL);

GRANT ALL ON simplestocks.* TO 'simplestocks'@'localhost';
GRANT ALL ON simplestocks.* TO 'simplestocks'@'%';