# 🔐 TGMSG - Exportador de Mensagens do Telegram

Um script Python que exporta mensagens de **grupos e canais** do Telegram para arquivos **TXT/CSV** e envia automaticamente para suas **Mensagens Salvas**.

## ✨ Funcionalidades

- 📥 Exporta mensagens de grupos e canais do Telegram  
- 💾 Salva em formatos TXT e CSV  
- 📤 Envia automaticamente para suas Mensagens Salvas  
- 🎯 Interface amigável com menus interativos  
- ⚡ Barra de progresso durante a exportação  
- 🔐 Sistema de login seguro com suas credenciais  

## 📋 Pré-requisitos

- Dispositivo Android com Termux  
- Conta no Telegram  
- Conexão com internet  

## 🚀 Instalação e Uso (LEIA COM ATENÇÃO)

Siga estes passos para usar o TGMSG:

1. **Abra o Termux** no seu dispositivo Android  

2. **Atualize os pacotes** e instale o Python:  
```
pkg update
pkg install python
```
3. Instale as bibliotecas necessárias:


```
pkg install git
pip install telethon
```
4. Baixe o TGMSG:


```
git clone https://github.com/jonperr/tgmsg.git
cd tgmsg
```
5. Execute o script:


```
python tgmsg.py
```
6. Siga as instruções na tela para:

Obter suas credenciais API (instruções abaixo)

Fazer login na sua conta do Telegram

Inserir seu número no formato: +5511XXXXXXXXX (11 = seu DDD)

Selecionar o grupo/canal para exportar

Escolher as opções de exportação




## 🔑 Como obter API ID e API Hash

O TGMSG precisa destas credenciais para acessar a API do Telegram:

1. Acesse my.telegram.org


2. Faça login com seu número do Telegram


3. Vá em API Development Tools


4. Preencha o formulário para criar um novo aplicativo


5. Anote o API ID e API Hash gerados

— IA
