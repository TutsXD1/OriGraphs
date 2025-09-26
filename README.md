#  OriGraphs

![Status](https://img.shields.io/badge/status-protótipo%20funcional-green)
![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Streamlit](https://img.shields.io/badge/Feito%20com-Streamlit-red)

Uma aplicação web interativa para criar, visualizar e analisar as instruções de construção de origamis. O projeto modela cada origami como uma sequência de ações (uma "palavra") de uma biblioteca definida (um "alfabeto"), aplicando conceitos de Linguagens Formais e Autômatos (LFA) e Teorida de Grafos (TG) para comparar e entender suas estruturas.

A interface, construída com [Streamlit](https://streamlit.io/), permite que usuários sem conhecimento de programação possam desenhar novos modelos e explorar as relações entre eles de forma visual e intuitiva.

## 📜 Tabela de Conteúdos
1. [Sobre o Projeto](#-sobre-o-projeto)
2. [✨ Funcionalidades](#-funcionalidades)
3. [🚀 Começando](#-começando)
    - [Pré-requisitos](#pré-requisitos)
    - [Instalação](#instalação)
    - [Execução](#execução)
4. [📂 Estrutura do Projeto](#-estrutura-do-projeto)
5. [💡 Conceitos-Chave](#-conceitos-chave)
6. [🛣️ Próximos Passos](#️-próximos-passos)

## 📖 Sobre o Projeto

A ideia central do OriGraphs é tratar a arte do origami como uma linguagem. Cada dobra, giro ou manipulação do papel é um "símbolo" em nosso alfabeto. Um origami completo, portanto, é uma "palavra" formada por uma sequência ordenada desses símbolos.

Este projeto implementa:
* Uma **biblioteca de ações** extensível que define o alfabeto de dobras possíveis.
* Uma **classe `Origami`** que representa uma palavra (a sequência de passos).
* Uma **interface web** construída com Streamlit que serve como um estúdio digital para:
    * Visualizar o grafo de ações de qualquer modelo.
    * Criar novos modelos passo a passo.
    * Analisar as relações entre modelos usando conceitos de LFA (prefixos, sufixos, subpalavras) e Teoria de Grafos.

## ✨ Funcionalidades

* **Visualização de Origamis:** Veja o grafo de ações e a lista de instruções de qualquer origami salvo.
* **Criação Interativa:** Crie seus próprios modelos de origami passo a passo através de uma interface gráfica amigável.
* **Análise Comparativa:** Compare dois origamis para descobrir se um é prefixo, sufixo, subpalavra ou subgrafo induzido do outro.
* **Biblioteca de Ações Extensível:** Adicione facilmente novas dobras e manipulações no arquivo `biblioteca_acoes.py` para expandir as capacidades do estúdio.
* **Estrutura Modular:** O código é organizado em arquivos distintos para lógica, biblioteca e interface, facilitando a manutenção e expansão.

## 🚀 Começando

Para executar este projeto em sua máquina local, siga os passos abaixo.

### Pré-requisitos

* Python 3.9 ou superior
* pip (gerenciador de pacotes do Python)

### Instalação

1.  **Clone o repositório** (ou baixe e descompacte os arquivos em uma pasta):
    ```bash
    git clone [https://github.com/TutsXD1/OriGraphs](https://github.com/TutsXD1/OriGraphs)
    cd OriGraphs
    ```

2.  **Crie um arquivo de dependências** chamado `requirements.txt` na pasta do projeto com o seguinte conteúdo:

    ```
    streamlit
    networkx
    matplotlib
    ```

3.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

### Execução

1.  Com o terminal aberto na pasta do projeto, execute o seguinte comando:
    ```bash
    streamlit run app.py
    ```
2.  Uma aba no seu navegador será aberta automaticamente com a aplicação em execução.

## 📂 Estrutura do Projeto

O projeto é dividido em três arquivos principais para garantir a organização e modularidade:

```
OriGraphs/
├── 📜 biblioteca_acoes.py   # Define a classe `Acao` e a biblioteca `BIBLIOTECA_DE_ACOES`. O "alfabeto".
├── ⚙️ classes_origami.py    # Define a classe `Origami`, sua lógica interna e os métodos de análise. A "gramática".
└── 🚀 app.py                # O ponto de entrada da aplicação Streamlit. Controla a interface do usuário.
└── 📄 requirements.txt      # Lista as dependências do projeto.
└── 📄 README.md             # Este arquivo.
```

## 💡 Conceitos-Chave

O projeto se baseia na analogia com **Linguagens Formais e Autômatos (LFA)**:
* **Alfabeto (`Σ`):** É a nossa `BIBLIOTECA_DE_ACOES`.
* **Palavra (`w`):** É o `caminho_de_acoes` de um objeto `Origami`.
* **Linguagem (`L`):** É o conjunto de todos os origamis válidos que podemos construir.
* Os métodos `is_prefixo`, `is_sufixo` e `is_subpalavra` são implementações diretas de operações sobre palavras.
