import socket #permite trabajar con sockets(en la red)
import struct #arma y desarpa paquetes binarios
import time # para tener el formato de tiempo

#variable que equivale al nombre del servidor NTP
NTP_SERVER = "1.south-america.pool.ntp.org"

#variable del tiempo que ha pasado desde 1970
TIME1970 = 2208988800 #si se quitan o agregan numeros cambia la fecha


#Pedir la hora al servidor
def sntp_client():
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #crea socket UDP

    data = b'\x1b' + 47 * b'\0' #paquete NTP de 48 bytes

    try:
        client.sendto(data, (NTP_SERVER, 123)) #puerto que sera usado 123 = NTP
                                 
        data, address = client.recvfrom(1024)

        if data:
            print("Respuesta recibida desde:", address)

            t = struct.unpack('!12I', data)[10]  
            t -= TIME1970

            print("Hora actual (servidor NTP):", time.ctime(t))
    except Exception as e:
        print("Error:", e)
    finally:
        client.close()

if __name__ == '__main__':
    sntp_client()
