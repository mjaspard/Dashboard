import re

def convert_to_gigabyte(value_str):
	#print("Convert {} to gigabyte".format(value_str))
	unit = value_str[-1]
	value = float(re.search(r"\d+\.*\d*", value_str)[0])
	#print("unit = '{}' - value = {}".format(unit, value))
	if unit == 'T':
		value = 1000 * value
	elif unit == 'P':
		value = 1000000 * value
	elif unit == 'G':
		value = value
	elif unit == 'k':
		value = value/1000
	elif unit == ' ':
		#print("unit is a space")
		value = value
	else:
		print("--- !!! error ---unit not found)")
		return None
	return value

def get_synth_disk_info_mac(disk_physical):
	disk_path = re.search(r"/dev/disk\d", disk_physical)[0]
	num = disk_path[-1]
	#new_num = int(num) + 1 #???
	new_num = int(num)
	synth_str = "{}{}".format(disk_path[:-1], str(new_num))
	loc = re.search(r"(internal|external)", disk_physical)[0]
	return loc, synth_str

def get_disk_info_linux(disk_physical):
	mnt_fullname= re.search(r"/mnt/.*", disk_physical)[0]
	mnt_name = mnt_fullname.split('/')[-1]
	return mnt_name, mnt_fullname