#!/bin/bash

# starting by analyzing the directory where we want to capture dependencies
clear
echo "Finding the components..."
echo ""
python3 client/dep_scan_root_dir.py
echo ""