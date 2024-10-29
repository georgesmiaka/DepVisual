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

# Function to parse pom.xml and check for a specific dependency
def parse_pom_for_dependency(pom_path, target_group_id, target_artifact_id):
    try:
        tree = ET.parse(pom_path)
        root = tree.getroot()
        ns = {'mvn': 'http://maven.apache.org/POM/4.0.0'}  # Namespace for Maven POM
        
        dependencies = root.findall(".//mvn:dependency", ns)
        
        for dependency in dependencies:
            dep_group_id = dependency.find("mvn:groupId", ns).text
            dep_artifact_id = dependency.find("mvn:artifactId", ns).text
            
            if dep_group_id == target_group_id and dep_artifact_id == target_artifact_id:
                return True
    except ET.ParseError as e:
        print(f"Error parsing {pom_path}: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error while processing {pom_path}: {e}")
        return False

# Function to scan directories and find dependencies for a specific doc
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
                if parse_pom_for_dependency(pom_path, target_group_id, target_artifact_id):
                    component_dir = os.path.dirname(pom_path)
                    dependencies.append({
                        "base_dir": component_dir,
                        "group_id": target_group_id,
                        "artifact_id": target_artifact_id,
                    })
                    print(f"Dependency found in: {pom_path}")
                    sys.stdout.flush()

    return dependencies

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
