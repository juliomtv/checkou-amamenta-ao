from flask import Flask, request, jsonify
import requests
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

app = Flask(__name__)

# === CONFIGURAÇÕES ===
MERCADO_PAGO_ACCESS_TOKEN = 'APP_USR-2946444663060784-060410-0d84fef851c131fd30cef8bae1a6c24f-2000476508'  # ⚠️ Coloque aqui seu token do Mercado Pago

EMAIL_REMETENTE = 'nalinnazarethdoula@gmail.com'
SENHA_EMAIL = 'mgnw npez drxv klug'  # ⚠️ Senha de app, não sua senha normal
SMTP_SERVIDOR = 'smtp.gmail.com'
SMTP_PORTA = 587

LINK_EBOOK = 'https://drive.google.com/file/d/1Akd6zzThAvoQug8ksNLEB8xB6ngZQfdE/view?usp=drive_link'

#✅ Defina qual é o external_reference do seu produto:
EXTERNAL_REFERENCE_DO_EBOOK = 'ebook-amamentacao'  # <- Isso vem da criação do link

# ✅ ROTA RAIZ
@app.route('/')
def home():
    return '🚀 Funcionando! Webhook de pagamento ativo.'

# === WEBHOOK DO MERCADO PAGO ===
@app.route('/webhook', methods=['POST'])
def webhook():
    dados = request.json

    if dados and 'type' in dados and dados['type'] == 'payment':
        payment_id = dados.get('data', {}).get('id')

        if payment_id:
            pagamento = consultar_pagamento(payment_id)

            if pagamento:
                status = pagamento.get('status')
                email_cliente = pagamento.get('payer', {}).get('email')
                nome_cliente = pagamento.get('payer', {}).get('first_name')
                referencia = pagamento.get('external_reference')  # 🔥 Aqui pega a referência

                if status == 'approved' and referencia == EXTERNAL_REFERENCE_DO_EBOOK:
                    enviar_email(email_cliente, nome_cliente)
                    return jsonify({'status': 'Ebook enviado com sucesso!'}), 200
                else:
                    print('Pagamento não corresponde ao ebook.')
                    return jsonify({'status': 'Pagamento não é do ebook.'}), 200

    return jsonify({'status': 'Webhook recebido'}), 200


# === CONSULTA O PAGAMENTO NA API DO MERCADO PAGO ===
def consultar_pagamento(payment_id):
    url = f'https://api.mercadopago.com/v1/payments/{payment_id}'
    headers = {
        'Authorization': f'Bearer {MERCADO_PAGO_ACCESS_TOKEN}'
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        print('Erro ao consultar pagamento:', response.text)
        return None


# === ENVIA O EMAIL COM O EBOOK ===
def enviar_email(destinatario, nome):
    try:
        mensagem = MIMEMultipart()
        mensagem['From'] = EMAIL_REMETENTE
        mensagem['To'] = destinatario
        mensagem['Subject'] = 'Seu Ebook está aqui! 📚'

        corpo = f"""
        Olá {nome}! 🎉

        Obrigado pela sua compra.

        Aqui está o link para download do seu Ebook:
        {LINK_EBOOK}

        Qualquer dúvida, estamos à disposição.

        Atenciosamente,
        Sua Empresa
        """

        mensagem.attach(MIMEText(corpo, 'plain'))

        servidor = smtplib.SMTP(SMTP_SERVIDOR, SMTP_PORTA)
        servidor.starttls()
        servidor.login(EMAIL_REMETENTE, SENHA_EMAIL)
        servidor.send_message(mensagem)
        servidor.quit()

        print(f"E-mail enviado para {destinatario}")

    except Exception as e:
        print(f"Erro ao enviar e-mail: {e}")


# === INICIA O SERVIDOR ===
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
