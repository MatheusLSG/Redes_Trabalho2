# Jogo de tanque multiplayer online

## Descrição
O projeto consiste em um jogo de batalha de tanques topdown multijogador online com suporte a multiplas salas. 

## Tecnologias Utilizadas
- Linguagens usadas:
    - **python** 
- Bibliotecas utilizadas:
    - **pygame** (Interface e controle de fluxo de jogo)
    - **sockets** (Comunicação via rede)
    - **pickle** (Conversão de objetos em streams de dados)
    - **pandas** e **numpy** (Leitura de planilhas para geração do mapa)
## Como Executar
### Requisitos
Instalar as dependencias presentes no *requirements.txt*
### Instruções de Execução
Clone o repositório:

    git clone <https://github.com/MatheusLSG/Redes_Trabalho2.git>

Instale as dependências:

    pip install -r requirements.txt

Execute o servidor passando como argumento o endereço ipv4:
    
    python server.py "server_ip_addr"

Execute o cliente do mesmo modo:
    
    python client.py "server_ip_addr"
## Como Testar
Com o seu servidor rodando basta criar ao menos dois clientes para ambos se conectarem ao server e conseguirem jogar juntos.

>Comandos de movimentação:
- **W** 
    >Segue em frente 
- **S**    
    > Recua para trás
- **A**
    > Rotaciona no sentido antihorário 
- **D** 
    > Rotaciona no sentido horário
- **ESPAÇO** 
    > Dispara tiro      
## Funcionalidades Implementadas
-   Controles basicos estilo tanque de guerra
-   Colisoes simples usando vetores
-   Menus basicos de feedback dos estados do jogo
-   Conexão e troca de informações simples entre clientes via sockets
-   Suporte a multiplas salas
-   Suporte a até quatro jogadores por sala 
    >configuravel alterando a variávael ***PLAYERS_QTD*** no arquivo *globals.py*

## Possíveis Melhorias Futuras
-   Comunicação:
    -   Refatoração da logica de jogo para facilitar comunicação serial   
    -   Melhora na logica de comunicação server/client via sockets 
-   Qualidade de vida:
    -   Criação de uma lista de salas com número 
    variável de jogadores
    - Aprimoramentos da logica de colisão
-   Gampelay:
    - Desenvolvimento de um sistema de vida do tanque
    - Power-ups coletáveis aleatorios pelo mapa
    - Aumento do acervo de mapas 
    - Randomização de mapas
    - Blocos interágiveis: 
        -   Caixas quebráveis
        -   Espelhos que refletem balas
    - Modos de jogo variados:
        -  Capture a bandeira
        -  Mata-mata em equipe
    - Melhora na qualidade da arte em geral