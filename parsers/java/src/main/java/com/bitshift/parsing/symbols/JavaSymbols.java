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
    private HashMap<String, HashMap<String, Object>> _fields;
    private HashMap<String, HashMap<String, Object>> _vars;

    public JavaSymbols() {
        _packageName = null;
        _classes = new HashMap<String, HashMap<String, Object>>();
        _interfaces = new HashMap<String, HashMap<String, Object>>();
        _methods = new HashMap<String, HashMap<String, Object>>();
        _fields = new HashMap<String, HashMap<String, Object>>();
        _vars = new HashMap<String, HashMap<String, Object>>();
    }

    public boolean setPackage(String name) {
        _packageName = name;
        return true;
    }

    public boolean insertClassDeclaration(String name, HashMap<String, Object> data) {
        this._classes.put(name, data);
        return true;
    }

    public boolean insertInterfaceDeclaration(String name, HashMap<String, Object> data) {
        this._interfaces.put(name, data);
        return true;
    }

    public boolean insertMethodDeclaration(String name, HashMap<String, Object> data) {
        HashMap<String, Object> method = this._methods.get(name);
        if (method == null) {
            method = new HashMap<String, Object>();
            ArrayList<Object> assignments = new ArrayList<Object>(10);
            ArrayList<Object> uses = new ArrayList<Object>(10);

            assignments.add(data.get("coord"));
            method.put("assignments", assignments);
            method.put("uses", uses);
        } else {
            ArrayList<Object> assignments = (ArrayList<Object>)method.get("assignments");

            assignments.add(data.get("coord"));
            method.put("assignments", assignments);
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
            method.put("assignments", assignments);
            method.put("uses", uses);
        } else {
            ArrayList<Object> uses = (ArrayList<Object>)method.get("uses");

            uses.add(data.get("coord"));
            method.put("uses", uses);
        }

        this._methods.put(name, method);
        return true;
    }

    public boolean insertFieldDeclaration(String name, HashMap<String, Object> data) {
        this._fields.put(name, data);
        return true;
    }

    public boolean insertVariableDeclaration(String name, HashMap<String, Object> data) {
        HashMap<String, Object> var = this._vars.get(name);
        if (var == null) {
            var = new HashMap<String, Object>();
            ArrayList<Object> assignments = new ArrayList<Object>(10);
            ArrayList<Object> uses = new ArrayList<Object>(10);

            assignments.add(data.get("coord"));
            var.put("assignments", assignments);
            var.put("uses", uses);
        } else {
            ArrayList<Object> assignments = (ArrayList<Object>)var.get("assignments");

            assignments.add(data.get("coord"));
            var.put("assignments", assignments);
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
            var.put("assignments", assignments);
            var.put("uses", uses);
        } else {
            ArrayList<Object> uses = (ArrayList<Object>)var.get("uses");

            uses.add(data.get("coord"));
            var.put("uses", uses);
        }

        this._vars.put(name, var);
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

