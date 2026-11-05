# Citizen Assist AI — Global Solution 2026.2 (DSA)

Sistema em **Python 3.8+** (somente biblioteca padrão) para cadastro, consulta, pesquisa,
ordenação e análise de serviços públicos ao cidadão.

## Integrantes
| Nome completo | RM |
|---|---|
| Eduardo Barcelos De Carvalho Braziliano | 573274 |
| Julia Johanson Peniche Dias Da Silva | 572220 |
| Lucas Bomfim Leite | 570420 |

Turma 1 CCPJ

## Como executar
```bash
python main.py                      # usa/gera dados_servicos.json (começa com 10 exemplos)
python main.py --sem-persistencia   # não grava arquivo (ideal para demonstração)
python main.py --vazio              # começa sem registros de exemplo
python main.py --arquivo meus.json  # usa outro arquivo de dados
```
(No Windows, se `python` não funcionar, use `py main.py`.)

## Como executar os testes
```bash
python -m unittest -v test_citizen_assist
```

## Demonstração automatizada (gera a mesma evidência anexada)
```bash
python main.py --sem-persistencia < demo_entrada.txt
```

## Arquivos
| Arquivo | Conteúdo |
|---|---|
| `main.py` | Menu interativo, leitura/validação de entradas |
| `modelo.py` | Registro `Servico`, categorias, exceções e validações |
| `lista_encadeada.py` | Classes `No` e `ListaEncadeada` (inserção, percurso, remoção, ordenação) |
| `algoritmos.py` | Busca sequencial e Merge Sort para listas encadeadas |
| `gerenciador.py` | Regras de negócio (CRUD, pesquisa, ordenação, análise, persistência JSON) |
| `dados_exemplo.py` | 10 registros fictícios para demonstração |
| `test_citizen_assist.py` | 40 testes automatizados |
| `evidencia_testes.txt` / `evidencia_demo.txt` | Saídas reais da execução dos testes e da demonstração |
