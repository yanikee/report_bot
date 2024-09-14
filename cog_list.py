import os

cog_list = []
dev_cog_list = []

path_l = ["manage", "report", "pticket"]

for path in path_l:
  files = os.listdir(f"cogs/{path}")
  for file in files:
    if file.startswith("_"):
      pass
    elif file in ["notification.py", "reload.py", "bot_update.py"]:
      dev_cog_list.append(f"cogs.{path}.{file[:-3]}")
    else:
      cog_list.append(f"cogs.{path}.{file[:-3]}")