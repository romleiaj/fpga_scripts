import re
import collections
import argparse


def create_testbench(fname):
    infile = open(fname)

    flags = {'port':0, 'generic':0}
    data = collections.defaultdict(list)
    gen = 0

    for line in infile:
        header = re.search(r"^[\t\s\r\n]*library|^[\t\s\r\n]*use",
                        line, re.IGNORECASE)
        entity = re.search(r"^[\t\s\r\n]*entity(.*)is", line, re.IGNORECASE)
        generic = re.search(r"^[\t\s\r\n]*generic[\t\s\r\n]*\(", line,
                        re.IGNORECASE)
        port = re.search(r"^[\t\s\r\n]*port[\t\s\r\n]*\(", line,
                        re.IGNORECASE)
        port_end = re.search(r"^[\t\s\r\n]*\);", line,
                        re.IGNORECASE)
        port_name = re.search(r"^[\t\s\r\n]*(.*):[\t\s\r\n]*"
                              r"(\w*)[\t\s\r\n]*(.*)", line, re.IGNORECASE)

        if flags['port']:
            if port_end:
                flags['port'] = False
            else:
                data['signal'].append(line.strip())
                types = port_name.group(3).strip()
                if types[-1] == ';':
                    typ = types[0:-1]
                data['signal_names'].append(port_name.group(1).strip())
                data['signal_dirs'].append(port_name.group(2).strip())
                data['signal_types'].append(typ)
        if flags['generic']:
            if port_end:
                flags['generic'] = False
            else:
                data['generic'].append(line.strip())
                gen += 1

        if header:
            data['header'].append(line.strip())
        elif entity:
            data['entity'].append(entity.group(1).strip())
        elif generic:
            flags['generic'] = True
        elif port:
            flags['port'] = True
    infile.close()

    write_tb(data, fname, gen)


def write_tb(data, fname, gen):
    of = open("tb_%s" % fname, "w+")

    for line in data['header']:
        of.write("%s\n" % line)
    of.write("\nentity %s_tb is\nend entity\n\n" % data['entity'][0])
    of.write("architecture behavioral of %s_tb is\n" % data['entity'][0])
    of.write("\tcomponent %s is\n" % data['entity'][0])
    if gen > 0:
        of.write("\tgeneric(\n")
        for line in data['generic']:
            of.write("\t\t%s\n" % line)
        of.write("\t\t);\n")
    of.write("\tport(\n")

    for line in data['signal']:
        of.write("\t\t\t%s\n" % line)

    of.write("\t\t);\n\tend component;\n\n")

    for name, logic in zip(data['signal_names'], data['signal_types']):
        of.write("\tsignal %s: %s;\n" % (name, logic))

    of.write("\nbegin\n\tclk <= not clk after 5 ns;\n\n\tUUT: %s\n\t\t"
             "port map(\n" % data['entity'][0])

    for name in data['signal_names']:
        of.write("\t\t\t%s=>%s,\n" % (name, name))

    of.write("\t\t\t);\n\nprocess\nbegin\n\n\t\twait;\nend process;\nend behavioral;")
    of.close()
    
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("input_fname", help="VHDL file to read.", type=str)
    args = parser.parse_args()
    create_testbench(args.input_fname)
    
