package com.bitshift.parsing;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;

import com.bitshift.parsing.parsers.JavaParser;

public class Parse {

    public static void main(String[] args) {
        try {
            BufferedReader br = new BufferedReader(
                new InputStreamReader(System.in));

            String str = "";
            StringBuilder source = new StringBuilder();
            while ((str = br.readLine()) != null) {
                source.append(str + "\n");
            }

            String symbols = (new JavaParser(source.toString())).parse();
            BufferedWriter bw = new BufferedWriter(
                new OutputStreamWriter(System.out));

            bw.write(symbols);
            bw.flush();
        } catch (IOException e) {

        }
    }

}
