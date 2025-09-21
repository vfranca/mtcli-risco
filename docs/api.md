API Interna

risco.py

- carregar_estado(arquivo): Carrega o estado do arquivo JSON
- salvar_estado(arquivo, data, bloqueado): Salva o estado atual
- risco_excedido(limite): Verifica se o lucro/prejuízo do dia já excedeu o limite
- calcular_lucro_total_dia(): Soma lucro realizado + posições abertas
- encerrar_todas_posicoes(): Encerra todas as posições abertas via MT5
- cancelar_todas_ordens(): Cancela todas as ordens pendentes

plugin.py

- CLI integrada ao mtcli
- Verifica e bloqueia ordens com base no risco
