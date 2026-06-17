import json
import random

# Listas de apoio para gerar nomes aleatórios
nomes = ["Ana", "Carlos", "Beatriz", "João", "Mariana", "Pedro", "Lucas", "Julia", "Roberto", "Fernanda"]
sobrenomes = ["Silva", "Santos", "Oliveira", "Souza", "Rodrigues", "Ferreira", "Alves", "Lima", "Gomes", "Costa"]

def gerar_banco_dados():
    # Estrutura base do nosso banco
    bd = {
        "usuarios": {
            # A conta 999 é a conta mestre do aplicativo (Custódia Escrow)
            "999": {"nome": "Conta Custódia App", "saldo": 0.0, "tipo": "sistema", "nivel": 0}
        },
        "servicos": {},
        "contador_servicos": 1
    }

    print("⏳ Iniciando a geração de dados...")

    # 1. Gerar 50 Clientes (IDs de 1 a 50)
    for i in range(1, 51):
        id_str = str(i)
        bd["usuarios"][id_str] = {
            "nome": f"{random.choice(nomes)} {random.choice(sobrenomes)}",
            "saldo": round(random.uniform(1000.0, 5000.0), 2), # Saldo entre R$ 1.000 e R$ 5.000
            "tipo": "cliente",
            "nivel": 0
        }

    # 2. Gerar 20 Pedreiros/Profissionais (IDs de 51 a 70)
    for i in range(51, 71):
        id_str = str(i)
        nivel_sorteado = random.choice([1, 2, 3]) # Distribui nos Níveis 1, 2 e 3
        
        bd["usuarios"][id_str] = {
            "nome": f"Profissional {random.choice(nomes)} {random.choice(sobrenomes)}",
            "saldo": round(random.uniform(0.0, 150.0), 2), # Saldo inicial baixo
            "tipo": "profissional",
            "nivel": nivel_sorteado
        }

    # 3. Salvar tudo em um arquivo físico JSON
    nome_arquivo = "banco_mock.json"
    with open(nome_arquivo, "w", encoding="utf-8") as arquivo_json:
        # indent=4 deixa o arquivo formatado e bonito para leitura humana
        json.dump(bd, arquivo_json, indent=4, ensure_ascii=False)

    print(f"✅ Sucesso! Arquivo '{nome_arquivo}' gerado com:")
    print("   - 1 Conta Custódia")
    print("   - 50 Clientes")
    print("   - 20 Profissionais (Níveis 1 a 3)")

if __name__ == "__main__":
    gerar_banco_dados()