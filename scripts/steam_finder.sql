DROP DATABASE IF EXISTS bloc_1;
CREATE DATABASE IF NOT EXISTS bloc_1;
USE bloc_1;

SELECT 'CREATING DATABASE STRUCTURE' as 'INFO';

CREATE TABLE games (
    game_id VARCHAR(255) NOT NULL UNIQUE,
    game_name VARCHAR(255) NOT NULL UNIQUE,
    PRIMARY KEY (game_id)
);

CREATE TABLE languages (
    language_id INT AUTO_INCREMENT,
    language_name VARCHAR(255) NOT NULL UNIQUE,
    PRIMARY KEY (language_id)
);

CREATE TABLE games_languages (
    game_id VARCHAR(255) NOT NULL UNIQUE,
    language_id INT NOT NULL,
    FOREIGN KEY (game_id) REFERENCES games (game_id) ON DELETE CASCADE,
    FOREIGN KEY (language_id) REFERENCES languages (language_id) ON DELETE CASCADE,
    PRIMARY KEY (game_id, language_id)
);
CREATE INDEX idx_games_languages_language_id ON games_languages(language_id);

CREATE TABLE features (
    feature_id INT AUTO_INCREMENT,
    feature_name VARCHAR(255) NOT NULL UNIQUE,
    PRIMARY KEY (feature_id)
);

CREATE TABLE games_features (
    game_id VARCHAR(255) NOT NULL,
    feature_id INT NOT NULL,
    FOREIGN KEY (game_id) REFERENCES games (game_id) ON DELETE CASCADE,
    FOREIGN KEY (feature_id) REFERENCES features (feature_id) ON DELETE CASCADE,
    PRIMARY KEY (game_id, feature_id)
);
CREATE INDEX idx_games_features_feature_id ON games_features(feature_id);

CREATE TABLE games_prices (
    game_id VARCHAR(255) NOT NULL,
    check_date DATE NOT NULL,
    price VARCHAR(32) DEFAULT NULL,
    FOREIGN KEY (game_id) REFERENCES games (game_id) ON DELETE CASCADE,
    PRIMARY KEY (game_id, check_date)
);

CREATE TABLE tags (
    tag_id INT AUTO_INCREMENT,
    tag_name VARCHAR(255) NOT NULL UNIQUE,
    PRIMARY KEY (tag_id)
);

CREATE TABLE games_tags (
    game_id VARCHAR(255) NOT NULL,
    tag_id INT NOT NULL,
    FOREIGN KEY (game_id) REFERENCES games (game_id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags (tag_id) ON DELETE CASCADE,
    PRIMARY KEY (game_id, tag_id)
);
CREATE INDEX idx_games_tags_tag_id ON games_tags(tag_id);

CREATE TABLE genres (
    genre_id INT AUTO_INCREMENT,
    genre_name VARCHAR(255) NOT NULL UNIQUE,
    PRIMARY KEY (genre_id)
);

CREATE TABLE games_genres (
    game_id VARCHAR(255) NOT NULL,
    genre_id INT NOT NULL,
    FOREIGN KEY (game_id) REFERENCES games (game_id) ON DELETE CASCADE,
    FOREIGN KEY (genre_id) REFERENCES genres (genre_id) ON DELETE CASCADE,
    PRIMARY KEY (game_id, genre_id)
);
CREATE INDEX idx_games_genres_genre_id ON games_genres(genre_id);

CREATE TABLE publishers (
    publisher_id INT AUTO_INCREMENT,
    publisher_name VARCHAR(255) NOT NULL UNIQUE,
    PRIMARY KEY (publisher_id)
);

CREATE TABLE games_publishers (
    publisher_id INT NOT NULL,
    game_id VARCHAR(255) NOT NULL,
    FOREIGN KEY (game_id) REFERENCES games (game_id) ON DELETE CASCADE,
    FOREIGN KEY (publisher_id) REFERENCES publishers (publisher_id) ON DELETE CASCADE,
    PRIMARY KEY (publisher_id, game_id)
);
CREATE INDEX idx_games_publishers_game_id ON games_publishers(game_id);

CREATE TABLE developers (
    developer_id INT AUTO_INCREMENT,
    developer_name VARCHAR(255) NOT NULL UNIQUE,
    PRIMARY KEY (developer_id)
);

CREATE TABLE games_developers (
    developer_id INT NOT NULL,
    game_id VARCHAR(255) NOT NULL,
    FOREIGN KEY (game_id) REFERENCES games (game_id) ON DELETE CASCADE,
    FOREIGN KEY (developer_id) REFERENCES developers (developer_id) ON DELETE CASCADE,
    PRIMARY KEY (developer_id, game_id)
);
CREATE INDEX idx_games_developers_game_id ON games_developers(game_id);

CREATE TABLE reviews (
    review_id INT AUTO_INCREMENT,
    review_name VARCHAR(255) NOT NULL UNIQUE,
    PRIMARY KEY (review_id)
);

CREATE TABLE games_summary (
    summary_id INT AUTO_INCREMENT,
    game_id VARCHAR(255) NOT NULL UNIQUE,
    release_date DATE DEFAULT NULL,
    review_id INT DEFAULT NULL,
    review_cnt INT DEFAULT 0,
    snippet TEXT(65535) DEFAULT NULL,
    metacritic INT DEFAULT NULL,
    link VARCHAR(255) DEFAULT NULL,
    FOREIGN KEY (game_id) REFERENCES games (game_id) ON DELETE CASCADE,
    FOREIGN KEY (review_id) REFERENCES reviews (review_id),
    PRIMARY KEY (summary_id)
);
