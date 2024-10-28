# DepVisual

DepVisual is a custom dependency visualization tool designed to enhance clarity and efficiency in software development workflows, particularly in environments where components depend on each other within complex codebases. Unlike traditional tools that focus solely on the dependencies a component contains, DepVisual highlights which components actively depend on a specific module, making it easier to identify areas affected by changes and understand the structure of component interdependencies.

## Key Features
- **Dependency Tracking by Usage**: Identifies components that rely on a specific module, filtering out unused dependencies to avoid clutter.
- **Two-Phase Analysis**:
  - **Preliminary Dependency Scan**: Extracts declared dependencies from `pom.xml` files across components.
  - **Usage Validation**: Confirms if dependencies are actively used in the codebase, reducing unnecessary dependencies.
- **Dependency Graph Visualization**: Displays a clean, concise dependency graph to help developers see potential impact areas.
- **Interactive CLI Interface**: Users can easily input a component's details, perform dependency scans, and view results in a structured manner.

## Installation

Clone the repository:
```bash
git clone https://github.com/yourusername/DepVisual.git
cd DepVisual