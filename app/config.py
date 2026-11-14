"""Configurações da aplicação, lidas de variáveis de ambiente (arquivo .env)."""
import os


def _carregar_env(caminho=".env"):
    """Lê um arquivo .env simples (CHAVE=valor) sem depender de bibliotecas externas."""
    if not os.path.exists(caminho):
        return
    with open(caminho, encoding="utf-8") as arq:
        for linha in arq:
            linha = linha.strip()
            if not linha or linha.startswith("#") or "=" not in linha:
                continue
            chave, valor = linha.split("=", 1)
            os.environ.setdefault(chave.strip(), valor.strip().strip('"').strip("'"))


_carregar_env()


class Config:
    # Chave usada para assinar o cookie de sessão. TROQUE em produção!
    SECRET_KEY = os.getenv("SECRET_KEY", "troque-esta-chave-em-producao")

    # Parâmetros de conexão com o PostgreSQL (aceita conexão remota)
    DB_ENGINE = os.getenv("DB_ENGINE", "postgres")       # postgres | sqlite
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = int(os.getenv("DB_PORT", "5432"))
    DB_NAME = os.getenv("DB_NAME", "dindin_math")
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
    DB_SSLMODE = os.getenv("DB_SSLMODE", "prefer")       # use "require" em bancos na nuvem
    SQLITE_PATH = os.getenv("SQLITE_PATH", "dindin_math.db")

    # Segurança do cookie de sessão
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "0") == "1"
    JSON_SORT_KEYS = False
