from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3
import random
import string

app = Flask(__name__)

# ─── BANCO DE DADOS ──────────────────────────────────────────────────────────

def get_db():
    conn = sqlite3.connect("ranking.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS jogadores (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            nome     TEXT NOT NULL UNIQUE,
            vitorias INTEGER DEFAULT 0,
            derrotas INTEGER DEFAULT 0,
            pontos   INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS partidas (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            pin       TEXT NOT NULL UNIQUE,
            pontos    INTEGER DEFAULT 0,
            tempo     TEXT DEFAULT '00:00',
            nickname  TEXT,
            criado_em DATETIME DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    conn.close()

# ─── UTILITÁRIOS ─────────────────────────────────────────────────────────────

def get_ranking(ordenacao):
    colunas_validas = ["vitorias", "derrotas", "pontos"]
    if ordenacao not in colunas_validas:
        ordenacao = "pontos"
    conn = get_db()
    dados = conn.execute(
        f"SELECT nome, vitorias, derrotas, pontos FROM jogadores ORDER BY {ordenacao} DESC LIMIT 10"
    ).fetchall()
    conn.close()
    return [dict(d) for d in dados]

def gerar_pin():
    conn = get_db()
    while True:
        pin = ''.join(random.choices(string.digits, k=4))
        existe = conn.execute("SELECT 1 FROM partidas WHERE pin = ?", (pin,)).fetchone()
        if not existe:
            conn.close()
            return pin

# ─── PÁGINAS DO SITE ─────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template(
        "index.html",
        rank1v1=get_ranking("vitorias"),
        rank1min=get_ranking("derrotas"),
        rankpontos=get_ranking("pontos")
    )

@app.route("/desafio")
def desafio():
    return render_template("desafio.html")

@app.route("/rank")
def rank():
    return render_template(
        "rank.html",
        rank1v1=get_ranking("vitorias"),
        rank1min=get_ranking("derrotas"),
        rankpontos=get_ranking("pontos")
    )

@app.route("/contato", methods=["GET", "POST"])
def contato():
    sucesso = False
    if request.method == "POST":
        nome     = request.form.get("nome", "").strip()
        email    = request.form.get("email", "").strip()
        assunto  = request.form.get("assunto", "").strip()
        mensagem = request.form.get("mensagem", "").strip()
        # Aqui você pode integrar envio de e-mail futuramente
        # Por ora apenas confirma o envio para o usuário
        sucesso = True
    return render_template("contato.html", sucesso=sucesso)

@app.route("/entrar", methods=["GET", "POST"])
def entrar():
    erro = None
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        senha = request.form.get("senha", "").strip()
        conn  = get_db()
        user  = conn.execute(
            "SELECT * FROM jogadores WHERE nome = ?", (email,)
        ).fetchone()
        conn.close()
        # Autenticação simples por nome — adapte para e-mail/senha conforme seu modelo
        if user:
            return redirect(url_for("index"))
        else:
            erro = "Usuário ou senha inválidos."
    return render_template("entrar.html", erro=erro)

@app.route("/registro", methods=["GET", "POST"])
def registro():
    erro = None
    if request.method == "POST":
        nome             = request.form.get("nome", "").strip()
        senha            = request.form.get("senha", "").strip()
        confirmar_senha  = request.form.get("confirmar_senha", "").strip()

        if not nome or len(nome) < 2:
            erro = "Nome deve ter pelo menos 2 caracteres."
        elif senha != confirmar_senha:
            erro = "As senhas não coincidem."
        else:
            conn = get_db()
            try:
                conn.execute(
                    "INSERT INTO jogadores (nome) VALUES (?)", (nome,)
                )
                conn.commit()
                conn.close()
                return redirect(url_for("entrar"))
            except sqlite3.IntegrityError:
                conn.close()
                erro = "Este nome já está em uso."

    return render_template("registro.html", erro=erro)

# ─── ATIVAÇÃO POR PIN ─────────────────────────────────────────────────────────

@app.route("/ativar", methods=["GET", "POST"])
def ativar():
    erro    = None
    partida = None

    if request.method == "POST":
        acao = request.form.get("acao")
        pin  = request.form.get("pin", "").strip()

        # PASSO 1 – buscar partida pelo PIN
        if acao == "buscar":
            if not pin.isdigit() or len(pin) != 4:
                erro = "PIN inválido. Digite exatamente 4 números."
            else:
                conn    = get_db()
                partida = conn.execute(
                    "SELECT * FROM partidas WHERE pin = ?", (pin,)
                ).fetchone()
                conn.close()
                if partida:
                    partida = dict(partida)
                else:
                    erro = "PIN não encontrado. Verifique o placar e tente novamente."

        # PASSO 2 – salvar nickname e registrar no ranking
        elif acao == "salvar":
            nickname = request.form.get("nickname", "").strip()

            if not pin.isdigit() or len(pin) != 4:
                erro = "PIN inválido."
            elif not nickname or len(nickname) < 2:
                erro = "Nickname deve ter pelo menos 2 caracteres."
            else:
                conn    = get_db()
                partida_row = conn.execute(
                    "SELECT * FROM partidas WHERE pin = ?", (pin,)
                ).fetchone()

                if not partida_row:
                    erro = "PIN não encontrado."
                else:
                    pontos_partida = partida_row["pontos"]
                    vitoria = 1
                    derrota = 0

                    conn.execute("UPDATE partidas SET nickname = ? WHERE pin = ?", (nickname, pin))

                    jogador = conn.execute(
                        "SELECT * FROM jogadores WHERE nome = ?", (nickname,)
                    ).fetchone()

                    if jogador:
                        conn.execute(
                            """UPDATE jogadores
                               SET vitorias = vitorias + ?,
                                   derrotas = derrotas + ?,
                                   pontos   = pontos + ?
                               WHERE nome = ?""",
                            (vitoria, derrota, pontos_partida, nickname)
                        )
                    else:
                        conn.execute(
                            "INSERT INTO jogadores (nome, vitorias, derrotas, pontos) VALUES (?, ?, ?, ?)",
                            (nickname, vitoria, derrota, pontos_partida)
                        )

                    conn.commit()
                    conn.close()
                    return redirect(url_for("index"))

                conn.close()

    return render_template("ativar.html", erro=erro, partida=partida)

# ═══════════════════════════════════════════════════════════════════════════════
#  API – ESP32
# ═══════════════════════════════════════════════════════════════════════════════

# POST /api/partida/nova
# Body: { "pontos_casa": 0, "pontos_visitante": 0, "tempo": "10:00" }
# Retorna: { "ok": true, "pin": "3847" }
@app.route("/api/partida/nova", methods=["GET"])
def api_partida_nova():
    pontos = request.args.get("pontos", 0, type=int)
    tempo  = request.args.get("tempo", "00:00")

    pin = gerar_pin()
    conn = get_db()
    conn.execute(
        "INSERT INTO partidas (pin, pontos, tempo) VALUES (?, ?, ?)",
        (pin, pontos, tempo)
    )
    conn.commit()
    conn.close()
    return jsonify({"ok": True, "pin": pin}), 201


# PUT /api/partida/<pin>/atualizar
# Body: { "pontos_casa": 5, "pontos_visitante": 3, "tempo": "07:30" }
# Retorna: { "ok": true }
@app.route("/api/partida/<string:pin>/atualizar", methods=["PUT"])
def api_partida_atualizar(pin):
    dados = request.get_json(silent=True)
    if not dados:
        return jsonify({"ok": False, "erro": "Body JSON ausente"}), 400

    conn = get_db()
    existe = conn.execute("SELECT 1 FROM partidas WHERE pin = ?", (pin,)).fetchone()
    if not existe:
        conn.close()
        return jsonify({"ok": False, "erro": "PIN não encontrado"}), 404

    conn.execute(
        "UPDATE partidas SET pontos_casa = ?, pontos_visitante = ?, tempo = ? WHERE pin = ?",
        (dados.get("pontos_casa", 0), dados.get("pontos_visitante", 0), dados.get("tempo", "00:00"), pin)
    )
    conn.commit()
    conn.close()
    return jsonify({"ok": True})


# GET /api/partida/<pin>
# Retorna: { "ok": true, "partida": { ... } }
@app.route("/api/partida/<string:pin>", methods=["GET"])
def api_partida_get(pin):
    conn    = get_db()
    partida = conn.execute("SELECT * FROM partidas WHERE pin = ?", (pin,)).fetchone()
    conn.close()
    if not partida:
        return jsonify({"ok": False, "erro": "PIN não encontrado"}), 404
    return jsonify({"ok": True, "partida": dict(partida)})


# ─── INICIALIZAÇÃO ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
