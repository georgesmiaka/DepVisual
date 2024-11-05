#!/bin/bash

#!/bin/bash

# Main menu
menu() {
    while true; do
        echo ""
        echo "What would you like to do?"
        echo "1. Track dependencies"
        echo "2. Dependencies Visualization"
        echo "3. Exit"
        read -p "Enter your choice: " choice

        case $choice in
            1)  # Scan the root directory
                clear
                echo "Scan the root directory to detect all components..."
                python3 dep_scan_root_dir.py
                echo ""
                echo "Scanning completed. All components have been detected successfully."
                echo ""
                sub_menu
                ;;
            2)  # Start dependency analysis and show sub-menu
                clear
                echo ""
                echo "Starting web server..."
                cd server
                npm i
                npm start &
                cd ..
                cd webclient
                echo ""
                echo "Starting web client..."
                npm i
                npm start &
                cd ..
                echo ""
                echo "Launching DepVisual"
                ;;
            3)  # Exit the program
                echo "Exiting."
                exit 0
                ;;
            *)  # Invalid option
                echo "Invalid choice. Please select again."
                ;;
        esac
    done
}

# Display the title and ASCII image
clear
cat << "EOF"
Dependencies Analysis - DepVisual

   __    __    ___  _        __    __
  /'__`\ /\ \  / __`/\ \  /'__`\ /\ \
 /\  __/ \ \ \/\ \L\ \ \ \/\  __/ \ \ \
 \ \____\ \ \_\ \____/\ \_\ \____\ \_\ \
  \/____/  \/_/\/___/  \/_/\/____/ \/_/

EOF

# Start the main menu loop
menu