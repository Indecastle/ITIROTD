-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema mydb
-- -----------------------------------------------------
-- -----------------------------------------------------
-- Schema ITIROTD
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Schema ITIROTD
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `ITIROTD` DEFAULT CHARACTER SET utf8 ;
USE `ITIROTD` ;

-- -----------------------------------------------------
-- Table `ITIROTD`.`name1`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `ITIROTD`.`name1` (
  `id` MEDIUMINT(8) UNSIGNED NOT NULL AUTO_INCREMENT,
  `firstname` VARCHAR(45) NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `firstname_UNIQUE` (`firstname` ASC) VISIBLE)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `ITIROTD`.`name2`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `ITIROTD`.`name2` (
  `id` MEDIUMINT(8) UNSIGNED NOT NULL AUTO_INCREMENT,
  `lastname` VARCHAR(45) NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `firstname_UNIQUE` (`lastname` ASC) VISIBLE)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `ITIROTD`.`name3`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `ITIROTD`.`name3` (
  `id` MEDIUMINT(8) UNSIGNED NOT NULL AUTO_INCREMENT,
  `patronymic` VARCHAR(45) NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `firstname_UNIQUE` (`patronymic` ASC) VISIBLE)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `ITIROTD`.`users`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `ITIROTD`.`users` (
  `id` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
  `login` VARCHAR(100) NOT NULL,
  `password` TEXT(128) NOT NULL,
  `name` VARCHAR(50) NOT NULL,
  `photopath` VARCHAR(100) NULL,
  `email` VARCHAR(100) NULL,
  `name1_id` MEDIUMINT(8) UNSIGNED NULL,
  `name2_id` MEDIUMINT(8) UNSIGNED NULL,
  `name3_id` MEDIUMINT(8) UNSIGNED NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `login_UNIQUE` (`login` ASC) VISIBLE,
  INDEX `fk_users_name11_idx` (`name1_id` ASC) VISIBLE,
  INDEX `fk_users_name21_idx` (`name2_id` ASC) VISIBLE,
  INDEX `fk_users_name31_idx` (`name3_id` ASC) VISIBLE,
  CONSTRAINT `fk_users_name11`
    FOREIGN KEY (`name1_id`)
    REFERENCES `ITIROTD`.`name1` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_users_name21`
    FOREIGN KEY (`name2_id`)
    REFERENCES `ITIROTD`.`name2` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_users_name31`
    FOREIGN KEY (`name3_id`)
    REFERENCES `ITIROTD`.`name3` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `ITIROTD`.`sessions`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `ITIROTD`.`sessions` (
  `id` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
  `user_id` INT(10) UNSIGNED NOT NULL,
  `hash` BINARY(64) NOT NULL,
  `when` INT(11) NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `session_to_user_idx` (`user_id` ASC) VISIBLE,
  CONSTRAINT `session_to_user`
    FOREIGN KEY (`user_id`)
    REFERENCES `ITIROTD`.`users` (`id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `ITIROTD`.`roles`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `ITIROTD`.`roles` (
  `id` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `name_UNIQUE` (`name` ASC) VISIBLE)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `ITIROTD`.`users_has_roles`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `ITIROTD`.`users_has_roles` (
  `users_id` INT(10) UNSIGNED NOT NULL,
  `roles_id` INT(10) UNSIGNED NOT NULL,
  PRIMARY KEY (`users_id`, `roles_id`),
  INDEX `fk_users_has_roles_roles1_idx` (`roles_id` ASC) VISIBLE,
  INDEX `fk_users_has_roles_users1_idx` (`users_id` ASC) VISIBLE,
  CONSTRAINT `fk_users_has_roles_users1`
    FOREIGN KEY (`users_id`)
    REFERENCES `ITIROTD`.`users` (`id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `fk_users_has_roles_roles1`
    FOREIGN KEY (`roles_id`)
    REFERENCES `ITIROTD`.`roles` (`id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `ITIROTD`.`chat`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `ITIROTD`.`chat` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(45) NOT NULL,
  `secure` TINYINT NOT NULL,
  `password` VARCHAR(100) NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `ITIROTD`.`chat_has_users`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `ITIROTD`.`chat_has_users` (
  `chat_id` INT UNSIGNED NOT NULL,
  `users_id` INT(10) UNSIGNED NOT NULL,
  PRIMARY KEY (`chat_id`, `users_id`),
  INDEX `fk_chat_has_users_users1_idx` (`users_id` ASC) VISIBLE,
  INDEX `fk_chat_has_users_chat1_idx` (`chat_id` ASC) VISIBLE,
  CONSTRAINT `fk_chat_has_users_chat1`
    FOREIGN KEY (`chat_id`)
    REFERENCES `ITIROTD`.`chat` (`id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `fk_chat_has_users_users1`
    FOREIGN KEY (`users_id`)
    REFERENCES `ITIROTD`.`users` (`id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `ITIROTD`.`messages`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `ITIROTD`.`messages` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `chat_id` INT UNSIGNED NOT NULL,
  `users_id` INT(10) UNSIGNED NULL,
  `when` INT(11) NOT NULL,
  `text` VARCHAR(1000) NOT NULL,
  `is_sticker` TINYINT(1) NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`),
  INDEX `fk_messages_chat1_idx` (`chat_id` ASC) VISIBLE,
  INDEX `fk_messages_users1_idx` (`users_id` ASC) VISIBLE,
  CONSTRAINT `fk_messages_chat1`
    FOREIGN KEY (`chat_id`)
    REFERENCES `ITIROTD`.`chat` (`id`)
    ON DELETE CASCADE
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_messages_users1`
    FOREIGN KEY (`users_id`)
    REFERENCES `ITIROTD`.`users` (`id`)
    ON DELETE SET NULL
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `ITIROTD`.`message_status`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `ITIROTD`.`message_status` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `users_id` INT(10) UNSIGNED NOT NULL,
  `messages_id` INT UNSIGNED NOT NULL,
  `status_type` ENUM('read', 'unread') NOT NULL,
  INDEX `fk_messages_status_users1_idx` (`users_id` ASC) VISIBLE,
  INDEX `fk_message_status_messages1_idx` (`messages_id` ASC) VISIBLE,
  PRIMARY KEY (`id`),
  CONSTRAINT `fk_message_status_users`
    FOREIGN KEY (`users_id`)
    REFERENCES `ITIROTD`.`users` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_message_status_messages1`
    FOREIGN KEY (`messages_id`)
    REFERENCES `ITIROTD`.`messages` (`id`)
    ON DELETE CASCADE
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
