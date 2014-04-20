package com.bitshift.parsing.symbols;

import java.util.ArrayList;

public abstract class Symbols {

    public Symbols() {
    
    }

    public static ArrayList<Integer> createCoord(Integer startLine, Integer startCol, Integer endLine, Integer endCol) {
        ArrayList<Integer> coord = new ArrayList<Integer>(4);
        coord.add(startLine); coord.add(startCol); coord.add(endLine); coord.add(endCol);
        return coord;
    }

}
