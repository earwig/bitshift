package com.bitshift.parsing;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.io.IOException;

import java.net.ServerSocket;
import java.net.Socket;

import com.bitshift.parsing.parsers.JavaParser;

public class Parse {

    public static void main(String[] args) {
        String fromClient;
        String toClient;

        try {
            ServerSocket server = new ServerSocket(5002);

            while(true) {
                Socket clientSocket = server.accept();

                JavaParser parser = new JavaParser(clientSocket);
                Thread parserTask = new Thread(parser);
                parserTask.start();
            }
        } catch (IOException ex) {
        }
    }

}
