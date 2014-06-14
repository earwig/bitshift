require 'socket'
require File.expand_path('../parser.rb', __FILE__)

def start_server(port_number)
    server = TCPServer.new port_number
    puts "Ruby Server listening on port #{port_number}\n"

    loop do
        # Start a new thread for each client accepted
        Thread.start(server.accept) do |client|
            begin
                # Get the amount of data to be read
                size = (client.readline).to_i
                eos = ">}e^"
                p = Bitshift::Parser.new client.read(size)
                # Get the parsed result
                symbols = p.parse
                client.puts symbols
                client.puts eos
            ensure
                # Close the socket
                client.close
            end
        end
    end
end
