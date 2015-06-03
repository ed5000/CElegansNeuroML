'''

    Still under developemnt!!
    
    Subject to change without notice!!
    
'''


from neurotune import optimizers
from neurotune import evaluators
from neurotune import utils
from matplotlib import pyplot as plt
from pyelectro import analysis

import sys
import os.path
import time

import pprint

from collections import OrderedDict
pp = pprint.PrettyPrinter(indent=4)


if not os.path.isfile('c302.py'):
    print('This script should be run from dir: CElegansNeuroML/CElegans/pythonScripts/c302')
    exit()
        
sys.path.append(".")


from C302Controller import C302Controller


if __name__ == '__main__':
    
    sim_time = 1000
    analysis_start_time = 0
    dt = 0.05
    
    ref = 'PharNetTest'
    
    my_controller = C302Controller(ref, 'B', 'Pharyngeal', sim_time, dt)

    parameters = ['chem_exc_syn_gbase',
                  'chem_exc_syn_decay',
                  'chem_inh_syn_gbase',
                  'chem_inh_syn_decay',
                  'elec_syn_gbase']
                  
    parameters = ['chem_exc_syn_gbase',
                  'chem_exc_syn_decay',
                  'elec_syn_gbase']

    #above parameters will not be modified outside these bounds:
    min_constraints = [0.05, 3, 0.01]
    max_constraints = [1,    50, 1]

    analysis_var={'peak_delta':0,'baseline':0,'dvdt_threshold':0, 'peak_threshold':-31}

    M5_max_peak = 'M5[0]/v:max_peak_no'
    MCL_max_peak = 'MCL[0]/v:max_peak_no'
             
    weights = {M5_max_peak: 1,
               MCL_max_peak: 1}

    data = ref+'.dat'


    sim_var = OrderedDict()
    for i in range(len(parameters)):
        sim_var[parameters[i]] = max_constraints[i]/2 + min_constraints[i]/2
        

    if len(sys.argv) == 2 and sys.argv[1] == '-opt':
        
        target_data = {M5_max_peak:  70,
                       MCL_max_peak: 70}
     
        print("Target data:")
        pp.pprint(target_data)

        #make an evaluator, using automatic target evaluation:
        my_evaluator=evaluators.NetworkEvaluator(controller=my_controller,
                                                analysis_start_time=analysis_start_time,
                                                analysis_end_time=sim_time,
                                                parameters=parameters,
                                                analysis_var=analysis_var,
                                                weights=weights,
                                                targets=target_data)

        population_size =  10
        max_evaluations =  100
        num_selected =     6
        num_offspring =    6
        mutation_rate =    0.5
        num_elites =       1
        
        #make an optimizer
        my_optimizer=optimizers.CustomOptimizerA(max_constraints,
                                                 min_constraints,
                                                 my_evaluator,
                                                 population_size=population_size,
                                                 max_evaluations=max_evaluations,
                                                 num_selected=num_selected,
                                                 num_offspring=num_offspring,
                                                 num_elites=num_elites,
                                                 mutation_rate=mutation_rate,
                                                 seeds=None,
                                                 verbose=False)
                                                 
        start = time.time()
        #run the optimizer
        best_candidate = my_optimizer.optimize(do_plot=False, seed=12345)
        
        secs = time.time()-start
        print("----------------------------------------------------\n\n"
              +"Ran %s evaluations (pop: %s) in %f seconds (%f mins)\n"%(max_evaluations, population_size, secs, secs/60.0))
        
        for key,value in zip(parameters,best_candidate):
            sim_var[key]=value
            
            
        best_candidate_t, best_candidate_v = my_controller.run_individual(sim_var,show=False)
        
        best_candidate_analysis=analysis.NetworkAnalysis(best_candidate_v,
                                                   best_candidate_t,
                                                   analysis_var,
                                                   start_analysis=analysis_start_time,
                                                   end_analysis=sim_time)
                                                   
        best_candidate_analysis.analyse()
                                                   
        best_candidate_analysis.evaluate_fitness(target_data, weights)    
        
        print(best_candidate_v.keys())
        
        added =[]
        for wref in weights.keys():
            ref = wref.split(':')[0]
            if not ref in added:
                added.append(ref)
                best_candidate_plot = plt.plot(best_candidate_t,best_candidate_v[ref], label="%s - %i evaluations"%(ref,max_evaluations))

        plt.legend()

        plt.ylim(-80.0,80.0)
        plt.xlim(0.0,1000.0)
        plt.title("Models")
        plt.xlabel("Time (ms)")
        plt.ylabel("Membrane potential(mV)")
        
        plt.show()

        utils.plot_generation_evolution(sim_var.keys())

    else:


        sim_var = OrderedDict([('chem_exc_syn_gbase',0.4),
                  ('chem_exc_syn_decay',10),
                  ('chem_inh_syn_gbase',1),
                  ('chem_inh_syn_decay',40)])
        
        
        example_run_t, example_run_v = my_controller.run_individual(sim_var, show=True)

        print("Have run individual instance...")


        example_run_analysis=analysis.NetworkAnalysis(example_run_v,
                                                   example_run_t,
                                                   analysis_var,
                                                   start_analysis=analysis_start_time,
                                                   end_analysis=sim_time)

        analysis = example_run_analysis.analyse()
        
        pp.pprint(analysis)
        
        analysis = example_run_analysis.analyse(weights.keys())
        
        pp.pprint(analysis)



