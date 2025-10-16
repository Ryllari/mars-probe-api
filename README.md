# Mars Probe API

Uma API para controle de sondas enviadas em missão para Marte com o objetivo de explorar um planalto estranhamente retangular, desenvolvida em FastAPI, com PostgreSQL, totalmente containerizada com Docker Compose. 

A aplicação implementa endpoints para:
- Lançamento de sondas com configuração do tamanho da malha.
- Listagem de sondas cadastradas e suas posiçōes atuais.
- Movimentação de sondas a partir de comandos válidos.

Além disso, há tratamento de erros e validações, onde garante que comandos inválidos ou movimentos fora da malha não sejam aplicados.

> Nota: A descriçāo original dos requisitos desta aplicaçāo está disponível no arquivo [./CHALLENGE.md](./CHALLENGE.md).

## Tecnologias Utilizadas
- Python 3.12
- FastAPI 0.119.0
- PostgreSQL 16
- SQLAlchemy 2
- Alembic 1.17
- Poetry 2.2.1
- Docker 28.5.1
- Docker Compose 2.40
- Pytest 8.4.2

## Especificaçōes da API

A API expõe documentação interativa no Swagger (/docs) e suporta exemplos de request/response para facilitar integração.

### 1. Criar uma sonda

#### Endpoint: POST /probes
Lança uma sonda e define o tamanho da malha. A sonda sempre inicia na posição (0, 0).

Exemplo de requisição:
```
{
  "x": 5,
  "y": 5,
  "direction": "NORTH"
}
```

Exemplo de resposta (201 Created):
```
{
  "id": "abc12345-6789-0123-4567-abcdef012345",
  "x": 0,
  "y": 0,
  "direction": "NORTH"
}
```

#### Erros comuns:
- 400 Bad Request – Coordenadas negativas ou direção inválida.
- 422 Unprocessable Entity – Campos obrigatórios faltantes ou tipo inválido.

### 2. Mover sonda
#### Endpoint: PUT /probes/{id}/move
Move uma sonda existente seguindo uma sequência de comandos.

Parâmetros:

- **id** – UUID da sonda.

Exemplo de requisição:
```
{
  "commands": "LRMMR"
}
```

#### Comandos válidos:

- **M**: para mover a sonda 1 espaço na direção que ela está apontando
- **L**: para fazer a sonda rotacionar uma vez para a direção à esquerda (exemplo, se estiver olhando para o Norte, irá olhar para o Oeste), mas sem se mover de quadrante.
- **R**: para fazer a sonda rotacionar para a direção à direita (exemplo, se estiver olhando para o Leste, irá olhar para o Sul), mas sem se mover de quadrante.

Exemplo de resposta (200 OK):
```
{
  "id": "abc12345-6789-0123-4567-abcdef012345",
  "x": 1,
  "y": 2,
  "direction": "EAST"
}
```

#### Erros comuns:
- 400 Bad Request – ID inválido, sequência de comandos inválida, ou movimento fora do grid.
- 404 Not Found – Sonda não encontrada.
- 422 Unprocessable Entity – Body mal formado (ex.: commands não é uma string).


### 3. Listar sondas e suas posiçoes
#### Endpoint: GET /probes
Retorna o estado de todas as sondas enviadas.

Exemplo de resposta (200 OK):
```
{
  "probes": [
    {
      "id": "abc12345-6789-0123-4567-abcdef012345",
      "x": 0,
      "y": 0,
      "direction": "NORTH"
    },
    {
      "id": "def67890-1234-5678-9012-abcdef678901",
      "x": 1,
      "y": 1,
      "direction": "EAST"
    }
  ]
}
```

## Execuçāo do Projeto
Com Docker e Docker Compose devidamente instalados na sua máquina (recomendamos a versāo mencionada anteriormente neste documento), basta executar os seguintes comandos:

### Executando a Aplicaçāo
Construir e iniciar todos os containers necessários:
```
docker compose up --build
```

Ou, para rodar em background:
```
docker compose up --build -d
```

Isso iniciará os seguintes serviços:
- mars_probe_db: PostgreSQL 16
- mars_probe_app: Aplicação (porta 8000)
- tests: Testes do projeto

*Obs: As migraçōes necessárias para o banco de dados sāo executadas automaticamente ao subir o container.*

### Execuçāo dos testes
Para rodar toda a suíte de testes (Pytest):
```
docker compose run --rm tests
```

### Limpar containers e volumes
Para remover todos os containers, volumes e caches (reset completo):
```
docker compose down -v
```

## Testes

Os testes são escritos em Pytest e cobrem:
- Modelos e validações.
- Endpoints REST da API.
- Lógica do serviço de movimentação de sondas (ProbeService).
- Casos de erro e respostas HTTP esperadas.

O serviço test utiliza banco isolado para garantir consistência.

## Notas de Desenvolvimento
- A lógica de movimentação da sonda está isolada em `ProbeService`, permitindo testes unitários completos e fácil manutenção.
- Assume-se que a malha (size_x e size_y) e posição (x e y) devem ser sempre não negativas.
- Assume-se que a direção da sonda deve ser uma das válidas: ["NORTH", "EAST", "SOUTH", "WEST"].
- Sequências de comando inválidas ou vazias retornam 400 Bad Request e não alteram o estado da sonda.
- Neste projeto, **as variáveis de ambiente estão propositalmente hardcoded** apenas para facilitar a execução do teste técnico, mas **isso não é recomendado em projetos reais**.
