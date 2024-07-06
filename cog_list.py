import os

cog_list = []
path_l = ["manage", "report", "pticket"]

for path in path_l:
  files = os.listdir(f"cogs/{path}")
  for file in files:
    if file.startswith("_"):
      pass
    else:
      cog_list.append(f"cogs.{path}.{file[:-3]}")