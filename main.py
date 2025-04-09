import time
import requests
from datetime import datetime

# === CONFIGURAÇÕES ===
HELIUS_API_KEY = "SUA_API_KEY_AQUI"
TELEGRAM_TOKEN = "SEU_TOKEN_TELEGRAM_AQUI"
TELEGRAM_CHAT_ID = "SEU_CHAT_ID_AQUI"
VALOR_MINIMO_USD = 10
CARTEIRA = "DfMxre4cKmvogbLrPigxmibVTTQDuzjdXojWzjCXXhzj"
INTERVALO_MINUTOS = 15

def enviar_telegram(mensagem):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": mensagem}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print("Erro ao enviar mensagem:", e)

def interpretar_transacao(tx):
    token_transfers = tx.get("tokenTransfers", [])
    if not token_transfers:
        return None

    token = token_transfers[0]
    amount = float(token.get("tokenAmount", {}).get("usdValue", 0))
    if amount < VALOR_MINIMO_USD:
        return None

    direcao = "Compra" if amount > 0 else "Venda"
    symbol = token.get("tokenSymbol", "TOKEN")
    qtd = float(token.get("tokenAmount", {}).get("amount", 0))
    hora = datetime.fromtimestamp(tx.get("timestamp", 0)).strftime("%d/%m %H:%M")

    return f"💰{direcao}: {symbol}\nQuantidade: {qtd:.2f}\nValor: ${abs(amount):.2f}\nHorário: {hora}"

def monitorar():
    print("🔎 Checando transações...")
    url = f"https://api.helius.xyz/v0/addresses/{CARTEIRA}/transactions?api-key={HELIUS_API_KEY}&limit=100"
    r = requests.get(url)
    if not r.ok:
        print("Erro ao buscar transações:", r.text)
        return

    data = r.json()
    mensagens = []
    for tx in data[:5]:
        msg = interpretar_transacao(tx)
        if msg:
            mensagens.append(msg)

    if mensagens:
        for m in mensagens:
            enviar_telegram(m)
    else:
        print("✅ Nenhuma transação relevante encontrada.")

# === LOOP ===
while True:
    monitorar()
    time.sleep(INTERVALO_MINUTOS * 60)