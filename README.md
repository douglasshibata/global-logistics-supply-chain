# Plataforma Global de Inteligência Logística e Supply Chain
## Arquitetura de Referência: Event-Driven Microservices & Air-Gapped AI Engine

Esta plataforma foi projetada sob uma arquitetura de microsserviços orientada a eventos (Event-Driven Microservices), operando em modo Offline-First na borda (Edge) e garantindo isolamento total de dados sensíveis (Air-Gapped AI Engine).

---

## 🗺️ 1. Diagrama de Arquitetura e Fluxo Fim a Fim

```text
+=======================================================================================================================+
| 1. EDGE LAYER (Veículos, Drones, Tablets, Sensores IoT)                                                              |
|   +---------------------------------------+   +------------------------------------+   +----------------------------+ |
|   | PouchDB (IndexedDB / Local Storage)   |   | Apache TVM Runtime (Edge AI / Vision)| | Sensores IoT (Temp/GPS/   | |
|   | - Registro local de telemetria/rotas  |   | - Análise de avaria via C++ Native | |   Abertura de Baú)         | |
|   +---------------------------------------+   +------------------------------------+   +----------------------------+ |
+===================================================|===================================================================+
                                                    | (HTTPS / gRPC / WebSockets quando online)
                                                    ▼
+=======================================================================================================================+
| 2. INGESTION & EVENT BACKBONE TIER                                                                                    |
|   +---------------------------------------------------------------------------------------------------------------+   |
|   | Apache RocketMQ 5.x Cluster (NameServer + Broker + DLedger Mode)                                              |   |
|   | - Tópico: `telemetry-stream` (Delay/FIFO)  |  Tópico: `audit-events` (Transactional Half-Messages)              |   |
|   +---------------------------------------------------------------------------------------------------------------+   |
+===================================================|===================================================================+
                                                    |
                                                    ▼
+=======================================================================================================================+
| 3. REAL-TIME ANALYTICS & COMPLEX EVENT PROCESSING (CEP)                                                               |
|   +---------------------------------------------------------------------------------------------------------------+   |
|   | Apache Flink 1.19+ (RocksDB StateBackend + Two-Phase Commit Sinks)                                           |   |
|   | - Geofencing violations | Temperature Threshold Alert (Sliding Window) | SLA ETA Breach Predictor                |   |
|   +---------------------------------------------------------------------------------------------------------------+   |
+===================================================|===================================================================+
                                                    | (Event Trigger)
                                                    ▼
+=======================================================================================================================+
| 4. LOCAL PRIVATE AI & AGENTIC WORKFLOW ENGINE                                                                         |
|   +------------------------------------------+   +------------------------------------+   +-------------------------+ |
|   | Agent Starter Kit (LangGraph Orchestration)|  | vLLM / Ollama (Local LLM Server)   |   | Qdrant Vector DB        | |
|   | - Autonomous Freight Resolution Agent    |   | - Llama 3.1 8B / Qwen 2.5 Coder    |   | - Embeddings de Notas/  | |
|   | - Discrepancy & Bill of Lading Auditor   |   | - PagedAttention / OpenAI API compat| |   CT-e RAG              | |
|   +------------------------------------------+   +------------------------------------+   +-------------------------+ |
+===================================================|===================================================================+
                                                    | (Internal RPC: bRPC / Triple Protocol)
                                                    ▼
+=======================================================================================================================+
| 5. PERSISTENCE, GOVERNANCE & SECURITY TIER                                                                            |
|   +-------------------------------------+  +-------------------------------------+  +-------------------------------+ |
|   | Apache ShardingSphere 5.x Proxy     |  | Apache CouchDB 3.x                  |  | Apache Casbin Engine          | |
|   | - PostgreSQL Sharded Nodes           |  | - Sync Gateway p/ PouchDB           |  | - ABAC/RBAC Multi-Tenant Auth | |
|   | - Transparent AES Column Encryption |  | - Data Replicas                     |  | - Dynamic PERM Models         | |
|   +-------------------------------------+  +-------------------------------------+  +-------------------------------+ |
+===================================================|===================================================================+
                                                    |
                                                    ▼
+=======================================================================================================================+
| 6. PRESENTATION & OBSERVABILITY TIER                                                                                  |
|   +--------------------------------------------------+   +--------------------------------------------------------+   |
|   | Apache ECharts (WebSockets Real-Time Dashboard)  |   | Apache SkyWalking 9.x+ (OAP + eBPF Agent Rastreio)     |   |
|   | - GeoJSON Map / Heatmaps / SLA Gauges            |   | - End-to-End Tracing & Distributed Latency Analysis    |   |
|   +--------------------------------------------------+   +--------------------------------------------------------+   |
+=======================================================================================================================+
```

---

## 📊 2. Tabela Mestra de Racionalização Arquitetural

| Componente | Tecnologia | Função no Ecossistema de Supply Chain | Protocolo / Formato | SLA / Performance Target |
|---|---|---|---|---|
| **Borda / Sensor** | PouchDB | Armazenamento temporário no tablet do veículo quando sem sinal. | JSON / IndexedDB | < 5 ms gravação local |
| **Borda / IA Visão** | Apache TVM | Execução de modelos de visão (ex: avaria de carga) em hardware embarcado. | C++ Compiled Native Library | < 15 ms por inferência |
| **Barramento** | Apache RocketMQ | Ingestão centralizada de telemetria IoT e mensagens transacionais. | gRPC / RocketMQ Protocol | > 100.000 msg/sec, latency < 10 ms |
| **Stream Analytics** | Apache Flink | Processamento contínuo para alertas de temperatura e violação de geofence. | Bytecode / Memory State | Processamento sub-segundo (< 500 ms) |
| **RPC / IPC** | Apache bRPC / Dubbo 3 | Comunicação interna de altíssima velocidade entre microsserviços. | Triple (gRPC + HTTP/2) | Sub-milissegundo (< 2 ms) |
| **Agentes de IA** | vLLM + Agent Starter Kit | Decisão autônoma para desvio de carga e auditoria de CT-e em ambiente fechado. | REST (OpenAI Spec) / JSON | > 80 tokens/sec local |
| **Persistência Sharded** | Apache ShardingSphere | Particionamento horizontal de histórico de rotas e transações fiscais. | SQL (Postgres Native) | I/O linear escalável |
| **Segurança** | Apache Casbin | Avaliação de permissões em tempo de execução (Ex: Fiscais vs Motoristas). | In-Memory Engine | < 1 ms por avaliação |
| **Observabilidade** | Apache SkyWalking | Rastreamento distribuído da telemetria desde o sensor até o banco. | OTLP / gRPC | Zero impacto de overhead (< 1%) |
| **Painel Operacional** | Apache ECharts | Visualização em tempo real da posição da frota e status dos contêineres. | WebSockets / JSON | Renderização a 60 FPS |

---

## 🎯 3. Caso de Uso Prático: "Gestão Inteligente de Cargas Críticas e Cadeia de Frio"

### Fluxo de Dados Fim a Fim
1. **Coleta e Borda (Edge):** O contêiner refrigera vacinas a -20°C. Sensores enviam temperatura e localização via Bluetooth LE para o tablet do motorista. O PouchDB grava localmente os dados. Se a carreta entra em uma zona sem sinal celular (ex: serra/floresta), os dados continuam acumulando localmente. Assim que a conexão é restabelecida, o PouchDB sincroniza com o Apache CouchDB e dispara streamings no Apache RocketMQ.
2. **Processamento em Tempo Real:** O Apache Flink consome as telemetrias do RocketMQ em janelas deslizantes (Sliding Windows de 5 minutos). Se a temperatura média ultrapassar -15°C, o Flink detecta a anomalia via CEP (Complex Event Processing) e emite um evento crítico no tópico `cold-chain-alerts`.
3. **Tomada de Decisão Autônoma via Agente de IA:** O evento aciona o Agent Starter Kit, que executa um modelo Llama 3.1 8B localmente via vLLM. O agente consulta o Qdrant para verificar a tolerância térmica daquela carga específica e faz uma chamada RPC via Dubbo 3/bRPC para consultar centros de distribuição próximos. O agente agenda autonomamente uma parada de emergência no hub mais próximo com câmara fria disponível.
4. **Governança e Exibição:** O Apache Casbin intercepta a requisição da nova rota criada pelo Agente, validando se a transportadora contratada possui certificação para operar aquele trecho. Uma vez autorizada, a nova rota e o status do contêiner atualizam dinamicamente a central logística via Apache ECharts renderizado na tela dos operadores.

---

## ⚙️ 4. Estrutura de Arquivos e Código do Projeto

```text
global-logistics-supply-chain/
├── docker-compose.yml              # Arquivo de orquestração do ecossistema de infraestrutura
├── README.md                       # Especificação técnica e arquitetura de referência (Este arquivo)
├── flink-pipeline/                 # Pipeline Java para Apache Flink
│   ├── pom.xml                     # Arquivo pom.xml do Maven contendo dependências
│   └── src/main/java/.../ColdChainAlertJob.java  # Monitor de temperatura em Flink
├── autonomous-agent/               # Agente ReAct inteligente com LangGraph e vLLM
│   ├── requirements.txt            # Dependências Python para execução do agente
│   └── logistics_agent.py          # Tomador de decisão autônomo baseado em IA
├── security-gateway/               # Middleware de segurança desenvolvido em Go
│   ├── go.mod                      # Módulo Go contendo referências do Casbin e Gin
│   ├── main.go                     # API REST com proteção ABAC/RBAC multi-tenant via Casbin
│   └── config/
│       ├── rbac_tenant_model.conf  # Modelo de autorização PERM do Casbin
│       └── policy.csv              # Políticas e relações de permissões declaradas
└── frontend-dashboard/             # Visualização da frota com Apache ECharts
    ├── package.json                # Dependências Node.js / React
    └── FleetMonitorDashboard.tsx   # Painel Web em tempo real consumindo WebSockets
```

---

## 🛡️ 5. Resiliência Logística e Trade-offs Técnicos

### Tratamento de Falhas de Conectividade Extrema (Desconexão Prolongada)
* **CouchDB/PouchDB Sync Protocol:** Quando navios ou caminhões ficam dias sem conexão, as alterações são salvas na árvore de revisões local (`_rev`). Ao reconectar, o algoritmo de resolução de conflitos determinístico do CouchDB entra em ação. Se o mesmo documento foi editado na borda e na central, a aplicação executa um Merge Engine customizado preservando o histórico de telemetria de maior precisão temporal.
* **Dead Letter Queue (DLQ) no RocketMQ:** Mensagens de telemetria com formato corrompido ou falha de processamento no Flink são enviadas para o tópico `%DLQ%cold-chain-group`. Um job do Apache Airflow inspeciona essa fila periodicamente para reprocessamento ou descarte auditado.

### Consistência de Dados vs. Latência (CAP Theorem)

```text
                                 [ TEORAMA CAP NA LOGÍSTICA ]
                                              /\
                                             /  \
                                            /    \
                                           /  CP  \
                                          /--------\  <-- Apache ShardingSphere (XA / Strong Consistency)
                                         /   AP     \     (Transações Financeiras, Estoque e Pagamento de Frete)
                                        /------------\
                                       /--------------\ <-- CouchDB & RocketMQ (Eventual Consistency)
                                      ------------------   (Rastreamento GPS, Telemetria de Sensores)
```

* **Garantia CP (Consistency + Partition Tolerance):** Aplicada via Apache ShardingSphere usando transações distribuídas no protocolo XA / Two-Phase Commit (2PC). Utilizada estritamente para alteração de propriedade da carga, liquidação financeira de frete e baixa de estoque nos hubs.
* **Garantia AP (Availability + Partition Tolerance):** Aplicada via CouchDB e RocketMQ. Utilizada para emissão de posições de GPS e leituras de temperatura. Se um nó central falhar, os nós da borda continuam aceitando gravações locais e disponibilizando a consulta aos motoristas.
