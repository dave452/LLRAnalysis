import matplotlib.pyplot as plt
import pandas as pd
import os.path
import numpy as np
import llranalysis.llr as llr
import llranalysis.error as error
import llranalysis.standard as standard
import llranalysis.utils as utils

plt.style.use('default')
plt.rcParams.update({'xtick.labelsize' : 18,
                     'ytick.labelsize' : 18,
                     'axes.formatter.useoffset' : False,
                     'legend.fontsize' : 20,
                     'axes.labelsize' : 30,
                     "text.usetex": True,
                     "font.family": "serif",
                     "font.serif": "Computer Modern Roman",
                     'lines.linewidth':1,
                     'figure.figsize' : (10,10),
                     'figure.autolayout': True})

def compare_dE_plot_a(boot_folders, n_repeats, blim,ulim,num_samples=200, error_type = 'standard deviation'):
    colours = ['b','g','r','c','m','y','b','g','r','c','m','y','b','g','r','c','m','y']
    j = 0
    plt.figure(figsize=(10,20))
    ax1 = plt.subplot(2,1,1)
    ax2 = plt.subplot(2,1,2)
    for bf, nr in zip(boot_folders, n_repeats):
        final_df = pd.read_csv(f'{bf}0/CSV/final.csv')
        Eks = final_df['Ek'].values
        V = final_df['V'].values[0]
        dE =  final_df['dE'].values[0]
        aks = np.zeros((nr, len(Eks)))
        for i in range(nr):
            final_df = pd.read_csv(f'{bf}{i}/CSV/final.csv')
            aks[i,:] = -final_df['a'].values
        aks_mean = aks.mean(axis = 0)
        aks_error = error.calculate_error_set(aks,num_samples,error_type)
        ax1.errorbar(Eks/(6*V),aks_mean,aks_error, fmt = colours[j] + '-', label = '$a^4 \delta_E / 6\\tilde{V}$' + f':{dE / (6*V) :.4f}')
        ax2.errorbar(Eks/(6*V),aks_mean,aks_error, fmt = colours[j] + '-', label = '$a^4 \delta_E / 6\\tilde{V}$' + f':{dE / (6*V) :.4f}')
        j += 1
    ax1.set_ylabel('$a_n$', fontsize = 30)
    ax2.set_ylabel('$a_n$', fontsize = 30)
    ax1.locator_params(axis="x", nbins=7)
    ax2.locator_params(axis="x", nbins=7)
    ax1.legend(fontsize = 20)
    ax2.set_xlim(ulim)
    ax2.set_ylim(blim)
    ax2.set_xlabel('$u_p$', fontsize = 30)
    plt.subplots_adjust(hspace=0.05)
    plt.show()

def dE_DG_critical_beta(full_folders, reduced_folders, additional_folders, num_repeats,num_samples=200, error_type = 'standard deviation', plt_a=False):
    miny =100.;maxy = 0.
    for i, rf in enumerate(additional_folders):
        c = 'orange'
        dEsq = ((pd.read_csv(rf  + '0/CSV/' + 'final.csv')['dE'].values[0]/( 6.*pd.read_csv(rf  + '0/CSV/' + 'final.csv')['V'].values[0])) ** 2.)
        DG_df = pd.DataFrame()
        for nr in range(num_repeats):
            DG_df = pd.concat([DG_df, pd.read_csv(f'{rf}/{nr}/CSV/DG.csv')])
        plt.plot(dEsq*np.ones_like(DG_df['Bc']), DG_df['Bc'], 'kx')
        DG_bc_dE = DG_df['Bc'].values.mean(); DG_bc_dE_err=error.calculate_error(DG_df['Bc'].values, num_samples, error_type = error_type)
        plt.errorbar(dEsq, DG_bc_dE ,DG_bc_dE_err, color = c, marker='o',capsize=7)
    mindEsq = dEsq
    DG_bc_dE = np.array([]); DG_bc_dE_err = np.array([])
    dEsq = np.array([])
    for i, rf in enumerate(reduced_folders):
        c = 'b'
        dEsq = np.append(dEsq,((pd.read_csv(rf  + '0/CSV/' + 'final.csv')['dE'].values[0]/(2 * 6.*pd.read_csv(rf  + '0/CSV/' + 'final.csv')['V'].values[0])) ** 2.))
        DG_df = pd.DataFrame()
        for nr in range(num_repeats):
            DG_df = pd.concat([DG_df, pd.read_csv(f'{rf}/{nr}/CSV/DG.csv')])
        DG_bc_dE = np.append(DG_bc_dE, DG_df['Bc'].values.mean()); DG_bc_dE_err = np.append(DG_bc_dE_err,error.calculate_error(DG_df['Bc'].values, num_samples, error_type))
        plt.errorbar(dEsq[-1], DG_bc_dE[-1] ,DG_bc_dE_err[-1], color= c, marker='o',capsize=5)
    DG_bc_0, DG_bc_0_err = utils.plot_extrap(dEsq,DG_bc_dE,DG_bc_dE_err, np.arange(len(dEsq)),c, mindEsq)
    DG_bc_dE = np.array([]); DG_bc_dE_err = np.array([])
    dEsq = np.array([])
    for i, rf in enumerate(full_folders):
        c = 'orange'
        dEsq = np.append(dEsq,((pd.read_csv(rf  + '0/CSV/' + 'final.csv')['dE'].values[0]/(6.*pd.read_csv(rf  + '0/CSV/' + 'final.csv')['V'].values[0])) ** 2.))
        if plt_a:
            for counter in range(num_repeats):
                micro_a = -pd.read_csv(f'{rf}{counter}/CSV/final.csv')['a'].values
                plt.plot(dEsq[-1]*np.ones_like(micro_a), micro_a, 'm.')
        DG_df = pd.DataFrame()
        for nr in range(num_repeats):
            DG_df = pd.concat([DG_df, pd.read_csv(f'{rf}/{nr}/CSV/DG.csv')])
        plt.plot(dEsq[-1]*np.ones_like(DG_df['Bc']), DG_df['Bc'], 'kx')
        if(miny > min(DG_df['Bc'])):miny =  min(DG_df['Bc'])
        if(maxy < max(DG_df['Bc'])):maxy =  max(DG_df['Bc'])
        DG_bc_dE = np.append(DG_bc_dE ,DG_df['Bc'].values.mean()); DG_bc_dE_err=np.append(DG_bc_dE_err,error.calculate_error(DG_df['Bc'].values, num_samples, error_type = error_type))
        plt.errorbar(dEsq[-1], DG_bc_dE[-1] ,DG_bc_dE_err[-1], color = c, marker= 'o',capsize=7)
    DG_bc_0, DG_bc_0_err = utils.plot_extrap(dEsq,DG_bc_dE,DG_bc_dE_err, np.arange(len(dEsq)), c, mindEsq)
    plt.ylabel('$\\beta_c$')
    plt.xlabel('$(a^4 \\delta_E / (6\\tilde{V}))^2$')
    plt.ylim([miny,maxy])
    plt.errorbar(np.NaN, np.NaN,np.NaN,marker = 'o', color = 'orange',label = 'All intervals')
    plt.errorbar(np.NaN, np.NaN,np.NaN,marker= 'o',color= 'b', label = 'Even intervals')
    plt.legend() 
    plt.show()

def dE_DG_critical_plaq(full_folders, reduced_folders, additional_folders, num_repeats,num_samples=200, error_type = 'standard deviation'):
    for i, rf in enumerate(additional_folders):
        c = 'orange'
        dEsq = ((pd.read_csv(rf  + '0/CSV/' + 'final.csv')['dE'].values[0]/( 6.*pd.read_csv(rf  + '0/CSV/' + 'final.csv')['V'].values[0])) ** 2.)
        DG_df = pd.DataFrame()
        for nr in range(num_repeats):
            DG_df = pd.concat([DG_df, pd.read_csv(f'{rf}/{nr}/CSV/DG.csv')])
        up_bc_dE = DG_df['lh'].values.mean(); up_bc_dE_err=error.calculate_error(DG_df['lh'].values, num_samples, error_type = error_type)
        plt.errorbar(dEsq, up_bc_dE ,up_bc_dE_err, color = c, marker='o',capsize=7)
    mindEsq = dEsq
    up_bc_dE = np.array([]); up_bc_dE_err = np.array([])
    dEsq = np.array([])
    for i, rf in enumerate(reduced_folders):
        c = 'b'
        dEsq = np.append(dEsq,((pd.read_csv(rf  + '0/CSV/' + 'final.csv')['dE'].values[0]/(2 * 6.*pd.read_csv(rf  + '0/CSV/' + 'final.csv')['V'].values[0])) ** 2.))
        DG_df = pd.DataFrame()
        for nr in range(num_repeats):
            DG_df = pd.concat([DG_df, pd.read_csv(f'{rf}/{nr}/CSV/DG.csv')])
        up_bc_dE = np.append(up_bc_dE, DG_df['lh'].values.mean()); up_bc_dE_err = np.append(up_bc_dE_err,error.calculate_error(DG_df['lh'].values, num_samples, error_type))
        plt.errorbar(dEsq[-1], up_bc_dE[-1] ,up_bc_dE_err[-1], color= c, marker='o',capsize=5)
    up_bc_0, up_bc_0_err = utils.plot_extrap(dEsq,up_bc_dE,up_bc_dE_err, np.arange(len(dEsq)),c, mindEsq)
    up_bc_dE = np.array([]); up_bc_dE_err = np.array([])
    dEsq = np.array([])
    for i, rf in enumerate(full_folders):
        c = 'orange'
        dEsq = np.append(dEsq,((pd.read_csv(rf  + '0/CSV/' + 'final.csv')['dE'].values[0]/(6.*pd.read_csv(rf  + '0/CSV/' + 'final.csv')['V'].values[0])) ** 2.))
        DG_df = pd.DataFrame()
        for nr in range(num_repeats):
            DG_df = pd.concat([DG_df, pd.read_csv(f'{rf}/{nr}/CSV/DG.csv')])
        up_bc_dE = np.append(up_bc_dE ,DG_df['lh'].values.mean()); up_bc_dE_err=np.append(up_bc_dE_err,error.calculate_error(DG_df['lh'].values, num_samples, error_type = error_type))
        plt.errorbar(dEsq[-1], up_bc_dE[-1] ,up_bc_dE_err[-1], color = c, marker= 'o',capsize=7)
    up_bc_0, up_bc_0_err = utils.plot_extrap(dEsq,up_bc_dE,up_bc_dE_err, np.arange(len(dEsq)), c, mindEsq)
    plt.ylabel('$\Delta \\langle u_p \\rangle_{\\beta_c}$')
    plt.xlabel('$(a^4 \\delta_E / (6\\tilde{V}))^2$')
    plt.errorbar(np.NaN, np.NaN,np.NaN,marker = 'o', color = 'orange',label = 'All intervals')
    plt.errorbar(np.NaN, np.NaN,np.NaN,marker= 'o',color= 'b', label = 'Even intervals')
    plt.legend() 
    plt.show()  

def compare_dE_plot_y(boot_folders, n_repeats, std_files, std_folder, std_key, llr_key, label,num_samples=200, error_type = 'standard deviation'):
    colours = ['b','g','r','c','m','y','b','g','r','c','m','y','b','g','r','c','m','y'] 
    std_df, hist_df = standard.CSV(std_files, std_folder)
    std_bs = std_df['Beta'].values
    std_ys = std_df[std_key].values
    std_ys_err = std_df[std_key + '_err'].values
    for i, (bf, nr) in enumerate(zip(boot_folders, n_repeats)):
        llr_comp_y = np.array([])
        llr_comp_b = np.array([])
        llr_full_y = np.array([])
        llr_full_b = np.array([])
        for j in range(nr):
            comp_df = pd.read_csv(f'{bf}{j}/CSV/comparison.csv')
            llr_comp_y = np.append(llr_comp_y, comp_df[llr_key])
            llr_comp_b = np.append(llr_comp_b, comp_df['b'])
            full_df = pd.read_csv(f'{bf}{j}/CSV/obs.csv')
            llr_full_y = np.append(llr_full_y, full_df[llr_key])
            llr_full_b = np.append(llr_full_b, full_df['b'])
        V = comp_df['V'].values[0]
        dE = pd.read_csv(f'{bf}0/CSV/final.csv')['dE'].values[0] 
        llr_comp_b.shape = [nr, len(comp_df['b'])]; llr_comp_y.shape = [nr, len(comp_df['b'])]
        llr_comp_b =llr_comp_b.mean(axis=0); 
        llr_comp_y_err = error.calculate_error_set(llr_comp_y, num_samples, error_type);
        llr_comp_y = llr_comp_y.mean(axis=0)

        llr_full_b.shape = [nr, len(full_df['b'])]; llr_full_y.shape = [nr, len(full_df['b'])]
        llr_full_b =llr_full_b.mean(axis=0); 
        llr_full_y_err = error.calculate_error_set(llr_full_y, num_samples, error_type);
        llr_full_y = llr_full_y.mean(axis=0)

        plt.plot(llr_full_b, llr_full_y, colours[i] + '-', label = 'LLR  $a^4 \delta_E/ 6\\tilde{V}$' + f': {dE / (6*V):.4f}' ) #
        plt.plot(llr_full_b, llr_full_y +llr_full_y_err, colours[i] + '--')
        plt.plot(llr_full_b,llr_full_y - llr_full_y_err, colours[i] + '--')
        plt.errorbar(llr_comp_b, llr_comp_y,llr_comp_y_err, fmt = colours[i] + 'o', capsize=10)
    plt.errorbar(std_bs, std_ys, std_ys_err, fmt ='k^', label='Importance sampling', capsize=10)
    plt.ylabel(label, fontsize = 30)
    plt.xlabel('$\\beta$', fontsize = 30)
    plt.legend()
    plt.locator_params(axis="x", nbins=7)
    plt.show()
    
def compare_dE_plot_y_difference(boot_folders, n_repeats, std_files, std_folder, std_key, llr_key, label,num_samples=200, error_type = 'standard deviation'):
    colours = ['b','g','r','c','m','y','b','g','r','c','m','y','b','g','r','c','m','y'] 
    std_df, hist_df = standard.CSV(std_files, std_folder)
    std_bs = std_df['Beta'].values
    std_ys = std_df[std_key].values
    std_ys_err = std_df[std_key + '_err'].values
    for i, (bf, nr) in enumerate(zip(boot_folders, n_repeats)):
        llr_comp_y = np.array([])
        llr_comp_b = np.array([])
        llr_full_y = np.array([])
        llr_full_b = np.array([])
        for j in range(nr):
            comp_df = pd.read_csv(f'{bf}{j}/CSV/comparison.csv')
            llr_comp_y = np.append(llr_comp_y, comp_df[llr_key])
            llr_comp_b = np.append(llr_comp_b, comp_df['b'])
            full_df = pd.read_csv(f'{bf}{j}/CSV/obs.csv')
            llr_full_y = np.append(llr_full_y, full_df[llr_key])
            llr_full_b = np.append(llr_full_b, full_df['b'])
        V = comp_df['V'].values[0]
        dE = pd.read_csv(f'{bf}0/CSV/final.csv')['dE'].values[0] 
        llr_comp_b.shape = [nr, len(comp_df['b'])]; llr_comp_y.shape = [nr, len(comp_df['b'])]
        llr_comp_b =llr_comp_b.mean(axis=0); 
        llr_comp_y_err = error.calculate_error_set(llr_comp_y, num_samples, error_type);
        llr_comp_y = llr_comp_y.mean(axis=0) - std_ys
        plt.errorbar(llr_comp_b, llr_comp_y,llr_comp_y_err, fmt = colours[i] + 'o', capsize=10, label = 'LLR  $a^4 \delta_E/ 6\\tilde{V}$' + f': {dE / (6*V):.4f}')
    plt.errorbar(std_bs, 0.*std_ys, std_ys_err, fmt ='k^', label='Importance sampling', capsize=10)
    plt.ylabel(label, fontsize = 30)
    plt.axhline(0,ls = '--', c = 'k')
    plt.xlabel('$\\beta$', fontsize = 30)
    plt.legend()
    plt.locator_params(axis="x", nbins=7)
    plt.show()
    