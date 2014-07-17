from c302 import generate

import parameters_A as params

if __name__ == '__main__':
    
    motor_cells = ["DB1", "VD1", "DD1", "VB1"]
    
    cells_to_stimulate = ["DB1", "VB1"]
    
    #params.unphysiological_offset_current_dur.value = "1000ms"
    
    #params.set_up_cells()
    
    generate("c302_A_Locomotion", params, cells=motor_cells, cells_to_stimulate=cells_to_stimulate, duration=500, dt=0.025, vmin=-72, vmax=-48)