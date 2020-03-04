from ict_charge import *
import settings


for file in settings.FILE_LIST:
    if file.endswith(settings.FILE_TYPE) and file.startswith(settings.FILE_START_STRING):
        ICT_signal = ProcessIctSignal(file, settings.FOLDER_PATH)
        volt_list_all, time_list_all = ICT_signal.ict_frame_data()
        charge, std = ICT_signal.get_ict_charge()
