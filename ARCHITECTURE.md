A estrutura segue o padrão da **Arquitetura Hexagonal (Ports and Adapters)** com separação clara entre a lógica de negócio central (o "miolo" da aplicação) e as tecnologias externas como banco de dados, scrapers e interfaces de usuário (as "cascas" externas), através das camadas de responsabilidade do domínio (lógica central), aplicação (casos de uso específico), infraestrutura (código de implementação) e apresentação (camada de interface entre o mundo lógico do código e o mundo real do usuário). Essa organização maximiza isolamento, testabilidade, e troca de implementações sem comprometer a lógica.

---

> Imagine uma empresa à moda antiga, sem tecnologia nem código, chamada **FLY (Financial Yearly Ledge)**. Você a contratou para fornecer informações financeiras das companhias listadas na bolsa de valores B3. Essa empresa tem uma missão, uma função principal, que é organizar para você as informações financeiras das companhias listadas na bolsa de valores. Você é o usuário, e a empresa é o código estruturado.

# 1. Domain
É a camada central e estável do sistema. Define o que o sistema faz através das lógicas do negócio e das regras de negócio. Sabe quais tipos de informação são relevantes e de que forma estas informações podem ser capturadas, manipuladas ou guardadas. Utiliza contêiner de dados e portas de interface.

> O domínio é como o **dono da empresa**. Sabe o que precisa ser feito para o cliente, e como pode ser feito, embora pessoalmente não faça nada. Ele sabe com que tipo de informação deve trabalhar e quais os caminhos para pegar e levar essa informação da forma que o cliente precisa.

## 1.1. DTO
É um contêiner de dados, ou **DTO (Data Transfer Object)** que transporta dados entre objetos. O DTO carrega a informação.

> É como um **caderno organizado**, que organiza que tipo de informação deve ser registrada, e leva e traz essas informações de um lado para o outro.
>
> O dono da FLY possui alguns cadernos DTOs diferentes. Um DTO para os dados cadastrais das companhias, como nome, CNPJ, ticker de negociação e outras informações desse tipo. Outro DTO para controlar a sequência das publicações dos relatórios da bolsa de valores (número serial de documento, NSD). Também existe outro DTO para registrar o conteúdo das publicações dos demonstrativos financeiros das companhias (DFP, ITR), que contém dados como patrimônio, lucro líquido do trimestre e outras informações periódicas.

## 1.2. Portas e Interfaces
São contratos abstratos formais que o domínio usa para padronizar a comunicação com o mundo exterior ao código. `Source` para obter dados e `Repository` para salvar e recuperar dados. Elas definem de forma agnóstica o que precisa ser feito, sem definir de que forma será feito. Apenas definem assinaturas de métodos, sem lógica interna. O objetivo é impor de forma radical um desacoplamento entre a lógica do negócio e as dependências de tecnologia da infraestrutura.

> A **persistência** é como o **depósito** da empresa FLY, onde os arquivos ficam guardados de forma permanente e organizada. O `Repository` é como o **manual de regras do depósito**, que define as únicas operações permitidas no arquivo oficial.
>
> Da mesma forma, a **aquisição** é o **Departamento de Prospecção ou de Garimpo de Dados** da empresa. O `Source` é como o **manual de regras do Departamento de Garimpo**, que define as únicas operações permitidas para garimpar dados.
>
> A independência entre esses departamentos é fundamental. O garimpeiro (`Source`) nem sabe quem é o arquivista (`Repository`). Se trocar um garimpeiro que vai a pé por um que vai de ônibus, tudo mais na empresa continua funcionando. A tecnologia usada pelo garimpeiro muda, mas o manual (`Source`) permanece o mesmo.

# 2. Application
É a ponte entre o Domínio (as regras de negócio) e o mundo exterior, é a camada de coordenação da lógica de negócio. Traduz a intenção do domínio em ações concretas. Ela não contém a lógica de negócio central, mas orquestra os objetos do Domínio (interfaces e DTO) para executar tarefas específicas.

> Esta é a **área de gerentes** da FLY. Os gerentes recebem as ordens do dono, e coordenam os departamentos e especialistas para realizar um trabalho. Eles conhecem os manuais de regras (Portas) e sabem a quais funcionários devem delegar as tarefas do chefe.

## 2.1. Service e UseCase
O `Service` é uma fachada, uma camada de coordenação ampla. A principal função do `Service` é estar entre a apresentação (interface do usuário) e os `UseCases` (os especialistas da operação).

> Na FLY, o dono não fala diretamente com cada funcionário. Ele chama em sua sala o **Gerente da Área de Companhias** (`Service`) e faz o pedido.
>
> O Gerente, então, vai até a sala do **Especialista em Sincronização de Companhias** (`UseCase`), repassa a tarefa e entrega as ferramentas necessárias. Ele diz: “Recebemos um pedido para sincronizar. Use as regras de `SQLite` do Repositório e a B3 para a Prospecção. Agora, execute!”.
>
> E o Especialista da Área então vai:
> 1. Consultar as regras do arquivo (`Repository`) e pedir para o funcionário `SQLite` (`SQLiteRepository`) listar todas as companhias que já existem (`list_existing_codes`).
> 2. Consultar as regras da Prospecção (`Source`) e pedir para o garimpeiro da B3 (`B3Scraper`) buscar dados novos de companhias (`fetch_all`).
> 3. Comparar os dados recebidos para filtrar apenas os DTOs que ainda não existem.
> 4. Dizer ao funcionário `SQLite` (`SQLiteRepository`) para arquivar (`save_all`) apenas o que for novo.

# 3. Infraestrutura
É a camada externa e volátil do sistema, que fornece os adaptadores concretos para traduzir os contratos do domínio. Ela implementa interfaces como `Source` e `Repository` com os detalhes técnicos da tecnologia. É onde as coisas acontecem de fato, permitindo total desacoplamento e a troca da tecnologia sem prejuízo ao negócio.

> No FLY, é o **chão de fábrica da empresa**: os departamentos, funcionários e ferramentas que realizam o trabalho de verdade.

* **3.1. Adaptadores:** Classes concretas que conectam a aplicação a uma tecnologia externa, implementando uma interface. Na FLY, o `B3CompanyScraper` é um adaptador que implementa a interface `Source`.
* **3.2. Models ORM:** Classes que modelam como os dados são armazenados no repositório.
* **3.3. Drivers ORM:** Ferramentas técnicas de acesso ao banco. O SQLAlchemy é a ferramenta, e `sqlite3` é o driver.
* **3.4. Scrapers e Fetchers:** Classes que interagem com o mundo externo para buscar dados.
* **3.5. Parsers e Cleaners:** Classes que convertem e limpam dados brutos para o formato do DTO.
* **3.6. Helpers:** Classes reutilizáveis que auxiliam em tarefas repetitivas.
* **3.7. Config:** Classes que carregam informações de configuração do sistema.
* **3.8. Logging:** Classes que permitem o monitoramento e rastreabilidade da execução.

# 4. Presentation
É a camada mais externa que inicia todo o fluxo de trabalho. É responsável por receber o comando inicial do usuário, montar o quebra-cabeça (conectando a Infraestrutura com a Aplicação) e dar a partida. Os comandos podem chegar via CLI, API REST, gRPC, websocket, etc., e vão acionar o `Service` adequado.

> Na FLY, é o **"balcão de atendimento"**, onde você (o cliente) chega e faz o seu pedido. A recepção não executa a tarefa, apenas entende o pedido e o passa ao gerente certo (`Service`). Ao final, entrega o pedido pronto ao cliente, sem se preocupar com o que acontece no meio do caminho.