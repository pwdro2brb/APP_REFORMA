from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import json
import os

app = FastAPI()


# ---------------------------------------------------------
# 1. BANCO DE DADOS SIMULADO (Para testes iniciais)
# Em um projeto real, você usaria SQLAlchemy com SQLite ou PostgreSQL
# ---------------------------------------------------------
# Função para carregar o banco de dados do arquivo JSON
def carregar_banco():
    if os.path.exists("banco_mock.json"):
        with open("banco_mock.json", "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        # Se o arquivo não existir, retorna um banco vazio como emergência
        return {"usuarios": {}, "servicos": {}, "contador_servicos": 1}

# Agora a variável bd recebe os 70 usuários que você acabou de gerar!
bd = carregar_banco()
# ---------------------------------------------------------
# 2. MODELOS DE DADOS (O que a API espera receber)
# ---------------------------------------------------------
class NovoServico(BaseModel):
    id_cliente: int
    id_profissional: int
    valor_total: float

# ---------------------------------------------------------
# 3. ROTAS DA API (A Lógica de Negócio)
# ---------------------------------------------------------

@app.post("/servico/criar")
def criar_servico(dados: NovoServico):
    # Converte o ID para texto (string) para buscar no JSON
    id_cliente_str = str(dados.id_cliente)
    cliente = bd["usuarios"].get(id_cliente_str)
    
    # Trava de Segurança 1: E se o cliente não existir?
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado no banco de dados.")

    # Trava de Segurança 2: E se o saldo for menor?
    if cliente["saldo"] < dados.valor_total:
        raise HTTPException(status_code=400, detail="Saldo insuficiente do cliente.")

    # Lógica de Custódia (O 999 também vira string "999")
    cliente["saldo"] -= dados.valor_total
    bd["usuarios"]["999"]["saldo"] += dados.valor_total

    # Registra o serviço no banco (Convertendo ID do serviço para string)
    id_servico_str = str(bd["contador_servicos"])
    bd["servicos"][id_servico_str] = {
        "id_cliente": dados.id_cliente,
        "id_profissional": dados.id_profissional,
        "valor_total": dados.valor_total,
        "status": "PENDENTE",
        "valor_ja_pago": 0.0
    }
    bd["contador_servicos"] += 1

    return {
        "mensagem": "Serviço criado com sucesso. Dinheiro em custódia!",
        "id_servico": id_servico_str,
        "saldo_cliente": cliente["saldo"],
        "saldo_app": bd["usuarios"]["999"]["saldo"]
    }

@app.post("/servico/{id_servico}/checkin")
def fazer_checkin(id_servico: int):
    # Converte ID do serviço para string
    id_servico_str = str(id_servico)
    servico = bd["servicos"].get(id_servico_str)
    
    # Trava de segurança
    if not servico:
        raise HTTPException(status_code=404, detail="Serviço não encontrado.")
    if servico["status"] != "PENDENTE":
        raise HTTPException(status_code=400, detail="Check-in já realizado ou serviço concluído.")

    valor_total = servico["valor_total"]
    parcela_checkin = min(valor_total * 0.25, 150.0)

    # Converte ID do profissional para string
    id_prof_str = str(servico["id_profissional"])
    
    # Transfere do App para o Profissional
    bd["usuarios"]["999"]["saldo"] -= parcela_checkin
    bd["usuarios"][id_prof_str]["saldo"] += parcela_checkin

    servico["status"] = "EM ANDAMENTO"
    servico["valor_ja_pago"] += parcela_checkin

    return {
        "mensagem": "Check-in aprovado! Primeira parcela liberada.",
        "valor_liberado": parcela_checkin,
        "novo_saldo_profissional": bd["usuarios"][id_prof_str]["saldo"],
        "status_obra": servico["status"]
    }