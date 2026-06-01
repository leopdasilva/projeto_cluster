from pymongo import MongoClient
from datetime import datetime
import random
import time

# --- CONFIGURAÇÃO DO REPLICA SET ---
# IPs comentados dos parceiros (mantenham aqui para o Dia do Desafio se precisarem)
# IP_BANCO = "10.68.20.25" 
# IP_BANCO = "10.69.20.160" 
IP_BANCO = "192.168.100.80"

PORTA_LIDER = "27017"
PORTA_RESERVA = "27018"
NOME_REPLICA_SET = "rs_escribas"  # Deve ser o mesmo nome configurado no rs.initiate()

# Nova string de conexão apontando para os dois caminhos possíveis
URI_CONEXAO = f"mongodb://{IP_BANCO}:{PORTA_LIDER},{IP_BANCO}:{PORTA_RESERVA}/?replicaSet={NOME_REPLICA_SET}"

print("🍕 Conectando ao cluster de Escribas (Modo Resiliência)...")

# Inicializa o cliente fora do loop. O PyMongo gerencia o cluster sozinho.
# serverSelectionTimeoutMS=5000 garante que ele não trave infinito se o banco sumir.
client = MongoClient(URI_CONEXAO, serverSelectionTimeoutMS=5000)

# banco e coleção
db = client["delivery"]
colecao = db["pedidos"]

# tabela de pizzas e preços fixos
pizzas = {
    "Calabresa": 45.90,
    "Frango": 52.00,
    "Portuguesa": 49.90,
    "4 Queijos": 58.50,
    "Chocolate": 39.90
}

# lista de clientes
clientes = [
    "João", "Maria", "Carlos", "Ana", "Pedro",
    "Fernanda", "Lucas", "Juliana", "Rafael", "Camila"
]

print("🚀 Sistema pronto. Enviando pedidos... derrube o Líder quando quiser!")
print("-" * 40)

while True:
    try:
        # escolhe cliente aleatório
        cliente = random.choice(clientes)

        # escolhe pizza aleatória
        sabor = random.choice(list(pizzas.keys()))

        # pega preço fixo da pizza
        preco = pizzas[sabor]

        # cria documento JSON
        pedido = {
            "cliente": cliente,
            "pizza": sabor,
            "valor": preco,
            "timestamp": datetime.now().isoformat()
        }

        # envia para MongoDB (Se o líder cair, o PyMongo joga o erro pro 'except' ou redireciona)
        colecao.insert_one(pedido)

        # mostra no terminal
        print("✅ Pedido enviado com sucesso:")
        print(pedido)
        print("-" * 40)

        # espera 2 segundos antes do próximo envio
        time.sleep(2)

    except Exception as erro:
        # Se o Líder desmaiar, o erro é pego aqui, o script NÃO morre e tenta de novo no reserva!
        print("\n🚨 ALERTA DE INSTABILIDADE: O Escriba Líder caiu ou está inacessível!")
        print(f"Detalhe do erro: {erro}")
        print("Aguardando eleição do Escriba Reserva... Tentando novamente em 5 segundos.\n")
        print("-" * 40)
        time.sleep(5)