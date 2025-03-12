import pdfplumber
import csv

def pdf_to_csv(pdf_path, csv_path):
    with pdfplumber.open(pdf_path) as pdf:
        extracted_data = []

        for page in pdf.pages:
            text = page.extract_text()

            if text:
                lines = text.split('\n')  
                extracted_data.extend(lines)  

        with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            for line in extracted_data:
                writer.writerow([line])  

        print(f"Arquivo CSV salvo em: {csv_path}")

# Exemplo de uso
pdf_path = 'nubank.pdf'  # Caminho do seu PDF ou nome do arquivo do PDF caso esteja na mesma pasta
csv_path = 'extrato_nubank.csv'  # Caminho onde o CSV será salvo ou nome do novo arquivo
pdf_to_csv(pdf_path, csv_path)