CREATE DATABASE	IF NOT EXISTS `apostas_db`;
USE `apostas_db`;

DROP TABLE IF EXISTS `apostas_db`.`aposta`;

CREATE TABLE IF NOT EXISTS `apostas_db`.`aposta` (
   `id` int NOT NULL AUTO_INCREMENT,
   `user_id` bigint NOT NULL,
   `jogo_id` int NOT NULL,
   `palpite` varchar(255) NOT NULL,
   `valor_aposta` float NOT NULL,
   `data_da_aposta` datetime NOT NULL,
   `situacao` varchar(50) DEFAULT NULL,
   PRIMARY KEY (`id`),
   CONSTRAINT `aposta_usuario_userid` FOREIGN KEY (`user_id`) REFERENCES `usuario` (`id`)
 );

DROP TABLE IF EXISTS `apostas_db`.`jogos`;

CREATE TABLE IF NOT EXISTS `apostas_db`.`jogos` (
   `id` int NOT NULL AUTO_INCREMENT,
   `time1` varchar(255) NOT NULL,
   `time2` varchar(255) NOT NULL,
   `resultado` varchar(255) DEFAULT NULL,
   `campeonato` varchar(500) DEFAULT NULL,
   `data_do_jogo` datetime NOT NULL,
   PRIMARY KEY (`id`)
 );

DROP TABLE IF EXISTS `apostas_db`.`usuario`;

CREATE TABLE IF NOT EXISTS `apostas_db`.`usuario` (
   `id` bigint NOT NULL,
   `saldo` float DEFAULT NULL,
   PRIMARY KEY (`id`)
 );

DROP TABLE IF EXISTS `apostas_db`.`transacoes`;

CREATE TABLE IF NOT EXISTS `apostas_db`.`transacoes` (
   `id` bigint NOT NULL AUTO_INCREMENT,
   `user_id` bigint NOT NULL,
   `tipo_transacao` varchar(50) NOT NULL,
   `data_da_transacao` datetime NOT NULL,
   `saldo_antes` float NOT NULL,
   `saldo_depois` float NOT NULL,
   PRIMARY KEY (`id`),
   KEY `user_id` (`user_id`),
   CONSTRAINT `transacoes_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `usuario` (`id`)
 );
