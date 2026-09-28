"""
Coletor de repositórios do GitHub (documento principal do RI).

ESTRATÉGIA DE ESCALA (o ponto central para superar 50 mil documentos):
A Search API do GitHub devolve no máximo 1.000 resultados por consulta. Para
coletar muito mais que isso, PARTICIONAMOS o espaço de busca em milhares de
consultas disjuntas, cada uma com <= 1.000 resultados, e somamos os itens.

Particionamento adotado: por número EXATO de estrelas. Para cada valor S de
star_min..star_max, a consulta é stars:S. Como cada valor de estrela isola
um subconjunto pequeno de repositórios, quase todas as partições cabem no
limite de 1.000 e a soma cobre dezenas/centenas de milhares de repositórios.

FLUXO:
  1. Gera as partições (fronteira), da mais rara (muitas estrelas) para a mais
     comum, e persiste em SQLite (permite retomar).
  2. Para cada partição: pagina a Search API (100/página, até 10 páginas =
     1.000 itens) coletando repositórios.
  3. De cada repositório: normaliza os metadados, extrai o proprietário
     (usuário) e, opcionalmente, baixa o README (texto rico para a busca).
  4. Critério de parada: meta de repositórios (padrão 50.000) OU partições
     esgotadas.
"""

import logging
from typing import Dict, Optional

from .config import CrawlerConfig
from .fetcher import Fetcher
from .storage import Storage

logger = logging.getLogger(__name__)


def parse_repository(item: Dict) -> Dict:
    """Normaliza um objeto de repositório da API para o nosso schema."""

    owner = item.get("owner") or {}
    lic = item.get("license") or {}

    return {
        "id": item.get("id"),
        "full_name": item.get("full_name"),
        "name": item.get("name"),
        "owner_login": owner.get("login"),
        "description": item.get("description"),
        "language": item.get("language"),
        "topics": item.get("topics", []) or [],
        "
