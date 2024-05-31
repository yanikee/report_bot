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


path_l = ["manage", "report", "pticket"]

cog_list = []
for path in path_l:
  files = os.listdir(f"cogs/{path}")
  for file in files:
    if file.startswith("_"):
      pass
    else:
      cog_list.append(f"cogs.{path}.{file[:-3]}")