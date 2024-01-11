CREATE DATABASE blog;
USE blog;

-- Create the posts table with an auto-incremented primary key (id)
CREATE TABLE posts (
  id INT AUTO_INCREMENT,
  title VARCHAR(255),
  content TEXT,
  PRIMARY KEY (id)
);

-- Create the comments table with an auto-incremented primary key (id)
-- and a foreign key (post_id) referencing the id column in the posts table
CREATE TABLE comments (
  id INT AUTO_INCREMENT,
  text VARCHAR(200),
  post_id INT,
  PRIMARY KEY (id),
  FOREIGN KEY (post_id) REFERENCES posts(id)
);

-- Insert some sample data into the posts table
INSERT INTO posts (title, content) VALUES
  ('Post 1', 'Content of post 1'),
  ('Post 2', 'Content of post 2');

-- Insert some sample data into the comments table
INSERT INTO comments (text, post_id) VALUES
  ('Comment 1 for Post 1', 1),
  ('Comment 2 for Post 1', 1),
  ('Comment 1 for Post 2', 2);
