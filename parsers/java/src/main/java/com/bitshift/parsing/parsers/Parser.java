package com.bitshift.parsing.parsers;

import java.util.Formatter;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.io.IOException;

import java.nio.ByteBuffer;

import java.net.Socket;

import com.bitshift.parsing.symbols.Symbols;

public abstract class Parser implements Runnable {

    protected Socket clientSocket;
    private String eos;

    public Parser(Socket clientSocket) {
        this.clientSocket = clientSocket;
    }

    protected String readFromClient() {
        String fromClient = "";

        try {
            BufferedReader clientReader = new BufferedReader(
                    new InputStreamReader(this.clientSocket.getInputStream()));

            int bytes = Integer.parseInt(clientReader.readLine());
            this.eos = clientReader.readLine();

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
            BufferedWriter clientWriter = new BufferedWriter(
                    new OutputStreamWriter(this.clientSocket.getOutputStream()));

            clientWriter.write(toClient);
            clientWriter.write(eos);
            clientWriter.flush();
            this.clientSocket.close();
        } catch (IOException ex) {
        }
    }

    protected abstract Symbols genSymbols();

    public abstract void run();

}

