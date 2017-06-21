from lxml import etree

# Get these from the workshop-creator GUI
PATH_TO_VBOXMANAGE = "C:\Program Files\Oracle\VirtualBox\VBoxManage.exe"
IP_ADDRESS = "localhost"
BASE_GROUPNAME = "Multi_Interfaces"
NUM_CLONES = "3"
CLONE_SNAPSHOTS = "true"
LINKED_CLONES = "true"
BASE_OUTNAME = "101"
VRDP_BASEPORT = "1011"

# VMs are in a list
# Each individual VM is also a list where:
# index 0 = name of that VM
# index 1 = vrdp-enabled (boolean)
# index 2 = list of internal network adapters for that VM
VM_LIST = [
	["kali-2016.2-debian_ecel", "true", ["intnetA", "intnetB"]], 
	["ubuntu-core4.7", "false", ["intnetB", "intnetC"]], 
	["windows7_HW_v3", "false", ["intnetC"]]
	]

# Create root of XML etree
root = etree.Element("xml")

# Populate vbox-setup fields
vbox_setup_element = etree.SubElement(root, "vbox-setup")
etree.SubElement(vbox_setup_element, "path-to-vboxmanage").text = PATH_TO_VBOXMANAGE

# Populate testbed-setup fields
testbed_setup_element = etree.SubElement(root, "testbed-setup")
network_config_element = etree.SubElement(testbed_setup_element, "network-config")
etree.SubElement(network_config_element, "ip-address").text = IP_ADDRESS

# Populate vm-set fields
vm_set_element = etree.SubElement(testbed_setup_element, "vm-set")
etree.SubElement(vm_set_element, "base-groupname").text = BASE_GROUPNAME
etree.SubElement(vm_set_element, "num-clones").text = NUM_CLONES
etree.SubElement(vm_set_element, "clone-snapshots").text = CLONE_SNAPSHOTS
etree.SubElement(vm_set_element, "linked-clones").text = LINKED_CLONES
etree.SubElement(vm_set_element, "base-outname").text = BASE_OUTNAME
etree.SubElement(vm_set_element, "vrdp-baseport").text = VRDP_BASEPORT

# Iterate through list of VMs and whether vrdp is enabled for that vm 
for vm in VM_LIST:
	vm_element = etree.SubElement(vm_set_element, "vm")
	etree.SubElement(vm_element, "name").text = vm[0]
	etree.SubElement(vm_element, "vrdp-enabled").text = vm[1]
	for internalnet in vm[2]:
		etree.SubElement(vm_element, "internalnet-basename").text = internalnet

# Create tree for writing to XML file
tree = etree.ElementTree(root) 

# Write tree to XML config file
tree.write("output.xml", pretty_print = True)