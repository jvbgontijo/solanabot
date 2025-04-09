import os
import time
import requests
from datetime import datetime

# === CONFIGURAÇÕES ===
HELIUS_API_KEY = "c9034612-15da-4d51-ac5d-d1bbf166a122"
TELEGRAM_TOKEN = "7208730071:AAEhTNKXSd9tW_i_VkfPHYWOpFjZ6XlDfRs"
TELEGRAM_CHAT_ID = "5064931049"
CARTEIRA = "DfMxre4cKmvogbLrPigxmibVTTQDuzjdXojWzjCXXhzj"
VALOR_MINIMO_USD = 10
INTERVALO_MINUTOS = 15

def enviar_telegram(mensagem):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": mensagem
    }
    try:
        r = requests.post(url, json=payload)
        if not r.ok:
            print("❌ Erro ao enviar Telegram:", r.text)
    except Exception as e:
        print("❌ Exceção ao enviar Telegram:", e)

def interpretar_transacao(tx):
    try:
        token_transfer = tx.get("tokenTransfers", [])
        native_transfer = tx.get("nativeTransfers", [])

        if not token_transfer and not native_transfer:
            return None

        if token_transfer:
            token = token_transfer[0]
            token_symbol = token.get("tokenSymbol", "TOKEN")
            token_amount = float(token.get("amount", 0))
        else:
            token_symbol = "SOL"
            token_amount = float(native_transfer[0].get("amount", 0)) / 1e9

        valor_usd = float(tx.get("fee", 0)) / 1e9  # fallback
        timestamp = datetime.fromtimestamp(tx.get("timestamp", 0)).strftime('%d/%m %H:%M')
        direcao = "Compra" if token_amount > 0 else "Venda"

        valor_real = abs(token_amount)
        if valor_real < VALOR_MINIMO_USD:
            return None

        return f"💰{direcao} - {token_symbol}\nValor: ~${valor_real:.2f}\nHorário: {timestamp}"
    except Exception as e:
        print("❌ Erro interpretando transação:", e)
        return None

def monitorar():
    print("🔎 Checando transações...\n")
    url = f"https://api.helius.xyz/v0/addresses/{CARTEIRA}/transactions?api-key={HELIUS_API_KEY}&limit=100"
    try:
        r = requests.get(url)
        if not r.ok:
            print("Erro ao buscar transações:", r.text)
            return

        data = r.json()
        mensagens = []
        for tx in data[:5]:  # analisando 5 mais recentes
            msg = interpretar_transacao(tx)
            if msg:
                mensagens.append(msg)

        if mensagens:
            enviar_telegram("\n\n".join(mensagens))
        else:
            print("✅ Nenhuma transação relevante encontrada.\n")

    except Exception as e:
        print("❌ Erro geral:", e)

# === LOOP PRINCIPAL ===
while True:
    monitorar()
    time.sleep(INTERVALO_MINUTOS * 60)
