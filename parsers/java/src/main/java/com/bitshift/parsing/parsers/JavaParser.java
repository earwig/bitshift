package com.bitshift.parsing.parsers;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Stack;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.io.IOException;

import java.net.Socket;

import org.eclipse.jdt.core.JavaCore;
import org.eclipse.jdt.core.dom.AST;
import org.eclipse.jdt.core.dom.ASTParser;
import org.eclipse.jdt.core.dom.ASTVisitor;
import org.eclipse.jdt.core.dom.CompilationUnit;
import org.eclipse.jdt.core.dom.ClassInstanceCreation;
import org.eclipse.jdt.core.dom.FieldAccess;
import org.eclipse.jdt.core.dom.FieldDeclaration;
import org.eclipse.jdt.core.dom.MethodDeclaration;
import org.eclipse.jdt.core.dom.MethodInvocation;
import org.eclipse.jdt.core.dom.Name;
import org.eclipse.jdt.core.dom.PackageDeclaration;
import org.eclipse.jdt.core.dom.QualifiedName;
import org.eclipse.jdt.core.dom.QualifiedType;
import org.eclipse.jdt.core.dom.SimpleName;
import org.eclipse.jdt.core.dom.SimpleType;
import org.eclipse.jdt.core.dom.Statement;
import org.eclipse.jdt.core.dom.Type;
import org.eclipse.jdt.core.dom.TypeDeclaration;
import org.eclipse.jdt.core.dom.VariableDeclarationFragment;

import com.bitshift.parsing.parsers.Parser;
import com.bitshift.parsing.symbols.Symbols;
import com.bitshift.parsing.symbols.JavaSymbols;

/*TODO: Work on parsing partial java code.
 * Change visits to endVisit and implement a cache for more concise code structure.
 * Get rid of unecessary imports.
 * Fix column and line numbers.*/
public class JavaParser extends Parser {

    public JavaParser(Socket clientSocket) {
        super(clientSocket);
    }

    private String readFromClient() {
        String fromClient = "";

        try {
            BufferedReader clientReader = new BufferedReader(
                    new InputStreamReader(this.clientSocket.getInputStream()));

            int bytes = Integer.parseInt(clientReader.readLine());
            System.out.println(bytes);

            StringBuilder builder = new StringBuilder();
            int i = 0;

            while(i < bytes) {
                char aux = (char)clientReader.read();
                builder.append(aux);
                i++;
            }

            fromClient = builder.toString();

        } catch (IOException ex) {
        }

        return fromClient;
    }

    private void writeToClient(String toClient) {
        try {
            PrintWriter clientWriter = new PrintWriter(
                    this.clientSocket.getOutputStream(), true);

            clientWriter.println(toClient);
        } catch (IOException ex) {
        }
    }

    @Override
    public Symbols genSymbols() {
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
        System.out.println(symbols.toString());
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

        public boolean visit(ClassInstanceCreation node) {
            return true;
        }

        public boolean visit(FieldAccess node) {
            Name nameObj = node.getName();
            String name = nameObj.isQualifiedName() ?
                ((QualifiedName) nameObj).getFullyQualifiedName() :
                ((SimpleName) nameObj).getIdentifier();

            int sl = this.root.getLineNumber(node.getStartPosition()) - 1;
            int sc = this.root.getColumnNumber(node.getStartPosition()) - 1;

            this.symbols.insertFieldAccess(name, sl, sc, null, null);
            return true;
        }

        public boolean visit(FieldDeclaration node) {
            return true;
        }

        public boolean visit(MethodDeclaration node) {
            Name nameObj = node.getName();
            String name = nameObj.isQualifiedName() ?
                ((QualifiedName) nameObj).getFullyQualifiedName() :
                ((SimpleName) nameObj).getIdentifier();
            List<Statement> statements = node.getBody().statements();
            Statement last = statements.get(statements.size() - 1);

            int sl = this.root.getLineNumber(node.getStartPosition()) - 1;
            int sc = this.root.getColumnNumber(node.getStartPosition()) - 1;
            int el = this.root.getLineNumber(last.getStartPosition()) - 1;
            int ec = this.root.getColumnNumber(last.getStartPosition()) - 1;

            this.symbols.insertMethodDeclaration(name, sl, sc, el, ec);
            return true;
        }

        public boolean visit(MethodInvocation node) {
            Name nameObj = node.getName();
            String name = nameObj.isQualifiedName() ?
                ((QualifiedName) nameObj).getFullyQualifiedName() :
                ((SimpleName) nameObj).getIdentifier();

            int sl = this.root.getLineNumber(node.getStartPosition()) - 1;
            int sc = this.root.getColumnNumber(node.getStartPosition()) - 1;

            this.symbols.insertMethodInvocation(name, sl, sc, null, null);
            return true;
        }

        public boolean visit(PackageDeclaration node) {
            Name nameObj = node.getName();
            String name = nameObj.isQualifiedName() ?
                ((QualifiedName) nameObj).getFullyQualifiedName() :
                ((SimpleName) nameObj).getIdentifier();

            this.symbols.setPackage(name);
            return true;
        }

        public boolean visit(TypeDeclaration node) {
            Name nameObj = node.getName();
            String name = nameObj.isQualifiedName() ?
                ((QualifiedName) nameObj).getFullyQualifiedName() :
                ((SimpleName) nameObj).getIdentifier();

            int sl = this.root.getLineNumber(node.getStartPosition()) - 1;
            int sc = this.root.getColumnNumber(node.getStartPosition()) - 1;

            if (node.isInterface()) {
                this.symbols.insertInterfaceDeclaration(name, sl, sc, null, null);
            } else {
                this.symbols.insertClassDeclaration(name, sl, sc, null, null);
            }
            return true;
        }

        public boolean visit(VariableDeclarationFragment node) {
            Name nameObj = node.getName();
            String name = nameObj.isQualifiedName() ?
                ((QualifiedName) nameObj).getFullyQualifiedName() :
                ((SimpleName) nameObj).getIdentifier();

            int sl = this.root.getLineNumber(node.getStartPosition()) - 1;
            int sc = this.root.getColumnNumber(node.getStartPosition()) - 1;
            this.symbols.insertVariableDeclaration(name, sl, sc, null, null);
            return true;
        }

    }
}
