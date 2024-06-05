import json
import os

webservers = 2
db_servers = 48

# Generate decoy file
layered = True
decoys = 5

file_name = "layered_equifaxLarge_env.json"


def main():

    subnets = [{"webserver_subnet": []}, {"db_subnet": []}]

    for i in range(0, webservers):
        host_info = {"ip": f"192.168.1.{i}", "users": ["tomcat"]}
        subnets[0]["webserver_subnet"].append(host_info)

        if layered:
            decoy_host = {
                "ip": f"192.168.1.{i + webservers}",
                "users": ["decoy_user"],
                "decoy": True,
            }
            subnets[0]["webserver_subnet"].append(decoy_host)

    for i in range(0, db_servers):
        host_info = {"ip": f"192.168.2.{i}", "users": [f"database_{i}"]}
        subnets[1]["db_subnet"].append(host_info)

    # Save json in current directory
    current_dir = os.path.dirname(os.path.realpath(__file__))
    with open(os.path.join(current_dir, file_name), "w") as f:
        json.dump(subnets, f, indent=4)


if __name__ == "__main__":
    main()
