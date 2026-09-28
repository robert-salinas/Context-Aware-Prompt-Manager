from pathlib import Path

root = Path(SPECPATH)
datas = [(str(root / "assets"), "assets"), (str(root / "prompts"), "prompts")]
a = Analysis([str(root / "src" / "prompt_mgr" / "gui.py")], pathex=[str(root / "src")], datas=datas, hiddenimports=["customtkinter", "git"], noarchive=False)
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, a.binaries, a.datas, [], name="RS-Context-Prompt-Manager", debug=False, strip=False, upx=True, console=False, icon=str(root / "assets" / "icon.ico"), version=str(root / "version_info.txt"))
