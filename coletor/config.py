"""
Configuração central do coletor (API do GitHub).

Todas as políticas, tolerâncias e critérios de parada do coletor ficam
concentrados aqui para facilitar a justificativa das decisões de projeto
exigida no relatório (Descrição do coletor - 40%).

Fonte de dados: API REST oficial do GitHub (https://api.github.com).

Documento principal: REPOSITÓRIOS.
De cada repositório extraímos também o PROPRIETÁRIO
(usuário/organização), armazenado de forma deduplicada.
"""

import os
from dataclasses import dataclass, field


def _load_token() -> str:
    """
    Lê o token da API do GitHub de forma segura:
      1. variável de ambiente GITHUB_TOKEN;
      2. arquivo .env na raiz (linha GITHUB_TOKEN=...).

    O token NUNCA fica no código versionado.
    """

    token = os.environ.get("GITHUB_TOKEN", "").strip()

    if token:
        return token

    for path in (
        ".env",
        os.path.join(os.path.dirname(__file__), "..", ".env")
    ):
        try:
            with open(path, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()

                    if (
                        line.startswith("GITHUB_TOKEN")
                        and "=" in line
                    ):
                        return (
                            line.split("=", 1)[1]
                            .strip()
                            .strip('"')
                            .strip("'")
                        )

        except FileNotFoundError:
            continue

    return ""


@dataclass
class CrawlerConfig:

    # ==========================================================
    # API
    # ==========================================================

    api_base: str = "https://api.github.com"

    token: str = field(default_factory=_load_token)

    user_agent: str = (
        "GitHubRICrawler/1.0 (Trabalho academico de RI)"
    )

    api_version: str = "2022-11-28"

    # ==========================================================
    # Polidez / Rate Limit
    # ==========================================================

    request_delay: float = 0.8
    request_delay_jitter: float = 0.4

    num_workers: int = 1

    # ==========================================================
    # Tolerância a falhas
    # ==========================================================

    request_timeout: float = 30.0

    max_retries: int = 4

    backoff_factor: float = 2.0

    backoff_base: float = 2.0

    retry_status_codes: tuple = (
        429,
        500,
        502,
        503,
        504
    )

    # ==========================================================
    # Critério de parada
    # ==========================================================

    target_pages: int = 50000

    max_frontier_size: int = 1000000

    # ==========================================================
    # README
    # ==========================================================

    fetch_readme: bool = True

    readme_max_bytes: int = 200000

    # ==========================================================
    # Armazenamento
    # ==========================================================

    output_dir: str = "data"

    db_filename: str = "github.db"

    raw_html_dir: str = "raw_readme"

    
