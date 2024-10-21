import os
import sys
import xml.etree.ElementTree as ET
import json

# Step 1: User input component information
#group_id = "com.wirelesscar.soa"
#artifact_id = "soa-sla-reporting-model"
#base_dir = "../soa-solution/sla/soa-sla-reporting-model"

# Extract arguments passed from the Bash script
group_id = sys.argv[1]
artifact_id = sys.argv[2]
base_dir = sys.argv[3]

# Directory to scan
root_dir = "../soa-solution"
output_file = "data/preliminary_dependencies.json"

# Function to parse pom.xml and check for dependency
def parse_pom_for_dependency(pom_path, target_group_id, target_artifact_id):
    try:
        tree = ET.parse(pom_path)
        root = tree.getroot()
        ns = {'mvn': 'http://maven.apache.org/POM/4.0.0'}  # Namespace for Maven POM
        
        # Find all dependencies in the POM file
        dependencies = root.findall(".//mvn:dependency", ns)
        
        for dependency in dependencies:
            dep_group_id = dependency.find("mvn:groupId", ns).text
            dep_artifact_id = dependency.find("mvn:artifactId", ns).text
            
            # Check if the dependency matches the target
            if (dep_group_id == target_group_id and 
                dep_artifact_id == target_artifact_id):  # Check for major version compatibility
                return True
    except ET.ParseError as e:
        print(f"Error parsing {pom_path}: {e}")  # Log parsing errors
        return False  # Skip this file
    except Exception as e:
        print(f"Unexpected error while processing {pom_path}: {e}")  # Log unexpected errors
        return False  # Skip this file

# Function to scan directories and detect dependencies
def find_dependencies(root_directory, target_group_id, target_artifact_id, exclude_dir):
    dependencies = []

    for dirpath, _, filenames in os.walk(root_directory):
        # Skip the user-provided component directory
        if exclude_dir in dirpath:
            continue

        for filename in filenames:
            if filename == "pom.xml":
                pom_path = os.path.join(dirpath, filename)
                if parse_pom_for_dependency(pom_path, target_group_id, target_artifact_id):
                    component_dir = os.path.dirname(pom_path)
                    dependencies.append({
                        "base_dir": component_dir,
                        "group_id": target_group_id,
                        "artifact_id": target_artifact_id,
                    })
                    print(f"Dependency found in: {pom_path}")
    
    return dependencies

# Run the function
dependencies = find_dependencies(root_dir, group_id, artifact_id, base_dir)

# Save preliminary dependencies to JSON
with open(output_file, 'w') as json_file:
    json.dump(dependencies, json_file, indent=4)

# save component info
# Write the group id to a JSON file
output_file_for_groupId_json = "data/key.json"
result = {"group_id": group_id, "artifact_id": artifact_id, "dir": base_dir}
with open(output_file_for_groupId_json, 'w') as outfile:
    json.dump(result, outfile, indent=4)
print(f"Component group id written to {output_file_for_groupId_json}")
print("")

print(f"Preliminary dependencies saved to {output_file}")
