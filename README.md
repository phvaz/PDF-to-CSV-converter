### 📄 **Conversor de PDF para CSV**  

Este script converte extratos de corretoras em formato PDF para um arquivo CSV, facilitando a manipulação e análise dos dados.  

---

## 🚀 **Como Usar**  

### **1. Instale as dependências**  
Certifique-se de que o Python esteja instalado e, em seguida, instale a biblioteca `pdfplumber` com o comando:  
```bash
pip install pdfplumber
```

---

### **2. Estrutura de Arquivos**  
📁 Projeto/  
├── 📄 `converter.py` *(Script de conversão)*  
├── 📄 `nubank.pdf` *(Arquivo PDF com o extrato)*  
└── 📄 `extrato_nubank.csv` *(Arquivo CSV gerado)*  

---

### **3. Código do Script**  
Salve o código abaixo em um arquivo chamado `converter.py`:  
```python
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
pdf_path = 'nubank.pdf'  # Caminho do seu PDF ou nome do arquivo caso esteja na mesma pasta
csv_path = 'extrato_nubank.csv'  # Caminho onde o CSV será salvo ou nome do novo arquivo
pdf_to_csv(pdf_path, csv_path)
```

---

### **4. Como Executar**  
No terminal ou prompt de comando, vá até a pasta onde o script está salvo e execute:  
```bash
python converter.py
```

---

### **5. Resultado**  
- O arquivo CSV será gerado no mesmo diretório do script.  
- O arquivo CSV conterá cada linha do PDF em uma nova linha no CSV.  

---

### 🛠️ **Personalização**  
- Para alterar o caminho do PDF, ajuste o valor de `pdf_path`.  
- Para mudar o nome ou o local onde o arquivo CSV será salvo, modifique `csv_path`.  

---

💡 **Dica:**  
- Se o PDF tiver uma formatação específica (como colunas separadas por espaço), você pode ajustar o método `extract_text()` ou processar o texto após a extração.  
- Para melhorar a detecção de dados tabulares, experimente usar `extract_table()` em vez de `extract_text()`.  

---

📌 **Licença**  
Este script é de uso livre. Personalize e adapte conforme suas necessidades! 😎
