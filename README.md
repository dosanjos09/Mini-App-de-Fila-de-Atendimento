# Mini App – Fila de Atendimento

Aplicação web desenvolvida com **Python, Flask e SQLite** para gerenciamento de uma fila de atendimento.

## Funcionalidades

### Requisitos principais
- Cadastro de clientes na fila;
- Visualização da fila de espera;
- Chamada do próximo cliente;
- Ordem de atendimento;
- Alteração de status:
  - Aguardando
  - Em Atendimento
  - Concluído
- Cancelamento de atendimento;
- Banco de dados SQLite.

### Bônus implementados
- Prioridade **Normal / Preferencial**;
- Histórico dos últimos atendimentos;
- Atualização automática da página a cada 10 segundos;
- Dashboard com contadores de clientes;
- Interface responsiva.

## Tecnologias

- Python 3
- Flask
- SQLite
- HTML5
- CSS3
- JavaScript

## Como executar

### 1. Instalar o Python

Tenha o Python 3 instalado na máquina.

### 2. Criar um ambiente virtual

No terminal, dentro da pasta do projeto:

```bash
python -m venv venv
```

No Windows:

```bash
venv\Scripts\activate
```

No Linux/macOS:

```bash
source venv/bin/activate
```

### 3. Instalar as dependências

```bash
pip install -r requirements.txt
```

### 4. Executar

```bash
python app.py
```

O terminal mostrará um endereço parecido com:

```text
http://127.0.0.1:5000
```

Abra esse endereço no navegador.

## Banco de dados

O arquivo `fila.db` é criado automaticamente na primeira execução.

A tabela principal é `atendimentos` e armazena:
- ID;
- nome;
- prioridade;
- status;
- horário de entrada;
- horário da chamada;
- horário de finalização.

## Regra da fila

O sistema utiliza FIFO (**First In, First Out**).

Para o bônus de prioridade, clientes **Preferenciais** são chamados antes dos clientes **Normais**. Dentro de cada grupo, a ordem de chegada é preservada.

## Estrutura

```text
mini_app_fila_atendimento/
├── app.py
├── requirements.txt
├── README.md
├── templates/
│   └── index.html
└── static/
    └── style.css
```

O arquivo `fila.db` será criado automaticamente após iniciar o sistema.

## GitHub

Para entregar:

```bash
git init
git add .
git commit -m "feat: mini app de fila de atendimento"
git branch -M main
git remote add origin SEU_LINK_DO_GITHUB
git push -u origin main
```

Depois, basta enviar o link do repositório por e-mail.

## Observação

Este projeto foi pensado como um mini projeto acadêmico, com uma estrutura simples e fácil de apresentar e explicar.
