package org.bitshift.parsing.parsers;

import java.util.Map;

import org.eclipse.jdt.core.JavaCore;
import org.eclipse.jdt.core.dom.AST;
import org.eclipse.jdt.core.dom.ASTParser;
import org.eclipse.jdt.core.dom.ASTVisitor;
import org.eclipse.jdt.core.dom.CompilationUnit;
import org.eclipse.jdt.core.dom.ClassInstanceCreation;
import org.eclipse.jdt.core.dom.FieldAccess
import org.eclipse.jdt.core.dom.FieldDeclaration;
import org.eclipse.jdt.core.dom.MethodDeclaration;
import org.eclipse.jdt.core.dom.MethodInvocation;
import org.eclipse.jdt.core.dom.PackageDeclaration;
import org.eclipse.jdt.core.dom.Statement;
import org.eclipse.jdt.core.dom.TypeDeclaration;
import org.eclipse.jdt.core.dom.VariableDeclarationStatement

import org.bitshift.parsing.parsers.Parser;
import org.bitshift.parsing.symbols.Symbols;
import org.bitshift.parsing.symbols.JavaSymbols;

/*TODO: Work on parsing partial java code.
 * Make sure all names of nodes are strings.*/
public class JavaParser extends Parser {

    @Override
    public Symbols genSymbols() {
        char[] source = this.source.toCharArray();

        ASTParser parser = ASTParser.newParser(AST.JLS3);
        parser.setSource(source);

        Map options = JavaCore.getOptions();
        parser.setCompilerOptions(options);

        //Work on parsing partial java code later
        CompilationUnit result = (CompilationUnit) parser.createAST(null);

        ASTVisitor visitor = new NodeVisitor(result);
        result.accept(visitor);

        return visitor.symbols;
    }

    class NodeVisitor extends ASTVisitor {

        protected Symbols symbols;
        protected CompilationUnit compUnit;

        public NodeVisitor(CompilationUnit compUnit) {
            symbols = new JavaSymbols();
        }

        public boolean visit(ClassInstanceCreation node) {
            String name = node.getType().getName();
            int sl = compUnit.getLineNumber(node.getStartPosition()) - 1;
            int sc = compUnit.getColumnNumber(node.getStartPosition()) - 1;
            symbols.insertClassInstance(name, sl, sc, null, null);
            return true;
        }

        public boolean visit(FieldAccess node) {
            String name = node.getName();
            int sl = compUnit.getLineNumber(node.getStartPosition()) - 1;
            int sc = compUnit.getColumnNumber(node.getStartPosition()) - 1;
            symbols.insertFieldAccess(name, sl, sc, null, null);
            return true;
        }

        public boolean visit(FieldDeclaration node) {
            String name = node.getType().getName();
            int sl = compUnit.getLineNumber(node.getStartPosition()) - 1;
            int sc = compUnit.getColumnNumber(node.getStartPosition()) - 1;
            symbols.insertFieldDeclaration(name, sl, sc, null, null);
            return true;
        }

        public boolean visit(MethodDeclaration node) {
            String name = node.getName();
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
            String name = node.getName();
            int sl = compUnit.getLineNumber(node.getStartPosition()) - 1;
            int sc = compUnit.getColumnNumber(node.getStartPosition()) - 1;
            symbols.insertMethodInvocation(name, sl, sc, null, null);
            return true;
        }

        public boolean visit(PackageDeclaration node) {
            symbols.setPackage(node.getName());
            return true;
        }

        public boolean visit(TypeDeclaration node) {
            String name = node.getName();
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
            String name = node.getType().getName();
            int sl = compUnit.getLineNumber(node.getStartPosition()) - 1;
            int sc = compUnit.getColumnNumber(node.getStartPosition()) - 1;
            symbols.insertVariableDeclaration(name, sl, sc, null, null);
            return true;
        }

    }
}
