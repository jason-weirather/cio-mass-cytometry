import yaml

# Load the environment.yml file
with open("environment.yml", "r") as yamfile:
    data = yaml.load(yamfile, Loader=yaml.FullLoader)

# Initialize the command with the mamba install command and channels
args = ""
for channel in data['channels']:
    args += "-c " + channel + " "

# Generate the mamba install command with all dependencies
deps = " ".join(data['dependencies'])

# Output the bash script
print("#!/usr/bin/env bash")
print(f"mamba install -y --strict-channel-priority {args.strip()} {deps}")

