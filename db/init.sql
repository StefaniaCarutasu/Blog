CREATE DATABASE blog;
use blog;

CREATE TABLE comments (
  id int AUTO_INCREMENT,
  text VARCHAR(200),
  PRIMARY KEY(id)
);

INSERT INTO comments
  (text)
VALUES
  ('Comm1'),
  ('Comm2');