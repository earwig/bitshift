package org.bitshift.parsing.symbols;

import java.util.List;
import java.util.Map;
import java.util.HashMap;
import java.util.ArrayList;
import org.bitshift.parsing.symbols.Symbols;

/*TODO: Overwrite toString*/
public class JavaSymbols extends Symbols {

    private String _packageName;
    private Map<String, List<List<Integer>>> _classes;
    private Map<String, List<List<Integer>>> _interfaces;
    private Map<String, List<List<Integer>>> _methods;
    private Map<String, List<List<Integer>>> _fields;
    private Map<String, List<List<Integer>>> _vars;

    public JavaSymbols() {
        _packageName = null;
        _classes = new HashMap<String, ArrayList<ArrayList<Integer>>>();
        _interfaces = new HashMap<String, ArrayList<ArrayList<Integer>>>();
        _methods = new HashMap<String, ArrayList<ArrayList<Integer>>>();
        _fields = new HashMap<String, ArrayList<ArrayList<Integer>>>();
        _vars = new HashMap<String, ArrayList<ArrayList<Integer>>>();
    }

    public boolean setPackage(String name) {
        _packageName = name;
    }

    public boolean insertClassDeclaration(String name, Integer startLine, Integer startCol, Integer endLine, Integer endCol) {
        List<Integer> pos = new ArrayList<Integer>(4);
        pos.set(0, startLine); pos.set(1, startCol); pos.set(2, endLine); pos.set(3, endCol);
        List<List<Integer>> copy = _classes.get(name);
        copy.add(0, pos);
        _classes.put(name, copy);
        return true;
    }
    public boolean insertClassInstance(String name, Integer startLine, Integer startCol, Integer endLine, Integer endCol) {
        List<Integer> pos = new ArrayList<Integer>(4);
        pos.set(0, startLine); pos.set(1, startCol); pos.set(2, endLine); pos.set(3, endCol);
        List<List<Integer>> copy = _classes.get(name);
        copy.add(pos);
        _classes.put(name, copy);
        return true;
    }

    public boolean insertInterfaceDeclaration(String name, Integer startLine, Integer startCol, Integer endLine, Integer endCol) {
        List<Integer> pos = new ArrayList<Integer>(4);
        pos.set(0, startLine); pos.set(1, startCol); pos.set(2, endLine); pos.set(3, endCol);
        List<List<Integer>> copy = _classes.get(name);
        copy.add(0, pos);
        _classes.put(name, copy);
        return true;
    }
    public boolean insertInterfaceInstance(String name, Integer startLine, Integer startCol, Integer endLine, Integer endCol) {
        List<Integer> pos = new ArrayList<Integer>(4);
        pos.set(0, startLine); pos.set(1, startCol); pos.set(2, endLine); pos.set(3, endCol);
        List<List<Integer>> copy = _classes.get(name);
        copy.add(pos);
        _classes.put(name, copy);
        return true;
    }

    public boolean insertMethodDeclaration(String name, Integer startLine, Integer startCol, Integer endLine, Integer endCol) {
        List<Integer> pos = new ArrayList<Integer>(4);
        pos.set(0, startLine); pos.set(1, startCol); pos.set(2, endLine); pos.set(3, endCol);
        List<List<Integer>> copy = _classes.get(name);
        copy.add(0, pos);
        _classes.put(name, copy);
        return true;
    }
    public boolean insertMethodInvocation(String name, Integer startLine, Integer startCol, Integer endLine, Integer endCol) {
        List<Integer> pos = new ArrayList<Integer>(4);
        pos.set(0, startLine); pos.set(1, startCol); pos.set(2, endLine); pos.set(3, endCol);
        List<List<Integer>> copy = _classes.get(name);
        copy.add(pos);
        _classes.put(name, copy);
        return true;
    }

    public boolean insertFieldDeclaration(String name, Integer startLine, Integer startCol, Integer endLine, Integer endCol) {
        List<Integer> pos = new ArrayList<Integer>(4);
        pos.set(0, startLine); pos.set(1, startCol); pos.set(2, endLine); pos.set(3, endCol);
        List<List<Integer>> copy = _classes.get(name);
        copy.add(0, pos);
        _classes.put(name, copy);
        return true;
    }
    public boolean insertFieldAccess(String name, Integer startLine, Integer startCol, Integer endLine, Integer endCol) {
        List<Integer> pos = new ArrayList<Integer>(4);
        pos.set(0, startLine); pos.set(1, startCol); pos.set(2, endLine); pos.set(3, endCol);
        List<List<Integer>> copy = _classes.get(name);
        copy.add(pos);
        _classes.put(name, copy);
        return true;
    }

    public boolean insertVariableDeclaration(String name, Integer startLine, Integer startCol, Integer endLine, Integer endCol) {
        List<Integer> pos = new ArrayList<Integer>(4);
        pos.set(0, startLine); pos.set(1, startCol); pos.set(2, endLine); pos.set(3, endCol);
        List<List<Integer>> copy = _classes.get(name);
        copy.add(0, pos);
        _classes.put(name, copy);
        return true;
    }
    public boolean insertVariableAccess(String name, Integer startLine, Integer startCol, Integer endLine, Integer endCol) {
        List<Integer> pos = new ArrayList<Integer>(4);
        pos.set(0, startLine); pos.set(1, startCol); pos.set(2, endLine); pos.set(3, endCol);
        List<List<Integer>> copy = _classes.get(name);
        copy.add(pos);
        _classes.put(name, copy);
        return true;
    }

    public String toString() {

    }
}

