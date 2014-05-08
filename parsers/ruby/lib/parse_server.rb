require 'socket'
require File.expand_path('../parser.rb', __FILE__)

def pack_int(i)
    bytes = []; mask = 255

    while bytes.length < 4
        bytes.unshift (i & mask)
        i = i >> 8
    end

    return bytes.pack('cccc')
end


def start_server
    server = TCPServer.new 5003

    loop do
        # Start a new thread for each client accepted
        Thread.start(server.accept) do |client|
            begin
                # Get the amount of data to be read
                size = (client.readline).to_i
                p = Bitshift::Parser.new client.read(size)
                # Get the parsed result
                symbols = p.parse
                client.puts pack_int(symbols.length)
                client.puts symbols
            ensure
                # Close the socket
                client.close
            end
        end
    end
end
