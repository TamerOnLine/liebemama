import os

def list_workspaces(directory):
    """
    Retrieve all .code-workspace files in the specified directory.
    Args:
        directory (str): Path to the directory to search.
    Returns:
        list: A list of filenames ending with .code-workspace.
    """
    return [f for f in os.listdir(directory) if f.endswith(".code-workspace")]

def show_menu(files):
    """
    Display a numbered list of available workspace files using real filenames.
    Args:
        files (list): List of workspace filenames.
    """
    print("\n📁 Available workspaces in this directory:\n")
    for idx, file in enumerate(files, start=1):
        print(f"[{idx}] {file}")
    print("[0] Exit")

def open_workspace(file_path):
    """
    Open a workspace file using the default application on Windows.
    Args:
        file_path (str): Full path to the workspace file.
    """
    print(f"\n🔄 Opening: {os.path.basename(file_path)} ...")
    os.startfile(file_path)  # Windows only

def main():
    """
    Main function that handles the workflow of listing, displaying,
    and opening workspace files in the current directory.
    """
    workspace_dir = os.path.dirname(os.path.abspath(__file__))

    while True:
        workspace_files = list_workspaces(workspace_dir)
        if not workspace_files:
            print("❌ No workspace files found in this directory.")
            break

        show_menu(workspace_files)

        choice = input("Enter the number of the workspace to open: ").strip()

        if choice == "0":
            print("👋 Exiting.")
            break

        try:
            index = int(choice) - 1
            if 0 <= index < len(workspace_files):
                filepath = os.path.join(workspace_dir, workspace_files[index])
                open_workspace(filepath)
            else:
                print("❌ Invalid number. Please select from the list.")
        except ValueError:
            print("❌ Invalid input. Please enter a number.")

if __name__ == "__main__":
    main()
