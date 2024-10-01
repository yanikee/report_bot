import os

cog_list = []
dev_cog_list = []

path_l = ["manage", "report", "pticket"]

for path in path_l:
  files = os.listdir(f"cogs/{path}")
  for file in files:
    if not file.startswith("_"):
      cog_list.append(f"cogs.{path}.{file[:-3]}")

files = os.listdir(f"cogs/dev")
for file in files:
  if not file.startswith("_"):
    dev_cog_list.append(f"cogs.dev.{file[:-3]}")