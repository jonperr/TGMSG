# 🔐 TGMSG - Exportador de Mensagens do Telegram

Um script Python que exporta mensagens de grupos e tópicos do Telegram para arquivos TXT/CSV e envia para suas Mensagens Salvas.

## ✨ Funcionalidades

- 📥 Exporta mensagens de grupos e tópicos do Telegram
- 💾 Salva em formatos TXT e CSV
- 📤 Envia automaticamente para suas Mensagens Salvas
- 🎯 Interface amigável com menus interativos
- ⚡ Barra de progresso durante a exportação
- 🔐 Sistema de login seguro com suas credenciais

## 📋 Pré-requisitos

- Dispositivo Android com Termux.
- Conta no Telegram
- Conexão com internet

## 🚀 Instalação e Uso, LEIA COM ATENÇÃO!

Siga estes passos para usar o TGMSG:

1. **Abra o Termux** no seu dispositivo Android

2. **Atualize os pacotes** e instale o Python:
```bash
pkg update
pkg install python
```

1. Instale a biblioteca necessária:

```bash
pip install telethon
pkg install git
```

1. Baixe o TGMSG:

```bash
git clone https://github.com/jonperr/tgmsg.git
cd tgmsg
```

1. Execute o script:

```bash
python tgmsg.py
```

1. Siga as instruções na tela para:
· Obter suas credenciais API (veja instruções abaixo)
· Fazer login na sua conta Telegram
· Formato do número precisa ser: +5511XXXXXXXXX (11 sendo seu ddd)
· Selecionar o grupo para exportar
· Escolher as opções de exportação

🔑 Como obter API ID e API Hash

O TGMSG precisa destas credenciais para acessar a API do Telegram:

1. Acesse https://my.telegram.org
2. Faça login com seu número do Telegram
3. Vá em "API Development Tools"
4. Preencha o formulário para criar um novo aplicativo
5. Anote o "API ID" e "API Hash" gerados

🆘 Troubleshooting

Erro de permissão

Se aparecer "Permission denied", execute:

```bash
chmod +x tgmsg.py
```

Erro de dependências

Se houver problemas com o Telethon, reinstale:

```bash
pip uninstall telethon
pip install telethon
```

Não consegue acessar o grupo

· Verifique se você é membro do grupo
· Certifique-se de que o link está correto


- IA
