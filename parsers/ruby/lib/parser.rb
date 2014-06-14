require 'ripper'

def parse
    source = STDIN.read
    walker = TreeWalker.new(source)
    walker.parse
    puts walker.to_s
end

class TreeWalker < Ripper::SexpBuilder
    attr_accessor :symbols

    def initialize(source)
        ns_hash = Hash.new {
            |hash, key|
            hash[key] = {
                :assignments => [], :uses => []
            }
        }
        class_hash = ns_hash.clone
        function_hash = ns_hash.clone
        var_hash = ns_hash.clone

        @symbols = {
            :namespaces => ns_hash,
            :classes    => class_hash,
            :functions  => function_hash,
            :vars       => var_hash
        }

        super(source)
    end

    def block_position(node)
        last_node = node[0]
        while last_node.is_a? Array
            sp = last_node
            while not (last_el = last_node[last_node.count - 1]) or
                (last_el.is_a? Array and last_el[last_el.count - 1].nil?)
                last_node = last_node[0..last_node.count - 2]
            end
            last_node = last_el
        end

        last_node = node[0]
        while last_node.is_a? Array
            ep = last_node
            while not (last_el = last_node[last_node.count - 1]) or
                (last_el.is_a? Array and last_el[last_el.count - 1].nil?)
                last_node = last_node[0..last_node.count - 2]
            end
            last_node = last_el
        end

        if sp == ep
            return sp + [sp[0], -1]
        end
        return sp + ep
    end

    def on_module(*node)
        pos = block_position(node)
        name = node[0][1][1]
        symbols[:namespaces][name][:assignments] << pos
        return node
    end

    def on_class(*node)
        pos = block_position(node)
        name = node[0][1][1]
        symbols[:classes][name][:assignments] << pos
        return node
    end

    def on_def(*node)
        pos = block_position(node)
        name = node[0][1]
        symbols[:functions][name][:assignments] << pos
        return node
    end

    def on_call(*node)
        pos = block_position(node)
        name = node[node.count - 1][1]
        symbols[:functions][name][:uses] << pos
        return node
    end

    def on_vcall(*node)
        pos = block_position(node)
        name = node[0][1]
        symbols[:functions][name][:uses] << pos
        return node
    end

    def on_assign(*node)
        pos = block_position(node)
        return node if not node[0][0].is_a? Array
        name = node[0][0][1]
        symbols[:vars][name][:assignments] << pos
        return node
    end

    def on_var_field(*node)
        pos = block_position(node)
        name = node[0][1]
        symbols[:vars][name][:uses] << pos
        return node
    end

    def on_var_ref(*node)
        pos = block_position(node)
        name = node[0][1]
        symbols[:vars][name][:uses] << pos
        return node
    end

    def on_command(*node)
        # catch require statements
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
