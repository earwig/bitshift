package com.bitshift.parsing.parsers;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.io.IOException;

import java.net.Socket;

import com.bitshift.parsing.symbols.Symbols;
import com.bitshift.parsing.utils.PackableMemory;

public abstract class Parser implements Runnable {

    protected Socket clientSocket;

    public Parser(Socket clientSocket) {
        this.clientSocket = clientSocket;
    }

    protected String readFromClient() {
        String fromClient = "";

        try {
            BufferedReader clientReader = new BufferedReader(
                    new InputStreamReader(this.clientSocket.getInputStream()));

            int bytes = Integer.parseInt(clientReader.readLine());

            StringBuilder builder = new StringBuilder();
            int i = 0;

            while(i < bytes) {
                char aux = (char)clientReader.read();
                builder.append(aux);
                i++;
            }

            fromClient = builder.toString();

        } catch (IOException ex) {
        }

        return fromClient;
    }

    protected void writeToClient(String toClient) {
        try {
            PrintWriter clientWriter = new PrintWriter(
                    this.clientSocket.getOutputStream(), true);

            PackableMemory mem = new PackableMemory(toClient.length());
            String dataSize = new String(mem.mem);
            clientWriter.println(dataSize + toClient);
        } catch (IOException ex) {
        }
    }

    protected abstract Symbols genSymbols();

    public abstract void run();

}

