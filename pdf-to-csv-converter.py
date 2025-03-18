import pdfplumber
import csv
import re
import unicodedata
from datetime import datetime

def normalize_str(s: str) -> str:
    """
    Remove acentos e caracteres especiais, retornando texto ASCII básico, 
    tudo em minúsculo, para facilitar comparação.
    """
    nfkd = unicodedata.normalize("NFKD", s)
    return "".join(c for c in nfkd if not unicodedata.combining(c)).lower()

def parse_date(date_str: str) -> str:
    """
    Converte data/hora no formato 'DD/MM/YYYY HH:MM:SS' para 'YYYY-MM-DD HH:MM UTC'.
    Se falhar, retorna 'Invalid Date'.
    """
    try:
        dt = datetime.strptime(date_str, "%d/%m/%Y %H:%M:%S")
        return dt.strftime("%Y-%m-%d %H:%M UTC")
    except ValueError:
        return "Invalid Date"

def parse_value_brl(brl_str: str) -> str:
    """
    Recebe algo como 'R$ 30.000,00' e retorna '30000.00'.
    Se não encontrar número, retorna string vazia.
    """
    # Remove 'R$', espaços e caracteres estranhos
    temp = brl_str.replace("R$", "").replace(" ", "")
    temp = re.sub(r"[^0-9\.,-]+", "", temp)  # deixa só dígitos, ponto, vírgula, sinal
    
    # Troca vírgula decimal por ponto
    temp = temp.replace(",", ".")

    # Se houver vários pontos, assumimos que os primeiros são separadores de milhar
    parts = temp.split(".")
    if len(parts) > 2:
        decimal_part = parts[-1]
        thousand_parts = parts[:-1]
        temp = "".join(thousand_parts) + "." + decimal_part

    if not temp.strip():
        return ""
    return temp

def parse_value_crypto(crypto_str: str) -> str:
    """
    Recebe algo como '242,17010332' e retorna '242.17010332'.
    """
    temp = re.sub(r"[^0-9,\.-]+", "", crypto_str).strip()
    if not temp:
        return ""
    # Substitui vírgulas por ponto
    temp = temp.replace(",", ".")
    return temp

def process_nubank_line(row: list) -> list:
    """
    Recebe uma linha da tabela do PDF (ex.: 
      [Data, Operação, Moeda, Fração, Valor transacionado, Taxa])
    e retorna a linha no formato Koinly (12 colunas).
    """
    if len(row) < 6:
        # Linha inválida ou cabeçalho incorreto
        return ["Invalid Row"] * 12

    data_str, operacao_str, moeda_str, fracao_str, valor_str, taxa_str = row[:6]

    # Converter data
    date = parse_date(data_str)

    # Normalizar nome da operação
    operacao_norm = normalize_str(operacao_str)

    # Parse de quantidades/valores
    crypto_amount = parse_value_crypto(fracao_str)  # fração em cripto
    valor_brl = parse_value_brl(valor_str)
    taxa_brl = parse_value_brl(taxa_str)

    # Campos Koinly
    sent_amount = ""
    sent_currency = ""
    received_amount = ""
    received_currency = ""
    fee_amount = ""
    fee_currency = ""
    label = ""
    description = operacao_str  # texto original para referência
    txhash = ""

    # Verifica se é "bônus" (usado como reward)
    # Você pode personalizar a lógica usando operacao_norm
    is_bonus = "bonus" in operacao_norm or "bônus" in operacao_norm

    # Regras de mapeamento para Koinly:
    # - "Compra": Sent = Valor em BRL, Received = Fração cripto, Fee = taxa em BRL
    # - "Venda": Sent = Fração cripto, Received = Valor em BRL, Fee = taxa em BRL
    # - "Bônus": Received = Fração cripto, label=reward
    if "compra" in operacao_norm:
        # Pagamos em BRL, recebemos cripto
        sent_amount = valor_brl
        sent_currency = "BRL"
        received_amount = crypto_amount
        received_currency = moeda_str
        fee_amount = taxa_brl
        fee_currency = "BRL"

    elif "venda" in operacao_norm:
        # Vendemos cripto, recebemos BRL
        sent_amount = crypto_amount
        sent_currency = moeda_str
        received_amount = valor_brl
        received_currency = "BRL"
        fee_amount = taxa_brl
        fee_currency = "BRL"

    elif is_bonus:
        # Bônus => recebemos cripto, sem fee
        received_amount = crypto_amount
        received_currency = moeda_str
        fee_amount = "0"
        fee_currency = ""
        label = "reward"

    else:
        # Outras situações possíveis (saque, transferência etc.)
        # Aqui, como fallback, recebemos cripto
        received_amount = crypto_amount
        received_currency = moeda_str
        fee_amount = taxa_brl
        fee_currency = "BRL"

    # Monta e retorna a linha no formato Koinly (12 colunas)
    return [
        date,            # Date
        sent_amount,     # Sent Amount
        sent_currency,   # Sent Currency
        received_amount, # Received Amount
        received_currency, 
        fee_amount,      
        fee_currency,    
        "",  # Net Worth Amount
        "",  # Net Worth Currency
        label, 
        description, 
        txhash
    ]

def convert_pdf_to_koinly(pdf_path: str, output_csv_path: str):
    """
    Lê o PDF do Nubank (ou Nucoin) diretamente, extrai linhas e colunas usando pdfplumber,
    e gera um CSV final no formato Koinly (12 colunas).
    """
    # Abre o CSV de saída
    with open(output_csv_path, "w", encoding="utf-8", newline="") as outfile:
        writer = csv.writer(outfile)

        # Escreve cabeçalho do Koinly
        writer.writerow([
            "Date", "Sent Amount", "Sent Currency",
            "Received Amount", "Received Currency",
            "Fee Amount", "Fee Currency",
            "Net Worth Amount", "Net Worth Currency",
            "Label", "Description", "TxHash"
        ])

        # Abre o PDF com pdfplumber
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                tables = page.extract_tables()
                for table in tables:
                    for row in table:
                        # Muitas vezes, a 1ª linha é o cabeçalho "Data, Operação..."
                        # Podemos filtrar se for igual ao cabeçalho
                        row_norm = [normalize_str(r) for r in row]
                        if "data" in row_norm[0] and "operacao" in row_norm[1]:
                            # Linha de cabeçalho => pular
                            continue

                        # Converte a linha para o formato Koinly
                        koinly_row = process_nubank_line(row)
                        writer.writerow(koinly_row)

    print(f"Conversão finalizada! Arquivo Koinly gerado em: {output_csv_path}")

# Exemplo de uso
if __name__ == "__main__":
    pdf_path = "nubank.pdf"
    output_csv = "extrato_nubank_koinly.csv"
    convert_pdf_to_koinly(pdf_path, output_csv)