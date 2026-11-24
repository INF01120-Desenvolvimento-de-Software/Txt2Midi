# Gerador Musical

Trabalho prático da disciplina INF01120 — Desenvolvimento de Software. A aplicação utiliza algumas bibliotecas da linguagem python para converter texto em um arquivo MIDI e possui um player para ouvir a música gerada.

## Integrantes

- João Walter Backes Nunes
- Guilherme Souza dos Santos
- Guilherme Bierhals Touchtenhagen

## Requisitos

- Python 3.12
- [pygame]
- [mido]
- [python-rtmidi]
- [tkinter]

## Executar

> Abra o terminal na pasta raiz do projeto.
> É necessário ter o Python 3.12 instalado.

### Windows (PowerShell)

1. Confira se o Python está instalado:

```powershell
python --version
```

2. Crie e ative o ambiente virtual:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

3. Instale as dependências:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

4. Execute:

```powershell
python main.py
```

### Linux (Ubuntu/Debian)

1. Confira se o Python está instalado e instale os pacotes complementares:

```bash
python3 --version
sudo apt update
sudo apt install -y python3-venv python3-pip python3-tk \
    build-essential pkg-config libasound2-dev libjack-dev
```

2. Crie e ative o ambiente virtual:

```bash
python3 -m venv venv
source venv/bin/activate
```

3. Instale as dependências:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

4. Execute:

```bash
python main.py
```

### Testes

Com o ambiente virtual ativo, na raiz do projeto:

```bash
python -m unittest discover
```

## Como usar

A aplicação é dividida em 3 telas:
Tela Inicial: Contém apenas o nome do projeto e o botão começar.

Tela de Edição: Tela onde é possível editar a entrada de texto e importar ou exportar arquivo txt, além de ser possível a modificação do valor de BPM através de um slider. Como solicitado nos requisitos, é possível importar um texto e editá-lo através da caixa de texto. A caixa de texto tem um limite de caracteres, textos maiores são cortados e isso é avisado ao usuário.

Tela de Player: Nesta tela é possível tocar o arquivo MIDI gerado a partir do texto, contendo 3 botões relacionados ao player, sendo eles o play(Toca música de onde parou), pause e reset(Toca a música do zero). Nesta tela também é possível exportar o MIDI para um local específico.

## Exemplo de texto

C:3EGEC:2a:3aa:1aaaaaC:3EGEC:2a:3a_C:3EGEC:2
[8]?C:3EGEC:2a:3aa:1aaaVC:3EGEC:2a:3a)C:3EGEC:2
[16]??C:3EGEC:2a:3aa:1aVVC:3EGEC:2a:3a^C:3EGEC:2
[24] ???C:3EGEC:2a:3aVVVC:3EGEC:2a:3a+C:3EGEC:2
