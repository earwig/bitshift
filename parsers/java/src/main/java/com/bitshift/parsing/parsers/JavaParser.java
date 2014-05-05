package com.bitshift.parsing.parsers;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Stack;

import java.net.Socket;

import org.eclipse.jdt.core.JavaCore;
import org.eclipse.jdt.core.dom.AST;
import org.eclipse.jdt.core.dom.ASTParser;
import org.eclipse.jdt.core.dom.ASTVisitor;
import org.eclipse.jdt.core.dom.CompilationUnit;
import org.eclipse.jdt.core.dom.ClassInstanceCreation;
import org.eclipse.jdt.core.dom.FieldDeclaration;
import org.eclipse.jdt.core.dom.MethodDeclaration;
import org.eclipse.jdt.core.dom.MethodInvocation;
import org.eclipse.jdt.core.dom.Name;
import org.eclipse.jdt.core.dom.PackageDeclaration;
import org.eclipse.jdt.core.dom.QualifiedName;
import org.eclipse.jdt.core.dom.SimpleName;
import org.eclipse.jdt.core.dom.Statement;
import org.eclipse.jdt.core.dom.TypeDeclaration;
import org.eclipse.jdt.core.dom.VariableDeclarationFragment;

import com.bitshift.parsing.parsers.Parser;
import com.bitshift.parsing.symbols.Symbols;
import com.bitshift.parsing.symbols.JavaSymbols;

/*TODO: Work on parsing partial java code.*/
public class JavaParser extends Parser {

    public JavaParser(Socket clientSocket) {
        super(clientSocket);
    }

    @Override
    protected Symbols genSymbols() {
        char[] source = this.readFromClient().toCharArray();

        ASTParser parser = ASTParser.newParser(AST.JLS3);
        parser.setSource(source);

        Map options = JavaCore.getOptions();
        parser.setCompilerOptions(options);

        CompilationUnit root = (CompilationUnit) parser.createAST(null);

        NodeVisitor visitor = new NodeVisitor(root);
        root.accept(visitor);

        return visitor.symbols;
    }

    @Override
    public void run() {
        JavaSymbols symbols = (JavaSymbols) this.genSymbols();
        writeToClient(symbols.toString());
    }

    class NodeVisitor extends ASTVisitor {

        protected CompilationUnit root;
        protected JavaSymbols symbols;
        private Stack<HashMap<String, Object>> _cache;

        public NodeVisitor(CompilationUnit root) {
            this.root = root;
            this.symbols = new JavaSymbols();
            this._cache = new Stack<HashMap<String, Object>>();
        }

        public boolean visit(FieldDeclaration node) {
            HashMap<String, Object> data = new HashMap<String, Object>();
            int sl = this.root.getLineNumber(node.getStartPosition());
            int sc = this.root.getColumnNumber(node.getStartPosition());

            data.put("coord", Symbols.createCoord(sl, sc, -1, -1));
            this._cache.push(data);
            return true;
        }

        public void endVisit(FieldDeclaration node) {
            HashMap<String, Object> data = this._cache.pop();
            String name = (String)data.remove("name");
            this.symbols.insertFieldDeclaration(name, data);
        }

        public boolean visit(MethodDeclaration node) {
            HashMap<String, Object> data = new HashMap<String, Object>();
            Name nameObj = node.getName();
            String name = nameObj.isQualifiedName() ?
                ((QualifiedName) nameObj).getFullyQualifiedName() :
                ((SimpleName) nameObj).getIdentifier();
            List<Statement> statements = node.getBody().statements();

            int sl = this.root.getLineNumber(node.getStartPosition());
            int sc = this.root.getColumnNumber(node.getStartPosition());
            Integer el = -1;
            Integer ec = -1;

            if (statements.size() > 0) {
                Statement last = statements.get(statements.size() - 1);
                el = this.root.getLineNumber(last.getStartPosition());
                ec = this.root.getColumnNumber(last.getStartPosition());
            }

            data.put("coord", Symbols.createCoord(sl, sc, el, ec));
            data.put("name", name);
            this._cache.push(data);
            return true;
        }

        public void endVisit(MethodDeclaration node) {
            HashMap<String, Object> data = this._cache.pop();
            String name = (String)data.remove("name");
            this.symbols.insertMethodDeclaration(name, data);
        }

        public boolean visit(MethodInvocation node) {
            HashMap<String, Object> data = new HashMap<String, Object>();
            Name nameObj = node.getName();
            String name = nameObj.isQualifiedName() ?
                ((QualifiedName) nameObj).getFullyQualifiedName() :
                ((SimpleName) nameObj).getIdentifier();
            int sl = this.root.getLineNumber(node.getStartPosition());
            int sc = this.root.getColumnNumber(node.getStartPosition());

            data.put("coord", Symbols.createCoord(sl, sc, -1, -1));
            data.put("name", name);
            this._cache.push(data);
            return true;
        }

        public void endVisit(MethodInvocation node) {
            HashMap<String, Object> data = this._cache.pop();
            String name = (String)data.remove("name");
            this.symbols.insertMethodInvocation(name, data);
        }

        public boolean visit(PackageDeclaration node) {
            HashMap<String, Object> data = new HashMap<String, Object>();
            this._cache.push(data);
            return true;
        }

        public void endVisit(PackageDeclaration node) {
            HashMap<String, Object> data = this._cache.pop();
            String name = (String)data.remove("name");
            this.symbols.setPackage(name);
        }

        public boolean visit(TypeDeclaration node) {
            HashMap<String, Object> data = new HashMap<String, Object>();

            int sl = this.root.getLineNumber(node.getStartPosition());
            int sc = this.root.getColumnNumber(node.getStartPosition());

            data.put("coord", Symbols.createCoord(sl, sc, -1, -1));
            this._cache.push(data);
            return true;
        }

        public void endVisit(TypeDeclaration node) {
            HashMap<String, Object> data = this._cache.pop();
            String name = (String)data.remove("name");

            if (node.isInterface()) {
                this.symbols.insertInterfaceDeclaration(name, data);
            } else {
                this.symbols.insertClassDeclaration(name, data);
            }
        }

        public boolean visit(VariableDeclarationFragment node) {
            HashMap<String, Object> data = new HashMap<String, Object>();
            int sl = this.root.getLineNumber(node.getStartPosition());
            int sc = this.root.getColumnNumber(node.getStartPosition());

            data.put("coord", Symbols.createCoord(sl, sc, -1, -1));
            this._cache.push(data);
            return true;
        }

        public void endVisit(VariableDeclarationFragment node) {
            HashMap<String, Object> data = this._cache.pop();
            String name = (String)data.remove("name");
            this.symbols.insertVariableDeclaration(name, data);
        }

        public boolean visit(QualifiedName node) {
            if (!this._cache.empty()) {
                HashMap<String, Object> data = this._cache.pop();

                if(!data.containsKey("name")) {
                    String name = node.getFullyQualifiedName();
                    data.put("name", name);
                }

                this._cache.push(data);
            }
            return true;
        }

        public boolean visit(SimpleName node) {
            if (!this._cache.empty()) {
                HashMap<String, Object> data = this._cache.pop();

                if(!data.containsKey("name")) {
                    String name = node.getIdentifier();
                    data.put("name", name);
                }

                this._cache.push(data);
            }
            return true;
        }

    }
}
