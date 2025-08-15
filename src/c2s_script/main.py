import subprocess
import time
import re

# --- Configuração ---
# O nome do pacote do aplicativo que você quer monitorar
TARGET_APP_PACKAGE = "com.c2s.c2s" 
# O identificador do seu BlueStacks
DEVICE_SERIAL = "localhost:5555"
# A porta do ADB para o BlueStacks, se necessário
ADB_PORT = "localhost:5555"

def connect_adb():
    """Tenta conectar o ADB ao emulador."""
    try:
        subprocess.run(['adb', '-s', DEVICE_SERIAL, 'connect', ADB_PORT], check=True)
        print("ADB conectado com sucesso.")
        time.sleep(1)
    except subprocess.CalledProcessError as e:
        print(f"Erro ao conectar ao ADB: {e}")
        return False
    return True

def get_notifications():
    """Obtém todas as notificações ativas, especificando o dispositivo."""
    try:
        cmd = ['adb', '-s', DEVICE_SERIAL, 'shell', 'dumpsys', 'notification']
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Erro ao executar dumpsys: {e}")
        return None

def parse_notifications(output):
    """Analisa a saída do dumpsys para extrair o pacote e o ID da notificação."""
    notifications = []
    # Expressão regular para encontrar o pacote e o ID
    # Ela busca por "NotificationRecord" e extrai 'pkg=' e 'id='
    pattern = re.compile(r'NotificationRecord\(.*?pkg=([^\s]+).*?id=([^\s]+).*?\)', re.DOTALL)
    
    for match in pattern.finditer(output):
        pkg_name = match.group(1)
        notif_id = match.group(2)
        
        notifications.append({
            "package": pkg_name,
            "id": notif_id
        })
        
    return notifications

def tap_with_adb(x, y):
    """
    Simula um 'tap' (toque) na tela do emulador nas coordenadas (x, y).
    """
    try:
        # A lista de argumentos do comando adb
        cmd = ['adb', '-s', DEVICE_SERIAL, 'shell', 'input', 'tap', str(x), str(y)]
        
        # Executa o comando e verifica se houve erro
        subprocess.run(cmd, check=True)
        print(f"Toque simulado em ({x}, {y}) no dispositivo '{DEVICE_SERIAL}'.")
        
    except subprocess.CalledProcessError as e:
        print(f"Erro ao simular o toque: {e}")
        
    except FileNotFoundError:
        print("Erro: 'adb' não foi encontrado. Certifique-se de que está instalado e no seu PATH.")

def main():
    if not connect_adb():
        print("Não foi possível conectar ao ADB. Verifique se o BlueStacks está rodando e a porta está correta.")
        return

    known_notifications = set()
    print(f"Monitorando novas notificações para o app: {TARGET_APP_PACKAGE}. Pressione Ctrl+C para parar.")
    
    cont = 0
    try:
        while True:
            print(cont)
            output = get_notifications()
            if output:
                current_notifications = parse_notifications(output)
                
                # Cria um identificador único para cada notificação com base no pacote e no ID
                current_unique_ids = set([f"{n['package']}_{n['id']}" for n in current_notifications])
                
                new_notifications_ids = current_unique_ids
                
                if new_notifications_ids:
                    for notif_id in new_notifications_ids:
                        pkg, notif_id_val = notif_id.split('_')
                        if pkg == TARGET_APP_PACKAGE:
                            print(new_notifications_ids)
                            print("\n--- Nova Notificação Detectada! ---")
                            print(f"App: {pkg}")
                            print(f"ID da Notificação: {notif_id_val}")
                            tap_with_adb(500, 60)
                            tap_with_adb(500, 80)
                            time.sleep(2)
                            tap_with_adb(559, 745)
                            time.sleep(.5)
                            tap_with_adb(557, 1737)

                            # --- AQUI VOCÊ COLOCA A AÇÃO QUE QUER AUTOMATIZAR ---
                            # Por exemplo:
                            # from seu_script_de_clique import click_with_adb
                            # click_with_adb(500, 1000)
                            
                            # Adiciona a nova notificação aos conhecidos para não detectá-la novamente
                    

            # Pausa antes de verificar novamente
            time.sleep(0.2)
            cont += 1
            
    except KeyboardInterrupt:
        print("\nMonitoramento interrompido.")
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")

if __name__ == "__main__":
    main()