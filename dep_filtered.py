import json

# Load final_dependencies.json file
with open('data/final_dependencies.json', 'r') as file:
    final_dependencies = json.load(file)

# Function to filter dependencies
def filter_dependencies(dependencies):
    filtered = []
    for dep in dependencies:
        # Check if current dependency is part of a shorter base_dir already in filtered
        should_add = True
        for existing_dep in filtered:
            if dep['base_dir'].startswith(existing_dep['base_dir']):
                # Check if both dependencies share the same maven_analyse_used status
                if dep['maven_analyse_used'] == existing_dep['maven_analyse_used']:
                    should_add = False  # Don't add the child if both statuses match
                    break

        if should_add:
            filtered.append(dep)
    
    return filtered

# Apply the filter to final_dependencies
filtered_dependencies = filter_dependencies(final_dependencies)

# Save the filtered data to a new file
with open('data/data.json', 'w') as output_file:
    json.dump(filtered_dependencies, output_file, indent=4)

print("Filtered dependencies saved to data.json")
