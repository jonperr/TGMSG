from telethon import TelegramClient
import re
import asyncio
import csv
import os
import sys
import json
from time import sleep

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
    print("🔐 Sessão persistente - Login uma vez apenas")
    print("─" * 50)

def save_credentials(api_id, api_hash):
    """Salva as credenciais em arquivo JSON"""
    credentials = {
        "api_id": api_id,
        "api_hash": api_hash
    }
    with open("tgmsg_config.json", "w") as f:
        json.dump(credentials, f)

def load_credentials():
    """Carrega as credenciais do arquivo JSON"""
    try:
        with open("tgmsg_config.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return None

def delete_credentials():
    """Remove as credenciais salvas"""
    try:
        if os.path.exists("tgmsg_config.json"):
            os.remove("tgmsg_config.json")
        if os.path.exists("user_session.session"):
            os.remove("user_session.session")
        return True
    except:
        return False

async def check_session_validity(client):
    """Verifica se a sessão é válida"""
    try:
        me = await client.get_me()
        return me is not None
    except:
        return False

async def setup_client():
    """Configura o cliente do Telegram com sessão persistente"""
    # Primeiro tenta usar a sessão existente
    if os.path.exists("user_session.session"):
        try:
            # Tenta carregar credenciais salvas
            credentials = load_credentials()
            
            if credentials:
                client = TelegramClient("user_session", credentials["api_id"], credentials["api_hash"])
                await client.start()
                
                # Verifica se a sessão é válida
                if await check_session_validity(client):
                    me = await client.get_me()
                    clear_screen()
                    print("✅ Sessão restaurada com sucesso!")
                    print(f"👤 Conectado como: {me.first_name}")
                    if me.username:
                        print(f"📱 Usuário: @{me.username}")
                    sleep(2)
                    
                    clear_screen()
                    show_welcome_banner()
                    return client
        except:
            # Se falhar, continua para o login normal
            pass
    
    # Se não tem sessão válida, faz login normal
    clear_screen()
    show_login_banner()
    
    print("📝 Caso não saiba seu API ID e API Hash, consulte:")
    print("   https://core.telegram.org/api/obtaining_api_id")
    print("   Ou pesquise no Google: 'como obter api id telegram'")
    print("")
    
    # Solicita credenciais API
    api_id = input("🔑 Digite seu API ID: ").strip()
    if api_id.lower() == 'sair':
        print("👋 Até mais!")
        sys.exit(0)
        
    api_hash = input("🔒 Digite seu API Hash: ").strip()
    
    # Salva as credenciais para uso futuro
    save_credentials(int(api_id), api_hash)
    
    # Cria cliente com as credenciais fornecidas
    client = TelegramClient("user_session", int(api_id), api_hash)
    
    # Inicia processo de conexão
    await client.start()
    
    # Limpa a tela e mostra welcome message
    clear_screen()
    print("✅ Login realizado com sucesso!")
    
    # Mostra informações da conta
    me = await client.get_me()
    print(f"👤 Conectado como: {me.first_name}")
    if me.username:
        print(f"📱 Usuário: @{me.username}")
    
    print("🔄 Iniciando TGMSG...")
    sleep(3)
    
    clear_screen()
    show_welcome_banner()
    
    return client

def print_progress(current, total, bar_length=10):
    """Exibe uma barra de progresso simplificada em uma única linha"""
    if total == 0:
        return
        
    percent = min(float(current) / total, 1.0)
    filled_length = int(round(bar_length * percent))
    arrow = '█' * filled_length
    spaces = '░' * (bar_length - filled_length)
    
    # Limpa a linha e move o cursor para o início
    sys.stdout.write('\r\033[K')
    
    if current == total:
        progress_text = "✅ Completo!"
    else:
        progress_text = f"{current}/{total}"
    
    sys.stdout.write(f"📥 Progresso: [{arrow + spaces}] {percent*100:.1f}% ({progress_text})")
    sys.stdout.flush()

async def export_chat(client):
    try:
        clear_screen()
        show_welcome_banner()
        
        # Solicita o link do grupo
        group_link = input("\n🔗 Cole o link ou @ do grupo: ").strip()
        
        # Tenta acessar o grupo
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
        
        # Verifica se o grupo tem tópicos (é um fórum)
        has_topics = False
        topic_id = None
        
        try:
            # Tenta detectar se é um grupo com tópicos
            full_chat = await client.get_entity(group_entity)
            if hasattr(full_chat, 'forum') and full_chat.forum:
                has_topics = True
                print("📌 Este grupo possui tópicos (fórum)")
        except:
            # Se não conseguir detectar, pergunta ao usuário
            has_topics_input = input("\n📝 Este grupo tem tópicos? (s/n): ").strip().lower()
            has_topics = has_topics_input == 's'
        
        # Se o grupo tem tópicos, pergunta se quer exportar um específico
        if has_topics:
            export_topic = input("\n📝 Deseja exportar mensagens de um tópico específico? (s/n): ").strip().lower()
            if export_topic == 's':
                topic_link = input("🔗 Cole o link do tópico: ").strip()
                
                # Tenta extrair o ID do tópico do link
                topic_match = re.search(r"/(\d+)(?:\?|$)", topic_link)
                if topic_match:
                    topic_id = int(topic_match.group(1))
                    print(f"✅ ID do tópico detectado: {topic_id}")
                else:
                    print("❌ Não foi possível detectar o ID do tópico do link")
                    try:
                        topic_id = int(input("🔢 Digite o ID do tópico manualmente: ").strip())
                    except:
                        print("❌ ID inválido. Continuando com o grupo inteiro.")
                        topic_id = None
        
        # Pergunta sobre o limite de mensagens
        try:
            limit_input = input("\n🔢 Quantidade máxima de mensagens a exportar (deixe em branco pra todas): ").strip()
            limit = int(limit_input) if limit_input else None
        except:
            print("❌ Valor inválido. Usando todas as mensagens.")
            limit = None
        
        # Confirmação antes de prosseguir
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
        if confirm != 's':
            print("❌ Operação cancelada.")
            return None, None, None
        
        return group_entity, topic_id, limit
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return None, None, None

async def collect_messages(client, group_entity, topic_id, limit):
    """Coleta mensagens do grupo/tópico"""
    messages = []
    
    # Configurações para a coleta
    kwargs = {'reverse': True}
    if topic_id:
        kwargs['reply_to'] = topic_id
    
    # Adiciona limite se especificado
    if limit:
        kwargs['limit'] = limit
    
    try:
        # Primeiro, conta o total de mensagens (estimativa)
        print("📊 Estimando quantidade de mensagens...")
        
        # Se não houver limite, tenta obter uma estimativa
        if limit:
            total_estimate = limit
        else:
            # Para grupos sem limite, tentamos contar as mensagens rapidamente
            try:
                total_estimate = 0
                async for msg in client.iter_messages(group_entity, limit=100, **kwargs):
                    if not msg.message or hasattr(msg, 'action') and msg.action:
                        continue
                    total_estimate += 1
                # Se encontrou menos de 100, essa é a contagem real
                if total_estimate < 100:
                    print(f"📊 Estimativa: {total_estimate} mensagens")
                else:
                    print("📊 Estimativa: Muitas mensagens (coletando todas)")
                    total_estimate = 10000  # Valor alto para indicar muitas mensagens
            except:
                total_estimate = 1000  # Valor padrão se não conseguir estimar
            
        # Agora coleta as mensagens com barra de progresso
        current_count = 0
        last_update = 0
        
        async for msg in client.iter_messages(group_entity, **kwargs):
            if not msg.message or hasattr(msg, 'action') and msg.action:
                continue
            messages.append(msg)
            current_count += 1
            
            # Atualiza a barra de progresso a cada 10 mensagens (ou quando necessário)
            if limit:
                # Se temos um limite, sabemos o total exato
                if current_count - last_update >= 10 or current_count == limit:
                    print_progress(current_count, limit)
                    last_update = current_count
            else:
                # Se não temos limite, mostramos apenas a contagem atual
                if total_estimate < 10000:  # Se temos uma estimativa razoável
                    if current_count - last_update >= 10 or current_count == total_estimate:
                        print_progress(current_count, total_estimate)
                        last_update = current_count
                else:
                    # Para muitos mensagens, apenas mostramos a contagem a cada 10 mensagens
                    if current_count - last_update >= 10:
                        sys.stdout.write('\r\033[K')
                        sys.stdout.write(f"📥 Mensagens coletadas: {current_count} (aguarde...)")
                        sys.stdout.flush()
                        last_update = current_count
            
            # Se atingiu o limite, para a coleta
            if limit and current_count >= limit:
                break
                
        # Limpa a linha de progresso e mostra mensagem final
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
    
    # Gera nome de arquivo baseado no grupo
    group_name = re.sub(r'[^\w\-_\. ]', '_', group_entity.title)
    txt_filename = f"{group_name}_mensagens.txt"
    csv_filename = f"{group_name}_mensagens.csv"
    
    print("💾 Salvando em arquivos...")
    
    # Salva TXT
    with open(txt_filename, "w", encoding="utf-8") as f:
        for m in messages:
            try:
                user = await m.get_sender()
                if user and user.username:
                    username = f"@{user.username[:5]}"  # Apenas 5 primeiras letras
                else:
                    username = "desconhecido"
                
                # Formata a data como (ano/mês)
                data_formatada = m.date.strftime('(%Y/%m)')
                
                f.write(f"{data_formatada} {username}: {m.text}\n")
            except Exception as e:
                continue

    # Salva CSV
    with open(csv_filename, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(["data", "username", "mensagem"])
        
        for m in messages:
            try:
                user = await m.get_sender()
                if user and user.username:
                    username = user.username[:5]  # Apenas 5 primeiras letras
                else:
                    username = "desconhecido"
                
                # Formata a data como (ano/mês)
                data_formatada = m.date.strftime('%Y/%m')
                
                writer.writerow([
                    data_formatada,
                    username,
                    m.text.replace("\n", " ") if m.text else ""
                ])
            except Exception as e:
                continue

    # Verifica se os arquivos foram criados com conteúdo
    txt_size = os.path.getsize(txt_filename) if os.path.exists(txt_filename) else 0
    csv_size = os.path.getsize(csv_filename) if os.path.exists(csv_filename) else 0
    
    print("📤 Enviando para suas Mensagens Salvas...")
    
    topic_name = f"Tópico {topic_id}" if topic_id else "Geral"
    success = False
    
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

    # Limpa arquivos
    if os.path.exists(txt_filename):
        os.remove(txt_filename)
    if os.path.exists(csv_filename):
        os.remove(csv_filename)
    
    return success

async def main(client):
    clear_screen()
    show_welcome_banner()
    
    # Pergunta se quer exportar outro grupo após terminar
    while True:
        group_entity, topic_id, limit = await export_chat(client)
        
        if group_entity is None:
            # Operação cancelada ou erro
            continuar = input("\n🔄 Deseja tentar com outro grupo? (s/n): ").strip().lower()
            if continuar != 's':
                break
            continue
        
        # Coleta as mensagens
        print("\n⏳ Coletando mensagens...")
        messages = await collect_messages(client, group_entity, topic_id, limit)
        
        # Salva e envia os arquivos
        success = await save_and_send_files(client, group_entity, topic_id, messages)
        
        if success:
            print("🎉 Processo concluído! As mensagens já estão no seu Telegram em Mensagens Salvas.")
        else:
            print("❌ O processo não foi concluído com sucesso.")
        
        continuar = input("\n🔄 Deseja exportar outro grupo? (s/n): ").strip().lower()
        if continuar != 's':
            break
    
    print("\n👋 Obrigado por usar o TGMSG! Até a próxima!")
    print("⭐ Se gostou, compartilhe com seus amigos!")

if __name__ == "__main__":
    try:
        # Configura e inicia o cliente
        loop = asyncio.get_event_loop()
        client = loop.run_until_complete(setup_client())
        
        # Executa o programa principal
        with client:
            loop.run_until_complete(main(client))
    except KeyboardInterrupt:
        print("\n\n❌ Operação cancelada pelo usuário.")
        print("👋 Até mais!")
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
