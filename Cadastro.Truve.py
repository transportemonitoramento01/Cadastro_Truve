from flask import Flask, render_template, request, send_file
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from fpdf import FPDF

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Google Sheets Authentication
scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive.file"]
creds = ServiceAccountCredentials.from_json_keyfile_name(
    r'C:\Users\weidney.junior.NORTETECH\OneDrive - NORTE ENERGIA SERVICOS DE TECNOLOGIA LTDA (1)\Área de Trabalho\Cadastro_Truve\credentials.json',
    scopes)

client = gspread.authorize(creds)
spreadsheet = client.open_by_key('15RVj_PzMLRkTWZR981CuVVmY5qoobRfcqJx5dSr5FdU').sheet1

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/enviar', methods=['POST'])
def enviar():
    nome = request.form['nome']
    cpf = request.form['cpf']

    # Upload da CNH
    cnh = request.files['cnh']
    cnh_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{nome}_{cpf}_cnh.png")
    cnh.save(cnh_path)

    # Assinatura enviada
    assinatura = request.form['assinatura']
    assinatura_path = os.path.join(UPLOAD_FOLDER, f"{nome}_{cpf}_assinatura.png")
    with open(assinatura_path, 'wb') as f:
        f.write(assinatura.encode())

    # Salvar os dados no Google Sheets
    spreadsheet.append_row([nome, cpf, cnh_path, assinatura_path])

    # Gerar PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="TERMO DE RESPONSABILIDADE", ln=True, align='C')
    pdf.cell(200, 10, txt=f"Nome: {nome}", ln=True)
    pdf.cell(200, 10, txt=f"CPF: {cpf}", ln=True)
    
    # Adicionar a CNH no PDF
    pdf.image(cnh_path, x=10, y=50, w=70)
    
    # Adicionar assinatura
    pdf.image(assinatura_path, x=10, y=130, w=50)

    pdf_output = os.path.join(UPLOAD_FOLDER, f"{nome}_{cpf}_termo.pdf")
    pdf.output(pdf_output)

    return send_file(pdf_output, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
