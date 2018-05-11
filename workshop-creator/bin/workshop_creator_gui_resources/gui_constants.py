import os
#TODO: make this file editable through the GUI somehow
# GUI constants
BOX_SPACING = 5
PADDING = 5
WORKSHOP_CONFIG_DIRECTORY = os.path.join(os.getcwd(),"workshop_creator_gui_resources","workshop_configs")
WORKSHOP_MATERIAL_DIRECTORY = os.path.join(os.getcwd(),"workshop_creator_gui_resources","workshop_materials")
WORKSHOP_RDP_DIRECTORY = os.path.join(os.getcwd(), "workshop_creator_gui_resources","workshop_rdp")
#VirtualBox files
VBOXMANAGE_DIRECTORY = "VBoxManage"
#External files
WORKSHOP_CREATOR_FILE_PATH = os.path.join(os.getcwd(),"workshop-creator.py")
WORKSHOP_RDP_CREATOR_FILE_PATH = os.path.join(os.getcwd(),"workshop-rdp.py")
WORKSHOP_RESTORE_FILE_PATH = os.path.join(os.getcwd(),"workshop-restore.py")
MANAGER_SAVE_DIRECTORY = os.path.join(os.getcwd(),"..","..","workshop-manager","bin","WorkshopData")
