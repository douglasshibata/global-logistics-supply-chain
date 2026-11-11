import os
import json
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent

# Conexão com o servidor local vLLM (API compatível com OpenAI)
llm = ChatOpenAI(
    model="meta-llama/Meta-Llama-3.1-8B-Instruct",
    base_url="http://localhost:8000/v1",
    api_key="EMPTY", # vLLM local não requer chave
    temperature=0.1
)

@tool
def verify_warehouse_capacity(warehouse_id: str) -> str:
    """Consulta a capacidade disponível de câmara fria em um hub logístico específico."""
    # Simulação de consulta via RPC/DB local
    capacities = {"HUB-SUL-01": 45, "HUB-SP-02": 0, "HUB-RJ-01": 12}
    cap = capacities.get(warehouse_id, -1)
    return json.dumps({"warehouse_id": warehouse_id, "available_pallets": cap})

@tool
def reroute_shipment(container_id: str, target_hub: str) -> str:
    """Executa a alteração de rota do contêiner para o novo hub logístico."""
    return json.dumps({"status": "SUCCESS", "container_id": container_id, "new_destination": target_hub})

# Lista de ferramentas disponíveis para o agente
tools = [verify_warehouse_capacity, reroute_shipment]

system_prompt = """Você é o Agente Autônomo de Resposta a Emergências Logísticas.
Sua missão é resolver violações de temperatura de cargas sensíveis.
Ao receber um alerta:
1. Verifique a capacidade dos hubs mais próximos.
2. Selecione um hub com capacidade disponível (available_pallets > 0).
3. Execute o redirecionamento da carga.
Responda sempre em português em formato estruturado."""

# Inicialização do Grafo de Agente ReAct
agent_executor = create_react_agent(llm, tools, state_modifier=system_prompt)

if __name__ == "__main__":
    alert_event = {
        "messages": [("user", "ALERTA CRÍTICO: Contêiner CONT-9988 com temperatura de -12C (limiar -15C). Posição próxima a HUB-SUL-01 e HUB-SP-02. Resolva imediatamente.")]
    }

    # Executado apenas para demonstração local em ambiente simulado
    print("Iniciando Agente Autônomo de Resposta a Emergências Logísticas...")
    # Em produção, o agente seria invocado pelo barramento de eventos ou orquestrador LangGraph.
    # Exemplo: response = agent_executor.invoke(alert_event)
