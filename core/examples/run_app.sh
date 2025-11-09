#!/bin/bash
# Quick start script for running the Math app with JSON storage

echo "Starting Math App with JSON File Storage..."
echo "Available agents: Math LlamaIndex Agent, Math Semantic Kernel Agent"
echo "Storage: JSON files (local)"
echo ""
echo "Opening app in browser..."
echo ""

cd /workspace
poetry run streamlit run core/examples/math_app.py
