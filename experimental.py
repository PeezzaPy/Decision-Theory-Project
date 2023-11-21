async def example():

  result = await get_user()
  print(result)

async def get_user():
  username = input("Enter username: ")
  password = input("Enter password: ")

  return username, password

if __name__ == "__main__":
  example()