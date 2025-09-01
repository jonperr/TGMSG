from telethon import TelegramClient
import re
import asyncio
import csv
import os
import sys
import json
import random
from datetime import datetime

# Configurações padrão
DEFAULT_CONFIG = {
    "max_messages": None,
    "request_delay": 2.0,
    "delay_variation": 0.5,
    "login_attempts": 0,
    "last_login_attempt": None
}

def clear_screen():
    """Limpa a tela do terminal"""
    os.system('cls' if os.name == 'nt' else 'clear')

def show_login_banner():
    """Exibe o banner de login"""
    print("")
    print("┌─────────────────────────────────────────────────────┐")
    print("│                  🔐 LOGIN TGMSG 🔐                  │")
    print("│        Por favor, faça login para continuar         │")
    print("└─────────────────────────────────────────────────────┘")
    print("")

def show_menu_banner():
    """Exibe o banner do menu principal"""
    print("")
    print("┌─────────────────────────────────────────────────────┐")
    print("│                   📋 MENU TGMSG 📋                  │")
    print("└─────────────────────────────────────────────────────┘")
    print("")

def show_config_banner():
    """Exibe o banner de configurações"""
    print("")
    print("┌─────────────────────────────────────────────────────┐")
    print("│                ⚙️ CONFIGURAÇÕES ⚙️                 │")
    print("└─────────────────────────────────────────────────────┘")
    print("")

def show_welcome_banner():
    """Exibe o banner do TGMSG"""
    print("")
    print("████████╗ ██████╗ ███╗   ███╗███████╗ ██████╗ ")
    print("╚══██╔══╝██╔════╝ ████╗ ████║██╔════╝██╔════╝ ")
    print("   ██║   ██║  ███╗██╔████╔██║███████╗██║  ███╗")
    print("   ██║   ██║   ██║██║╚██╔╝██║╚════██║██║   ██║")
    print("   ██║   ╚██████╔╝██║ ╚═╝ ██║███████║╚██████╔╝")
    print("   ╚═╝    ╚═════╝ ╚═╝     ╚═╝╚══════╝ ╚═════╝ ")
    print("")
    print("🤖 Exportador de Mensagens do Telegram")
    print("📥 Extrai mensagens de grupos e tópicos")
    print("💾 Salva em formato TXT e CSV")
    print("📤 Envia para suas Mensagens Salvas")
    print("🔐 Sistema anti-banimento incorporado")
    print("─" * 50)

def save_config(config):
    """Salva as configurações em arquivo JSON"""
    with open("tgmsg_config.json", "w") as f:
        json.dump(config, f)

def load_config():
    """Carrega as configurações do arquivo JSON"""
    try:
        with open("tgmsg_config.json", "r") as f:
            config = json.load(f)
            # Garante que todas as chaves padrão existam
            for key, value in DEFAULT_CONFIG.items():
                if key not in config:
                    config[key] = value
            return config
    except FileNotFoundError:
        return DEFAULT_CONFIG.copy()

def delete_session():
    """Remove a sessão salva"""
    try:
        session_files = ["user_session.session", "tgmsg_config.json"]
        for file in session_files:
            if os.path.exists(file):
                os.remove(file)
        return True
    except Exception as e:
        print(f"Erro ao apagar a sessão: {e}")
        return False

async def check_session_validity(client):
    """Verifica se a sessão é válida"""
    try:
        me = await client.get_me()
        return me is not None
    except Exception as e:
        print(f"Erro ao verificar validade da sessão: {e}")
        return False

def check_login_abuse(config):
    """Verifica se há abuso de tentativas de login"""
    now = datetime.now()
    if not config["last_login_attempt"]:
        config["last_login_attempt"] = now.isoformat()
        config["login_attempts"] = 1
        save_config(config)
        return False
    last_attempt = datetime.fromisoformat(config["last_login_attempt"])
    time_diff = (now - last_attempt).total_seconds() / 3600
    if time_diff > 24:
        config["login_attempts"] = 1
        config["last_login_attempt"] = now.isoformat()
        save_config(config)
        return False
    config["login_attempts"] += 1
    config["last_login_attempt"] = now.isoformat()
    save_config(config)
    if config["login_attempts"] >= 4:
        print("")
        print("⚠️  AVISO: Muitas tentativas de login em um curto período!")
        print("   O Telegram pode banir sua conta por excesso de tentativas.")
        print("   Recomendamos esperar pelo menos 24 horas antes de tentar novamente.")
        print("")
        continuar = input("   Deseja continuar mesmo assim? (s/n): ").strip().lower()
        if continuar != 's':
            return True
    return False

def sanitize_filename(name):
    """Remove caracteres inválidos do nome do arquivo"""
    return re.sub(r'[^\w\-_\. ]', '_', name)

async def setup_client():
    """Configura o cliente do Telegram com sessão persistente"""
    config = load_config()
    if check_login_abuse(config):
        print("👋 Operação cancelada para prevenir banimento.")
        return None
    if os.path.exists("user_session.session"):
        try:
            if "api_id" in config and "api_hash" in config:
                client = TelegramClient("user_session", config["api_id"], config["api_hash"])
                await client.start()
                if await check_session_validity(client):
                    me = await client.get_me()
                    clear_screen()
                    print("✅ Sessão restaurada com sucesso!")
                    print(f"👤 Conectado como: {me.first_name}")
                    if me.username:
                        print(f"📱 Usuário: @{me.username}")
                    await asyncio.sleep(2)
                    return client
        except Exception as e:
            print(f"❌ Erro ao restaurar sessão: {e}")
    clear_screen()
    show_login_banner()
    print("📝 Caso não saiba seu API ID e API Hash, consulte:")
    print("   https://core.telegram.org/api/obtaining_api_id")
    print("   Ou pesquise no Google: 'como obter api id telegram'")
    print("")
    while True:
        api_id = input("🔑 Digite seu API ID: ").strip()
        if api_id.lower() in ["menu", "voltar"]:
            return None
        try:
            api_id = int(api_id)
            break
        except ValueError:
            print("❌ Valor inválido. Digite um número.")
    api_hash = input("🔒 Digite seu API Hash: ").strip()
    config["api_id"] = api_id
    config["api_hash"] = api_hash
    save_config(config)
    client = TelegramClient("user_session", api_id, api_hash)
    await client.start()
    clear_screen()
    print("✅ Login realizado com sucesso!")
    me = await client.get_me()
    print(f"👤 Conectado como: {me.first_name}")
    if me.username:
        print(f"📱 Usuário: @{me.username}")
    print("🔄 Iniciando TGMSG...")
    await asyncio.sleep(3)
    return client

def print_progress(current, total, bar_length=10):
    """Exibe uma barra de progresso simplificada em uma única linha"""
    if total == 0:
        return
    percent = min(float(current) / total, 1.0)
    filled_length = int(round(bar_length * percent))
    arrow = '█' * filled_length
    spaces = '░' * (bar_length - filled_length)
    sys.stdout.write('\r\033[K')
    if current == total:
        progress_text = "✅ Completo!"
    else:
        progress_text = f"{current}/{total}"
    sys.stdout.write(f"📥 Progresso: [{arrow + spaces}] {percent*100:.1f}% ({progress_text})")
    sys.stdout.flush()

async def export_chat(client, config):
    """Menu de exportação de mensagens do grupo/tópico"""
    try:
        clear_screen()
        show_menu_banner()
        print("📤 Exportar Mensagens de Grupo")
        print("─" * 50)
        group_link = input("\n🔗 Cole o link ou @ do grupo: ").strip()
        if group_link.lower() in ['menu', 'voltar']:
            return None, None, None
        try:
            group_entity = await client.get_entity(group_link)
            print(f"✅ Conectado ao grupo: {group_entity.title}")
        except Exception as e:
            print(f"❌ Não foi possível acessar o grupo: {e}")
            print("📝 Verifique se:")
            print("   - O link está correto")
            print("   - Você é membro do grupo")
            print("   - O grupo não é restrito")
            return None, None, None
        has_topics = False
        topic_id = None
        try:
            full_chat = await client.get_entity(group_entity)
            if hasattr(full_chat, 'forum') and full_chat.forum:
                has_topics = True
                print("📌 Este grupo possui tópicos (fórum)")
        except Exception as e:
            has_topics_input = input("\n📝 Este grupo tem tópicos? (s/n): ").strip().lower()
            if has_topics_input in ['menu', 'voltar']:
                return None, None, None
            has_topics = has_topics_input == 's'
        if has_topics:
            export_topic = input("\n📝 Deseja exportar mensagens de um tópico específico? (s/n): ").strip().lower()
            if export_topic in ['menu', 'voltar']:
                return None, None, None
            if export_topic == 's':
                topic_link = input("🔗 Cole o link do tópico: ").strip()
                if topic_link.lower() in ['menu', 'voltar']:
                    return None, None, None
                topic_match = re.search(r"/(\d+)(?:\?|$)", topic_link)
                if topic_match:
                    topic_id = int(topic_match.group(1))
                    print(f"✅ ID do tópico detectado: {topic_id}")
                else:
                    print("❌ Não foi possível detectar o ID do tópico do link")
                    try:
                        topic_id_input = input("🔢 Digite o ID do tópico manualmente: ").strip()
                        if topic_id_input.lower() in ['menu', 'voltar']:
                            return None, None, None
                        topic_id = int(topic_id_input)
                    except Exception:
                        print("❌ ID inválido. Continuando com o grupo inteiro.")
                        topic_id = None
        limit = config["max_messages"]
        if not limit:
            try:
                limit_input = input("\n🔢 Quantidade máxima de mensagens a exportar (deixe em branco pra todas): ").strip()
                if limit_input.lower() in ['menu', 'voltar']:
                    return None, None, None
                limit = int(limit_input) if limit_input else None
            except ValueError:
                print("❌ Valor inválido. Usando todas as mensagens.")
                limit = None
        print(f"\n📋 Resumo:")
        print(f"   Grupo: {group_entity.title}")
        if topic_id:
            print(f"   Tópico: {topic_id}")
        else:
            print(f"   Tópico: Geral (todas as mensagens)")
        if limit:
            print(f"   Limite: {limit} mensagens")
        else:
            print(f"   Limite: Todas as mensagens")
        confirm = input("\n💾 Deseja continuar com a exportação? (s/n): ").strip().lower()
        if confirm in ['menu', 'voltar']:
            return None, None, None
        if confirm != 's':
            print("❌ Operação cancelada.")
            return None, None, None
        return group_entity, topic_id, limit
    except Exception as e:
        print(f"❌ Erro: {e}")
        return None, None, None

async def collect_messages(client, group_entity, topic_id, limit, config):
    """Coleta mensagens do grupo/tópico"""
    messages = []
    kwargs = {'reverse': True}
    if topic_id:
        kwargs['thread_id'] = topic_id
    if limit:
        kwargs['limit'] = limit
    try:
        print("📊 Estimando quantidade de mensagens...")
        total_estimate = limit if limit else 0
        if not limit:
            try:
                total_estimate = 0
                async for msg in client.iter_messages(group_entity, limit=100, **kwargs):
                    if not msg.message or hasattr(msg, 'action') and msg.action:
                        continue
                    total_estimate += 1
                if total_estimate < 100:
                    print(f"📊 Estimativa: {total_estimate} mensagens")
                else:
                    print("📊 Estimativa: Muitas mensagens (coletando todas)")
                    total_estimate = 10000
            except Exception:
                total_estimate = 1000
        current_count = 0
        last_update = 0
        async for msg in client.iter_messages(group_entity, **kwargs):
            if not msg.message or hasattr(msg, 'action') and msg.action:
                continue
            messages.append(msg)
            current_count += 1
            delay = max(0.1, random.uniform(
                config["request_delay"] - config["delay_variation"],
                config["request_delay"] + config["delay_variation"]
            ))
            await asyncio.sleep(delay)
            if limit:
                if current_count - last_update >= 10 or current_count == limit:
                    print_progress(current_count, limit)
                    last_update = current_count
            else:
                if total_estimate < 10000:
                    if current_count - last_update >= 10 or current_count == total_estimate:
                        print_progress(current_count, total_estimate)
                        last_update = current_count
                else:
                    if current_count - last_update >= 10:
                        sys.stdout.write('\r\033[K')
                        sys.stdout.write(f"📥 Mensagens coletadas: {current_count} (aguarde...)")
                        sys.stdout.flush()
                        last_update = current_count
            if limit and current_count >= limit:
                break
        sys.stdout.write('\r\033[K')
        print(f"✅ Coleta concluída: {len(messages)} mensagens")
    except Exception as e:
        print(f"❌ Erro ao coletar mensagens: {e}")
        return []
    return messages

async def save_and_send_files(client, group_entity, topic_id, messages):
    """Salva e envia os arquivos"""
    if not messages:
        print("❌ Nenhuma mensagem para salvar.")
        return False
    print(f"💾 Total de mensagens coletadas: {len(messages)}")
    group_name = sanitize_filename(group_entity.title)
    txt_filename = f"{group_name}_mensagens.txt"
    csv_filename = f"{group_name}_mensagens.csv"
    print("💾 Salvando em arquivos...")
    try:
        with open(txt_filename, "w", encoding="utf-8") as f:
            for m in messages:
                try:
                    user = await m.get_sender()
                    if user and user.username:
                        username = f"@{user.username[:5]}"
                    else:
                        username = "desconhecido"
                    data_formatada = m.date.strftime('(%Y/%m)')
                    f.write(f"{data_formatada} {username}: {m.text}\n")
                except Exception:
                    continue
        with open(csv_filename, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f, delimiter=";")
            writer.writerow(["data", "username", "mensagem"])
            for m in messages:
                try:
                    user = await m.get_sender()
                    if user and user.username:
                        username = user.username[:5]
                    else:
                        username = "desconhecido"
                    data_formatada = m.date.strftime('%Y/%m')
                    writer.writerow([
                        data_formatada,
                        username,
                        m.text.replace("\n", " ") if m.text else ""
                    ])
                except Exception:
                    continue
    except Exception as e:
        print(f"Erro ao salvar arquivos: {e}")
        return False
    txt_size = os.path.getsize(txt_filename) if os.path.exists(txt_filename) else 0
    csv_size = os.path.getsize(csv_filename) if os.path.exists(csv_filename) else 0
    print("📤 Enviando para suas Mensagens Salvas...")
    topic_name = f"Tópico {topic_id}" if topic_id else "Geral"
    success = False
    try:
        if txt_size > 0:
            await client.send_file("me", txt_filename, caption=f"📂 Backup de {group_entity.title} - {topic_name} (TXT)")
            print("✅ Arquivo TXT enviado")
            success = True
        else:
            print("❌ Arquivo TXT vazio")
        if csv_size > 0:
            await client.send_file("me", csv_filename, caption=f"📂 Backup de {group_entity.title} - {topic_name} (CSV)")
            print("✅ Arquivo CSV enviado")
            success = True
        else:
            print("❌ Arquivo CSV vazio")
        if os.path.exists(txt_filename):
            os.remove(txt_filename)
        if os.path.exists(csv_filename):
            os.remove(csv_filename)
    except Exception as e:
        print(f"Erro ao enviar arquivos: {e}")
        return False
    return success

async def config_menu(config):
    """Menu de configurações"""
    while True:
        clear_screen()
        show_config_banner()
        print("🔧 Configurações atuais:")
        print(f"   1. Limite máximo de mensagens: {config['max_messages'] or 'Todas'}")
        print(f"   2. Intervalo entre requisições: {config['request_delay']}s")
        print(f"   3. Variação do intervalo: ±{config['delay_variation']}s")
        print("")
        print("📝 Digite o número da opção para editar")
        print("↩️  Digite 'voltar' ou 'menu' para retornar ao menu principal")
        print("")
        option = input("💡 Escolha uma opção: ").strip().lower()
        if option in ['voltar', 'menu']:
            return config
        elif option == '1':
            clear_screen()
            show_config_banner()
            print("📊 Limite máximo de mensagens")
            print("💡 Deixe em branco para exportar todas as mensagens")
            print("")
            try:
                new_limit = input("🔢 Novo limite: ").strip()
                if new_limit == '':
                    config["max_messages"] = None
                    print("✅ Limite removido - serão exportadas todas as mensagens")
                else:
                    config["max_messages"] = int(new_limit)
                    print(f"✅ Limite definido para {new_limit} mensagens")
                save_config(config)
                await asyncio.sleep(2)
            except ValueError:
                print("❌ Valor inválido. Deve ser um número inteiro.")
                await asyncio.sleep(2)
        elif option == '2':
            clear_screen()
            show_config_banner()
            print("⏱️ Intervalo entre requisições")
            print("💡 Recomendado: 1.0 a 3.0 segundos para prevenir banimento")
            print("")
            try:
                new_delay = float(input("🕒 Novo intervalo (segundos): ").strip())
                if new_delay < 0.5:
                    print("⚠️  Intervalo muito baixo. Pode causar banimento!")
                    confirm = input("   Continuar mesmo assim? (s/n): ").strip().lower()
                    if confirm != 's':
                        continue
                config["request_delay"] = new_delay
                print(f"✅ Intervalo definido para {new_delay}s")
                save_config(config)
                await asyncio.sleep(2)
            except ValueError:
                print("❌ Valor inválido. Deve ser um número.")
                await asyncio.sleep(2)
        elif option == '3':
            clear_screen()
            show_config_banner()
            print("🎲 Variação do intervalo")
            print("💡 Adiciona aleatoriedade ao intervalo para parecer mais humano")
            print("")
            try:
                new_variation = float(input("📊 Nova variação (segundos): ").strip())
                if new_variation < 0:
                    print("❌ A variação não pode ser negativa.")
                    await asyncio.sleep(2)
                    continue
                config["delay_variation"] = new_variation
                print(f"✅ Variação definida para {new_variation}s")
                save_config(config)
                await asyncio.sleep(2)
            except ValueError:
                print("❌ Valor inválido. Deve ser um número.")
                await asyncio.sleep(2)
        else:
            print("❌ Opção inválida. Tente novamente.")
            await asyncio.sleep(1)

async def logout_menu(client, config):
    """Menu de logout"""
    clear_screen()
    show_menu_banner()
    try:
        me = await client.get_me()
        phone = f"+{me.phone}" if me and me.phone else "Número não disponível"
        print("🚪 Logout")
        print(f"📱 Número atual: {phone}")
        print("")
        print("⚠️  Ao fazer logout, sua sessão será apagada")
        print("   e você precisará fazer login novamente.")
        print("")
        confirm = input("❓ Deseja realmente fazer logout? (s/n): ").strip().lower()
        if confirm == 's':
            if delete_session():
                print("✅ Logout realizado com sucesso!")
                print("👋 Até mais!")
                return True
            else:
                print("❌ Erro ao fazer logout. Sessão não encontrada.")
                await asyncio.sleep(2)
        else:
            print("↩️  Voltando ao menu...")
            await asyncio.sleep(1)
    except Exception as e:
        print(f"❌ Erro ao obter informações da conta: {e}")
        await asyncio.sleep(2)
    return False

async def main_menu(client):
    """Menu principal do TGMSG"""
    config = load_config()
    while True:
        clear_screen()
        show_menu_banner()
        print("📋 Opções disponíveis:")
        print("   1. 📤 Exportar mensagens de grupo")
        print("   2. ⚙️ Configurações")
        print("   3. 🚪 Logout")
        print("")
        print("💡 Dica: Digite 'menu' ou 'voltar' a qualquer momento para voltar")
        print("")
        option = input("💡 Escolha uma opção: ").strip().lower()
        if option == '1':
            group_entity, topic_id, limit = await export_chat(client, config)
            if group_entity is None:
                continue
            print("\n⏳ Coletando mensagens...")
            messages = await collect_messages(client, group_entity, topic_id, limit, config)
            success = await save_and_send_files(client, group_entity, topic_id, messages)
            if success:
                print("🎉 Processo concluído! As mensagens já estão no seu Telegram em Mensagens Salvas.")
            else:
                print("❌ O processo não foi concluído com sucesso.")
            input("\n📝 Pressione Enter para continuar...")
        elif option == '2':
            config = await config_menu(config)
        elif option == '3':
            if await logout_menu(client, config):
                return True
        else:
            print("❌ Opção inválida. Tente novamente.")
            await asyncio.sleep(1)

async def main():
    """Função principal"""
    client = None
    try:
        client = await setup_client()
        if client is None:
            return
        should_logout = await main_menu(client)
        if should_logout:
            return
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        input("Pressione Enter para continuar...")
    finally:
        if client:
            await client.disconnect()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n❌ Operação cancelada pelo usuário.")
        print("👋 Até mais!")