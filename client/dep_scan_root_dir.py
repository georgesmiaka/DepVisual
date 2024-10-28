import os
import sys
import xml.etree.ElementTree as ET
import json

# Directory to scan
root_dir = "../soa-solution"
output_file = "data/component.json"

# Helper function to parse pom.xml and extract group_id, artifact_id, and version
def get_component_info(pom_path):
    try:
        tree = ET.parse(pom_path)
        root = tree.getroot()
        # Define namespaces if needed
        ns = {'maven': 'http://maven.apache.org/POM/4.0.0'}

        # Extract group_id, artifact_id, and version
        group_id = root.find('maven:groupId', ns)
        artifact_id = root.find('maven:artifactId', ns)
        version = root.find('maven:version', ns)

        return (
            group_id.text if group_id is not None else "Unknown",
            artifact_id.text if artifact_id is not None else "Unknown",
            version.text if version is not None else "Unknown"
        )
    except ET.ParseError:
        print(f"Error parsing {pom_path}")
        return None, None, None

# Function to scan directory and find components
def find_component(root_directory):
    components = []
    for dirpath, _, filenames in os.walk(root_directory):
        for filename in filenames:
            if filename == "pom.xml":
                pom_path = os.path.join(dirpath, filename)
                group_id, artifact_id, version = get_component_info(pom_path)
                components.append({
                    "name": artifact_id,
                    "group_id": group_id,
                    "version": version,
                    "base_dir": pom_path
                })
                print(f"Component found in: {pom_path}")
    # Ensure the output directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    # Write to JSON file
    with open(output_file, 'w') as f:
        json.dump(components, f, indent=4)

print("")
# Call the function
find_component(root_dir)
print("")
print("...")
print(f"Components saved to {output_file}")
print("")