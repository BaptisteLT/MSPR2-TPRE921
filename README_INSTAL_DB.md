kubectl get pods

kubectl exec -it TON_NOM_DE_POD -- mariadb -u root -p

USE cofrap_db;

CREATE TABLE IF NOT EXISTS users (
    ID INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    MFA VARCHAR(255) NOT NULL,
    gendate BIGINT NOT NULL,
    expired TINYINT(1) DEFAULT 0
);

SHOW TABLES;