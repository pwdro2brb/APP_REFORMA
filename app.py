from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

# ---------------------------------------------------------
# 1. BANCO DE DADOS SIMULADO (Para testes iniciais)
# Em um projeto real, você usaria SQLAlchemy com SQLite ou PostgreSQL
# ---------------------------------------------------------
bd = {
    "usuarios": {
        1: {"nome": "Cliente João", "saldo": 2000.0, "tipo": "cliente"},
        2: {"nome": "Pedreiro Marcos", "saldo": 10.0, "tipo": "profissional"},
        # A conta "999" é a conta bancária do seu Super App (Conta Escrow)
        999: {"nome": "Conta Custódia do App", "saldo": 0.0, "tipo": "sistema"} 
    },
    "servicos": {},
    "contador_servicos": 1
}

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
    cliente = bd["usuarios"].get(dados.id_cliente)
    
    # Verifica se o cliente tem dinheiro para pagar antecipado
    if cliente["saldo"] < dados.valor_total:
        raise HTTPException(status_code=400, detail="Saldo insuficiente do cliente.")

    # LÓGICA DE CUSTÓDIA: Tira do cliente e joga para o App (dinheiro travado)
    cliente["saldo"] -= dados.valor_total
    bd["usuarios"][999]["saldo"] += dados.valor_total

    # Registra o serviço no banco
    id_servico = bd["contador_servicos"]
    bd["servicos"][id_servico] = {
        "id_cliente": dados.id_cliente,
        "id_profissional": dados.id_profissional,
        "valor_total": dados.valor_total,
        "status": "PENDENTE",
        "valor_ja_pago": 0.0
    }
    bd["contador_servicos"] += 1

    return {
        "mensagem": "Serviço criado com sucesso. Dinheiro em custódia!",
        "id_servico": id_servico,
        "saldo_cliente": cliente["saldo"],
        "saldo_app": bd["usuarios"][999]["saldo"]
    }

@app.post("/servico/{id_servico}/checkin")
def fazer_checkin(id_servico: int):
    servico = bd["servicos"].get(id_servico)
    
    if not servico:
        raise HTTPException(status_code=404, detail="Serviço não encontrado.")
    if servico["status"] != "PENDENTE":
        raise HTTPException(status_code=400, detail="Check-in já realizado ou serviço concluído.")

    # A Regra dos 25% (ou Teto Máximo de R$ 150)
    valor_total = servico["valor_total"]
    parcela_checkin = min(valor_total * 0.25, 150.0)

    # Transfere do App (Custódia) para o Profissional
    id_prof = servico["id_profissional"]
    bd["usuarios"][999]["saldo"] -= parcela_checkin
    bd["usuarios"][id_prof]["saldo"] += parcela_checkin

    # Atualiza o status da obra
    servico["status"] = "EM ANDAMENTO"
    servico["valor_ja_pago"] += parcela_checkin

    return {
        "mensagem": "Check-in aprovado! Primeira parcela liberada.",
        "valor_liberado": parcela_checkin,
        "novo_saldo_profissional": bd["usuarios"][id_prof]["saldo"],
        "status_obra": servico["status"]
    }