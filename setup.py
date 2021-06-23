import os
import sys
import shutil

def main():
	FOLDER  = "/.FaceUnlocker"
	AUTOFILE= "/.config/autostart/faceunlocker.desktop"
	try:
		# create FOLDER if not exist
		if not os.path.isdir(os.environ["HOME"]+FOLDER):
			os.makedirs(os.environ["HOME"]+FOLDER)

		# copy source files into destination
		dl=os.listdir(os.getcwd())
		for file in dl:
			if "setup.py" in file:
				continue
			else:
				if not os.path.isdir(file):
					shutil.copy(file, os.environ["HOME"]+FOLDER)
				else:
					shutil.copytree(file, os.environ["HOME"]+FOLDER+"/Img_DB")
		# create autofile 
		if os.path.isfile(os.environ["HOME"]+AUTOFILE):
			lines = [
				"[Desktop Entry]\n",
				"Type=Application\n",
				"Exec=python \"/home/student/.FaceUnlocker/main.py\"\n",
				"Hidden=false\n",
				"NoDisplay=false\n",
				"X-GNOME-Autostart-enabled=true\n",
				"Name[en_IN]=faceunlocker.desktop\n",
				"Name=FaceUnlocker\n",
				"Comment[en_IN]=Enjoy Laziness\n",
				"Comment=Enjoy Laziness\n"
			]
			with open(os.environ["HOME"]+AUTOFILE,"w") as sa:
				sa.writelines(lines)
			sa.close()
	except OSError as e:
		print e
	except Exception as e:
		print "Error occurred while copying file.\n",e
	finally:
		req = True if raw_input("Would you like run Application right after installation? [Y/N]: ")=="Y" else False
		if not req:
			print "Thank you for installing our application"
		else:
			print "Application started"

if __name__ == '__main__':
	main()
