# The following variables may be modified to change how often certain processes will run.
# All variables represent time in seconds.

# 'VBOX_PROBETIME': Used by vbox_monitor. The interval of time it will probe VirtualBox for VM info.
# Also used by the webdata_aggregator. The interval of time it will probe vbox_monitor for VM info.
VBOX_PROBETIME = 5

# 'VM_RESTORE_TIME': Used by vbox_monitor. The interval of time to check for VMs that need to be restored.
VM_RESTORE_TIME = 1

# 'LOCK_WAIT_TIME': Used by vbox_monitor. The amount of time to wait for locks to be released when an error occurs.
LOCK_WAIT_TIME = 5

# 'CHECKOUT_TIME': Used by the webdata_aggregator. The amount of time a workshop is 'on hold' after checkout.
CHECKOUT_TIME = 30

# 'THREAD_TIME': Used by the flask_server. The interval of time to run queued threads.
THREAD_TIME = 2

# 'ZIP_CLEAR_TIME': Used by the flask_server. The interval of time to clear up zipped files.
ZIP_CLEAR_TIME = 15
