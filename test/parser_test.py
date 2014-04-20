import socket

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(("localhost", 5002))

with open("resources/Matrix.java", "r") as java_file:
    source = java_file.read() + "\nEOS_BITSHIFT"
    client_socket.send("%d\n%s" % (len(source), source));

data = ''
while True:
    data = client_socket.recv(10000)

    if data != '':
        client_socket.close()
        break;

print data;
