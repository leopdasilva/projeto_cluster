
PROJETO: MONGODB 8.0 REPLICA SET (ALTA DISPONIBILIDADE)

----------------------------------------------------------------------
1. RESUMO DO PROJETO

Este projeto apresenta a configuração e validação de um ambiente de 
banco de dados NoSQL resiliente utilizando o MongoDB 8.0 em modo 
Replica Set (Cluster). O objetivo principal é garantir a tolerância 
a falhas (failover automático) e permitir que uma aplicação externa 
(como um script Python) envie dados continuamente para o servidor 
sem interrupções, mesmo com a queda simulada do nó principal.


----------------------------------------------------------------------
2. ARQUITETURA DO CLUSTER LOCAL

O cluster é configurado na máquina servidora utilizando três nós 
independentes rodando em portas distintas:

* NÓ PRINCIPAL (Primary - Porta 27017):
  Responsável por receber todas as operações de escrita e leitura 
  diretas da aplicação.

* NÓ RESERVA (Secondary - Porta 27018):
  Replica os dados do Nó Principal em tempo real. Se o nó principal 
  ficar offline, este nó é elegível para se tornar o novo líder.

* NÓ ÁRBITRO (Arbiter - Porta 27019):
  Não armazena dados. A sua única função é desempatar a votação 
  interna (quórum) para eleger um novo líder rapidamente.


----------------------------------------------------------------------
3. PASSO A PASSO DA EXECUÇÃO (INFRAESTRUTURA)

⚠️ ATENÇÃO IMPORTANTE SOBRE OS ENDEREÇOS DE IP:
Nos comandos abaixo, o IP "10.68.21.78" foi utilizado como exemplo 
durante os testes de desenvolvimento. Quem estiver seguindo este 
passo a passo DEVE obrigatoriamente descobrir o IP da sua própria 
máquina atual (digitando "ipconfig" no terminal do Windows) e 
substituir o "10.68.21.78" pelo IP da sua própria rede local.

Passo 1: Limpeza dos Diretórios
Criar a estrutura limpa de pastas no disco local: C:\data\db1, 
C:\data\db2 e C:\data\arb. Os arquivos antigos devem ser removidos 
para evitar travas de memória. O serviço padrão do Windows (MongoDB 
Server) deve ser parado no Gerenciador de Tarefas antes de começar.

Passo 2: Inicialização dos Nós (CMD como Administrador)
Abrir três janelas de terminal separadas para rodar os nós, configurados 
para escutar tanto localmente (127.0.0.1) quanto no IP real da sua rede:

  CMD 1 (Porta 27017):
  "C:\Program Files\MongoDB\Server\8.0\bin\mongod.exe" --port 27017 --dbpath "C:\data\db1" --replSet rs_escribas --bind_ip 127.0.0.1,SEU_IP_AQUI

  CMD 2 (Porta 27018):
  "C:\Program Files\MongoDB\Server\8.0\bin\mongod.exe" --port 27018 --dbpath "C:\data\db2" --replSet rs_escribas --bind_ip 127.0.0.1,SEU_IP_AQUI

  CMD 3 (Porta 27019):
  "C:\Program Files\MongoDB\Server\8.0\bin\mongod.exe" --port 27019 --dbpath "C:\data\arb" --replSet rs_escribas --bind_ip 127.0.0.1,SEU_IP_AQUI

*(Lembre-se de substituir "SEU_IP_AQUI" pelo número do seu IP local).*

Passo 3: Ativação do Cluster (MONGOSH no Compass)
Conectar ao MongoDB Compass através do seu IP real (ex: SEU_IP_AQUI:27017) 
adicionando a flag "?directConnection=true" no campo de URI. 

Ex: mongodb://192.168.100.11:27018/?directConnection=true

No terminal MONGOSH (>_ Open MongoDb shell), rodar o comando de unificação:

  rs.initiate({
    _id: "rs_escribas",
    members: [
      { _id: 0, host: "SEU_IP_AQUI:27017" },
      { _id: 1, host: "SEU_IP_AQUI:27018" },
      { _id: 2, host: "SEU_IP_AQUI:27019", arbiterOnly: true }
    ]
  })

O comando retornará { ok: 1 }, ativando o Replica Set com sucesso.


----------------------------------------------------------------------
4. DESAFIOS RESOLVIDOS (TROUBLESHOOTING)

Durante as fases de testes, o projeto enfrentou e superou os 
seguintes erros de sistemas distribuídos:

* Incompatibilidade de Versão (Ponto de entrada não encontrado):
  A tentativa de rodar a versão 8.3 exigia recursos ausentes no 
  sistema operacional do laboratório. Resolvido com a fixação 
  estável na versão nativa 8.0 instalada na máquina.

* Queda do Árbitro (exitCode:100):
  O processo da porta 27019 fechava sozinho ao herdar metadados 
  corrompidos ou travas de testes anteriores. Resolvido limpando 
  completamente o conteúdo da pasta C:\data\arb.

* Erro de Quórum (replSetInitiate quorum check failed):
  Os nós não se comunicavam na rede usando o bind genérico (0.0.0.0). 
  Resolvido passando explicitamente o IP correto e o loopback de 
  forma combinada no comando de inicialização.

* Conexão Recusada Externa (ECONNREFUSED / Timeout):
  Outro computador da rede local não conseguia enviar dados para o 
  servidor. Resolvido mapeando o IP físico no bind e desativando o 
  Firewall do Windows Defender para liberar o tráfego das portas.


----------------------------------------------------------------------
5. VALIDAÇÃO DO FAILOVER (TESTE PRÁTICO)

1. A aplicação cliente (Python) deve ser configurada apontando para 
   o IP da máquina que está hospedando o banco de dados:
   mongodb://SEU_IP_DO_SERVIDOR:27017,SEU_IP_DO_SERVIDOR:27018/?replicaSet=rs_escribas

2. O script Python inicia o envio e a gravação de dados contínuos.

3. A janela do CMD correspondente ao Nó Principal (27017) é fechada 
   manualmente para simular uma queda inesperada de hardware.

4. O Nó Árbitro (27019) detecta a ausência do líder e promove o Nó 
   Reserva (27018) a novo líder (Primary).

5. O driver da aplicação Python gerencia a troca de nós em tempo 
   real, continuando a salvar os novos registros na porta 27018 
   de forma automatizada, sem interromper o sistema ou perder dados.

