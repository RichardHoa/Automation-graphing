import os
import re
import io
import json
import tkinter as tk
from tkinter import Canvas, font


def main():
    # Copy all the code from the directory to copy_functions.txt
    copy_main_py()
    # A dictionary to store all the functions and their order
    function_order_dict = {}
    # Functions to be ignored when searching for function
    special_funcs = ["def to_html(self):", "def props_to_html(self):"]

    # Read the content of copy_functions.txt
    with open("copy_functions.txt", "r") as file:
        content = file.read()

    # Extract all functions from the copy_functions.txt
    all_functions = extract_all_functions(content, special_funcs)

    # For each of the function
    for i in range(0, len(all_functions)):
        # Get the function
        function = all_functions[i]
        # function example: helper_function(self, param1, param2)
        full_function = all_functions[i].replace("def ", "").replace(":", "")
        # Function name example: helper_function
        function_name = get_function_name(function)
        # Find all the context function of the function,
        # context function is defined as the function that call this function
        context_functions_list = extract_context_functions(
            content, function_name, all_functions
        )
        # print("------------------------------------------------")
        # print(f"full function: {full_function}")
        # print(f"function name: {function_name}")
        # print(f"context functions: {context_functions_list}")
        # if there is no context function, insert the function into the dict
        if len(context_functions_list) == 0:
            function_order_dict[full_function] = {}
        else:
            for function in context_functions_list:
                # print("----------")
                # print(f"function: {function}")
                # Context function name example: helper_markdown_to_html_paragraph
                context_function_name = function.replace("def ", "").replace(":", "")
                # print("context function: " + context_function_name)
                # Insert the function into the ALMOST CORRECT position in the dict
                insert_in_nested_dict(
                    function_order_dict, context_function_name, full_function
                )

        # for function in context_functions_list:
        #     identation = len(function) - len(function.lstrip())
        #     print(f"function: {function}")

    print("------------------------------------------------------------------")
    # function_order_dict["main()"][
    #     "helper_markdown_to_html_paragraph(block, props_list)"
    # ]["text_to_textnodes(text)"] = function_order_dict["main()"][
    #     "text_to_textnodes(text)"
    # ]

    # Get all the outer keys in the dict
    outer_keys = list(function_order_dict["main()"].keys())

    # Context function list stores all the function with its context parents
    # Ex: ['main()', 'main()copy_folder(source, destination)']
    context_function_list = []

    # Deleted function list stores all the functions that will be deleted at the end
    deleted_func = []

    # Add context functions to the context_function_list
    add_context_function_list(function_order_dict, "", context_function_list)

    # Function to modify the current dict to make it into CORRECT format
    for one_context_function_list in context_function_list:
        # Multiple functions in one_context_function_list
        functions = one_context_function_list.split(")")
        # Prepare parents function string
        parent_functions_string = ""

        # Find parent functions of the current function
        # functions[:-1] because the last item in the functions list is always empty string
        for function in functions[:-1]:
            if function == "main(":
                singular_function = f"'{function})'"
            else:
                singular_function = f",'{function})'"
            parent_functions_string += singular_function

        # Get the function name
        function_name = functions[-2] + ")"

        # If function name in the outer keys and there are more than 2 functions in the parent functions
        # Each function always has 2 parent functions: main and itself
        if function_name in outer_keys and parent_functions_string.count("'") > 4:
            # Convert the string into list
            parent_functions_list = string_to_list(parent_functions_string)
            # print("--------------------------")
            # print("Change structure")
            # print(f"function_name: {function_name}")
            # print(f"parent functions: {parent_functions_list}")
            # We format the dictionary again, make sure it's in the nested format

            replace_value_nested_dictionary(
                function_order_dict,
                parent_functions_list,
                function_order_dict["main()"][function_name],
            )
            # If the
            deleted_func.append(function_name)

    # Remove all duplicate in deleted_func
    deleted_func = list(set(deleted_func))

    # Delete all the functions in deleted_func
    for function in deleted_func:
        del function_order_dict["main()"][function]
    # print(f"delete function: {deleted_func}")
    # print(f"function order dist: {json.dumps(function_order_dict, indent=4)}")

    # Generate the HTML content
    html_content = dict_to_html(function_order_dict)

    # Full HTML document structure
    full_html = f"""<!DOCTYPE html>
    <html>
    <head>
        <title>Dictionary to HTML</title>
    </head>
    <body>
    {html_content}
    </body>
    </html>"""

    # Write the HTML content to a file
    with open("result.html", "w") as file:
        file.write(full_html)


def dict_to_html(dictionary, indent=1):
    html = ""
    for key, value in dictionary.items():
        # Heading does not exceed 4
        heading_level = min(indent, 4)  
        # Set style for indentation
        indent_style = f"style='margin-left: {40 * (indent - 1)}px;'" 
        html += f"<h{heading_level} {indent_style}>{key}</h{heading_level}>\n"
        if isinstance(value, dict):
            html += dict_to_html(value, indent + 1)
    return html


def string_to_list(input_string):
    return re.findall(r"'([^']*)'", input_string)


def add_context_function_list(dictionary, prefix="", context_function_list=[]):
    for key, value in dictionary.items():
        context_function_list.append(f"{prefix}{key}")
        if isinstance(value, dict):
            add_context_function_list(value, prefix + key, context_function_list)
    return context_function_list

def replace_value_nested_dictionary(dictionary, path_to_key, new_key_value):
    value = dictionary
    for index in path_to_key[:-1]:
        value = value.get(index)
        if value is None:
            return None
    last_index = path_to_key[-1]
    value[last_index] = new_key_value
    return new_key_value


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

    # Store the content into another file,
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


def extract_context_functions(file_content, target_function_name, full_functions_list):

    # Initialize a list to store function definitions that call the target function
    file_lines = file_content.split("\n")
    context_functions = []
    # print(target_function_name)

    pattern = rf"^(?!.*#).*{re.escape(target_function_name)}.*"

    # Compile the regex pattern
    regex = re.compile(pattern, re.MULTILINE)

    # Find all matches in the file content
    pre_matches = regex.findall(file_content)
    # print(f"pre matches: {pre_matches}")

    modified_pattern = rf"\w{re.escape(target_function_name)}\b"

    # Iterate over the list of matches
    stage_2_matches = []

    for match in pre_matches:
        result = re.search(modified_pattern, match)
        # Check if the match contains 'def' and should be excluded
        if "def" in match:
            # print("def in match: " + match)
            continue
        # print(f"matches: {match}")
        # Check if the target function name is modified
        if result:
            # print("modified pattern: " + result.group())
            continue

        if "__" in match:
            # print("__ in match: " + match)
            continue

        if get_function_name(match) != target_function_name:
            # if target_function_name not in match:
            continue

        if match in stage_2_matches:
            continue

        # If neither condition is met, keep the match
        stage_2_matches.append(match)

    # print("----------------------------------------------")

    filtered_matches = list(set(stage_2_matches))

    # print(f"filtered matches: {filtered_matches}")
    # print(f"target function name: {target_function_name}")
    for match in filtered_matches:
        # Find the line number of the match
        for i, line in enumerate(file_lines):
            if line.strip() == match.strip():
                match_line_index = i
                break
        # Get the indentation of the matched function line
        match_indentation = len(match) - len(match.lstrip())
        # print("---")
        # print(f"Function: {match} | Indentation: {match_indentation}")
        # print(f"function index line: {match_line_index + 1}")
        # print("---")

        # Go above the match line by line
        for j in range(match_line_index - 1, -1, -1):
            line = file_lines[j]
            line_indentation = len(line) - len(line.lstrip())
            # print("-")
            # print(f"context function: {context_functions}")
            # print(f"line: {line} | Indentation: {line_indentation}, function name: {get_function_name(line)},line not in context: {line not in context_functions}, not {not re.search(r"__\w+__", line)}")
            # Check if the line has indentation of zero
            if target_function_name == "main":
                break
            if (
                line_indentation == 0
                and get_function_name(line) == target_function_name
            ):
                # print("This function refers to itself")
                break

            if (
                line_indentation == 0
                and line != ""
                and get_function_name(line) != target_function_name
                and line not in context_functions
                and not re.search(r"__\w+__", line)
                and "#" not in line
            ):
                function_block = extract_function_block_from_file(
                    get_function_name(line), file_content
                )
                if not function_block:
                    break
                # print(f"function block: {function_block}")
                if target_function_name in function_block:
                    # print(f"Have found a context function call at line {j + 1} with function name: {get_function_name(line)}")
                    context_functions.append(line.strip())
                    break

    # print("-------")
    # print(f"Context functions: {context_functions}")
    return context_functions


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
                    (
                        stripped_line.startswith("def ")
                        or stripped_line.startswith("class ")
                    )
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


def get_function_name(one_line_function):
    return one_line_function.split("(")[0].strip().split(" ")[-1]


def extract_all_functions(file_content, special_funcs):
    # Regex pattern to match function definitions
    function_def_pattern = re.compile(r"^\s*def\s+(\w+)\s*\([^)]*\):", re.MULTILINE)

    # Regex pattern to match class definitions
    class_def_pattern = re.compile(r"^\s*class\s+\w+:", re.MULTILINE)

    # List to store function definitions
    functions = []

    file_like_object = io.StringIO(file_content)
    in_class = False

    for line in file_like_object:
        # Check if we are inside a class
        if class_def_pattern.match(line):
            in_class = True
        elif re.match(r"^\s*class\s+\w+:", line) and in_class:
            in_class = False

        # Extract function definitions whether inside or outside a class
        match = function_def_pattern.match(line)
        if match:
            func_name = match.group(1)
            # Check if function name does not contain "__" twice and is not in special_funcs
            full_signature = line.strip()
            if func_name.count("__") < 2:
                if all(
                    full_signature != special_func for special_func in special_funcs
                ):
                    functions.append(match.group(0))

    return functions


def insert_in_nested_dict(nested_dict, target_key, new_value):
    def helper(current_dict, target_key, new_value):
        # Base case: if the target key is found
        if target_key in current_dict:
            # If the current value is a dictionary, add the new value
            if isinstance(current_dict[target_key], dict):
                if target_key in current_dict:
                    # print(f"target key: {target_key} | current_dict:  {current_dict} | new_value: {new_value}")
                    if new_value not in current_dict[target_key]:
                        current_dict[target_key][new_value] = {}
            else:
                # Otherwise, replace the current value with a new dictionary
                current_dict[target_key] = {new_value: {}}
            return True

        # Recursive case: traverse the nested dictionaries
        for key, value in current_dict.items():
            if isinstance(value, dict):
                if helper(value, target_key, new_value):
                    return True

        return False

    if not helper(nested_dict, target_key, new_value):
        # If the target key was not found in the nested dict, add it at the top level
        # print(f"Nested list duplicated: {nested_dict}")
        if target_key in nested_dict:
            # print("Duplicate function name")
            pass
        else:
            nested_dict["main()"][target_key] = {new_value: {}}


if __name__ == "__main__":
    main()
