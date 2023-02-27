import os


def check_io(inp_dir, outp_dir, inp_file_ext):
    # Get absolute paths for input and output directories
    inp_dir = os.path.abspath(inp_dir)
    outp_dir = os.path.abspath(outp_dir)

    # Check if input and output directories are the same
    if inp_dir == outp_dir:
        raise ValueError("Input and output directories cannot be the same")

    # Check if input directory exists and contains files with the specified extension
    if not os.path.isdir(inp_dir):
        raise FileNotFoundError(f"Input directory '{inp_dir}' does not exist")
    if not any(fname.endswith(inp_file_ext) for fname in os.listdir(inp_dir)):
        raise FileNotFoundError(f"No files with {inp_file_ext} extension in input directory '{inp_dir}'")

    # Check if output directory exists and is empty
    if os.path.isdir(outp_dir):
        if os.listdir(outp_dir):
            raise FileExistsError(f"Output directory '{outp_dir}' is not empty")
    else:
        os.mkdir(outp_dir)
