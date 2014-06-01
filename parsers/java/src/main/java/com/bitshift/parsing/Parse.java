package com.bitshift.parsing;

import java.io.IOException;

import java.net.ServerSocket;
import java.net.Socket;

import com.bitshift.parsing.parsers.JavaParser;

public class Parse {

    public static void main(String[] args) {
        try {
            ServerSocket server = new ServerSocket(5033);

            while(true) {
                Socket clientSocket = server.accept();
                new Thread(new JavaParser(clientSocket)).start();
            }
        } catch (IOException ex) {
        }
    }

}
