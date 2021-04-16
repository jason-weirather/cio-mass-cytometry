import yaml
with open("environment.yml","r") as yamfile:
    data = yaml.load(yamfile,Loader=yaml.FullLoader)
args = " "
for channel in data['channels']:
    args += "-c "+channel+" "
print("#!/usr/bin/env bash")
for dep in data['dependencies']:
    args += dep+" "
    #print("conda install -y --strict-channel-priority "+args+" "+dep)
print("conda install -y --strict-channel-priority "+args.strip())
