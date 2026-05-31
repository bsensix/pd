# Design: Adicao de SOI com Analise Historica na Pagina El Nino

## Contexto

A pagina `pages/el_nino.py` ja entrega monitoramento historico de ONI e anomalias de SST (GEE), com cards, graficos e texto interpretativo. A solicitacao aprovada e adicionar o Indice de Oscilacao Sul (SOI) usando dados da NOAA/NCEI, com analise historica, sem mudar o layout atual.

## Objetivo

- Adicionar carregamento e tratamento da serie historica de SOI.
- Exibir serie historica de SOI no mesmo padrao visual da pagina (Plotly + texto).
- Incluir leitura historica simples e objetiva do SOI atual versus historico.
- Preservar a estrutura e distribuicao atual da interface.

## Escopo Aprovado

No escopo:

- Coleta de dados SOI a partir de `https://www.ncei.noaa.gov/access/monitoring/enso/soi`.
- Novo bloco de analise historica SOI adicionado na pagina existente.
- Explicacao curta de interpretacao de sinal do SOI no contexto ENSO.

Fora de escopo:

- Refatoracao estrutural da pagina para novos modulos/arquivos.
- Redesenho visual, rearranjo de layout, novos componentes de navegacao.
- Mudancas profundas na logica atual de ONI e GEE.

## Abordagens Consideradas

1. Integracao direta no arquivo atual (recomendada)
   - Cria funcoes novas para SOI dentro de `pages/el_nino.py`.
   - Menor risco e maior aderencia ao pedido de nao alterar layout.

2. Refatoracao para modulo de utilitarios ENSO
   - Melhor manutencao futura, mas envolve mudanca estrutural desnecessaria para o objetivo atual.

3. Inclusao minima sem metricas historicas
   - Mais rapida, mas nao atende totalmente o pedido de analise historica.

Decisao: abordagem 1.

## Arquitetura Proposta

### 1) Entrada de dados SOI

- Nova funcao `carregar_soi()` com `@st.cache_data(ttl=3600)`.
- Busca HTTP com `requests`, parse com `BeautifulSoup` (seguindo padrao ja usado no ONI).
- Extrai registros em formato mensal: ano, mes e valor SOI.

### 2) Normalizacao

- Padronizar colunas para contrato interno:
  - `data` (`datetime` mensal)
  - `ano` (int)
  - `mes` (int)
  - `soi` (float)
- Ordenacao cronologica crescente.
- Tratamento de simbolos de sinal unicode (`−`, `–`) e faltantes.

### 3) Metricas de analise historica SOI

- Ultimo valor disponivel de SOI.
- Media historica completa da serie.
- Desvio padrao amostral.
- Percentil historico do valor mais recente.
- Z-score do valor mais recente.

Observacao de interpretacao:

- SOI mais negativo tende a reforcar condicoes de El Nino.
- SOI mais positivo tende a reforcar condicoes de La Nina.
- Texto sempre com linguagem observacional, sem previsao deterministica.

### 4) Visualizacao (sem alterar layout)

- Inserir um novo bloco SOI abaixo das secoes atuais, mantendo o fluxo visual existente.
- Grafico unico de serie historica SOI (linha + linha zero de referencia).
- Caption e texto curto de leitura historica com as metricas calculadas.

## Fluxo de Dados

1. Pagina carrega ONI e GEE (fluxo atual, sem mudanca).
2. Pagina chama `carregar_soi()`.
3. Se SOI valido:
   - calcula metricas historicas;
   - renderiza bloco de grafico + texto.
4. Se SOI indisponivel:
   - exibe aviso nao bloqueante;
   - restante da pagina permanece funcionando.

## Erros e Degradacao

- Falha de requisicao/parsing SOI: `st.warning` com mensagem clara.
- Serie vazia ou nao numerica: bloco SOI nao renderiza e fluxo principal segue.
- Sem impacto no comportamento de ONI/GEE.

## Testes e Verificacao

Validacoes minimas durante execucao:

- DataFrame SOI nao vazio apos parsing.
- `soi` numerico e ordenacao temporal correta.
- Ultima data e ultimo valor coerentes com a fonte.
- Renderizacao da pagina sem erro com e sem dados SOI.

## Criterios de Sucesso

- SOI carregado da fonte NOAA/NCEI e exibido na pagina.
- Analise historica do SOI aparece com metricas basicas (ultimo valor, percentil e z-score).
- Nenhuma alteracao de layout estrutural e nenhum bloqueio do fluxo atual em caso de falha SOI.
