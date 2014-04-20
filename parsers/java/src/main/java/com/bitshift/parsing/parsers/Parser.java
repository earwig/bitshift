package com.bitshift.parsing.parsers;

import java.net.Socket;
import com.bitshift.parsing.symbols.Symbols;

public abstract class Parser implements Runnable {

    protected Socket clientSocket;

    public Parser(Socket clientSocket) {
        this.clientSocket = clientSocket;
    }

    abstract Symbols genSymbols();

    public abstract void run();
    
}

