package org.bitshift.parsing.parsers;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Stack;

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
import org.eclipse.jdt.core.dom.VariableDeclarationStatement;

import org.bitshift.parsing.parsers.Parser;
import org.bitshift.parsing.symbols.Symbols;
import org.bitshift.parsing.symbols.JavaSymbols;

/*TODO: Work on parsing partial java code.
 * Change visits to endVisit and implement a cache*/
public class JavaParser extends Parser {

    protected JavaSymbols symbols;
    protected CompilationUnit compUnit;
    private Stack<Map<String, Object>> _cache;

    public JavaParser(String source) {
        super(source);
        this.symbols = new JavaSymbols();
        this._cache = new Stack<Map<String, Object>>();
    }

    @Override
    public Symbols genSymbols() {
        char[] source = this.source.toCharArray();

        ASTParser parser = ASTParser.newParser(AST.JLS3);
        parser.setSource(source);

        Map options = JavaCore.getOptions();
        parser.setCompilerOptions(options);

        //Work on parsing partial java code later
        this.compUnit = (CompilationUnit) parser.createAST(null);

        ASTVisitor visitor = new NodeVisitor();
        this.compUnit.accept(visitor);

        return this.symbols;
    }

    class NodeVisitor extends ASTVisitor {

        public boolean visit(ClassInstanceCreation node) {
            Type typeObj = node.getType();
            Name nameObj = typeObj.isQualifiedType() ? ((QualifiedType) typeObj).getName() : ((SimpleType) typeObj).getName();
            String name = nameObj.isQualifiedName() ? ((QualifiedName)nameObj).getFullyQualifiedName() : ((SimpleName)nameObj).getIdentifier();

            int sl = compUnit.getLineNumber(node.getStartPosition()) - 1;
            int sc = compUnit.getColumnNumber(node.getStartPosition()) - 1;

            symbols.insertClassInstance(name, sl, sc, null, null);
            return true;
        }

        public boolean visit(FieldAccess node) {
            Name nameObj = node.getName();
            String name = nameObj.isQualifiedName() ? ((QualifiedName)nameObj).getFullyQualifiedName() : ((SimpleName)nameObj).getIdentifier();

            int sl = compUnit.getLineNumber(node.getStartPosition()) - 1;
            int sc = compUnit.getColumnNumber(node.getStartPosition()) - 1;

            symbols.insertFieldAccess(name, sl, sc, null, null);
            return true;
        }

        public boolean visit(FieldDeclaration node) {
            Type typeObj = node.getType();
            Name nameObj = typeObj.isQualifiedType() ? ((QualifiedType) typeObj).getName() : ((SimpleType) typeObj).getName();
            String name = nameObj.isQualifiedName() ? ((QualifiedName)nameObj).getFullyQualifiedName() : ((SimpleName)nameObj).getIdentifier();

            int sl = compUnit.getLineNumber(node.getStartPosition()) - 1;
            int sc = compUnit.getColumnNumber(node.getStartPosition()) - 1;

            symbols.insertFieldDeclaration(name, sl, sc, null, null);
            return true;
        }

        public boolean visit(MethodDeclaration node) {
            Name nameObj = node.getName();
            String name = nameObj.isQualifiedName() ? ((QualifiedName)nameObj).getFullyQualifiedName() : ((SimpleName)nameObj).getIdentifier();
            List<Statement> statements = node.getBody().statements();
            Statement last = statements.get(statements.size() - 1);

            int sl = compUnit.getLineNumber(node.getStartPosition()) - 1;
            int sc = compUnit.getColumnNumber(node.getStartPosition()) - 1;
            int el = compUnit.getLineNumber(last.getStartPosition()) - 1;
            int ec = compUnit.getColumnNumber(last.getStartPosition()) - 1;

            symbols.insertMethodDeclaration(name, sl, sc, el, ec);
            return true;
        }

        public boolean visit(MethodInvocation node) {
            Name nameObj = node.getName();
            String name = nameObj.isQualifiedName() ? ((QualifiedName)nameObj).getFullyQualifiedName() : ((SimpleName)nameObj).getIdentifier();

            int sl = compUnit.getLineNumber(node.getStartPosition()) - 1;
            int sc = compUnit.getColumnNumber(node.getStartPosition()) - 1;

            symbols.insertMethodInvocation(name, sl, sc, null, null);
            return true;
        }

        public boolean visit(PackageDeclaration node) {
            Name nameObj = node.getName();
            String name = nameObj.isQualifiedName() ? ((QualifiedName)nameObj).getFullyQualifiedName() : ((SimpleName)nameObj).getIdentifier();

            symbols.setPackage(name);
            return true;
        }

        public boolean visit(TypeDeclaration node) {
            Name nameObj = node.getName();
            String name = nameObj.isQualifiedName() ? ((QualifiedName)nameObj).getFullyQualifiedName() : ((SimpleName)nameObj).getIdentifier();

            int sl = compUnit.getLineNumber(node.getStartPosition()) - 1;
            int sc = compUnit.getColumnNumber(node.getStartPosition()) - 1;

            if (node.isInterface()) {
                symbols.insertInterfaceDeclaration(name, sl, sc, null, null);
            } else {
                symbols.insertClassDeclaration(name, sl, sc, null, null);
            }
            return true;
        }

        public boolean visit(VariableDeclarationStatement node) {
            Type typeObj = node.getType();
            Name nameObj = typeObj.isQualifiedType() ? ((QualifiedType) typeObj).getName() : ((SimpleType) typeObj).getName();
            String name = nameObj.isQualifiedName() ? ((QualifiedName)nameObj).getFullyQualifiedName() : ((SimpleName)nameObj).getIdentifier();

            int sl = compUnit.getLineNumber(node.getStartPosition()) - 1;
            int sc = compUnit.getColumnNumber(node.getStartPosition()) - 1;
            symbols.insertVariableDeclaration(name, sl, sc, null, null);
            return true;
        }

    }
}
