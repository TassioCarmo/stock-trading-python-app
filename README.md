# Stock Data Pipeline 🚀

Um sistema profissional de pipeline de dados para coleta, processamento e armazenamento de informações financeiras em tempo real. Desenvolvido para demonstrar habilidades em engenharia de dados, APIs, e integração com cloud services.

## 🎯 Sobre o Projeto

Este projeto implementa um pipeline completo de dados financeiros que coleta informações de ações da Polygon API, oferecendo múltiplas opções de armazenamento e execução automatizada. Ideal para demonstração de habilidades em desenvolvimento backend e engenharia de dados.

## ✨ Destaques Técnicos

### 🏗️ Arquitetura e Design
- **Arquitetura modular** com separação de responsabilidades
- **Padrão de resiliência** com sistema de resume automático
- **Configuração externalizada** via environment variables
- **Logging detalhado** para monitoramento do pipeline

### 🔧 Habilidades Demonstradas
- **Integração com APIs REST** (Polygon.io) com rate limiting
- **Processamento de dados** com Pandas e manipulação de JSON
- **Banco de dados cloud** (Snowflake) com conexão otimizada
- **Agendamento de tarefas** com schedule e controle de execução
- **Gestão de dependências** e ambiente virtual Python
- **Tratamento de erros** e exceções robusto
- **Versionamento de dados** com timestamps e metadados

### 📊 Funcionalidades Avançadas
- **Resume inteligente** - Continua de interrupções sem perda de dados
- **Rate limiting adaptativo** - Respeita limites da API automaticamente
- **Múltiplos destinos** - CSV local ou Snowflake na nuvem
- **Backup progressivo** - Checkpoints a cada página de dados
- **Cleanup automático** - Gestão de arquivos temporários

## 🛠️ Stack Tecnológico

| Camada | Tecnologias |
|--------|-------------|
| **Linguagem** | Python 3.7+ |
| **APIs** | Polygon.io REST API |
| **Banco de Dados** | Snowflake (Cloud) |
| **Data Processing** | Pandas, JSON |
| **Scheduling** | schedule, time |
| **Environment** | python-dotenv, os |
| **HTTP Requests** | requests |

## 🚀 Começando

### Pré-requisitos
- Python 3.7 ou superior
- Chave de API gratuita do [Polygon.io](https://polygon.io/)
- (Opcional) Conta Snowflake para demonstração cloud

### Instalação Rápida

1. **Clone e prepare o ambiente**
```bash
git clone https://github.com/seu-usuario/stock-data-pipeline.git
cd stock-data-pipeline
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

2. **Instale as dependências**
```bash
pip install -r requirements.txt
```

3. **Configure as variáveis de ambiente**
```bash
cp .env.example .env
# Edite .env com suas chaves API
```

## ⚙️ Configuração

### Polygon API (Gratuita)
1. Registre-se em [polygon.io](https://polygon.io/)
2. Obtenha sua API key gratuita
3. Adicione ao `.env`:
```env
POLYGON_API_KEY=sua_chave_aqui
```

### Snowflake (Opcional - Demonstração Cloud)
```env
SNOWFLAKE_ACCOUNT=seu_account
SNOWFLAKE_USER=seu_usuario
SNOWFLAKE_PASSWORD=sua_senha
SNOWFLAKE_WAREHOUSE=COMPUTE_WH
SNOWFLAKE_DATABASE=STOCKS_DB
SNOWFLAKE_SCHEMA=PUBLIC
SNOWFLAKE_ROLE=ACCOUNTADMIN
```

## 💻 Uso

### Modo de Execução Única
```bash
# Para CSV local
python script-csv.py

# Para Snowflake (cloud)
python script-snowflake.py
```

### Modo Agendado (Production-like)
```bash
python scheduler.py
```

## 📈 Estrutura de Dados

### Schema dos Tickers
```python
COLUMNS = [
    "ticker",           # Símbolo (AAPL, TSLA)
    "name",             # Nome da empresa
    "market",           # Tipo de mercado
    "locale",           # Região geográfica
    "primary_exchange", # Bolsa principal
    "type",             # Tipo de segurança
    "active",           # Status ativo/inativo
    "currency_name",    # Moeda de negociação
    "cik",              # SEC identifier
    "composite_figi",   # FIGI global
    "share_class_figi", # FIGI da classe
    "last_updated_utc"  # Timestamp UTC
]
```

## 🏗️ Estrutura do Projeto

```
stock-data-pipeline/
├── scheduler.py              # 🕒 Agendador de execuções
├── script-csv.py             # 💾 Coleta para CSV local
├── script-snowflake.py       # ☁️  Coleta para Snowflake
├── requirements.txt          # 📦 Dependências
├── .env.example             # 🔐 Template variáveis ambiente
└── README.md               # 📚 Documentação
```

## 🔄 Fluxo de Dados

1. **Conexão API** → Autenticação e rate limiting
2. **Paginação** → Coleta incremental com resume
3. **Transformação** → Cleanup e padronização
4. **Persistência** → CSV ou Snowflake
5. **Logging** → Monitoramento e debug

## 🎯 Casos de Uso Demonstrados

### 💼 Para Entrevistas Técnicas
- **Engenharia de Dados**: Pipeline completo ETL/ELT
- **Backend Development**: Integração API + Database
- **DevOps**: Scheduling + Environment management
- **Data Engineering**: Cloud data warehousing

### 🏢 Aplicações Reais
- **Financial Analytics**: Base para análise de ações
- **Data Products**: Fonte para aplicações financeiras
- **ML Pipelines**: Dados para modelos preditivos
- **Reporting**: Dados para dashboards e relatórios

## 🔍 Exemplo de Código

### Sistema de Resume Inteligente
```python
def save_progress(next_url, tickers):
    """Salva progresso para resume em caso de falhas"""
    progress = {"next_url": next_url, "ticker_count": len(tickers)}
    with open("progress.json", 'w') as f:
        json.dump(progress, f)
    # Backup incremental dos dados
    if tickers:
        pd.DataFrame(tickers).to_csv("tickers_partial.csv", index=False)
```

### Conexão Cloud Optimizada
```python
def upload_to_snowflake(df):
    """Upload otimizado para Snowflake com gestão de recursos"""
    conn = snowflake.connector.connect(
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        # ... configurações
    )
    # Upload batch eficiente
    success, nchunks, nrows, _ = write_pandas(conn, df, "STOCK_TICKERS")
```

## 📊 Métricas do Sistema

- **≈8,000+ tickers** coletados por execução
- **≈2-3 horas** para coleta completa (rate limit)
- **100% resiliência** a interrupções
- **Dual storage** local e cloud

## 🚨 Solução de Problemas

### Erros Comuns
```bash
# Rate Limit Exceeded
"Waiting 12 seconds before next request..."

# API Key Inválida
"Verifique POLYGON_API_KEY no .env"

# Snowflake Connection
"Confirme variáveis de ambiente do Snowflake"
```

### Debug
```python
# Ative logging detalhado
import logging
logging.basicConfig(level=logging.DEBUG)
```



## 📄 Licença

Distribuído sob licença MIT. Veja `LICENSE` para mais informações.

## 👨💻 Autor

Tassio Carmo- [GitHub](https://github.com/TassioCarmo) - [LinkedIn](https://linkedin.com/in/tassioluiz)
