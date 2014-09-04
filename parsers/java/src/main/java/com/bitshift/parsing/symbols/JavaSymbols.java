package com.bitshift.parsing.symbols;

import java.util.HashMap;
import java.util.ArrayList;
import com.bitshift.parsing.symbols.Symbols;

/*TODO: Overwrite toString.*/
public class JavaSymbols extends Symbols {

    private String _packageName;
    private HashMap<String, HashMap<String, Object>> _classes;
    private HashMap<String, HashMap<String, Object>> _interfaces;
    private HashMap<String, HashMap<String, Object>> _methods;
    private HashMap<String, HashMap<String, Object>> _vars;
    private HashMap<String, HashMap<String, Object>> _imports;

    private final String assignKey = "\"assignments\"";
    private final String useKey = "\"uses\"";

    public JavaSymbols() {
        _packageName = null;
        _classes = new HashMap<String, HashMap<String, Object>>();
        _interfaces = new HashMap<String, HashMap<String, Object>>();
        _methods = new HashMap<String, HashMap<String, Object>>();
        _vars = new HashMap<String, HashMap<String, Object>>();
        _imports = new HashMap<String, HashMap<String, Object>>();
    }

    public boolean setPackage(String name) {
        _packageName = name;
        return true;
    }

    public boolean insertClassDeclaration(String name, HashMap<String, Object> data) {
        ArrayList<Object> assignments = new ArrayList<Object>(10);
        ArrayList<Object> uses = new ArrayList<Object>(10);
        HashMap<String, Object> klass = new HashMap<String, Object>();

        assignments.add(data.get("coord"));
        klass.put(assignKey, assignments);
        klass.put(useKey, uses);

        this._classes.put(name, klass);
        return true;
    }

    public boolean insertInterfaceDeclaration(String name, HashMap<String, Object> data) {
        ArrayList<Object> assignments = new ArrayList<Object>(10);
        ArrayList<Object> uses = new ArrayList<Object>(10);
        HashMap<String, Object> klass = new HashMap<String, Object>();

        assignments.add(data.get("coord"));
        klass.put(assignKey, assignments);
        klass.put(useKey, uses);

        this._interfaces.put(name, klass);
        return true;
    }

    public boolean insertMethodDeclaration(String name, HashMap<String, Object> data) {
        HashMap<String, Object> method = this._methods.get(name);
        if (method == null) {
            method = new HashMap<String, Object>();
            ArrayList<Object> assignments = new ArrayList<Object>(10);
            ArrayList<Object> uses = new ArrayList<Object>(10);

            assignments.add(data.get("coord"));
            method.put(assignKey, assignments);
            method.put(useKey, uses);
        } else {
            ArrayList<Object> assignments = (ArrayList<Object>)method.get(assignKey);

            assignments.add(data.get("coord"));
            method.put(assignKey, assignments);
        }

        this._methods.put(name, method);
        return true;
    }
    public boolean insertMethodInvocation(String name, HashMap<String, Object> data) {
        HashMap<String, Object> method = this._methods.get(name);
        if (method == null) {
            method = new HashMap<String, Object>();
            ArrayList<Object> assignments = new ArrayList<Object>(10);
            ArrayList<Object> uses = new ArrayList<Object>(10);

            uses.add(data.get("coord"));
            method.put(assignKey, assignments);
            method.put(useKey, uses);
        } else {
            ArrayList<Object> uses = (ArrayList<Object>)method.get(useKey);

            uses.add(data.get("coord"));
            method.put(useKey, uses);
        }

        this._methods.put(name, method);
        return true;
    }

    public boolean insertVariableDeclaration(String name, HashMap<String, Object> data) {
        HashMap<String, Object> var = this._vars.get(name);
        if (var == null) {
            var = new HashMap<String, Object>();
            ArrayList<Object> assignments = new ArrayList<Object>(10);
            ArrayList<Object> uses = new ArrayList<Object>(10);

            assignments.add(data.get("coord"));
            var.put(assignKey, assignments);
            var.put(useKey, uses);
        } else {
            ArrayList<Object> assignments = (ArrayList<Object>)var.get(assignKey);

            assignments.add(data.get("coord"));
            var.put(assignKey, assignments);
        }

        this._vars.put(name, var);
        return true;
    }

    public boolean insertVariableAccess(String name, HashMap<String, Object> data) {
        HashMap<String, Object> var = this._vars.get(name);
        if (var == null) {
            var = new HashMap<String, Object>();
            ArrayList<Object> assignments = new ArrayList<Object>(10);
            ArrayList<Object> uses = new ArrayList<Object>(10);

            uses.add(data.get("coord"));
            var.put(assignKey, assignments);
            var.put(useKey, uses);
        } else {
            ArrayList<Object> uses = (ArrayList<Object>)var.get(useKey);

            uses.add(data.get("coord"));
            var.put(useKey, uses);
        }

        this._vars.put(name, var);
        return true;
    }

    public boolean insertImportStatement(String name, HashMap<String, Object> data) {
        HashMap<String, Object> lib = this._imports.get(name);
        if (lib == null) {
            lib = new HashMap<String, Object>();
            ArrayList<Object> assignments = new ArrayList<Object>(10);
            ArrayList<Object> uses = new ArrayList<Object>(10);

            uses.add(data.get("coord"));
            lib.put(assignKey, assignments);
            lib.put(useKey, uses);
        } else {
            ArrayList<Object> uses = (ArrayList<Object>)lib.get(useKey);

            uses.add(data.get("coord"));
            lib.put(useKey, uses);
        }

        this._imports.put(name, lib);
        return true;
    }

    public String toString() {
        StringBuilder builder = new StringBuilder();
        builder.append("\"classes\":" + this._classes + ",");
        builder.append("\"interfaces\":" + this._interfaces + ",");
        builder.append("\"functions\":" + this._methods + ",");
        builder.append("\"vars\":" + this._vars + ",");
        builder.append("\"imports\":" + this._imports + ",");

        String s = builder.toString().replaceAll("=", ":");
        s = s.substring(0, s.length() - 1);
        return "{" + s + "}";
    }
}

