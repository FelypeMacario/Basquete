CREATE TABLE IF NOT EXISTS jogadores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL UNIQUE,
    vitorias INTEGER DEFAULT 0,
    derrotas INTEGER DEFAULT 0,
    pontos INTEGER DEFAULT 0
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