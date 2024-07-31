import os
import re
import io


def main():
    copy_main_py()
    total_function_order = []
    function_order = []
    content_lines = []

    # Get only the content of one .py file at a time
    with open("copy_functions.txt", "r") as file:
        content = file.read()

    # Extract the main function block
    main_function = extract_function_block_from_file("main", content)

    if main_function:
        # print("Extracted def main() function:")
        # print(main_function)

        # Split the function to many lines
        function_lines = main_function.splitlines()

        # Turn functions lines into list of functions
        function_list = get_functions(function_lines)
        print(f"main function list: {function_list}")
        print("---------------------------")
        print("\n\n")

        for function in function_list:
            # Get the name of the function
            function_name = get_function_name(function)

            # Get the function block based on the name
            function_block = extract_function_block_from_file(function_name, content)
            print(f"Outer recursive function name: {function_name}")
            print("---------------------------")
            # Recursive functions to find the deepest functions and add it to function_order
            get_function_r(function_block, content, function_order)

            # function_order.insert(0,function)
            print("---------------------------")
            print(f"function order: {function_order}")
            total_function_order.insert(0, function_order)
            function_order = []
            print(f"function order after reset: {function_order}")
            print(f"total function order: {total_function_order}")

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

    # Check if the file exists
    if os.path.exists(output_file_path):
        # Delete the file
        os.remove(output_file_path)

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
    function_def_pattern = re.compile(rf"^def {name}\([^)]*\):", re.MULTILINE)
    chunks = file_content.split("-------CUT THE READING FILE HERE------")

    for chunk in chunks:
        indent_level = None
        function_lines = []
        inside_function = False

        for line in chunk.splitlines(True):
            stripped_line = line.lstrip()
            current_indent = len(line) - len(stripped_line)

            if not inside_function:
                # Check if the current line starts the function
                if function_def_pattern.match(line):
                    inside_function = True
                    indent_level = current_indent
                    function_lines.append(line)
                continue

            # Handle the case where we are inside the function
            if inside_function:
                if (
                    stripped_line.startswith("def ")
                    and current_indent == indent_level
                    and len(stripped_line) > 0
                ):
                    # End of the current function block if another function starts with the same indentation level
                    break
                function_lines.append(line)

        # Return the function block if found
        if function_lines:
            return "".join(function_lines)

    return None


def get_function_r(function_block, content, function_order):
    # Turn the function block into array of function lines
    function_lines = function_block.splitlines()
    # Turn function lines into list of functions
    function_list = get_functions(function_lines)

    # print(f"function block: {function_block}")
    # print("\n\n")
    print(f"functions list from the block: {function_list}")
    # print("\n\n")

    for function in function_list:
        function_name = get_function_name(function)
        print("---------------------------")
        print("function: ", function)
        print("function name: ", function_name)
        function_block_code = extract_function_block_from_file(function_name, content)
        # If function_block_code is not found -> there is no nested functions inside this function
        if not function_block_code:
            # If function name contains . -> it is a library function
            if "." in function_name:
                print(f"Library function: {function_name}")
            # Else it's a normal function, add this to the function_order
            else:
                function_order.append(function)
                print(f"Function order end: {function_order}")
        else:
            # print(f"block code: {function_block_code} from the function: {function_name}")

            # Get the name of the funtion_block_code
            # function_block_code_name = get_function_name(function_block_code.split("\n")[0])

            if function in function_block_code:

                if any(
                    function_name == get_function_name(sublist)
                    for sublist in function_order
                ):
                    print(f"Function already added:  {function_name} ")
                    print(f"function order: {function_order}")
                    continue
                else:
                    print(f"order_list: {function_order}")
                    function_order.append(function)
                print(f"function_block_code: {function_block_code}")
                print(f"recursive function found:  {function_name} ")
            else:
                # If it's not a recursive functions, continue to find the deeper functions
                get_function_r(function_block_code, content, function_order)


def get_functions(function_lines):
    # function_list = []
    # for line in function_lines:
    #     stripped_line = line.strip()
    #     # Check if the line represents a function
    #     if (
    #         stripped_line
    #         and not stripped_line.startswith("#")
    #         and re.search(r"\(.*\)", stripped_line)
    #         and "def" not in stripped_line
    #         and "print" not in stripped_line
    #     ):
    #         function_list.append(line)
    # return function_list
    function_calls = []
    function_block = []
    parathesis_counter = 0

    for line in function_lines:
        stripped_line = line.strip()
        if (
            not stripped_line
            or stripped_line.startswith("#")
            or "main" in stripped_line
        ):
            continue

        parathesis_counter += stripped_line.count("(") - stripped_line.count(")")
        function_block.append(line)

        if parathesis_counter <= 0 and function_block:
            complete_function_call = " ".join(
                [block_line.strip() for block_line in function_block]
            )
            complete_function_call_name = get_function_name(complete_function_call)
            if (
                "(" in complete_function_call
                and ")" in complete_function_call
                and "_" in complete_function_call_name
                and "." not in complete_function_call_name
            ):
                function_calls.append(complete_function_call)
            function_block = []

    return function_calls


def get_function_name(one_line_function):
    return one_line_function.split("(")[0].strip().split(" ")[-1]


if __name__ == "__main__":
    main()
