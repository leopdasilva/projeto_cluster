
# 🚀 MongoDB 8.0 Replica Set: Alta Disponibilidade e Tolerância a Falhas

Este projeto apresenta a implementação prática, configuração e validação de um ambiente de banco de dados NoSQL resiliente utilizando o **MongoDB 8.0** em modo **Replica Set (Cluster)**. O objetivo principal é garantir alta disponibilidade através de um mecanismo de *failover* automático, mantendo uma aplicação cliente (Python) operacional e sem interrupções mesmo diante da queda simulada do nó principal.


## 🏗️ 1. Arquitetura do Cluster Local

A infraestrutura foi projetada para simular um ambiente distribuído na mesma máquina servidora, segmentando as funções do ecossistema em três nós independentes operando em portas lógicas distintas:

| Nó | Função | Porta | Diretório de Dados |
| :--- | :--- | :--- | :--- |
| **Nó Principal** (Primary) | Recebe todas as operações de escrita e leitura diretas da aplicação. | `27017` | `C:\data\db1` |
| **Nó Reserva** (Secondary) | Replica os dados em tempo real. Elegível para assumir a liderança em caso de queda. | `27018` | `C:\data\db2` |
| **Nó Árbitro** (Arbiter) | Não armazena dados. Responsável apenas por desempatar a votação de quórum. | `27019` | `C:\data\arb` |

---

## 🛠️ 2. Passo a Passo da Configuração (Infraestrutura)

> ⚠️ **ATENÇÃO CRÍTICA SOBRE OS ENDEREÇOS DE IP:**
> O endereço de IP `10.68.21.78` utilizado neste guia serve estritamente como exemplo de desenvolvimento. Para replicar os passos com sucesso, você **DEVE** descobrir o IP atual da sua própria máquina (executando `ipconfig` no prompt de comando do Windows) e substituir todas as menções pelo IP da sua própria rede local.

### Passo 1: Sanetização e Limpeza do Ambiente
1. Crie a estrutura de pastas vazias no disco local exatamente em: `C:\data\db1`, `C:\data\db2` e `C:\data\arb`.
2. Certifique-se de remover arquivos residuais de execuções anteriores para evitar travas de memória (*lock files*).
3. Abra o **Gerenciador de Tarefas do Windows** (`Ctrl + Shift + Esc`), acesse a aba **Serviços**, localize o serviço automático `MongoDB Server` e force a sua **Interrupção** para liberar a porta padrão `27017`.

### Passo 2: Inicialização dos Nós via Prompt de Comando (CMD)
Abra três janelas separadas do Prompt de Comando como **Administrador**. Execute um comando em cada terminal para iniciar os processos em segundo plano (substituindo `SEU_IP_AQUI` pelo seu IP numérico real):

* **Terminal 1 — Nó Principal:**
    ```cmd
    "C:\Program Files\MongoDB\Server\8.0\bin\mongod.exe" --port 27017 --dbpath "C:\data\db1" --replSet rs_escribas --bind_ip 127.0.0.1,SEU_IP_AQUI
    ```
* **Terminal 2 — Nó Reserva:**
    ```cmd
    "C:\Program Files\MongoDB\Server\8.0\bin\mongod.exe" --port 27018 --dbpath "C:\data\db2" --replSet rs_escribas --bind_ip 127.0.0.1,SEU_IP_AQUI
    ```
* **Terminal 3 — Nó Árbitro:**
    ```cmd
    "C:\Program Files\MongoDB\Server\8.0\bin\mongod.exe" --port 27019 --dbpath "C:\data\arb" --replSet rs_escribas --bind_ip 127.0.0.1,SEU_IP_AQUI
    ```

### Passo 3: Orquestração e Vinculação do Cluster (MONGOSH)
1. Abra o **MongoDB Compass**.
2. No campo de URI, estabeleça uma conexão direta apontando para o IP do seu nó principal:
   ```text
   mongodb://SEU_IP_AQUI:27017/?directConnection=true

    ```

3. Com a conexão estabelecida, expanda o terminal integrado **MONGOSH** (`>_ Open MongoDB shell`) localizado no rodapé da interface.
4. Execute o comando de inicialização em bloco para unificar os membros propostos:

```javascript
rs.initiate({
  _id: "rs_escribas",
  members: [
    { _id: 0, host: "SEU_IP_AQUI:27017" },
    { _id: 1, host: "SEU_IP_AQUI:27018" },
    { _id: 2, host: "SEU_IP_AQUI:27019", arbiterOnly: true }
  ]
})

```

*A saída bem-sucedida retornará a flag `{ ok: 1 }` e mudará o cabeçalho do prompt para o modo `[primary]`.*

---

## 🔍 3. Desafios Resolvidos (Troubleshooting)

Durante o ciclo de desenvolvimento da infraestrutura, foram mapeados e superados os seguintes gargalos de sistemas distribuídos baseados em evidências de logs de erro reais:

* **Incompatibilidade de Versão (`Ponto de entrada não encontrado`):** Ocorria ao tentar executar binários do MongoDB compilados para builds do Windows mais recentes (como a v8.3) em sistemas operacionais acadêmicos que não possuíam o suporte necessário. **Solução:** Downgrade e fixação do ambiente na versão nativa estável **MongoDB 8.0**.
* **Crash do Nó Árbitro (`exitCode:100`):** O processo da porta `27019` encerrava abruptamente ao herdar metadados conflitantes ou arquivos corrompidos de testes passados. **Solução:** Limpeza total e profunda de todos os arquivos remanescentes dentro da pasta `C:\data\arb`.
* **Falha no Consenso de Rede (`replSetInitiate quorum check failed`):** Os nós não conseguiam se comunicar na rede local quando configurados com mapeamentos de escuta genéricos (ex: `0.0.0.0`). **Solução:** Amarração explícita combinando o loopback (`127.0.0.1`) e o IP numérico físico no parâmetro `--bind_ip`.
* **Rejeição de Identidade de Host (`InvalidReplicaSetConfig`):** Ocorria quando a inicialização do cluster era solicitada via Compass usando apelidos de conexão (como `localhost` ou nomes textuais customizados) que divergiam dos endereços numéricos configurados. **Solução:** Padronização absoluta da string de conexão utilizando estritamente o IP de rede ativo.
* **Conexão Recusada por Agentes Externos (`ECONNREFUSED` / Timeout):** Computadores clientes na rede local ficavam impedidos de enviar informações para o servidor. **Solução:** Configuração correta de múltiplas interfaces no bind e **desativação temporária do Firewall do Windows Defender** na máquina hospedeira para liberar o tráfego de entrada das portas utilizadas.

---

## 🎯 4. Validação do Failover (Teste Prático)

Para comprovar a resiliência e a tempo de resposta da arquitetura criada, o seguinte cenário de teste pode ser executado:

1. A aplicação cliente (Python) é configurada para se comunicar com o cluster passando os nós de dados disponíveis na string de conexão:
```python
mongodb://SEU_IP_DO_SERVIDOR:27017,SEU_IP_DO_SERVIDOR:27018/?replicaSet=rs_escribas

```


2. O script Python inicia o fluxo contínuo de envio e gravação de documentos no banco de dados.
3. A janela do CMD correspondente ao Nó Principal (`27017`) é **fechada manualmente**, simulando um cenário real de queda de hardware ou oscilação de energia.
4. **Comportamento Observado:** O Nó Árbitro (`27019`) detecta a ausência do líder instantaneamente e, em conjunto com o nó secundário, atinge o quórum necessário para promover o Nó Reserva (`27018`) ao papel de **Primary**.
5. O driver da aplicação Python intercepta a mudança de topologia de forma automatizada, impede o travamento (*crash*) do software e redireciona todo o tráfego de gravação diretamente para a nova porta líder (`27018`) em tempo real e sem perda de dados.

```

```
