import os
import subprocess
import platform
import nmap
import psutil
import cpuinfo
import time
import sched
import socket

socket_servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
disco = psutil.disk_usage('.')
info_cpu = cpuinfo.get_cpu_info()
scheduler = sched.scheduler(time.time, time.sleep)

def print_event(name):
    print ('EVENTO:', time.ctime(), name)

def print_event2(name):
    print ('EVENTO:', time.ctime(), name)

def execucao_evento():
    print("----------------------------------------------------")
    print ('INICIO:', time.ctime())
    scheduler.enter(2, 1, print_event, ('primeira chamada',))
    scheduler.enter(8, 1, print_event2, ('segunda chamada',))
    print ('CHAMADAS ESCALONADAS DA FUNÇÃO:', time.ctime())
    print("----------------------------------------------------")

def obtem_nome_familia(familia):
  if familia == socket.AF_INET:
      return("IPv4")
  elif familia == socket.AF_INET6:
      return("IPv6")
  elif familia == socket.AF_UNIX:
      return("Unix")
  else:
      return("-")

def obtem_tipo_socket(tipo):
  if tipo == socket.SOCK_STREAM:
    return("TCP")
  elif tipo == socket.SOCK_DGRAM:
    return("UDP")
  elif tipo == socket.SOCK_RAW:
    return("IP")
  else:
    return("-")

def interfaces():
    interfaces = psutil.net_if_addrs()
    io_status = psutil.net_io_counters(pernic=True)
    status = psutil.net_if_stats()

    nomes = []

    for i in interfaces:
        nomes.append(str(i))

    for i in nomes:
        print(i+":")
        for j in interfaces[i]:
            print("\t"+str(j))
        print("\t"+str(status[i]))
        print("-----------------------------------------------------------------------------------------------------------------------------------")

    nomes = []

    for i in io_status:
        nomes.append(str(i))
    for j in nomes:
        print(j)
        print("\t"+str(io_status[j]))
    for i in range(4):
        time.sleep(1)
        io_status = psutil.net_io_counters(pernic=True)
        for j in nomes:
            print(j)
            print("\t"+str(io_status[j]))

def diretorio():
    pasta_atual = os.listdir()

    lista_diretorios = []
    lista_arquivos = []

    for item in pasta_atual:
        if os.path.isfile(item):
            lista_arquivos.append(item)
        else:
            if item not in [".git", ".vscode"]:        
                lista_diretorios.append(item)

    msg = ("LISTA DE DIRETÓRIOS\n", str(*lista_diretorios))
    # print(*lista_diretorios, sep=" \n")
    msg2 = ("LISTA DE ARQUIVOS\n", str(*lista_arquivos))
    # print(*lista_arquivos, sep=" \n")
    return msg, msg2

def mostra_informacoes():
    msg = ("Informações do computador: " "Frequência (MHz): " + str(round(psutil.cpu_freq().current, 2)) 
        + "\nNúcleos (físicos): " + str(psutil.cpu_count()) + " (" + str(psutil.cpu_count(logical=False)) + ")" 
        + "\nProcessador info: " + str(platform.processor()) + " | " + str(platform.node() + " | " + platform.platform() + " | " + platform.system()) 
        + "\nDisco info, Total: " + str(round(disco.total/(1024*1024*1024), 2)) + "GB ,     " 
        + "Usado: " + str(round(disco.used/(1024*1024*1024), 2)) + "GB ,       " 
        + "Livre: " + str(round(disco.free/(1024*1024*1024), 2)) + "GB" + ",       " 
        + "Percentual usado: " + str(disco.percent) + "%" 
        + "\nMemória total: " + str(round(psutil.virtual_memory().total/(1024*1024*1024), 2)) + "GB"
        + "\nUso da CPU: " + str(psutil.cpu_percent(interval=1, percpu=True))
        + "\nRede: " + str(psutil.net_if_addrs()['Ethernet0'][0].address))
    return msg

def processos():
    return [proc.info for proc in psutil.process_iter(attrs=['pid', 'name', 'memory_percent'])]

host = socket.gethostname()
porta = 9999

socket_servidor.bind((host, porta))

socket_servidor.listen()
print("Servidor de nome", host, "esperando conexão na porta", porta)

(socket_cliente,addr) = socket_servidor.accept()
print("Conectado a:", str(addr))

while True:
    msg = socket_cliente.recv(15360)

    if '$' == msg.decode('utf-8'): 
        print("Fechando conexao com", str(addr), "...")
        socket_cliente.close()
        break
    elif 'Informacoes pc?' in msg.decode('utf-8'): 
        msg = mostra_informacoes()
        print(msg)
        # + print("Informações gerais : " + str(info_cpu))
        # + "\n\n" + str(diretorio()) + "\n\n\n" + str(mostra_informacoes()) + "\n\n\n" + str(processos())  + "\n\n\n" + str(interfaces())
    elif 'Informacoes diretorios?' in msg.decode('utf-8'): 
        msg = diretorio()
        print(msg)
    elif 'Informacoes processos?' in msg.decode('utf-8'): 
        msg = str(processos())
        print(msg)
    elif 'Informacoes rede?' in msg.decode('utf-8'): 
        msg = interfaces()
        print(msg)
    else:
        msg = "O que quer dizer com isso? ---> " + msg.decode('utf-8') 
    socket_cliente.send(msg.encode('utf-8'))

scheduler.run()    
socket_servidor.close()
input("Pressione qualquer tecla para sair...") 
