package org.bitshift.parsing.parsers;

import java.util.Map;

import org.eclipse.jdt.core.JavaCore;
import org.eclipse.jdt.core.dom.AST;
import org.eclipse.jdt.core.dom.ASTParser;
import org.eclipse.jdt.core.dom.ASTVisitor;
import org.eclipse.jdt.core.dom.CompilationUnit;
import org.eclipse.jdt.core.dom.Assignment;
import org.eclipse.jdt.core.dom.ClassInstanceCreation;
import org.eclipse.jdt.core.dom.FieldAccess
import org.eclipse.jdt.core.dom.FieldDeclaration;
import org.eclipse.jdt.core.dom.MethodDeclaration;
import org.eclipse.jdt.core.dom.MethodInvocation;
import org.eclipse.jdt.core.dom.PackageDeclaration;
import org.eclipse.jdt.core.dom.TypeDeclaration;
import org.eclipse.jdt.core.dom.VariableDeclarationStatement

import org.bitshift.parsing.parsers.Parser;
import org.bitshift.parsing.symbols.Symbols;
import org.bitshift.parsing.symbols.JavaSymbols;

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

        ASTVisitor visitor = new NodeVisitor();
        result.accept(visitor);

        return visitor.symbols;
    }

    class NodeVisitor extends ASTVisitor {

        protected Symbols symbols;

        public NodeVisitor() {
            symbols = new JavaSymbols();
        }

        public boolean visit(Assignment node) {
        
        }

        public boolean visit(ClassInstanceCreation node) {
        
        }

        public boolean visit(FieldAccess node) {
        
        }

        public boolean visit(FieldDeclaration node) {
        
        }

        public boolean visit(MethodDeclaration node) {
        
        }

        public boolean visit(MethodInvocation node) {
        
        }

        public boolean visit(PackageDeclaration node) {
        
        }

        public boolean visit(TypeDeclaration node) {
        
        }

        public boolean visit(VariableDeclarationStatement node) {
        
        }

    }
}
