from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import sqlite3
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent
DATABASE = BASE_DIR / "fila.db"

app = Flask(__name__)
app.config["SECRET_KEY"] = "chave-fila-atendimento"

STATUS_VALIDOS = {"Aguardando", "Em Atendimento", "Concluído", "Cancelado"}
PRIORIDADES = {"Normal", "Preferencial"}


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS atendimentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            prioridade TEXT NOT NULL DEFAULT 'Normal',
            status TEXT NOT NULL DEFAULT 'Aguardando',
            criado_em TEXT NOT NULL,
            chamado_em TEXT,
            finalizado_em TEXT
        )
    """)
    conn.commit()
    conn.close()


def agora():
    return datetime.now().strftime("%d/%m/%Y %H:%M:%S")


def agora_iso():
    return datetime.now().isoformat(timespec="seconds")


def buscar_atendimentos(status=None):
    conn = get_db()
    if status:
        rows = conn.execute(
            "SELECT * FROM atendimentos WHERE status = ? ORDER BY id ASC",
            (status,)
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM atendimentos ORDER BY id DESC"
        ).fetchall()
    conn.close()
    return rows


@app.route("/")
def index():
    conn = get_db()

    # Preferencial passa à frente dos normais, mantendo FIFO dentro de cada prioridade.
    fila = conn.execute("""
        SELECT * FROM atendimentos
        WHERE status = 'Aguardando'
        ORDER BY
            CASE WHEN prioridade = 'Preferencial' THEN 0 ELSE 1 END,
            id ASC
    """).fetchall()

    em_atendimento = conn.execute("""
        SELECT * FROM atendimentos
        WHERE status = 'Em Atendimento'
        ORDER BY chamado_em ASC
    """).fetchall()

    historico = conn.execute("""
        SELECT * FROM atendimentos
        WHERE status IN ('Concluído', 'Cancelado')
        ORDER BY id DESC
        LIMIT 20
    """).fetchall()

    totais = conn.execute("""
        SELECT
            SUM(CASE WHEN status = 'Aguardando' THEN 1 ELSE 0 END) AS aguardando,
            SUM(CASE WHEN status = 'Em Atendimento' THEN 1 ELSE 0 END) AS atendimento,
            SUM(CASE WHEN status = 'Concluído' THEN 1 ELSE 0 END) AS concluidos,
            SUM(CASE WHEN status = 'Cancelado' THEN 1 ELSE 0 END) AS cancelados
        FROM atendimentos
    """).fetchone()

    conn.close()

    return render_template(
        "index.html",
        fila=fila,
        em_atendimento=em_atendimento,
        historico=historico,
        totais=totais
    )


@app.post("/cadastrar")
def cadastrar():
    nome = request.form.get("nome", "").strip()
    prioridade = request.form.get("prioridade", "Normal")

    if not nome:
        flash("Digite o nome do cliente.", "erro")
        return redirect(url_for("index"))

    if prioridade not in PRIORIDADES:
        prioridade = "Normal"

    conn = get_db()
    conn.execute("""
        INSERT INTO atendimentos (nome, prioridade, status, criado_em)
        VALUES (?, ?, 'Aguardando', ?)
    """, (nome, prioridade, agora()))
    conn.commit()
    conn.close()

    flash(f"{nome} foi adicionado à fila.", "sucesso")
    return redirect(url_for("index"))


@app.post("/chamar-proximo")
def chamar_proximo():
    conn = get_db()

    cliente = conn.execute("""
        SELECT * FROM atendimentos
        WHERE status = 'Aguardando'
        ORDER BY
            CASE WHEN prioridade = 'Preferencial' THEN 0 ELSE 1 END,
            id ASC
        LIMIT 1
    """).fetchone()

    if not cliente:
        conn.close()
        flash("Não há clientes aguardando.", "aviso")
        return redirect(url_for("index"))

    conn.execute("""
        UPDATE atendimentos
        SET status = 'Em Atendimento', chamado_em = ?
        WHERE id = ?
    """, (agora(), cliente["id"]))

    conn.commit()
    conn.close()

    flash(f"Cliente chamado: {cliente['nome']}.", "sucesso")
    return redirect(url_for("index"))


@app.post("/status/<int:atendimento_id>")
def alterar_status(atendimento_id):
    novo_status = request.form.get("status")

    if novo_status not in STATUS_VALIDOS:
        flash("Status inválido.", "erro")
        return redirect(url_for("index"))

    conn = get_db()
    cliente = conn.execute(
        "SELECT * FROM atendimentos WHERE id = ?", (atendimento_id,)
    ).fetchone()

    if not cliente:
        conn.close()
        flash("Atendimento não encontrado.", "erro")
        return redirect(url_for("index"))

    finalizado_em = cliente["finalizado_em"]

    if novo_status in {"Concluído", "Cancelado"}:
        finalizado_em = agora()

    conn.execute("""
        UPDATE atendimentos
        SET status = ?, finalizado_em = ?
        WHERE id = ?
    """, (novo_status, finalizado_em, atendimento_id))

    conn.commit()
    conn.close()

    flash(f"Status de {cliente['nome']} alterado para {novo_status}.", "sucesso")
    return redirect(url_for("index"))


@app.post("/cancelar/<int:atendimento_id>")
def cancelar(atendimento_id):
    conn = get_db()
    cliente = conn.execute(
        "SELECT * FROM atendimentos WHERE id = ?", (atendimento_id,)
    ).fetchone()

    if not cliente:
        conn.close()
        flash("Atendimento não encontrado.", "erro")
        return redirect(url_for("index"))

    conn.execute("""
        UPDATE atendimentos
        SET status = 'Cancelado', finalizado_em = ?
        WHERE id = ?
    """, (agora(), atendimento_id))

    conn.commit()
    conn.close()

    flash(f"Atendimento de {cliente['nome']} cancelado.", "aviso")
    return redirect(url_for("index"))


@app.get("/api/fila")
def api_fila():
    conn = get_db()
    fila = conn.execute("""
        SELECT id, nome, prioridade, status, criado_em
        FROM atendimentos
        WHERE status = 'Aguardando'
        ORDER BY
            CASE WHEN prioridade = 'Preferencial' THEN 0 ELSE 1 END,
            id ASC
    """).fetchall()
    conn.close()

    return jsonify([dict(item) for item in fila])


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
