import os

cog_list = []

files = os.listdir("cogs")
for file in files:
  if file.startswith("_"):
    pass
  elif file == "reload":
    pass
  else:
    cog_list.append(f"cogs.{file[:-3]}")