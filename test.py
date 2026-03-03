import json


def json_test():
    data = json.load(open("config.json"))
    print(type(data))
    print(data)
    users = data["users"]
    print(type(users))
    print(users)


if __name__ == "__main__":
    json_test()
