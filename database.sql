CREATE TABLE IF NOT EXISTS partidas (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    pin       TEXT NOT NULL UNIQUE,
    pontos    INTEGER DEFAULT 0,
    tempo     TEXT DEFAULT '00:00',
    nickname  TEXT,
    criado_em DATETIME DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO jogadores (nome, vitorias, derrotas, pontos) VALUES
('Victor', 10, 2, 30),
('Ana', 8, 3, 24),
('Lucas', 6, 5, 18),
('Marcos', 12, 1, 36),
('Julia', 9, 4, 27),
('Carlos', 7, 6, 21),
('Fernanda', 11, 2, 33),
('Rafael', 5, 7, 15),
('Beatriz', 4, 8, 12),
('Pedro', 3, 9, 9);