import os
import json
import subprocess

# Input files
preliminary_file = "data/preliminary_dependencies.json"
final_output_file = "data/final_dependencies.json"

# Function to run Maven's dependency:analyze and check for used dependencies
def run_maven_dependency_analyze(base_dir):
    try:
        # Running Maven command to analyze dependencies
        result = subprocess.run(
            ['mvn', 'dependency:analyze'],
            cwd=base_dir,  # Set the working directory to the component's base directory
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        output = result.stdout
        
        # Check if there are any unused dependencies reported
        if "No dependency problems found" in output:
            return True  # Dependency is used
        elif "Unused declared dependencies found" in output:
            return False  # Dependency is unused
        else:
            print(f"Unexpected Maven output in {base_dir}")
            return False  # Default case, assume dependency is unused if output is unclear
    except Exception as e:
        print(f"Error running Maven in {base_dir}: {e}")
        return False

# Function to check if a dependency is actually used in the component using Maven
def is_dependency_used(base_dir, group_id, artifact_id):
    print(f"Analyzing Maven dependencies in {base_dir}...")
    return run_maven_dependency_analyze(base_dir)

# Load preliminary dependencies
with open(preliminary_file, 'r') as file:
    preliminary_dependencies = json.load(file)

# Check each dependency for actual usage via Maven analysis
final_dependencies = []

for dependency in preliminary_dependencies:
    is_used = is_dependency_used(dependency['base_dir'], dependency['group_id'], dependency['artifact_id'])
    dependency['maven_analyse_used'] = is_used
    final_dependencies.append(dependency)
    status = "used" if is_used else "not used"
    print(f"Dependency {dependency['artifact_id']} is {status} in {dependency['base_dir']}")

# Save final dependencies with Maven analysis to JSON
with open(final_output_file, 'w') as json_file:
    json.dump(final_dependencies, json_file, indent=4)

print(f"Final dependencies saved to {final_output_file}")
