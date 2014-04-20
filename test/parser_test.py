import socket, sys

file_name = 'resources/<name>.c'
server_socket_number = 5001

if __name__ == '__main__':
    if len(sys.argv) == 1:
        print "Please input a parser to test."

    elif len(sys.argv) > 2:
        print "Too many arguments."

    else:
        if sys.argv[1] == 'c':
            pass

        elif sys.argv[1] == 'java':
            file_name = "resources/Matrix.java"
            server_socket_number = 5002

        elif sys.argv[1] == 'ruby':
            file_name = "resources/<name>.rb"
            server_socket_number = 5003

        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(("localhost", server_socket_number))

        with open(file_name, "r") as source_file:
            source = source_file.read()
            client_socket.send("%d\n%s" % (len(source), source));

        data = ''
        while True:
            data = client_socket.recv(10000)

            if data != '':
                client_socket.close()
                break;

        print data;
