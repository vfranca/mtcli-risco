Como usar

Comando principal

bash
mtcli risco --limite -500


- --limite (ou -l): Define o limite de perda diária.
- Se o prejuízo total do dia (realizado + posições abertas) ultrapassar esse valor, o plugin:
  - Encerra todas as posições abertas
  - Cancela todas as ordens pendentes
  - Bloqueia novas ordens até o próximo dia

Estados

O estado é salvo em um arquivo JSON, por padrão em ~/.mtcli/risco.json.

Exemplo:

json
{
  "data": "2025-09-21",
  "bloqueado": true
}


---

Verificar lucro atual do dia (caso implementado)

bash
mtcli risco --lucro


(Saída esperada: Lucro do dia: R$ 243.20)

