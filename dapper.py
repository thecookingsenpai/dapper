import os
from sys import argv as arguments


# Getting the filename
if len(arguments) < 2:
    print("[x] Usage: python3 dapper.py <file.sol> [<address> <abifile.json>]")
    os._exit(0)
    
filename = arguments[1]

# Ensuring is a sol file
if not ".sol" in filename:
    print("[x] Usage: python3 dapper.py <file.sol> [<address> <abifile.json>]")
    os._exit(-1)

# If specified, getting address and abi
if len(arguments) > 2:
    address = arguments[2]
else:
    address = "''"
    if len(arguments) > 3:
        abifile = arguments[3]
        if not(".json" in abifile):    
            print("[x] Usage: python3 dapper.py <file.sol> [<address> <abifile.json>]")
            os._exit(-2)
        abi = open(abifile, "r").read()
    else:
        abi = "[]"

# Preparing the environment

filename_js = filename.replace(".sol", ".js")

if os.path.exists(filename_js):
    os.remove(filename_js)
js_file =  open(filename_js, "a+")
js_file.write("var abi;\n")
# Invoking

with open(filename, "r") as source:
    lines = source.readlines()
    
line_buffer = ""
prefix = ""
for index in range(len(lines)):
    print("Processing line " + str(index) + " of " + str(len(lines)))
    line = lines[index].strip()
    # Compatibility with interfaces and contracts
    if "interface" in line or "contract" in line:
        if "/" in line:
            continue
        if not " is " in line:
            prefix = line.split("{")[0].strip().split(" ")[-1]
        else:
            prefix = line.split("{")[0].strip().split(" is ")[0].split(" ")[-1]
        abi_string = "abi = '" + abi.replace("\n", "") + "'"
        invocation = abi_string + "\nlet " + prefix + " = new ethers.Contract(" + address + ", JSON.parse(abi), signer);\n\n"
        js_file.write(invocation)
    # Spotting functions
    if "function" in line:
        line_buffer += line
        # Reading them until the { token
        while not "{" in line and not ";" in line:
            index += 1
            line = lines[index]
            line_buffer += line
        # Detecting publicy available functions
        if ("public" in line_buffer) or ("external" in line_buffer):
            print("============\n")
            # One lining and prettyfing
            line_buffer.strip().replace("\n", "")
            while "  " in line_buffer:
                line_buffer = line_buffer.replace("  ", " ")
            # Getting name and arguments if any
            fname = line_buffer.split("function")[1].split("(")[0].strip()
            print("Function " + fname)
            args = line_buffer.split("(")[1].split(")")[0].strip().replace("\n", "")
            print("Raw arguments " + str(args))
            # Splitting arguments if needed
            try:
                args = args.split(",")
                arg_num = len(args)
            except:
                args = []
                arg_num = 0
            print("We have " + str(arg_num) + " arguments")
            # Logging to user
            print("PUBLIC: " + line_buffer)
            print("NAME: " + fname)
            print("ARGS (" + str(arg_num) + ") :" + str(args))
            # Building the js equivalent
            js_function = "async function " + prefix + "_" + fname + "("
            argtypes = "//( "
            counter = 0
            call_args = ""
            print("Working on " + str(args))
            # Writing arguments in js
            for arg in args:
                arg = arg.strip()
                print("Now on " + arg)
                if arg == "":
                    continue
                counter += 1
                if not " " in arg:
                    argname = "argument_" + str(counter)
                    argtypes += arg + " "
                else:
                    argname = arg.split(" ")[-1]
                    argtypes += arg.split(" ")[0] + " "
                call_args += argname + ", "
                js_function += argname + ", "
            if (counter > 0):
                call_args = call_args[:-2]
            # Opening the method
            print("Arguments are " + call_args)
            print("Adding them to " + fname)
            js_function += ") {\n\t"
            print("Obtained " + js_function)
            # Calling the contract
            js_function += "let result = await " + prefix + "." + fname + "("
            # Adding arguments to the call
            js_function += call_args + ");\n"
            # If is a view or pure, returns the result
            if ("view" in line_buffer) or ("pure" in line_buffer):
                js_function += "\treturn JSON.stringify(result);\n}\n"
            # If is a transaction, returns the receipt 
            else:
                js_function += "\tlet receipt = await result.wait();\n"
                js_function += "\treturn receipt;\n}\n"
            # If is payable we add that info too
            if "payable" in line_buffer:
                argtypes += " [payable] "
            argtypes += ")\n\n"
            js_function += argtypes + "\n"
            print(js_function)
            js_file.write(js_function)
            
        line_buffer = ""
        argtypes = ""
        
print("Done!")