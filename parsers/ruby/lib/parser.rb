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
            return '{}' if tree.nil?

            offset = tree.line - 1
            processor = CachedWalker.new offset, tree
            processor.process(tree)
            return processor.to_s
        end
    end

    class CachedWalker < SexpProcessor
        attr_accessor :symbols
        attr_accessor :offset

        def initialize(offset, tree)
            super()

            module_hash = Hash.new {|hash, key|
                hash[key] = { assignments: [], uses: [] }}
            class_hash = module_hash.clone
            function_hash = module_hash.clone
            var_hash = module_hash.clone

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
            end_ln = (start_ln = exp.line - offset)
            cur_exp = exp

            while cur_exp.is_a? Sexp
                end_ln = cur_exp.line - offset
                cur_exp = cur_exp.last
                break if cur_exp == nil
            end

            pos = [start_ln, -1, end_ln, -1]
            return pos
        end

        def statement_position(exp)
            pos = Hash.new
            end_ln = start_ln = exp.line - offset

            pos = [start_ln, -1, end_ln, -1]
            return pos
        end

        def process_module(exp)
            pos = block_position(exp)
            exp.shift
            name = exp.shift
            symbols[:modules][name][:assignments] << pos
            exp.each_sexp {|s| process(s)}
            return exp.clear
        end

        def process_class(exp)
            pos = block_position(exp)
            exp.shift
            name = exp.shift
            symbols[:classes][name][:assignments] << pos
            exp.each_sexp {|s| process(s)}
            return exp.clear
        end

        def process_defn(exp)
            pos = block_position(exp)
            exp.shift
            name = exp.shift
            symbols[:functions][name][:assignments] << pos
            exp.each_sexp {|s| process(s)}
            return exp.clear
        end

        def process_call(exp)
            pos = statement_position(exp)
            exp.shift
            exp.shift
            name = exp.shift
            symbols[:functions][name][:uses] << pos
            exp.each_sexp {|s| process(s)}
            return exp.clear
        end

        def process_iasgn(exp)
            pos = statement_position(exp)
            exp.shift
            name = exp.shift
            symbols[:vars][name][:assignments] << pos
            exp.each_sexp {|s| process(s)}
            return exp.clear
        end

        def process_lasgn(exp)
            pos = statement_position(exp)
            exp.shift
            name = exp.shift
            symbols[:vars][name][:assignments] << pos
            exp.each_sexp {|s| process(s)}
            return exp.clear
        end

        def to_s
            new_symbols = Hash.new {|hash, key| hash[key] = Hash.new}

            symbols.each do |type, sym_list|
                sym_list.each do |name, sym|
                    new_symbols[type.to_s][name.to_s] = {
                        "assignments" => sym[:assignments],
                        "uses" => sym[:uses]}
                end
            end

            str = new_symbols.to_s
            str = str.gsub(/=>/, ":")
            return str
        end
    end
end
