import os
import re


def main():
    copy_main_py()

    function_order = []
    content_lines = []
    with open("copy_functions.txt", "r") as file:
        for line in file:
            if line.strip() == "-------CUT THE READING FILE HERE------":
                break
            content_lines.append(line)

    content = "".join(content_lines)

    main_function = extract_function_block_from_file("main", content)

    if main_function:
        # print("Extracted def main() function:")
        # print(main_function)
        function_lines = main_function.splitlines()
        function_list = find_functions_in_function_lines(function_lines)
        print(f"top function list: {function_list}")


        # for function in function_list:
        function = function_list[0]
        function_name = get_function_name(function)
        function_block = extract_function_block_from_file(function_name, content)
        print(f"Function special: {function_name}")
        get_function_r(function_block, content, function_order)
        
        function_order.insert(0,function) 
        print(f"function order: {function_order}")

    else:
        print("No def main() function found.")


def copy_main_py():
    project_path = "/Users/hoathaidang/Documents/bootdev/static_site_generator"

    # Construct the path to the main.py file
    main_py_path = os.path.join(project_path, "main.py")

    # Check if the file exists
    if not os.path.isfile(main_py_path):
        # If main.py is not found, check for src/main.py
        main_py_path = os.path.join(project_path, "src", "main.py")
        if not os.path.isfile(main_py_path):
            print(f"No main.py found at {main_py_path}")
            return

    code_file_path = os.path.dirname(main_py_path)

    # Read the content of main.py
    with open(main_py_path, "r") as file:
        content = file.read()

    # Store the content into another file, appending if the file already exists
    output_file_path = "copy_functions.txt"
    with open(output_file_path, "a") as file:
        file.write(content)
        file.write("\n\n")

    main_py_dir = os.path.dirname(main_py_path)
    py_files = [
        f
        for f in os.listdir(main_py_dir)
        if f.endswith(".py") and "test" not in f and f != "main.py"
    ]

    # print(
    #     "\nPython files in the same directory as main.py (excluding those with 'test' in the name):"
    # )
    for py_file in py_files:
        file_path = os.path.join(code_file_path, py_file)
        # print(file_path)
        with open(file_path, "r") as file:
            content = file.read()
            with open(output_file_path, "a") as file:
                file.write("-------CUT THE READING FILE HERE------\n")
                file.write(f"## {py_file}")
                file.write("\n\n")
                file.write(content)
                file.write("\n\n\n\n\n\n")


def extract_function_block_from_file(name, file_content):
    pattern = re.compile(rf"def {name}\([^)]*\):[\s\S]*?(?=\ndef |\Z)", re.MULTILINE)
    result = pattern.search(file_content)
    if not result:
        return None
    else:
        return result.group(0)


def get_function_r(function_block, content, function_order):
    function_lines = function_block.splitlines()
    function_list = find_functions_in_function_lines(function_lines)


    # print(f"function block: {function_block}")
    # print("\n\n")
    # print(f"functions list from the block: {function_list}")
    # print("\n\n")

    for function in function_list:
        function_name = get_function_name(function)
        print("---------------------------")
        print("function: ", function)
        print("function name: ", function_name)
        function_block_code = extract_function_block_from_file(function_name, content)
        if not function_block_code:
            if "." in function_name:
                print(f"Library function: {function_name}")
            else:
                function_order.append(function)
        else:
            print(f"block code: {function_block_code} from the function: {function_name}")
            function_block_code_name = function_block_code.split("\n")[0]
            if function_name in function_block_code_name:
                print(f"recursive function found:  {function_name}")
                function_order.append(function) 
            else:
                get_function_r(function_block_code, content, function_order)

def find_functions_in_function_lines(function_lines):
    function_list = []
    for line in function_lines:
        stripped_line = line.strip()
        # Check if the line represents a function
        if (
            stripped_line
            and not stripped_line.startswith("#")
            and re.search(r"\(.*\)", stripped_line)
            and "def" not in stripped_line
        ):
            function_list.append(line)
    return function_list

def get_function_name(one_line_function):
   return one_line_function.split("(")[0].strip().split(" ")[-1] 
        
    
    
if __name__ == "__main__":
    main()
