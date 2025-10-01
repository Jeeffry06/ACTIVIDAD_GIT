from netmiko import ConnectHandler
import pandas as pd
import glob

# Buscar cualquier archivo CSV en la carpeta
csv_files = glob.glob("*.csv")
if not csv_files:
    raise FileNotFoundError("❌ No se encontró ningún archivo CSV en la carpeta.")
filename = csv_files[0]  # Toma el primer archivo encontrado
print(f"📂 Usando archivo: {filename}")

# Leer CSV universal (separador ;)
df = pd.read_csv(filename, sep=";")

# Obtener los hosts únicos
hosts = df['host'].unique()

for host in hosts:
    df_host = df[df['host'] == host]

    device_type = df_host.iloc[0]['device_type']
    username = df_host.iloc[0]['username']
    password = df_host.iloc[0]['password']
    enable_password = df_host.iloc[0]['enable_password']

    device = {
        'device_type': 'cisco_ios',
        'host': host,
        'username': username,
        'password': password,
        'secret': enable_password,  # Usa 'enable_password' si no usas 'secret'
    }

    print(f"\n🔗 Conectando a {device_type.upper()} {host}...")
    try:
        net_connect = ConnectHandler(**device)
        net_connect.enable()

        # Borrar configuraciones
        print("🚫 Eliminando configuración del dispositivo...")

        # Eliminar configuraciones de interfaces
        cmd_clear_interfaces = "no interface range fa0/1 - 48"
        print(net_connect.send_config_set([cmd_clear_interfaces]))

        # Eliminar configuraciones de VLANs
        cmd_clear_vlans = "no vlan 1-4094"
        print(net_connect.send_config_set([cmd_clear_vlans]))

        # Eliminar configuración de hostname
        cmd_clear_hostname = "no hostname"
        print(net_connect.send_config_set([cmd_clear_hostname]))

        # Eliminar Banner MOTD
        cmd_clear_banner = "no banner motd"
        print(net_connect.send_config_set([cmd_clear_banner]))

        # Eliminar contraseñas y secretos
        cmd_clear_passwords = [
            "no enable secret",
            "no enable password",
            "no line vty 0 4",
            "no line console 0",
            "no password"
        ]
        print(net_connect.send_config_set(cmd_clear_passwords))

        # Eliminar interfaces físicas
        cmd_clear_interfaces = "no interface range g0/1 - 48"
        print(net_connect.send_config_set([cmd_clear_interfaces]))

        # Eliminar rutas estáticas o cualquier configuración de IP
        cmd_clear_ip_routes = "no ip route 0.0.0.0 0.0.0.0"
        print(net_connect.send_config_set([cmd_clear_ip_routes]))

        # Eliminar cualquier configuración adicional como ACLs, NATs, etc.
        cmd_clear_advanced = [
            "no access-list",
            "no ip nat inside source list",
            "no ip nat inside source static"
        ]
        print(net_connect.send_config_set(cmd_clear_advanced))

        # Borrar la configuración de 'enable secret'
        cmd_clear_enable_password = "no enable secret"
        print(net_connect.send_config_set([cmd_clear_enable_password]))

        # Borrar la configuración de arranque (esto reinicia el dispositivo)
        cmd_clear_startup = "write erase"
        print(net_connect.send_config_set([cmd_clear_startup]))

        # Reiniciar el dispositivo
        print("🔄 Reiniciando el dispositivo...")
        net_connect.send_command_timing("reload")  # Comando para reiniciar el dispositivo
        print("✅ Configuración eliminada y reinicio solicitado.")

        net_connect.disconnect()

    except Exception as e:
        print(f"❌ Error conectando a {host}: {e}")
