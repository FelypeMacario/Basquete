from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

def get_dados(ordenacao):
    conn = sqlite3.connect("ranking.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    colunas_validas = ["vitorias", "derrotas", "pontos"]

    if ordenacao not in colunas_validas:
        ordenacao = "pontos"

    query = f"""
    SELECT nome, vitorias, derrotas, pontos
    FROM jogadores
    ORDER BY {ordenacao} DESC
    LIMIT 10
    """

    cursor.execute(query)
    dados = cursor.fetchall()
    conn.close()

    return [dict(d) for d in dados]


@app.route("/")
def index():
    return render_template(
        "index.html",
        rank1v1=get_dados("vitorias"),
        rank1min=get_dados("derrotas"),
        rankpontos=get_dados("pontos")
    )

@app.route("/desafio")
def desafio():
    return render_template("desafio.html")


@app.route("/contato", methods=["GET", "POST"])
def contato():
    if request.method == "POST":
        return redirect(url_for("contato"))  
    return render_template("contato.html")


@app.route("/rank")
def rank():
    return render_template("rank.html")

@app.route("/entrar", methods=["GET", "POST"])
def entrar():
    if request.method == "POST":
        return redirect(url_for("index"))
    return render_template("entrar.html")

@app.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        return redirect(url_for("entrar"))  # ← volta para o login após registrar
    return render_template("registro.html")

if __name__ == "__main__":
    app.run(debug=True)