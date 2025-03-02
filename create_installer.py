# -*- coding: utf-8 -*-

import os, subprocess, sys
from os import path

wix_version = "5.0.2"
user_profie = os.environ["USERPROFILE"]
wix_exe = path.join(user_profie, ".dotnet", "tools", "wix.exe")
wix_ui_ext = "WixToolset.UI.wixext"
project_dir = path.dirname(path.realpath(__file__))


def ensure_wix_installed():
  if path.exists(wix_exe):
    subprocess.run([
      wix_exe,
      "--version",
    ], check=True)
    print("WiX Toolset installation found, path: {}".format(wix_exe))
    return

  print("Intalling WiX Toolset, version: {} ...".format(wix_version))
  subprocess.run([
    "dotnet",
    "tool", 
    "install", 
    "--global",
    "wix",
    "--version",
    wix_version,
  ], check=True)

  if not path.exists(wix_exe):
    print("ERROR: WiX Toolset installation failed, expected path: {}".format(wix_exe))
    sys.exit(1)

  subprocess.run([
    wix_exe,
    "--version",
  ], check=True)
  print("WiX Toolset installed successfully, path: {}",  wix_exe)


def ensure_extensions(names):
  ps = subprocess.run([
    wix_exe,
    "extension",
    "list",
  ], capture_output=True)
  if not ps.returncode in [0, 2]:
    print("ERROR: Cannot list WiX extensions, code: {}, message: {}".format(ps.returncode, ps.stderr.decode("utf-8")))
    sys.exit(1)
  existing_list = ps.stdout.decode("utf-8").split("\r\n")

  missing_list = []
  for name in names:
    if "{} {}".format(name, wix_version) not in existing_list:
      missing_list.append(name)

  for name in missing_list: 
    print("Installing WiX extension, name: {}, version: {} ...".format(name, wix_version))
    subprocess.run([
      wix_exe,
      "extension",
      "add",
      "{}/{}".format(name, wix_version),
    ], check=True)
    print("Extension installed successfully.")


def bundle_msi():
  msi = "duckdb_odbc.msi"
  if path.exists(msi):
    os.remove(msi)
  print("Bundling MSI installer, name: {} ...".format(msi))
  subprocess.run([
    wix_exe,
    "build",
    "-arch", "x64",
    "-ext", wix_ui_ext,
    "duckdb_odbc.wxs",
  ], cwd=project_dir, check=True)
  print("Installer bundled successfully")


if __name__ == "__main__":
  ensure_wix_installed()
  ensure_extensions([
    wix_ui_ext
  ])
  bundle_msi()