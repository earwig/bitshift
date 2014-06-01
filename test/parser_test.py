import socket, sys, struct

file_name = 'resources/<name>.c'
server_socket_number = 5001
recv_size = 8192

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
            file_name = "resources/parser.rb"
            server_socket_number = 5065

        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.connect(("localhost", server_socket_number))

        with open(file_name, "r") as source_file:
            source = source_file.read()
            server_socket.send("%d\n%s" % (len(source), source));

        total_data = []; size_data = cur_data = ''
        total_size = 0; size = sys.maxint

        while total_size < size:
            cur_data = server_socket.recv(recv_size)

            if not total_data:
                if len(size_data) > 4:
                    size_data += cur_data
                    size = struct.unpack('>i', size_data[:4])[0]
                    recv_size = size
                    if recv_size > sys.maxint: recv_size = sys.maxint
                    total_data.append(size_data[4:])
                else:
                    size_data += cur_data

            else:
                total_data.append(cur_data)

            total_size = sum([len(s) for s in total_data])


        server_socket.close()
        print ''.join(total_data);
