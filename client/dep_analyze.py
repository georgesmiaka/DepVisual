import os
import sys
import xml.etree.ElementTree as ET
import json
import subprocess

# Directory to scan and output files
ROOT_DIR = "../../soa-solution"
OUTPUT_FILE = "../data/component_dependencies.json"

# Parse arguments passed from the server
docs = json.loads(sys.argv[1])

# Function to parse pom.xml and check for a specific dependency, returning version if found
def parse_pom_for_dependency(pom_path, target_group_id, target_artifact_id):
    try:
        tree = ET.parse(pom_path)
        root = tree.getroot()
        ns = {'mvn': 'http://maven.apache.org/POM/4.0.0'}
        
        dependencies = root.findall(".//mvn:dependency", ns)
        
        for dependency in dependencies:
            dep_group_id = dependency.find("mvn:groupId", ns).text
            dep_artifact_id = dependency.find("mvn:artifactId", ns).text
            
            # If target dependency is found, retrieve its version
            if dep_group_id == target_group_id and dep_artifact_id == target_artifact_id:
                version = dependency.find("mvn:version", ns).text if dependency.find("mvn:version", ns) is not None else "unknown"
                return True, version
    except ET.ParseError as e:
        print(f"Error parsing {pom_path}: {e}")
    except Exception as e:
        print(f"Unexpected error while processing {pom_path}: {e}")
    return False, None

# Updated find_dependencies function to save dependent's own group_id, artifact_id, and target version
def find_dependencies(doc):
    target_group_id = doc['group_id']
    target_artifact_id = doc['name']
    base_dir = doc['base_dir']
    dependencies = []

    for dirpath, _, filenames in os.walk(ROOT_DIR):
        if base_dir in dirpath:
            continue

        for filename in filenames:
            if filename == "pom.xml":
                pom_path = os.path.join(dirpath, filename)
                found, version = parse_pom_for_dependency(pom_path, target_group_id, target_artifact_id)
                if found:
                    component_dir = os.path.dirname(pom_path)
                    # Now capture the dependent's group_id and artifact_id
                    dep_group_id, dep_artifact_id = extract_component_info(pom_path)
                    dependencies.append({
                        "base_dir": component_dir,
                        "group_id": dep_group_id,
                        "artifact_id": dep_artifact_id,
                        "target_version": version,
                    })
                    print(f"Dependency found in: {pom_path}")
                    sys.stdout.flush()

    return dependencies

# Function to extract group_id and artifact_id from the pom.xml of the dependent component
def extract_component_info(pom_path):
    try:
        tree = ET.parse(pom_path)
        root = tree.getroot()
        ns = {'mvn': 'http://maven.apache.org/POM/4.0.0'}  # Namespace for Maven POM

        # Extract groupId and artifactId from the project
        group_id = root.find("mvn:groupId", ns)
        artifact_id = root.find("mvn:artifactId", ns)

        # In some cases, groupId and artifactId are nested within a parent element
        # If not found directly under project, look under parent
        if group_id is None:
            group_id = root.find("mvn:parent/mvn:groupId", ns)
        if artifact_id is None:
            artifact_id = root.find("mvn:parent/mvn:artifactId", ns)

        # Extract text from the found elements or set to "unknown" if not found
        group_id = group_id.text if group_id is not None else "unknown"
        artifact_id = artifact_id.text if artifact_id is not None else "unknown"
        
        return group_id, artifact_id

    except ET.ParseError as e:
        print(f"Error parsing {pom_path}: {e}")
    except Exception as e:
        print(f"Unexpected error while processing {pom_path}: {e}")

    return "unknown", "unknown"


# Run Maven dependency analysis on a directory to check for unused dependencies
def run_maven_dependency_analyze(base_dir):
    try:
        result = subprocess.run(
            ['mvn', 'dependency:analyze'],
            cwd=base_dir,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        output = result.stdout
        
        if "No dependency problems found" in output:
            return True
        elif "Unused declared dependencies found" in output:
            return False
        else:
            print(f"Unexpected Maven output in {base_dir}")
            return False
    except Exception as e:
        print(f"Error running Maven in {base_dir}: {e}")
        return False

# Check if each dependency is actually used
def analyze_dependencies(dependencies):
    for dependency in dependencies:
        is_used = run_maven_dependency_analyze(dependency['base_dir'])
        dependency['maven_analyse_used'] = is_used
    return dependencies

# Main function to process each document and perform analysis
def analyze_docs(docs):
    results = {}
    for doc in docs:
        dependencies = find_dependencies(doc)
        analyzed_dependencies = analyze_dependencies(dependencies)
        results[doc['name']] = analyzed_dependencies
    return results

# Run analysis on all docs and save the output to JSON
final_results = analyze_docs(docs)

with open(OUTPUT_FILE, 'w') as json_file:
    json.dump(final_results, json_file, indent=4)

print(f"Component dependencies saved to {OUTPUT_FILE}")
sys.stdout.flush()



# Beginning dependency filtering
# Load final_dependencies.json file
print("")
print("Starting to filter dependencies...")
print("")
with open('../data/component_dependencies.json', 'r') as file:
    final_dependencies = json.load(file)

# Function to filter dependencies
def filter_dependencies(dependencies):
    filtered = {}

    # Iterate over each component and its dependencies
    for component, deps in dependencies.items():
        filtered[component] = []  # Initialize a list to store filtered dependencies for this component
        
        # Iterate over each dependency
        for dep in deps:
            should_add = True
            
            # Check if current dependency is part of a shorter base_dir already in filtered
            for existing_dep in filtered[component]:
                if dep['base_dir'].startswith(existing_dep['base_dir']):
                    # Check if both dependencies share the same maven_analyse_used status
                    if dep['maven_analyse_used'] == existing_dep['maven_analyse_used']:
                        should_add = False  # Don't add the child if both statuses match
                        break

            if should_add:
                filtered[component].append(dep)  # Add the dependency to the filtered list
    
    return filtered

# Apply the filter to final_dependencies
filtered_dependencies = filter_dependencies(final_dependencies)

# Save the filtered data to a new file
with open('../data/component_dependencies_filtered.json', 'w') as output_file:
    json.dump(filtered_dependencies, output_file, indent=4)

print("")
print("Filtered dependencies saved to data/component_dependencies_filtered.sjon")
sys.stdout.flush()
print("")
