require 'socket'
require 'ruby_parser'
require 'sexp_processor'

module Bitshift
    class Parser
        def initialize(source)
            @source = source
        end

        def parse
            parser = RubyParser.new
            tree = parser.parse(@source)
            offset = tree.line - 1
            processor = NodeVisitor.new offset, tree
            processor.process(tree)
            return processor.to_s
        end
    end

    class NodeVisitor < SexpProcessor
        attr_accessor :symbols
        attr_accessor :offset

        def initialize(offset, tree)
            super()

            module_hash = Hash.new {|hash, key| hash[key] = Hash.new}
            class_hash = module_hash.clone
            function_hash = Hash.new {|hash, key| hash[key] = { calls: [] } }
            var_hash = Hash.new {|hash, key| hash[key] = [] }

            @require_empty = false
            @offset = offset
            @symbols = {
                modules: module_hash,
                classes: class_hash,
                functions: function_hash,
                vars: var_hash
            }
        end

        def block_position(exp)
            pos = Hash.new
            end_ln = (start_ln = exp.line - offset)
            cur_exp = exp

            while cur_exp.is_a? Sexp
                end_ln = cur_exp.line - offset
                cur_exp = cur_exp.last
                break if cur_exp == nil
            end

            pos[:coord] = {
                start_ln: start_ln,
                end_ln: end_ln }
            return pos
        end

        def statement_position(exp)
            pos = Hash.new
            end_ln = start_ln = exp.line - offset

            pos[:coord] = {
                start_ln: start_ln,
                end_ln: end_ln }
            return pos
        end

        def process_module(exp)
            pos = block_position(exp)
            exp.shift
            name = exp.shift
            symbols[:modules][name] = pos
            exp.each_sexp {|s| process(s)}
            return exp.clear
        end

        def process_class(exp)
            pos = block_position(exp)
            exp.shift
            name = exp.shift
            symbols[:classes][name] = pos
            exp.each_sexp {|s| process(s)}
            return exp.clear
        end

        def process_defn(exp)
            pos = block_position(exp)
            exp.shift
            name = exp.shift
            symbols[:functions][name][:declaration] = pos
            exp.each_sexp {|s| process(s)}
            return exp.clear
        end

        def process_call(exp)
            pos = statement_position(exp)
            exp.shift
            exp.shift
            name = exp.shift
            symbols[:functions][name][:calls] << pos
            exp.each_sexp {|s| process(s)}
            return exp.clear
        end

        def process_iasgn(exp)
            pos = statement_position(exp)
            exp.shift
            name = exp.shift
            symbols[:vars][name] << pos
            exp.each_sexp {|s| process(s)}
            return exp.clear
        end

        def process_lasgn(exp)
            pos = statement_position(exp)
            exp.shift
            name = exp.shift
            symbols[:vars][name] << pos
            exp.each_sexp {|s| process(s)}
            return exp.clear
        end

        def to_s
            str = symbols.to_s
            str = str.gsub(/:(\w*)=>/, '"\1":')
            return str
        end
    end
end
