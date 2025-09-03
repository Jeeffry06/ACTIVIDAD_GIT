import argparse
import sys
from scapy.all import PcapReader, send, IP, PacketList

def send_packet(recvd_pkt, src_ip, dst_ip, count):
    """Enviar paquetes modificados desde el pcap"""
    pkt_cnt = 0
    p_out = []
    
    for p in recvd_pkt:
        pkt_cnt += 1
        
        # Tomamos el payload del paquete (la parte con IP y demás)
        new_pkt = p.payload
        
        # Verificamos que tenga capa IP para modificarla
        if IP in new_pkt:
            new_pkt[IP].src = src_ip
            new_pkt[IP].dst = dst_ip
            # Eliminamos checksum para que se recalculen
            if 'chksum' in new_pkt[IP].fields:
                del new_pkt[IP].chksum
            
            p_out.append(new_pkt)
            
            # Cada "count" paquetes, enviamos el batch
            if pkt_cnt % count == 0:
                send(PacketList(p_out))
                p_out = []
    
    # Enviamos los que quedan
    if p_out:
        send(PacketList(p_out))
    
    print(f"Total paquetes enviados: {pkt_cnt}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Reproduce pcap modificando IP origen y destino')
    parser.add_argument('--infile', default='pcap1.pcap', help='Archivo pcap de entrada')
    parser.add_argument('--src-ip', default='1.1.1.1', help='IP origen a asignar')
    parser.add_argument('--dst-ip', default='2.2.2.2', help='IP destino a asignar')
    parser.add_argument('--count', default=100, type=int, help='Cantidad de paquetes a enviar por lote')
    
    args = parser.parse_args()
    
    try:
        pkt_reader = PcapReader(args.infile)
        send_packet(pkt_reader, args.src_ip, args.dst_ip, args.count)
    except IOError:
        print(f"No se pudo leer el archivo {args.infile}")
        sys.exit(1)


