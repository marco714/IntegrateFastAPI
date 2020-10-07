from dataclasses import dataclass, field

@dataclass
class Person:

    first_name:str
    last_name:str
    age:int
    youtube:object = field


    def name1(self, first_name, last_name, age):

        return f"{first_name}, {last_name}, {age}"

# person1 = Person("Marco", "Narca", 16)
api_key = 'AIzaSyCnFh303loltfwQVvlJfzRECZupxY0z6Bw'
print(len(api_key))


{
  "videos": [
    "UO98lJQ3QGI",
    "nKxLfUrkLE8",
    "MPiz50TsyF0",
    "xN-Supd4H38",
    "x0Uguu7gqgk"
  ]
}


{
  "videos": [
    "XFZRVnP-MTU","Ercd-Ip5PfQ","_LWjaAiKaf8","zZZ_RCwp49g","XDv6T4a0RNc","x0Uguu7gqgk","UO98lJQ3QGI","nKxLfUrkLE8","MPiz50TsyF0","xN-Supd4H38","x0Uguu7gqgk"
  ]
}
