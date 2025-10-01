from netmiko import ConnectHandler
import pandas as pd
import glob

# Buscar cualquier archivo CSV en la carpeta
csv_files = glob.glob("*.csv")
if not csv_files:
    raise FileNotFoundError(" No se encontró ningún archivo CSV en la carpeta.")
filename = csv_files[0]  # Toma el primer archivo encontrado
print(f" Usando archivo: {filename}")

# Leer CSV universal (separador ;)
df = pd.read_csv(filename, sep=";")
print("Contenido del CSV leído:")
print(df)

# Obtener los hosts únicos
hosts = df['host'].unique()

for host in hosts:
    df_host = df[df['host'] == host]

    device_type = df_host.iloc[0]['device_type']
    username = df_host.iloc[0]['username']
    password = df_host.iloc[0]['password']
    enable_password = df_host.iloc[0]['enable_password']
    banner_motd = df_host.iloc[0]['banner_motd']

    # Asignar un nombre fijo para el hostname
    hostname = df_host.iloc[0]['hostname']

    device = {
        'device_type': 'cisco_ios',
        'host': host,
        'username': username,
        'password': password,
        'secret': enable_password,  # Usa 'enable_password' si no usas 'secret'
    }

    print(f"\n Conectando a {device_type.upper()} {host}...")
    try:
        net_connect = ConnectHandler(**device)
        net_connect.enable()

        # Configuración general con hostname fijo
        general_cmds = [
            f"hostname {hostname}", 
            f"banner motd #{banner_motd}#",
            f"enable secret {enable_password}"
        ]
        print(net_connect.send_config_set(general_cmds))

        if device_type == "switch":
            # Crear VLANs
            for vlan in df_host['vlan'].dropna().unique():
                row_vlan = df_host[df_host['vlan'] == vlan].iloc[0]
                cmds_vlan = [
                    f"vlan {int(vlan)}",
                    f"name {row_vlan['vlan_name']}"
                ]
                print(net_connect.send_config_set(cmds_vlan))

                # Configurar SVI
                if pd.notna(row_vlan['ip_address']) and pd.notna(row_vlan['subnet_mask']):
                    cmds_svi = [
                        f"interface vlan {int(vlan)}",
                        f"ip address {row_vlan['ip_address']} {row_vlan['subnet_mask']}",
                        "no shutdown",
                        "exit"
                    ]
                    print(net_connect.send_config_set(cmds_svi))

                    # Default gateway
                    if pd.notna(row_vlan['default_gateway']):
                        gw_cmd = f"ip default-gateway {row_vlan['default_gateway']}"
                        print(net_connect.send_config_set([gw_cmd]))

            # Interfaces físicas
            for _, row in df_host.iterrows():
                if pd.notna(row['interface']):
                    cmds_int = [
                        f"interface {row['interface']}",
                        f"description {row['description']}",
                        f"switchport access vlan {int(row['vlan'])}",
                        "no shutdown",
                        "exit"
                    ]
                    print(net_connect.send_config_set(cmds_int))

        elif device_type == "router":
            # Interfaces físicas con IP
            for _, row in df_host.iterrows():
                if pd.notna(row['interface']):
                    cmds_int = [
                        f"interface {row['interface']}",
                        f"description {row['description']}",
                        f"ip address {row['ip_address']} {row['subnet_mask']}",
                        "no shutdown",
                        "exit"
                    ]
                    print(net_connect.send_config_set(cmds_int))

                    # Ruta por defecto
                    if pd.notna(row['default_gateway']):
                        gw_cmd = f"ip route 0.0.0.0 0.0.0.0 {row['default_gateway']}"
                        print(net_connect.send_config_set([gw_cmd]))

        # Guardar configuración
        net_connect.save_config()
        net_connect.disconnect()
        print(f"✅ Configuración aplicada y guardada en {host}")

    except Exception as e:
        print(f" Error conectando a {host}: {e}")
