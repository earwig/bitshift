require 'socket'
require File.expand_path('../parser.rb', __FILE__)

server = TCPServer.new 5003

loop do
    # Start a new thread for each client accepted
    Thread.start(server.accept) do |client|
        begin
            # Get the amount of data to be read
            size = (client.readline).to_i
            p = Bitshift::Parser.new client.read(size)
            # Get the parsed result
            symbols = p.parse.to_s
            client.puts [symbols.length].pack('c')
            client.puts symbols
        ensure
            # Close the socket
            client.close
        end
    end
end
