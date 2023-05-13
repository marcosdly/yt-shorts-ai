from sys import argv, path as PYTHON_PATH
from os.path import join, dirname

PYTHON_PATH.insert(0, join(dirname(__file__), ".."))

# TODO implement an actual cli application

def main() -> None:
    first_argument = ""
    try:
        first_argument = argv[1]
    except IndexError:
        print("Provide at least one argument.")
        exit(1)

    if first_argument in ["-h", "--help"]:
        print("""
        Available commands:
            add
                Add a piece of media (movie or series) to be cutted and processed.
        """)

    if first_argument == "add":
        from media_add import media_add
        relevant_argv = []
        try:
            relevant_argv = argv[2:]
        except IndexError:
            # if indexes doesn't exist maintain the empty array
            pass
        
        media_add(relevant_argv)

if __name__ == "__main__":
    main()