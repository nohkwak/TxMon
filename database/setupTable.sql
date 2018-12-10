DROP DATABASE IF EXISTS TxMonDB;
CREATE DATABASE TxMonDB;
use TxMonDB;

CREATE TABLE  white_lists (
    addr             varchar(256)  NOT NULL ,
    depth            int   NOT NULL ,
    CONSTRAINT pk_white_lists PRIMARY KEY ( addr )
) engine=InnoDB;

CREATE TABLE  black_lists (
    addr             varchar(256)  NOT NULL ,
    depth            int   NOT NULL ,
    CONSTRAINT pk_black_lists PRIMARY KEY ( addr )
) engine=InnoDB;

CREATE TABLE  alarm_lists (
    input      varchar(256)  NOT NULL ,
    output        varchar(256)  NOT NULL ,
    CONSTRAINT fk_input FOREIGN KEY ( input ) REFERENCES  white_lists( addr ),
    CONSTRAINT fk_output FOREIGN KEY ( output ) REFERENCES  black_lists( addr )
) engine=InnoDB;
