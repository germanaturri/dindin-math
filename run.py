"""Ponto de entrada do DinDin Math.

Uso:
    python run.py              -> inicia o servidor em http://127.0.0.1:5000
    python run.py --reset-db   -> recria o banco com os dados de exemplo e inicia
"""
import os
import sys

from app import create_app
from app.db import criar_banco

app = create_app()

if __name__ == "__main__":
    with app.app_context():
        if "--reset-db" in sys.argv or not os.path.exists(app.config["DATABASE"]):
            criar_banco(com_dados_exemplo=True)
            print("Banco de dados criado com dados de exemplo (login: demo@dindin.com / Demo1234)")
    host = os.environ.get("DINDIN_HOST", "127.0.0.1")
    porta = int(os.environ.get("DINDIN_PORTA", "5000"))
    app.run(host=host, port=porta, debug=os.environ.get("DINDIN_DEBUG") == "1")
