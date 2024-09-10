import inspect


def get_function_semantic_lines(functions: list):
    if not isinstance(functions, list):
        functions = [functions]

    semantic_lines = []
    for func in functions:
        lines = inspect.getsourcelines(func)
        semantic_lines += get_semantic_lines(lines[0])

    return semantic_lines


# Returns list of semantic lines of code from a list of lines of code
def get_semantic_lines(lines: list[str]):
    semantic_lines = []
    for line in lines:
        if line.strip().startswith("#"):
            continue
        if "log" in line.strip():
            continue
        if "print" in line.strip():
            continue
        if line.strip() == "":
            continue
        if line.strip() == "\n":
            continue

        semantic_lines.append(line)
    return semantic_lines


# Returns list of semantic lines of code from an ansible file
def get_ansible_semantic_lines(filepath: str):
    with open(filepath, "r") as f:
        lines = f.readlines()
        semantic_lines = get_semantic_lines(lines)
        return semantic_lines


def count_low_level_action_lines(low_level_action):
    lines = 0
    for function in low_level_action:
        # if function is string
        if isinstance(function, str):
            lines += len(get_ansible_semantic_lines(function))
        else:
            lines += len(get_function_semantic_lines(function))

    return lines
