package com.bitshift.parsing;

import com.bitshift.parsing.utils.ParseServer;

public class Parse {

    public static void main(String[] args) {
        ParseServer server = new ParseServer(Integer.parseInt(args[0]));
        System.out.println("Java Server listening on port " + args[0]);
        new Thread(server).start();
    }

}
