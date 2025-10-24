import re
import pytesseract
from PIL import Image

import shutil

pytesseract.pytesseract.tesseract_cmd = shutil.which("tesseract")




def extrair_data(texto):
    padrao = r"(\d{2}/\d{2}/\d{4})"
    match = re.search(padrao, texto)
    return match.group(1) if match else None


def extrair_valor_aposta(texto):
    padrao = r"Aposta\s+R\$\s?(\d{1,3}(?:\.\d{3})*,\d{2})"
    match = re.search(padrao, texto)
    return match.group(1) if match else None


def extrair_valor_retorno(texto):
    padrao = r"Retorno\s+R\$\s?(\d{1,3}(?:\.\d{3})*,\d{2})"
    match = re.search(padrao, texto)
    return match.group(1) if match else None


def extrair_odd_aposta(texto):
    padrao = r"Detalhes da Aposta\s+(\d{1,3}(?:,\d{2})?)"
    match = re.search(padrao, texto)
    odd = match.group(1) if match else None
    if odd:
        odd = formatar_odd(odd)
    return odd

def formatar_odd(x):
    print("Estou dentro do formatar odd com x =", x)
    x_str = str(x)
    print("transformei o x em string:", x_str)

    # Se já tem ponto ou vírgula, retorna como float normalizado
    if '.' in x_str or ',' in x_str:
        return float(x_str.replace(',', '.'))

    # Se tem menos de 3 dígitos, completa com zeros à direita
    if len(x_str) == 1:
        return float(f"{x_str}.00")
    elif len(x_str) == 2:
        return float(f"{x_str[0]}.{x_str[1]}0")
    else:
        parte_inteira = x_str[:-2]
        parte_decimal = x_str[-2:]
        return float(f"{parte_inteira}.{parte_decimal}")

def extrair_texto_imagem(caminho_imagem):
    imagem = Image.open(caminho_imagem)
    texto = pytesseract.image_to_string(imagem, lang='por')
    return texto

