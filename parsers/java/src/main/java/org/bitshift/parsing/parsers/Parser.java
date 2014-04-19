package org.bitshift.parsing.parsers;

import org.bitshift.parsing.symbols.Symbols;

public abstract class Parser {

    protected String source;

    public Parser(String source) {
        this.source = source;
    }

    abstract Symbols genSymbols();
    
}

