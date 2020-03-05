import numpy as np
from scipy.integrate import simps
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import settings
import exceptions


def linear_fit(x, a):
    return a * x


class ProcessIctSignal:
    def __init__(self, file, file_path):
        self.file = file
        self.file_path = file_path
        self.volt_list_all = []
        self.time_list_all = []
        self.offset = []
        self.dt = []

    def ict_frame_data(self):
        volts_ls_all = []
        time_ls_all = []
        frame_number = 0
        with open(self.file_path + self.file, 'r') as f:
            lines = f.readlines()
            num_data = int(lines[3].split()[4])
            for i in range(len(lines)):
                # get the total number of frames
                if "time" in lines[i].split():
                    frame_number += 1

            # construct the voltage and time list
            for i in range(len(lines)):
                try:
                    float(lines[i][0])
                    ans = True
                except:
                    ans = False

                if ans is True:
                    volts_ls_all.append(format(float(lines[i].split()[-1]), '.9f'))
                    time_ls_all.append(format(float(lines[i].split()[0]), '.20f'))

        self.volt_list_all = np.reshape(volts_ls_all, (frame_number, num_data)).astype(np.float)
        self.time_list_all = np.reshape(time_ls_all, (frame_number, num_data)).astype(np.float)
        return self.volt_list_all, self.time_list_all

    # def get_ict_raw_data(self):
    #     if not self.volt_list_all or self.time_list_all:
    #         raise exceptions.IctDataError("Not able to get the ICT raw data.")
    #     else:
    #         self.volt_list_all, self.time_list_all = self.ict_frame_data()
    #         return self.volt_list_all, self.time_list_all

    def get_volt_offset(self):
        # Get signal offset from the first couple of elements
        for i in range(len(self.volt_list_all)):
            offset_single_frame = np.mean(self.volt_list_all[i][:settings.AVERAGE_NUMBER])
            self.offset.append(offset_single_frame)
        return self.offset

    def integration_step(self):
        # Get time step for integration.
        for i in range(len(self.time_list_all)):
            dt_single_frame = abs(self.time_list_all[i][1] - self.time_list_all[i][0])
            self.dt.append(dt_single_frame)
        return self.dt

    def get_ict_charge(self):
        charge_list_all = []
        offset = self.get_volt_offset()
        dt = self.integration_step()
        volt_w_offset = [self.volt_list_all[i] - offset[i] for i in range(len(offset))]

        for i in range(len(volt_w_offset)):
            charge = simps(y=np.array(volt_w_offset[i]), dx=float(dt[i]))
            charge_list_all.append(charge * 10 ** 12 / settings.ICT_CALIBRATION_FACTOR)    # charge in pC

        # remove highest a few and lowest a few results.
        desired_charges = sorted(charge_list_all)[settings.ICT_CUT_LOW_BOUNDARY: (len(charge_list_all) - settings.ICT_CUT_HIGH_BOUNDARY)]
        print('min charge  =>', np.max(desired_charges))
        print('max charge =>', np.min(desired_charges))
        print('std => ', np.std(desired_charges))
        print('absolute value of the averaged charges=> ', abs(np.mean(desired_charges)))

        return abs(np.mean(desired_charges)), np.std(desired_charges)

    def plot_ict_data(self):
        pdf = PdfPages(self.file.split('.')[0] + '_ICT_raw.pdf')
        for i in range(len(self.volt_list_all)):
            plt.plot(self.time_list_all[i], self.volt_list_all[i], c='b')
            plt.axhline(self.offset[i], c='darkorange', ls=':')
            plt.xlabel('Time (s)')
            plt.ylabel('Voltage (V)')
            plt.title(self.file + "\nframe# %.1f (Offest = %.5f)" % (i + 1, self.offset[i]))
            pdf.savefig(bbox_inches='tight')
            plt.close()
        pdf.close()
