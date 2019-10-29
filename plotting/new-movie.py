#!/usr/bin/python3

import sys, re
import numpy as np
import matplotlib.pyplot as plt
import re
import martiniani

def latex_float(x):
    exp = int(np.log10(x*1.0))
    if abs(exp) > 2:
        x /= 10.0**exp
        if ('%.1g' % x) == '1':
            return r'10^{%.0f}' % (exp)
        return r'%.1g\times10^{%.0f}' % (x, exp)
    else:
        return '%g' % x

allcolors = list(reversed(['tab:blue', 'tab:orange', 'tab:green', 'tab:red', 'tab:purple',
                           'tab:brown', 'tab:pink', 'tab:gray', 'tab:olive', 'tab:cyan',
                           'xkcd:lightblue', 'xkcd:puke', 'xkcd:puce', 'xkcd:turquoise']))

T = martiniani.T
CV = martiniani.CV
j_lower_peak = 0
for j in range(len(T)):
    if T[j] < 0.2:
        j_lower_peak = j

my_energy = {}
my_de = {}
my_histogram = {}
my_entropy = {}
my_time = {}
my_color = {}
max_iter = 0
Smin = None
my_minT = {}
my_too_lo = {}
my_too_hi = {}
minT = None

my_cv_error = {}
cv_iters = []

def lookup_entry(entry, yaml_data):
    x = re.search('{}: (\S+)'.format(entry), yaml_data)
    if x:
        return float(x.group(1))

def fix_fname(fname):
    if fname[-5:] == '.yaml':
        return fname[:-5]
    return fname

# will be None if a float i.e. the user input a min temperature.
last_fname = re.search('[a-zA-Z]', sys.argv[-1])

if not last_fname:
    fnames = [fix_fname(f) for f in sys.argv[1:-1]]
else:
    fnames = [fix_fname(f) for f in sys.argv[1:]]


for fname in fnames:
    print(fname)
    if len(sys.argv) > 1 and not last_fname: # the user has input a min temp.
        minT = float(sys.argv[-1])
        print('minT =', minT)
    else:
        for i in range(len(fname)-5):
            if fname[i:i+len('minT')] == 'minT':
                minT = float(fname[i+len('minT'):].split('-')[0])
                print('minT =', minT)
    with open(fname+'.yaml') as f:
        yaml = f.read()
        my_too_hi[fname] = lookup_entry('too_hi', yaml)
        my_too_lo[fname] = lookup_entry('too_lo', yaml)
        my_minT[fname] = lookup_entry('min_T', yaml)
    my_histogram[fname] = np.loadtxt(fname+'.histogram')
    my_energy[fname] = np.loadtxt(fname+'.energy')
    my_de[fname] = my_energy[fname][1] - my_energy[fname][0]
    my_entropy[fname] = np.loadtxt(fname+'.entropy')
    my_cv_error[fname] = []
    if minT is None and my_minT[fname] is not None:
        minT = my_minT[fname]
    my_time[fname] = np.loadtxt(fname+'.time')
    my_color[fname] = allcolors.pop()
    if len(my_time[fname]) > max_iter:
        max_iter = len(my_time[fname])
    if Smin is None:
        Ebest = my_energy[fname];
        Sbest = my_entropy[fname][-1,:]
        Smin = Sbest[Sbest!=0].min() - Sbest.max()

EmaxS = Ebest[np.argmax(Sbest)]
EminT = Ebest[np.argmax(Sbest*minT - Ebest)]
ind_minT = np.argwhere(Ebest == EminT)[0][0]
ind_maxS = np.argwhere(Ebest == EmaxS)[0][0]
print('energies:', Ebest[ind_minT], 'at temperature', minT, 'and max entropy', Ebest[ind_maxS])
Sbest_interesting = Sbest[np.argwhere(Ebest == EminT)[0][0]:np.argwhere(Ebest == EmaxS)[0][0]+1]
Ebest_interesting = Ebest[np.argwhere(Ebest == EminT)[0][0]:np.argwhere(Ebest == EmaxS)[0][0]+1]

plt.ion()

def heat_capacity(T, E, S):
    C = np.zeros_like(T)
    for i in range(len(T)):
        boltz_arg = S - E/T[i]
        P = np.exp(boltz_arg - boltz_arg.max())
        P = P/P.sum()
        U = (E*P).sum()
        C[i] = ((E-U)**2*P).sum()/T[i]**2
    return C

# Tbest_interesting = convex_hull_T(Ebest_interesting, Sbest_interesting)
# plt.figure('temperature-comparison')
# for fname in my_energy.keys():
#     if my_energy[fname][0] <= EminT:
#         errors = np.zeros(len(my_time[fname]))
#         ind_minT = np.argwhere(my_energy[fname] == EminT)[0][0]
#         ind_maxS = np.argwhere(my_energy[fname] == EmaxS)[0][0]
#         E_interesting = my_energy[fname][ind_minT:ind_maxS+1]
#         for i in range(len(my_time[fname])):
#             S_interesting = my_entropy[fname][i,ind_minT:ind_maxS+1]
#             T_interesting = convex_hull_T(E_interesting, S_interesting)
#             e = (T_interesting - Tbest_interesting)/Tbest_interesting
#             errors[i] = np.sqrt((e**2).mean())
#         plt.loglog(my_time[fname], errors, color=my_color[fname], label=fname)
# plt.legend(loc='best')
# plt.xlabel('$t$')
# plt.ylabel(r'rms relative error in $T$')

def indwhere(array, value):
    best = 0
    for i in range(len(array)):
        if abs(array[i]-value) < abs(array[best]-value):
            best = i
    return best

def Sbest_function(e):
    return np.interp(e, Ebest_interesting, Sbest_interesting)

plt.figure('comparison')
for fname in fnames:
    if my_energy[fname][0] <= EminT:
        errors = np.zeros(len(my_time[fname]))
        ind_minT = indwhere(my_energy[fname], EminT)
        ind_maxS = indwhere(my_energy[fname], EmaxS)
        for i in range(len(my_time[fname])):
            S_interesting = my_entropy[fname][i,ind_minT:ind_maxS+1]
            E_interesting = my_energy[fname][ind_minT:ind_maxS+1]
            e = np.zeros_like(S_interesting)
            for j in range(len(e)):
                e[j] = S_interesting[j] - Sbest_function(E_interesting[j])
            e -= e.mean() # WARNING, this causes problems if there are impossible states in the interesting energy range.
            errors[i] = np.sqrt((e**2).mean()) # WARNING, this causes problems if there are impossible states in the interesting energy range.
        plt.loglog(my_time[fname], errors, color=my_color[fname], label=fname)
    else:
        print("We cannot compare with", fname, "because it doesn't have all the energies")
        print("  ", EminT,"<", my_energy[fname][0])
plt.legend(loc='best')
plt.xlabel('$t$')
plt.ylabel(r'rms entropy error')

all_figures = set()
keep_going = True
while keep_going:
    keep_going = False
    for i in range(max_iter):
        for fig in all_figures:
            fig.clf()
        all_figures.add(plt.figure('Heat capacity'))
        plt.axvline(minT, linestyle=':', color='#ffaaaa')
        all_figures.add(plt.figure('Histogram'))
        plt.axvline(EminT, linestyle=':', color='#ffaaaa')

        all_figures.add(plt.figure('Normed entropy'))
        for E0 in np.linspace(2*Ebest.min() - Ebest.max(), Ebest.max(), 20):
            plt.plot(Ebest, Smin + (Ebest - E0)/minT, ':', color='#ddaa00')
        plt.axvline(EminT, linestyle=':', color='#ffaaaa')
        plt.plot(Ebest, Sbest - Sbest.max(), ':', color='#aaaaaa')
        # all_figures.add(plt.figure('Temperature'))
        # plt.semilogy(Ebest_interesting,
        #              convex_hull_T(Ebest_interesting, Sbest_interesting), ':', color='#aaaaaa')
        for fname in fnames:
            if i < len(my_time[fname]):
                t = my_time[fname][i]
                j = i
            else:
                j = -1
            #if fname == fnames[0]:
            #    print('frame', i, 'with', t, 'iterations')

            # all_figures.add(plt.figure('Entropy'))
            # if j > 0:
            #     plt.plot(my_energy[fname], my_entropy[fname][j-1,:], my_color[fname],
            #              alpha=0.2)
            # if j == -1:
            #     plt.plot(my_energy[fname], my_entropy[fname][j,:], my_color[fname],
            #              label=fname+' '+latex_float(len(my_entropy[fname])),
            #              alpha=0.2)
            # else:
            #     plt.plot(my_energy[fname], my_entropy[fname][j,:], my_color[fname],
            #              label=fname)
            # plt.title('$t=%s/%s$' % (latex_float(t),
            #                          latex_float(my_time[fname][-1])))
            # plt.ylabel('$S$')
            # plt.legend(loc='best')

            all_figures.add(plt.figure('Normed entropy'))
            if my_too_lo[fname]:
                plt.axvline(my_too_lo[fname], linestyle=':', color=my_color[fname])
            if j > 0:
                plt.plot(my_energy[fname],
                         my_entropy[fname][i-1,:]-my_entropy[fname][j-1,:].max(),
                         my_color[fname],
                         alpha=0.2)
            if j == -1:
                plt.plot(my_energy[fname],
                         my_entropy[fname][j,:]-my_entropy[fname][j,:].max(),
                         my_color[fname],
                         label=fname+' '+latex_float(len(my_entropy[fname])),
                         alpha=0.2)
            else:
                plt.plot(my_energy[fname],
                         my_entropy[fname][j,:]-my_entropy[fname][j,:].max(),
                         my_color[fname],
                         label=fname)
                # plt.plot(my_energy[fname],
                #          convex_hull(my_entropy[fname][j,:])-my_entropy[fname][j,:].max(),
                #          ':',
                #          color=my_color[fname],
                #          label=fname)
            plt.title('$t=%s/%s$' % (latex_float(t),
                                     latex_float(my_time[fname][-1])))
            plt.ylabel('$S$')
            plt.legend(loc='best')
            plt.ylim(Smin, 0)

            # all_figures.add(plt.figure('Temperature'))
            # T = convex_hull_T(my_energy[fname], my_entropy[fname][j,:])
            # if len(T[T>0]) > 1:
            #     if j == -1:
            #         plt.semilogy(my_energy[fname][T>0],
            #                      T[T>0],
            #                      color=my_color[fname],
            #                      label=fname+' '+latex_float(len(my_entropy[fname])),
            #                      alpha=0.5)
            #     else:
            #         plt.semilogy(my_energy[fname][T>0],
            #                      T[T>0],
            #                      color=my_color[fname],
            #                      label=fname)
            # plt.title('$t=%s/%s$' % (latex_float(t),
            #                          latex_float(my_time[fname][-1])))
            # plt.ylabel('$T$')
            # plt.legend(loc='best')
            # # plt.ylim(Tbest_interesting.min(), Tbest_interesting.max())

            all_figures.add(plt.figure('Histogram'))
            plt.title('$t=%s/%s$' % (latex_float(t),
                                     latex_float(my_time[fname][-1])))
            if my_too_lo[fname]:
                plt.axvline(my_too_lo[fname], linestyle=':', color=my_color[fname])
            if my_too_hi[fname]:
                plt.axvline(my_too_hi[fname], linestyle=':', color=my_color[fname])
            plt.ylabel('histogram')
            if j > 0:
                plt.plot(my_energy[fname], my_histogram[fname][j-1,:]/my_de[fname], my_color[fname],
                         alpha=0.2)
            if j == -1:
                plt.plot(my_energy[fname], my_histogram[fname][j,:]/my_de[fname], my_color[fname],
                         label=fname+' '+latex_float(len(my_entropy[fname])),
                         alpha=0.2)
            else:
                plt.plot(my_energy[fname], my_histogram[fname][j,:]/my_de[fname], my_color[fname],
                         label=fname)
            plt.legend(loc='best')

            all_figures.add(plt.figure('Heat capacity'))
            plt.title('$t=%s/%s$' % (latex_float(t),
                                     latex_float(my_time[fname][-1])))
            plt.ylabel('heat capacity')
            plt.xlabel('temperature')
            mycv = heat_capacity(T, my_energy[fname], my_entropy[fname][j,:])
            plt.plot(T, mycv, my_color[fname], label=fname)
            plt.legend(loc='best')

            err = 0
            norm = 0
            for j in range(1,j_lower_peak):
                err += (T[j+1]-T[j-1])*abs(CV[j]-mycv[j])
                norm += (T[j+1]-T[j-1])
            my_cv_error[fname].append(err/norm)

            all_figures.add(plt.figure('CV errors'))
            if len(my_time[fname]) >= len(my_cv_error[fname]):
                plt.loglog(my_time[fname][:len(my_cv_error[fname])], my_cv_error[fname],
                           my_color[fname], label=fname)
            else:
                plt.loglog(my_time[fname], my_cv_error[fname][:len(my_time[fname])],
                           my_color[fname], label=fname)
            plt.legend(loc='best')

        all_figures.add(plt.figure('Heat capacity'))
        plt.plot(T, CV, 'k:', label='Martiniani et al.')
        plt.xlabel('number of moves')
        plt.ylabel('mean error in $C_V$')
        plt.ylim(0,140)
        plt.legend(loc='best')

        plt.pause(0.1)

plt.ioff()
plt.show()