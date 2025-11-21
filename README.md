# Projeto – Algoritmo Flood Fill Multi-Regiões

![Pré-visualização da animação](assets/demo.gif)

## Descrição do Projeto

O **Algoritmo Flood Fill Multi-Regiões** identifica e colore, de forma automática, todas as áreas navegáveis de um grid 2D, atribuindo uma cor distinta para cada componente conexa. A solução foi projetada para apoiar robôs autônomos durante o mapeamento inicial de um terreno desconhecido, respeitando obstáculos e regiões previamente demarcadas.

**Principais objetivos:**

1. Receber um grid `n x m` contendo células livres (`0`), obstáculos (`1`) e áreas já coloridas (`>=2`).
2. Iniciar o preenchimento a partir de uma célula informada, expandindo ortogonalmente por células navegáveis.
3. Localizar automaticamente as próximas regiões livres e repetir o processo até que não existam mais `0` no grid.

## Lógica do Algoritmo Implementado

Trecho central (arquivo `floodfill.py`):

```python
def flood_fill_all(grid, start):
	used_colors = {value for row in grid for value in row if value >= 2}
	next_candidate = 2

	def fill_and_count(coord):
		nonlocal next_candidate
		if grid[coord[0]][coord[1]] != 0:
			return 0
		color, next_candidate = reserve_color(used_colors, next_candidate)
		return paint_region(grid, coord, color)

	regions = 0
	if fill_and_count(start):
		regions += 1
	for i, row in enumerate(grid):
		for j, value in enumerate(row):
			if value == 0 and fill_and_count((i, j)):
				regions += 1
	return grid, regions
```

Linha a linha:

1. **Linhas 2-3**: Identificam cores já usadas para evitar colisões e definem o próximo candidato (mínimo 2).
2. **Linhas 5-12**: Definem `fill_and_count`, que só dispara uma pintura se a célula ainda for `0`. A função reserva uma cor livre e delega a pintura para `paint_region`, que faz a busca em largura.
3. **Linhas 14-15**: Pintam a região que contém o ponto inicial, caso ainda esteja livre.
4. **Linhas 16-19**: Fazem uma varredura completa em busca de novos zeros. Cada vez que `fill_and_count` retorna positivo, incrementamos o contador de regiões.
5. **Linha 20**: Retorna o grid atualizado e o número de regiões coloridas.

Esse fluxo combina a estratégia “preencha primeiro onde o robô está” com uma busca posterior por áreas ainda não exploradas, garantindo cobertura total do mapa.

### Visualização da Estrutura Hierárquica

```
Região inicial ──► BFS (fila) ──► marca vizinhos livres
						   │
						   └──► Obstáculos e cores ≥2 bloqueiam a propagação

Após BFS: scan linha/coluna ──► encontrou 0? ──► reserva nova cor ──► BFS novamente
```

Essa visão ilustra como a solução alterna entre **explorar** (BFS) e **varrer** (scan sequencial) até esgotar os espaços navegáveis.

## Estrutura do Repositório

- `floodfill.py`: implementação completa do algoritmo e CLI simples via entrada padrão.
- `examples/`: arquivos de teste prontos (por exemplo, `examples/basic.txt`).
- `assets/`: espaço reservado para diagramas ou imagens explicativas (adicione conforme necessário para relatórios).

## Como Executar o Projeto

### Pré-requisitos

- Python 3.10 ou superior.
- Nenhuma dependência externa.

### Passos para Execução

1. (Opcional) Criar ambiente virtual:

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Executar o programa principal com um arquivo de entrada:

```bash
python floodfill.py < examples/basic.txt
```

3. Saída típica:

```
2 2 1 3 3 3
2 1 1 3 1 3
2 2 1 3 1 3
1 1 1 1 1 1
4 4 1 5 5 5
#regioes=4
```

O grid colorido aparece em `stdout`, enquanto `#regioes=<valor>` é impresso em `stderr`.

## Interface Gráfica Interativa

Para observar o preenchimento acontecendo passo a passo e testar configurações aleatórias, utilize `visualizer.py`, que oferece:

- Geração automática de grids com controle de proporção de obstáculos (slider).
- Seleção dinâmica de linhas/colunas e velocidade de animação.
- Limite de 10x10 no modo gráfico (mantém as células legíveis e animação fluida).
- Escolha da célula inicial por clique (ou seleção aleatória automática).
- Visualização em tempo real das regiões sendo coloridas e contagem final de componentes.
- Painel dedicado exibindo as cores utilizadas em cada região durante a animação.

### Executando

```bash
python visualizer.py
```

Controles principais:

- **Novo grid**: respeita as dimensões/percentual configurados e escolhe uma célula inicial navegável.
- **Iniciar preenchimento**: dispara a animação do Flood Fill multi-regiões.
- **Clique no grid**: reposiciona o ponto inicial (apenas em células livres, antes de começar a animação).

Caso esteja em um ambiente headless, utilize apenas o modo CLI (`floodfill.py`).


