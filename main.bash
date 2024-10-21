#!/bin/bash

# Main menu
menu() {
    while true; do
        echo ""
        echo "What would you like to do?"
        echo "1. Track dependencies"
        echo "2. Exit"
        read -p "Enter your choice: " choice

        case $choice in
            1)  # Start dependency analysis and show sub-menu
                clear
                echo "Starting dependency analysis..."
                python3 dep_preliminary.py "$group_id" "$artifact_id" "$component_path"
                echo "Preliminary analysis completed."
                sub_menu
                ;;
            2)  # Exit the program
                echo "Exiting."
                exit 0
                ;;
            *)  # Invalid option
                echo "Invalid choice. Please select again."
                ;;
        esac
    done
}

# Sub-menu
sub_menu() {
    while true; do
        echo ""
        echo "What would you like to do next?"
        echo "1. Display dependencies"
        echo "2. Track active dependencies"
        echo "3. Exit to main menu"
        read -p "Enter your choice: " sub_choice

        case $sub_choice in
            1)  # Display preliminary dependencies
                clear
                cat data/preliminary_dependencies.json
                ;;
            2)  # Check active dependencies and show sub-sub menu
                clear
                echo "Checking active dependencies..."
                python3 dep_usage.py
                sub_sub_menu
                ;;
            3)  # Return to the main menu
                return
                ;;
            *)  # Invalid option
                echo "Invalid choice. Please select again."
                ;;
        esac
    done
}

# Sub-sub menu
sub_sub_menu() {
    while true; do
        echo ""
        echo "1. Display active dependencies"
        echo "2. Dependencies Visualization"
        echo "3. Exit to previous menu"
        read -p "Select an option: " option3

        case $option3 in
            1)  # Display active dependencies
                clear
                echo "Displaying active dependencies:"
                cat data/final_dependencies.json
                ;;
            2)  # Launch Dependencies Visualization
                clear
                python3 dep_filtered.py
                echo ""
                echo "Launching Dependencies Visualization..."
                python3 -m webbrowser -t "http://localhost:1338"
                ;;
            3)  # Return to the sub-menu
                return
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
Component Dependencies Analysis

   __    __    ___  _        __    __
  /'__`\ /\ \  / __`/\ \  /'__`\ /\ \
 /\  __/ \ \ \/\ \L\ \ \ \/\  __/ \ \ \
 \ \____\ \ \_\ \____/\ \_\ \____\ \_\ \
  \/____/  \/_/\/___/  \/_/\/____/ \/_/

EOF

# Prompt user for input
echo "Please enter your component details:"
read -p "Enter the groupId: " group_id
read -p "Enter the artifactId: " artifact_id
read -p "Enter the path to the component: " component_path

# Start the main menu loop
menu
