mtcli-risco

mtcli-risco é um plugin para o [mtcli](https://github.com/vfranca/mtcli) que adiciona controle de risco automático com base no lucro/prejuízo diário da conta no MetaTrader 5.

Recursos

- Bloqueio automático ao atingir limite de prejuízo
- Encerra todas as posições abertas
- Cancela ordens pendentes
- Armazena estado do risco por dia

Instalação

bash
poetry add mtcli-risco


Execução

bash
mtcli risco --limite -300


`🚫 Limite diário (-300) excedido. Encerrando posições e bloqueando novas ordens.`
