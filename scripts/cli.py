import argparse
import os
import curses  # Import curses
from scripts import views
from scripts.validation import main as run_validation  # Import the validation function

MARKER = '_org'  # Customize the marker you want to use for valid subdirectories

def init():

    """Initializes org in the current directory."""
    current_dir = os.getcwd()

    # Path to the .org directory
    org_dir_path = os.path.join(current_dir, '.org')

    # Check if .org already exists
    if os.path.exists(org_dir_path):
        # Check if it's a directory
        if os.path.isdir(org_dir_path):
            print(f"Directory '{current_dir}' is already initialized for org.")
            return
        else:
            # If it's a file, remove it and create a directory
            print(f"Error: '{org_dir_path}' exists as a file. Removing and creating as a directory.")
            os.remove(org_dir_path)

    # Create the .org directory
    os.makedirs(org_dir_path)
    print(f"Created .org directory in {current_dir}")

    # Create 'notes', 'todos', 'events' directories inside valid subfolders
    for subfolder in os.listdir(current_dir):
        subfolder_path = os.path.join(current_dir, subfolder)
        # Check if the subfolder has the marker and is a directory
        if os.path.isdir(subfolder_path) and MARKER in subfolder:
            for folder in ['notes', 'todos', 'events']:
                folder_path = os.path.join(subfolder_path, folder)
                if not os.path.exists(folder_path):
                    os.makedirs(folder_path)
                    print(f"Created: {folder_path}")

    # Check for .gitignore and add .org to it if necessary
    gitignore_path = os.path.join(current_dir, ".gitignore")
    
    if os.path.exists(gitignore_path):
        with open(gitignore_path, 'r') as gitignore_file:
            gitignore_lines = gitignore_file.readlines()
        
        # Add .org to .gitignore if it's not already there
        if ".org\n" not in gitignore_lines and ".org" not in gitignore_lines:
            with open(gitignore_path, 'a') as gitignore_file:
                gitignore_file.write("/.org\n")
            print("Added .org to existing .gitignore")
        else:
            print(".org is already listed in .gitignore")
    else:
        # Create .gitignore and add .org
        with open(gitignore_path, 'w') as gitignore_file:
            gitignore_file.write(".org\n")
        print("Created .gitignore and added .org")

def display_graphical_view(file_type, search_prop=None, search_term=None, exact=False, sort_prop=None, reverse=False):
    """Handle graphical view display with optional filters and sorting."""
    
    # Start curses graphical view with filters and sorting applied
    def inner(stdscr):
        entries = []

        if file_type == 'notes':
            entries = views.load_files_from_subdir('notes')
        elif file_type == 'todos':
            entries = views.load_files_from_subdir('todos')
        elif file_type == 'events':
            entries = views.load_files_from_subdir('events')
        elif file_type == 'all':
            notes = views.load_files_from_subdir('notes')
            todos = views.load_files_from_subdir('todos')
            events = views.load_files_from_subdir('events')
            entries = notes + todos + events

        # Apply search/filter if specified
        if search_prop and search_term:
            if exact:
                entries = views.exact_search(entries, search_prop, search_term)
            else:
                entries = views.fuzzy_search(entries, search_prop, search_term)

        # Apply sorting if specified
        if sort_prop:
            entries = views.sort_items(entries, prop=sort_prop, reverse=reverse)

        # Display the entries in the graphical interface
        views.display_files_with_view(stdscr, entries, file_type)

    curses.wrapper(inner)

def main():
    parser = argparse.ArgumentParser(description="Org Command Line Interface")
    
    # Add subcommands
    subparsers = parser.add_subparsers(dest='command')

    # Add init subcommand
    init_parser = subparsers.add_parser('init', help='Initialize Org in the current directory')

    # Add view subcommand for viewing notes, todos, events
    view_parser = subparsers.add_parser('view', help='View files of a specific type')
    view_parser.add_argument('file_type', choices=['notes', 'todos', 'events', 'all'], help='Type of file to view (notes, todos, events, or all)')
    view_parser.add_argument('search_command', nargs='?', choices=['s', 'es', 'o', 'r', 'a'], help='Search/sort/filter/reset command (optional)')
    view_parser.add_argument('search_prop', nargs='?', help='Property to search/sort (optional)')
    view_parser.add_argument('search_term', nargs='?', help='Term to search for (optional)')

    # Add validation subcommand
    val_parser = subparsers.add_parser('val', help='Run validation scripts')

    # Parse the arguments
    args = parser.parse_args()

    # Dispatch commands
    if args.command == 'init':
        init()  # Run init function
    elif args.command == 'view':
        # First, run validation before proceeding with view commands
        run_validation()

        # Handle the 'view' command with various options
        if args.search_command == 's' and args.search_prop and args.search_term:
            # Fuzzy search and graphical view
            display_graphical_view(args.file_type, search_prop=args.search_prop, search_term=args.search_term)
        elif args.search_command == 'es' and args.search_prop and args.search_term:
            # Exact search and graphical view
            display_graphical_view(args.file_type, search_prop=args.search_prop, search_term=args.search_term, exact=True)
        elif args.search_command == 'o' and args.search_prop:
            # Sort and graphical view
            display_graphical_view(args.file_type, sort_prop=args.search_prop)
        elif args.search_command == 'r' and args.search_prop:
            # Reverse sort and graphical view
            display_graphical_view(args.file_type, sort_prop=args.search_prop, reverse=True)
        elif args.search_command == 'a':
            # Reset/clear filters and graphical view
            display_graphical_view(args.file_type)
        else:
            # Simple view without filters in the graphical view
            display_graphical_view(args.file_type)
    elif args.command == 'val':
        # Run the validation script when 'org val' is run
        run_validation()
    else:
        # Check if .org file exists before running commands
        current_dir = os.getcwd()
        org_file_path = os.path.join(current_dir, '.org')
        
        if not os.path.exists(org_file_path):
            print(f"Error: '.org' file not found in {current_dir}. This directory is not initialized for org.")
            return

        # Wrap views.main() with curses.wrapper() to handle stdscr argument
        curses.wrapper(views.main)

if __name__ == "__main__":
    main()
