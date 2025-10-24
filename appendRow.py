import gspread
from oauth2client.service_account import ServiceAccountCredentials


def append_valores(aba, coluna_inicial, valores):
    """
    Insere os valores a partir da coluna especificada na última linha disponível.

    Parâmetros:
    - aba: objeto worksheet do gspread
    - coluna_inicial: letra da coluna inicial (ex: 'J')
    - valores: lista de valores a serem inseridos
    """
    import string

    # Converte letra da coluna para número (ex: 'J' → 10)
    colunas = {letra: idx + 1 for idx, letra in enumerate(string.ascii_uppercase)}
    col_inicio = colunas.get(coluna_inicial.upper(), 1)

    # Descobre a última linha com conteúdo na coluna inicial
    ultima_linha = len(aba.col_values(col_inicio)) + 1

    # Insere os valores nas colunas consecutivas
    for i, valor in enumerate(valores):
        aba.update_cell(ultima_linha, col_inicio + i, valor)

