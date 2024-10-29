#!/bin/bash

# starting by analyzing the directory where we want to capture dependencies
clear
echo "Finding the components..."
echo ""
#python3 client/dep_scan_root_dir.py
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
echo "Launching Dependencies Visualization..."