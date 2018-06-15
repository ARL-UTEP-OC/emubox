import os
#TODO: make this file editable through the GUI somehow
#OS-specific constants
if os.name == 'nt':
    VBOXMANAGE_DIRECTORY = "C:\Program Files\Oracle\VirtualBox\VBoxManage.exe"
    POSIX = False
else:
    VBOXMANAGE_DIRECTORY = "VBoxManage"
    POSIX = True
# GUI constants
BOX_SPACING = 0
PADDING = 1
WORKSHOP_CONFIG_DIRECTORY = os.path.join(os.getcwd(),"workshop_creator_gui_resources","workshop_configs")
WORKSHOP_MATERIAL_DIRECTORY = os.path.join(os.getcwd(),"workshop_creator_gui_resources","workshop_materials")
WORKSHOP_RDP_DIRECTORY = os.path.join(os.getcwd(), "workshop_creator_gui_resources","workshop_rdp")
#External files
VM_STARTER_FILE_PATH = os.path.join(os.getcwd(),"workshop-start.py")
VM_POWEROFF_FILE_PATH = os.path.join(os.getcwd(),"workshop-poweroff.py")
WORKSHOP_CREATOR_FILE_PATH = os.path.join(os.getcwd(),"workshop-creator.py")
WORKSHOP_RDP_CREATOR_FILE_PATH = os.path.join(os.getcwd(),"workshop-rdp.py")
WORKSHOP_RESTORE_FILE_PATH = os.path.join(os.getcwd(),"workshop-restore.py")
MANAGER_SAVE_DIRECTORY = os.path.join(os.getcwd(),"..","..","workshop-manager","bin","WorkshopData")
MANAGER_BIN_DIRECTORY = os.path.join(os.getcwd(), "..", "..", "workshop-manager", "bin")
#Labels
VM_TREE_LABEL = "V: "
MATERIAL_TREE_LABEL = "M: "
