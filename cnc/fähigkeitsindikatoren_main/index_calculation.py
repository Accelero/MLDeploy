import scipy
import numpy as np

class IndexClass():

    # Class for the index calculation
    # Currently just for x,y,z axis ans spindle --> update for all axis
    
    PERCENT_AREA_1 = 0.20   # percentage of the firts wear area
    PERCENT_AREA_2 = 0.60   # percentage of the second wear area
    PERCENT_AREA_3 = 0.80   # percentage of the third wear area
    
    def __init__(self, index_matrix):
        # Initialize the class

        self.pos_start = [0]*len(index_matrix)   # Sartingposition of the current tool wear cycle
        self.last_len = [0]*len(index_matrix)   # len of the indexmatrix at the last calculation
    
        # Data for tool index calculation
        self.factor_matrix_tool = np.ones([len(index_matrix),len(index_matrix[0])])
        self.wear_index_tool = [[] for i in range(len(index_matrix))]
        self.factor_tool = [0.1,0.1,0.1,0.1]
        self.f_thrs = 0.5
        self.upper_tool = [[0] for i in range(len(index_matrix))]
        self.lower_tool = [[0] for i in range(len(index_matrix))]
        self.wear_percentage_tool = [[] for i in range(len(index_matrix))]

        # Data for spindel index calculation
        self.wear_index_spindle = [[] for i in range(len(index_matrix))]
        self.diff_wear_index_spindle = [[] for i in range(len(index_matrix))]
        self.wear_area_spindle = [0]*len(index_matrix)
        self.wear_percentage_base_spindle = [0]*len(index_matrix)
        self.wear_percentage_spindle = [[] for i in range(len(index_matrix))]
    
    
        # Data for x axis index calculation
        self.wear_index_x = [[] for i in range(len(index_matrix))]
        self.diff_wear_index_x = [[] for i in range(len(index_matrix))]
        self.wear_area_x = [0]*len(index_matrix)
        self.wear_percentage_base_x = [0]*len(index_matrix)
        self.wear_percentage_x = [[] for i in range(len(index_matrix))]
    
        # Data for y axis index calculation
        self.wear_index_y = [[] for i in range(len(index_matrix))]
        self.diff_wear_index_y = [[] for i in range(len(index_matrix))]
        self.wear_area_y = [0]*len(index_matrix)
        self.wear_percentage_base_y = [0]*len(index_matrix)
        self.wear_percentage_y = [[] for i in range(len(index_matrix))]
    
        # Data for z axis index calculation
        self.wear_index_z = [[] for i in range(len(index_matrix))]
        self.diff_wear_index_z = [[] for i in range(len(index_matrix))]
        self.wear_area_z = [0]*len(index_matrix)
        self.wear_percentage_base_z = [0]*len(index_matrix)
        self.wear_percentage_z = [[] for i in range(len(index_matrix))]

              
    def __recalculate_tool_index__(self, index_matrix, class_nr, i_pos):
        # recalculate the tool index if there is a sudden change in tool current for a cycle
    
        # get the right factor vector for the calculation
        if self.pos_start[class_nr] == 0:
            f = [1,1,1,1]
        else:
            f = self.factor_tool

        # update the factor matrix for the cycle based on the last correlation
        self.factor_matrix_tool[class_nr,:] = np.array([self.factor_matrix_tool[class_nr,0]*(1-f[0]) + scipy.stats.spearmanr( index_matrix[class_nr][0][self.pos_start[class_nr]:i_pos-2] , range(i_pos-2-self.pos_start[class_nr]))[0]**3*f[0],
                                                  self.factor_matrix_tool[class_nr,1]*(1-f[1]) + scipy.stats.spearmanr( index_matrix[class_nr][1][self.pos_start[class_nr]:i_pos-2] , range(i_pos-2-self.pos_start[class_nr]))[0]**3*f[1],
                                                  self.factor_matrix_tool[class_nr,2]*(1-f[2]) + scipy.stats.spearmanr( index_matrix[class_nr][2][self.pos_start[class_nr]:i_pos-2] , range(i_pos-2-self.pos_start[class_nr]))[0]**3*f[2],
                                                  self.factor_matrix_tool[class_nr,3]*(1-f[3]) + scipy.stats.spearmanr( index_matrix[class_nr][3][self.pos_start[class_nr]:i_pos-2] , range(i_pos-2-self.pos_start[class_nr]))[0]**3*f[3]
                                                  ])

        # Update the tool wear index
        self.wear_index_tool[class_nr] += [ sum( [self.factor_matrix_tool[class_nr,sig]*index_matrix[class_nr][sig][i_pos] for sig in range(len(index_matrix[class_nr]))] )]

        # Update the axis index
        self.__update_axis_index__(index_matrix, class_nr, i_pos)

        # claculate new staring position and the threshold

        if self.pos_start[class_nr] == 0:
            self.lower_tool[class_nr] += [0]
            self.upper_tool[class_nr] += [self.wear_index_tool[class_nr][-3]]
        else:
            self.lower_tool[class_nr] += [self.lower_tool[class_nr][-1]*(1-self.f_thrs) + self.wear_index_tool[class_nr][self.pos_start[class_nr]]*self.f_thrs]
            self.upper_tool[class_nr] += [self.upper_tool[class_nr][-1]*(1-self.f_thrs) + self.wear_index_tool[class_nr][-3]*self.f_thrs]

        self.pos_start[class_nr] = len(self.wear_index_tool[class_nr])-1

    def __update_axis_index__(self, index_matrix, class_nr, i_pos):
        # Update the axis wear indice and calculate the area (0=new, 1=progress, 2=end of lifecycle)
    
        # update the index for the x axis
        self.wear_index_x[class_nr] += [sum(index_matrix[class_nr][0][self.pos_start[class_nr]:i_pos-2])/(i_pos-self.pos_start[class_nr]-2)]
    
        if len(self.wear_index_x[class_nr]) >= 20:
            # recalculate the wear index and the area for the x axis
            index = self.wear_index_x[class_nr][-20:]   # get the relevant indices
            index_mean = [sum(index[i:i+5])/5 for i in range(15)]   # calculate the rolling mean
            index_dmax = [max([index_mean[i+ii+1]- index_mean[i+ii]  for ii in   range(5)]) for i in range(10)]   # calculate the derivative and get max
            index_ddmax = [max([index_dmax[i+ii+1]- index_dmax[i+ii]  for ii in   range(5)]) for i in range(5)]  # calculate the derivative and get max
            index_ddmin = [min([index_mean[i+ii+1]- index_mean[i+ii]  for ii in   range(5)]) for i in range(5)]  # calculate the derivative and get max 
            index_ddmax_mean = sum(index_ddmax)/5   # calculate the mean
            index_ddmin_mean = sum(index_ddmin)/5   # calculate the mean
            
            if index_ddmin_mean > -0.001 and self.wear_area_x[class_nr]==0:
                # first wear area
                self.wear_percentage_base_x[class_nr] = len(self.wear_index_x[class_nr])    
                self.wear_area_x[class_nr] = 1
            elif index_ddmax_mean > 0 and self.wear_area_x[class_nr]==1:
                # second wear area
                self.wear_percentage_base_x[class_nr] = len(self.wear_index_x[class_nr])    
                self.wear_area_x[class_nr] = 2
            elif index_ddmax_mean > 0.001 and self.wear_area_x[class_nr]==2:
                # third wear area
                self.wear_percentage_base_x[class_nr] = len(self.wear_index_x[class_nr])    
                self.wear_area_x[class_nr] = 3

            if self.wear_area_x[class_nr] == 1:
                # calculate the percentage if the x axis is in the first wear area
                self.wear_percentage_x[class_nr] += [len(self.wear_index_x[class_nr])/(self.wear_percentage_base_x[class_nr]/self.PERCENT_AREA_1)*100]
            if self.wear_area_x[class_nr] == 2:
                # calculate the percentage if the x axis is in the second wear area
                self.wear_percentage_x[class_nr] += [len(self.wear_index_x[class_nr])/(self.wear_percentage_base_x[class_nr]/self.PERCENT_AREA_2)*100]
            if self.wear_area_x[class_nr] == 3:
                # calculate the percentage if the x axis is in the third wear area
                self.wear_percentage_x[class_nr] += [len(self.wear_index_x[class_nr])/(self.wear_percentage_base_x[class_nr]/self.PERCENT_AREA_3)*100]     
        else:
            self.wear_percentage_x[class_nr] += ['nan']      


        # recalculate the wear index and area for the y axis, change of area if 25% threshold of teh index is passed
        self.wear_index_y[class_nr] += [sum(index_matrix[class_nr][1][self.pos_start[class_nr]:i_pos-2])/(i_pos-self.pos_start[class_nr]-2)]
    
        if len(self.wear_index_y[class_nr]) >= 20:
            # recalculate the wear index and the area for the y axis
            index = self.wear_index_y[class_nr][-20:]   # get the relevant indices
            index_mean = [sum(index[i:i+5])/5 for i in range(15)]   # calculate the rolling mean
            index_dmax = [max([index_mean[i+ii+1]- index_mean[i+ii]  for ii in   range(5)]) for i in range(10)]   # calculate the derivative and get max
            index_ddmax = [max([index_dmax[i+ii+1]- index_dmax[i+ii]  for ii in   range(5)]) for i in range(5)]  # calculate the derivative and get max
            index_ddmin = [min([index_mean[i+ii+1]- index_mean[i+ii]  for ii in   range(5)]) for i in range(5)]  # calculate the derivative and get max 
            index_ddmax_mean = sum(index_ddmax)/5   # calculate the mean
            index_ddmin_mean = sum(index_ddmin)/5   # calculate the mean
            
            if index_ddmin_mean > -0.001 and self.wear_area_y[class_nr]==0:
                # first wear area
                self.wear_percentage_base_y[class_nr] = len(self.wear_index_y[class_nr])    
                self.wear_area_y[class_nr] = 1
            elif index_ddmax_mean > 0 and self.wear_area_y[class_nr]==1:
                # second wear area
                self.wear_percentage_base_y[class_nr] = len(self.wear_index_y[class_nr])    
                self.wear_area_y[class_nr] = 2
            elif index_ddmax_mean > 0.001 and self.wear_area_y[class_nr]==2:
                # third wear area
                self.wear_percentage_base_y[class_nr] = len(self.wear_index_y[class_nr])    
                self.wear_area_y[class_nr] = 3

            if self.wear_area_y[class_nr] == 1:
                # calculate the percentage if the x axis is in the first wear area
                self.wear_percentage_y[class_nr] += [len(self.wear_index_y[class_nr])/(self.wear_percentage_base_y[class_nr]/self.PERCENT_AREA_1)*100]
            if self.wear_area_x[class_nr] == 2:
                # calculate the percentage if the x axis is in the second wear area
                self.wear_percentage_y[class_nr] += [len(self.wear_index_y[class_nr])/(self.wear_percentage_base_y[class_nr]/self.PERCENT_AREA_2)*100]
            if self.wear_area_y[class_nr] == 3:
                # calculate the percentage if the x axis is in the third wear area
                self.wear_percentage_y[class_nr] += [len(self.wear_index_y[class_nr])/(self.wear_percentage_base_y[class_nr]/self.PERCENT_AREA_3)*100] 
        else:
            self.wear_percentage_y[class_nr] += ['nan']      

        # recalculate the wear index and area for the z axis, change of area if 25% threshold of teh index is passed
        self.wear_index_z[class_nr] += [sum(index_matrix[class_nr][2][self.pos_start[class_nr]:i_pos-2])/(i_pos-self.pos_start[class_nr]-2)]

        if len(self.wear_index_z[class_nr]) >= 20:
            # recalculate the wear index and the area for the z axis
            index = self.wear_index_z[class_nr][-20:]   # get the relevant indices
            index_mean = [sum(index[i:i+5])/5 for i in range(15)]   # calculate the rolling mean
            index_dmax = [max([index_mean[i+ii+1]- index_mean[i+ii]  for ii in   range(5)]) for i in range(10)]   # calculate the derivative and get max
            index_ddmax = [max([index_dmax[i+ii+1]- index_dmax[i+ii]  for ii in   range(5)]) for i in range(5)]  # calculate the derivative and get max
            index_ddmin = [min([index_mean[i+ii+1]- index_mean[i+ii]  for ii in   range(5)]) for i in range(5)]  # calculate the derivative and get max 
            index_ddmax_mean = sum(index_ddmax)/5   # calculate the mean
            index_ddmin_mean = sum(index_ddmin)/5   # calculate the mean

            if index_ddmin_mean > -0.001 and self.wear_area_z[class_nr]==0:
                # first wear area
                self.wear_percentage_base_z[class_nr] = len(self.wear_index_z[class_nr])    
                self.wear_area_z[class_nr] = 1
            elif index_ddmax_mean > 0 and self.wear_area_z[class_nr]==1:
                # second wear area
                self.wear_percentage_base_z[class_nr] = len(self.wear_index_z[class_nr])    
                self.wear_area_z[class_nr] = 2
            elif index_ddmax_mean > 0.001 and self.wear_area_z[class_nr]==2:
                # third wear area
                self.wear_percentage_base_z[class_nr] = len(self.wear_index_z[class_nr])    
                self.wear_area_z[class_nr] = 3

            if self.wear_area_z[class_nr] == 1:
                # calculate the percentage if the x axis is in the first wear area
                self.wear_percentage_z[class_nr] += [len(self.wear_index_z[class_nr])/(self.wear_percentage_base_z[class_nr]/self.PERCENT_AREA_1)*100]
            if self.wear_area_z[class_nr] == 2:
                # calculate the percentage if the x axis is in the second wear area
                self.wear_percentage_z[class_nr] += [len(self.wear_index_z[class_nr])/(self.wear_percentage_base_z[class_nr]/self.PERCENT_AREA_2)*100]
            if self.wear_area_z[class_nr] == 3:
                # calculate the percentage if the x axis is in the third wear area
                self.wear_percentage_z[class_nr] += [len(self.wear_index_z[class_nr])/(self.wear_percentage_base_z[class_nr]/self.PERCENT_AREA_3)*100]
        else:
            self.wear_percentage_z[class_nr] += ['nan']      


        # recalculate the wear index and area for the spindle, change of area if 25% threshold of teh index is passed
        self.wear_index_spindle[class_nr] += [sum(index_matrix[class_nr][3][self.pos_start[class_nr]:i_pos-2])/(i_pos-self.pos_start[class_nr]-2)]

        if len(self.wear_index_spindle[class_nr]) >= 20:
            # recalculate the wear index and the area for the x axis
            index = self.wear_index_spindle[class_nr][-20:]   # get the relevant indices
            index_mean = [sum(index[i:i+5])/5 for i in range(15)]   # calculate the rolling mean
            index_dmax = [max([index_mean[i+ii+1]- index_mean[i+ii]  for ii in   range(5)]) for i in range(10)]   # calculate the derivative and get max
            index_ddmax = [max([index_dmax[i+ii+1]- index_dmax[i+ii]  for ii in   range(5)]) for i in range(5)]  # calculate the derivative and get max
            index_ddmin = [min([index_mean[i+ii+1]- index_mean[i+ii]  for ii in   range(5)]) for i in range(5)]  # calculate the derivative and get max 
            index_ddmax_mean = sum(index_ddmax)/5   # calculate the mean
            index_ddmin_mean = sum(index_ddmin)/5   # calculate the mean
            
            if index_ddmin_mean > -0.001 and self.wear_area_spindle[class_nr]==0:
                # first wear area
                self.wear_percentage_base_spindle[class_nr] = len(self.wear_index_spindle[class_nr])    
                self.wear_area_spindle[class_nr] = 1
            elif index_ddmax_mean > 0 and self.wear_area_spindle[class_nr]==1:
                # second wear area
                self.wear_percentage_base_spindle[class_nr] = len(self.wear_index_spindle[class_nr])    
                self.wear_area_spindle[class_nr] = 2
            elif index_ddmax_mean > 0.001 and self.wear_area_spindle[class_nr]==2:
                # third wear area
                self.wear_percentage_base_spindle[class_nr] = len(self.wear_index_spindle[class_nr])    
                self.wear_area_spindle[class_nr] = 3

            if self.wear_area_spindle[class_nr] == 1:
                # calculate the percentage if the x axis is in the first wear area
                self.wear_percentage_spindle[class_nr] += [len(self.wear_index_spindle[class_nr])/(self.wear_percentage_base_spindle[class_nr]/self.PERCENT_AREA_1)*100]
            if self.wear_area_spindle[class_nr] == 2:
                # calculate the percentage if the x axis is in the second wear area
                self.wear_percentage_spindle[class_nr] += [len(self.wear_index_spindle[class_nr])/(self.wear_percentage_base_spindle[class_nr]/self.PERCENT_AREA_2)*100]
            if self.wear_area_spindle[class_nr] == 3:
                # calculate the percentage if the x axis is in the third wear area
                self.wear_percentage_spindle[class_nr] += [len(self.wear_index_spindle[class_nr])/(self.wear_percentage_base_spindle[class_nr]/self.PERCENT_AREA_3)*100]
        else:
            self.wear_percentage_spindle[class_nr] += ['nan']

    def update_index(self, index_matrix):
        # update the index

        # update the index for each cylce class found
        for class_nr in range(len(index_matrix)):

            # update the indices for everay cycleindex
            for i in range(int(self.last_len[class_nr]), len(index_matrix[class_nr][0]),1):

                if index_matrix[class_nr][-1][i] - index_matrix[class_nr][-1][i-1]  < -0.4 and i>=1:
                    # update the toolindex formula and recalculate the anxis indices if there is a sudden change in the current of the main Spindel
                    self.__recalculate_tool_index__(index_matrix, class_nr, i)
                else:
                    # update the tool wear index
                    self.wear_index_tool[class_nr] += [sum([self.factor_matrix_tool[class_nr,sig]*index_matrix[class_nr][sig][i] for sig in range(len(index_matrix[class_nr]))])]

                # calculate the wear percntage of the spindle
                if len(self.upper_tool[class_nr]) > 1:
                    self.wear_percentage_tool[class_nr] += [(self.wear_index_tool[class_nr][-1]-self.lower_tool[class_nr][-1])/(self.upper_tool[class_nr][-1]-self.lower_tool[class_nr][-1])*100]
                else:
                    self.wear_percentage_tool[class_nr] += ['nan']
    
            # Update the length of the indexmatrix entry for the found cycle
            self.last_len[class_nr] = len(index_matrix[class_nr][0])
        

    def get_index_tool(self):
        # get the index of the tool
        return self.wear_index_tool
    def get_threshold_tool_up(self):
        # get the threshold of the tool
        return self.upper_tool
    def get_threshold_tool_low(self):
        # get the threshold of the tool
        return self.lower_tool
    def get_current_threshold_tool(self):
        # get the current threshold of the tool
         return [upper_i[-1] for upper_i in self.upper_tool] 
    def get_current_index_tool(self):
        # get the current wear index for the tool
        return [wear_index_i[-1] for wear_index_i in self.wear_index_tool]
    def get_wear_percentage_tool(self):
        # get the wear percentage of the spindle axis
        return self.wear_percentage_tool

    def get_index_x(self):
        # get the wear index of the x axis
        return self.wear_index_x
    def get_current_index_x(self):
        # get the current wear index of the x axis
        return [wear_index_i[-1] for wear_index_i in self.wear_index_x]
    def get_wear_area_x(self):
        # get the wear area of the x axis
        return self.wear_area_x
    def get_wear_percentage_x(self):
        # get the wear percentage of the x axis
        return self.wear_percentage_x
    
    def get_index_y(self):
        # get the wear index of the y axis
        return self.wear_index_y
    def get_current_index_y(self):
        # get the current wear index of the y axis
        return [wear_index_i[-1] for wear_index_i in self.wear_index_y]
    def get_wear_area_y(self):
        # get the wear area of the y axis
        return self.wear_area_y
    def get_wear_percentage_y(self):
        # get the wear percentage of the x axis
        return self.wear_percentage_y
    
    def get_index_z(self):
        # get the wear index of the z axis
        return self.wear_index_z
    def get_current_index_z(self):
        # get the current wear index of the z axis
        return [wear_index_i[-1] for wear_index_i in self.wear_index_z]
    def get_wear_area_z(self):
        # get the wear area of the z axis
        return self.wear_area_z
    def get_wear_percentage_z(self):
        # get the wear percentage of the x axis
        return self.wear_percentage_z
    
    def get_index_spindle(self):
        # get the wear index of the spindle
        return self.wear_index_spindle
    def get_current_index_spindle(self):
        # get the current wear index of the spindel
        return [wear_index_i[-1] for wear_index_i in self.wear_index_spindle]
    def get_wear_area_spindle(self):
        # get the wear area of the spindle
        return self.wear_area_spindle
    def get_wear_percentage_spindle(self):
        # get the wear percentage of the spindle axis
        return self.wear_percentage_spindle


    def get_index_matrix_axis(self):
        # get the index matrix for all axis and the spindle
        index_matrix_axis = np.array([self.get_wear_area_x(), self.get_wear_area_y(), self.get_wear_area_z(), self.get_wear_area_spindle()])
        return index_matrix_axis

    def get_percentage_axis(self):
        # get the percentage matrix for all axis and the spindle
        percentage_matrix = np.array([self.get_wear_percentage_tool()[-1], self.get_wear_percentage_x(), self.get_wear_percentage_y(), self.get_wear_percentage_z(), self.get_wear_percentage_spindle()])
        return percentage_matrix