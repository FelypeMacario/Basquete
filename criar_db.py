import sqlite3

conn = sqlite3.connect("ranking.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS jogadores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    vitorias INTEGER DEFAULT 0,
    derrotas INTEGER DEFAULT 0,
    pontos INTEGER DEFAULT 0
)
""")

# Inserir dados (só se a tabela estiver vazia)
cursor.execute("SELECT COUNT(*) FROM jogadores")
if cursor.fetchone()[0] == 0:
    cursor.executemany("""
    INSERT INTO jogadores (nome, vitorias, derrotas, pontos)
    VALUES (?, ?, ?, ?)
    """, [
        ('Victor', 10, 2, 30),
        ('Ana', 8, 3, 24),
        ('Lucas', 6, 5, 18),
        ('Marcos', 12, 1, 36),
        ('Julia', 9, 4, 27),
        ('Carlos', 7, 6, 21),
        ('Fernanda', 11, 2, 33),
        ('Rafael', 5, 7, 15),
        ('Beatriz', 4, 8, 12),
        ('Pedro', 3, 9, 9)
    ])

conn.commit()
conn.close()

print("Banco criado e populado com sucesso!")