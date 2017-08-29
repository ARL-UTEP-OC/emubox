class Workshop_Unit:
	""" A Workshop Unit encapsulates a single Workshop Unit.

	Attributes:
		workshopName (str): The name of the workshop.
		vmName (str): The name of the virtual machine running the workshop unit. 
		ms_rdp (str): The filename of the Microsoft Remote Desktop (.rdp) file that is used to connect to the workshop unit.
		rdesktop (str): The filename of the Linux rdesktop file that is used to connect to the workshop unit
		state (str): A description of the state of the virtual machine hosting the workshop unit (Available / Unavailable).
		materials (list of str): A list of relative paths to materials associated with the workshop.
	
	"""
	def __init__(self, workshopName, vmName, ms_rdp, rdesktop, state, materials):
    	""" Constructor for a Workshop Unit object.

		Args:
			workshopName (str): The name of the workshop.
			vmName (str): The name of the virtual machine running the workshop unit. 
			ms_rdp (str): The filename of the Microsoft Remote Desktop (.rdp) file that is used to connect to the workshop unit.
			rdesktop (str): The filename of the Linux rdesktop file that is used to connect to the workshop unit
			state (str): A description of the state of the virtual machine hosting the workshop unit (Available / Unavailable).
			materials (list of str): A list of relative paths to materials associated with the workshop.

		"""
		self.workshopName = workshopName
        self.vmName = vmName
        self.ms_rdp = ms_rdp
        self.rdesktop = rdesktop
        self.state = state
        self.materials = materials