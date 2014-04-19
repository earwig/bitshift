package org.bitshift.parsing.symbols;

import java.util.List;
import java.util.Map;
import java.util.HashMap;
import java.util.ArrayList;
import org.bitshift.parsing.symbols.Symbols;

/*TODO: Overwrite toString
 * Change instance vars to HashMaps of HashMaps*/
public class JavaSymbols extends Symbols {

    private String _packageName;
    private Map<String, Object> _classes;
    private Map<String, Object> _interfaces;
    private Map<String, Object> _methods;
    private Map<String, Object> _fields;
    private Map<String, Object> _vars;

    public JavaSymbols() {
        _packageName = null;
        _classes = new HashMap<String, Object>();
        _interfaces = new HashMap<String, Object>();
        _methods = new HashMap<String, Object>();
        _fields = new HashMap<String, Object>();
        _vars = new HashMap<String, Object>();
    }

    public boolean setPackage(String name) {
        _packageName = name;
        return true;
    }

    public boolean insertClassDeclaration(String name, Integer startLine, Integer startCol, Integer endLine, Integer endCol) {
        List<Integer> pos = new ArrayList<Integer>(4);
        pos.set(0, startLine); pos.set(1, startCol); pos.set(2, endLine); pos.set(3, endCol);
        
        List<List<Integer>> copy = (List<List<Integer>>)_classes.get(name);
        copy = (copy == null) ? new ArrayList<List<Integer>>() : copy;

        copy.add(0, pos);
        _classes.put(name, copy);
        return true;
    }
    public boolean insertClassInstance(String name, Integer startLine, Integer startCol, Integer endLine, Integer endCol) {
        List<Integer> pos = new ArrayList<Integer>(4);
        pos.set(0, startLine); pos.set(1, startCol); pos.set(2, endLine); pos.set(3, endCol);
        
        List<List<Integer>> copy = (List<List<Integer>>)_classes.get(name);
        copy = (copy == null) ? new ArrayList<List<Integer>>() : copy;

        copy.add(pos);
        _classes.put(name, copy);
        return true;
    }

    public boolean insertInterfaceDeclaration(String name, Integer startLine, Integer startCol, Integer endLine, Integer endCol) {
        List<Integer> pos = new ArrayList<Integer>(4);
        pos.set(0, startLine); pos.set(1, startCol); pos.set(2, endLine); pos.set(3, endCol);
        
        List<List<Integer>> copy = (List<List<Integer>>)_classes.get(name);
        copy = (copy == null) ? new ArrayList<List<Integer>>() : copy;

        copy.add(0, pos);
        _classes.put(name, copy);
        return true;
    }
    public boolean insertInterfaceInstance(String name, Integer startLine, Integer startCol, Integer endLine, Integer endCol) {
        List<Integer> pos = new ArrayList<Integer>(4);
        pos.set(0, startLine); pos.set(1, startCol); pos.set(2, endLine); pos.set(3, endCol);
        
        List<List<Integer>> copy = (List<List<Integer>>)_classes.get(name);
        copy = (copy == null) ? new ArrayList<List<Integer>>() : copy;

        copy.add(pos);
        _classes.put(name, copy);
        return true;
    }

    public boolean insertMethodDeclaration(String name, Integer startLine, Integer startCol, Integer endLine, Integer endCol) {
        List<Integer> pos = new ArrayList<Integer>(4);
        pos.set(0, startLine); pos.set(1, startCol); pos.set(2, endLine); pos.set(3, endCol);
        
        List<List<Integer>> copy = (List<List<Integer>>)_classes.get(name);
        copy = (copy == null) ? new ArrayList<List<Integer>>() : copy;

        copy.add(0, pos);
        _classes.put(name, copy);
        return true;
    }
    public boolean insertMethodInvocation(String name, Integer startLine, Integer startCol, Integer endLine, Integer endCol) {
        List<Integer> pos = new ArrayList<Integer>(4);
        pos.set(0, startLine); pos.set(1, startCol); pos.set(2, endLine); pos.set(3, endCol);
        
        List<List<Integer>> copy = (List<List<Integer>>)_classes.get(name);
        copy = (copy == null) ? new ArrayList<List<Integer>>() : copy;

        copy.add(pos);
        _classes.put(name, copy);
        return true;
    }

    public boolean insertFieldDeclaration(String name, Integer startLine, Integer startCol, Integer endLine, Integer endCol) {
        List<Integer> pos = new ArrayList<Integer>(4);
        pos.set(0, startLine); pos.set(1, startCol); pos.set(2, endLine); pos.set(3, endCol);
        
        List<List<Integer>> copy = (List<List<Integer>>)_classes.get(name);
        copy = (copy == null) ? new ArrayList<List<Integer>>() : copy;

        copy.add(0, pos);
        _classes.put(name, copy);
        return true;
    }
    public boolean insertFieldAccess(String name, Integer startLine, Integer startCol, Integer endLine, Integer endCol) {
        List<Integer> pos = new ArrayList<Integer>(4);
        pos.set(0, startLine); pos.set(1, startCol); pos.set(2, endLine); pos.set(3, endCol);
        
        List<List<Integer>> copy = (List<List<Integer>>)_classes.get(name);
        copy = (copy == null) ? new ArrayList<List<Integer>>() : copy;

        copy.add(pos);
        _classes.put(name, copy);
        return true;
    }

    public boolean insertVariableDeclaration(String name, Integer startLine, Integer startCol, Integer endLine, Integer endCol) {
        List<Integer> pos = new ArrayList<Integer>(4);
        pos.set(0, startLine); pos.set(1, startCol); pos.set(2, endLine); pos.set(3, endCol);
        
        List<List<Integer>> copy = (List<List<Integer>>)_classes.get(name);
        copy = (copy == null) ? new ArrayList<List<Integer>>() : copy;

        copy.add(0, pos);
        _classes.put(name, copy);
        return true;
    }
    public boolean insertVariableAccess(String name, Integer startLine, Integer startCol, Integer endLine, Integer endCol) {
        List<Integer> pos = new ArrayList<Integer>(4);
        pos.set(0, startLine); pos.set(1, startCol); pos.set(2, endLine); pos.set(3, endCol);
        
        List<List<Integer>> copy = (List<List<Integer>>)_classes.get(name);
        copy = (copy == null) ? new ArrayList<List<Integer>>() : copy;

        copy.add(pos);
        _classes.put(name, copy);
        return true;
    }

    public String toString() {
        return "";
    }
}

