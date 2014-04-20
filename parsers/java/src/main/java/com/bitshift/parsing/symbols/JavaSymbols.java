package com.bitshift.parsing.symbols;

import java.util.List;
import java.util.Map;
import java.util.HashMap;
import java.util.ArrayList;
import com.bitshift.parsing.symbols.Symbols;

/*TODO: Overwrite toString.*/
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
        pos.add(startLine); pos.add(startCol); pos.add(endLine); pos.add(endCol);
        
        List<List<Integer>> copy = (List<List<Integer>>)_classes.get(name);
        copy = (copy == null) ? new ArrayList<List<Integer>>() : copy;

        copy.add(0, pos);
        this._classes.put(name, copy);
        return true;
    }
    public boolean insertClassInstance(String name, Integer startLine, Integer startCol, Integer endLine, Integer endCol) {
        List<Integer> pos = new ArrayList<Integer>(4);
        pos.add(startLine); pos.add(startCol); pos.add(endLine); pos.add(endCol);
        
        List<List<Integer>> copy = (List<List<Integer>>)_classes.get(name);
        copy = (copy == null) ? new ArrayList<List<Integer>>() : copy;

        copy.add(pos);
        this._classes.put(name, copy);
        return true;
    }

    public boolean insertInterfaceDeclaration(String name, Integer startLine, Integer startCol, Integer endLine, Integer endCol) {
        List<Integer> pos = new ArrayList<Integer>(4);
        pos.add(startLine); pos.add(startCol); pos.add(endLine); pos.add(endCol);
        
        List<List<Integer>> copy = (List<List<Integer>>)_classes.get(name);
        copy = (copy == null) ? new ArrayList<List<Integer>>() : copy;

        copy.add(0, pos);
        this._interfaces.put(name, copy);
        return true;
    }
    public boolean insertInterfaceInstance(String name, Integer startLine, Integer startCol, Integer endLine, Integer endCol) {
        List<Integer> pos = new ArrayList<Integer>(4);
        pos.add(startLine); pos.add(startCol); pos.add(endLine); pos.add(endCol);
        
        List<List<Integer>> copy = (List<List<Integer>>)_classes.get(name);
        copy = (copy == null) ? new ArrayList<List<Integer>>() : copy;

        copy.add(pos);
        this._interfaces.put(name, copy);
        return true;
    }

    public boolean insertMethodDeclaration(String name, Integer startLine, Integer startCol, Integer endLine, Integer endCol) {
        List<Integer> pos = new ArrayList<Integer>(4);
        pos.add(startLine); pos.add(startCol); pos.add(endLine); pos.add(endCol);
        
        List<List<Integer>> copy = (List<List<Integer>>)_classes.get(name);
        copy = (copy == null) ? new ArrayList<List<Integer>>() : copy;

        copy.add(0, pos);
        this._methods.put(name, copy);
        return true;
    }
    public boolean insertMethodInvocation(String name, Integer startLine, Integer startCol, Integer endLine, Integer endCol) {
        List<Integer> pos = new ArrayList<Integer>(4);
        pos.add(startLine); pos.add(startCol); pos.add(endLine); pos.add(endCol);
        
        List<List<Integer>> copy = (List<List<Integer>>)_classes.get(name);
        copy = (copy == null) ? new ArrayList<List<Integer>>() : copy;

        copy.add(pos);
        this._methods.put(name, copy);
        return true;
    }

    public boolean insertFieldDeclaration(String name, Integer startLine, Integer startCol, Integer endLine, Integer endCol) {
        List<Integer> pos = new ArrayList<Integer>(4);
        pos.add(startLine); pos.add(startCol); pos.add(endLine); pos.add(endCol);
        
        List<List<Integer>> copy = (List<List<Integer>>)_classes.get(name);
        copy = (copy == null) ? new ArrayList<List<Integer>>() : copy;

        copy.add(0, pos);
        this._fields.put(name, copy);
        return true;
    }
    public boolean insertFieldAccess(String name, Integer startLine, Integer startCol, Integer endLine, Integer endCol) {
        List<Integer> pos = new ArrayList<Integer>(4);
        pos.add(startLine); pos.add(startCol); pos.add(endLine); pos.add(endCol);
        
        List<List<Integer>> copy = (List<List<Integer>>)_classes.get(name);
        copy = (copy == null) ? new ArrayList<List<Integer>>() : copy;

        copy.add(pos);
        this._fields.put(name, copy);
        return true;
    }

    public boolean insertVariableDeclaration(String name, Integer startLine, Integer startCol, Integer endLine, Integer endCol) {
        List<Integer> pos = new ArrayList<Integer>(4);
        pos.add(startLine); pos.add(startCol); pos.add(endLine); pos.add(endCol);
        
        List<List<Integer>> copy = (List<List<Integer>>)_classes.get(name);
        copy = (copy == null) ? new ArrayList<List<Integer>>() : copy;

        copy.add(0, pos);
        this._vars.put(name, copy);
        return true;
    }
    public boolean insertVariableAccess(String name, Integer startLine, Integer startCol, Integer endLine, Integer endCol) {
        List<Integer> pos = new ArrayList<Integer>(4);
        pos.add(startLine); pos.add(startCol); pos.add(endLine); pos.add(endCol);
        
        List<List<Integer>> copy = (List<List<Integer>>)_classes.get(name);
        copy = (copy == null) ? new ArrayList<List<Integer>>() : copy;

        copy.add(pos);
        this._vars.put(name, copy);
        return true;
    }

    public String toString() {
        StringBuilder builder = new StringBuilder();
        builder.append("classes:" + this._classes + ",");
        builder.append("interfaces:" + this._interfaces + ",");
        builder.append("methods:" + this._methods + ",");
        builder.append("fields:" + this._fields + ",");
        builder.append("vars:" + this._vars + ",");

        return "{" + builder.toString() + "}";
    }
}

