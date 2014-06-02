package com.bitshift.parsing.utils;

import java.util.List;
import java.util.Arrays;

public class Tuple<T> {
    private List<T> _objects;

    public Tuple(T... args) {
        _objects = Arrays.asList(args);
    }

    public String toString() {
        StringBuilder builder = new StringBuilder();

        for(T o: this._objects) {
            builder.append(o + ",");
        }

        String s = builder.toString();
        return "(" + s.substring(0, s.length() - 1) + ")";
    }
}
