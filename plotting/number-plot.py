#!/usr/bin/python3

import yaml, sys
import numpy as np
import matplotlib.pyplot as plt

def latex_float(x):
    exp = np.log10(x*1.0)
    if abs(exp) > 2:
        x /= 10.0**exp
        if ('%g' % x) == '1':
            return r'10^{%.0f}' % (exp)
        return r'%g\times 10^{%.0f}' % (x, exp)
    else:
        return '%g' % x

allcolors = list(reversed(['tab:blue', 'tab:orange', 'tab:green', 'tab:red', 'tab:purple',
                           'tab:brown', 'tab:pink', 'tab:gray', 'tab:olive', 'tab:cyan']))

my_histogram = {}
current_histogram = {}
my_entropy = {}
my_volume = {}
current_free_energy = {}
current_total_energy = {}
my_temperature = {}
my_time = {}
my_color = {}
max_iter = 0
my_gamma = {}
my_gamma_t = {}
Smin = None
fnames = sys.argv[1:]
for fname in fnames:
    print(fname)
    with open(fname) as f:
        yaml_data = f.read()
    data = yaml.load(yaml_data)
    my_temperature[fname] = data['T']
    current_histogram[fname] = np.array(data['bins']['histogram'])
    current_free_energy[fname] = -my_temperature[fname]*np.array(data['bins']['lnw'])
    current_free_energy[fname] = current_free_energy[fname]-current_free_energy[fname][0]
    my_volume[fname] = float(data['system']['cell']['box_diagonal']['x'])**3
    current_total_energy[fname] = np.array(data['bins']['total_energy'])
    my_color[fname] = allcolors.pop()
    my_time[fname] = np.array(data['movies']['time'])
    if len(my_time[fname]) > max_iter:
        max_iter = len(my_time[fname])
    my_entropy[fname] = np.array(data['movies']['lnw'])
    my_histogram[fname] = np.array(data['movies']['histogram'])
    my_gamma[fname] = np.array(data['movies']['gamma'], dtype=float)
    my_gamma_t[fname] = np.array(data['movies']['gamma_time'])
    if 'Sad' in data['method']:
        minT = data['method']['Sad']['min_T']
    if Smin is None:
        Sbest = my_entropy[fname][-1,:]
        Smin = Sbest[Sbest!=0].min() - Sbest.max()

Uexc_N = current_total_energy[fname]/current_histogram[fname]
Fexc_N = current_free_energy[fname]
V = my_volume[fname]
T = my_temperature[fname]
FN = np.arange(0, len(Fexc_N), 1)
Fideal = FN*T*(np.log(FN/V*1e2)- 1) #ignoring nQ for the moment
Fideal = FN*T*(np.log(FN)- 1) #ignoring V for the moment?!
#solving for u with derivative



# plt.figure('gamma')
# for fname in fnames:
#         plt.loglog(my_gamma_t[fname], my_gamma[fname], color=my_color[fname], label=fname)
# plt.legend(loc='best')
# plt.xlabel('$t$')
# plt.ylabel(r'$\gamma$')
# plt.ylim(1e-12, 1.1)


plt.figure('histograms')
for fname in fnames:
        plt.plot(current_histogram[fname],
                   color=my_color[fname], label='Temperature of 1.0')
        plt.xlabel('Number of Atoms')
        plt.ylabel('Number of Moves')
        plt.tick_params(axis='y', which='both', left='true', right='true')
plt.tight_layout()
plt.legend(loc='best')
#
# plt.figure('histogram')
# for fname in fnames:
#         plt.plot(current_histogram[fname],
#                    color=my_color[fname], label=fname)
#         plt.xlabel('Number of Atoms')
#         plt.ylabel('histogram (number of moves')
#         plt.title('Figure 2: Example of partially converged histogram')
# plt.legend(loc='best')
#
plt.figure('excess free energy')
for fname in fnames:
        plt.plot(current_free_energy[fname],
                   color=my_color[fname], label='F Excess')
        plt.plot(Fideal, '--',
                   color=my_color[fname], label='F Ideal')
        plt.plot(current_free_energy[fname] + Fideal, '--',
                   color=my_color[fname], label='Total Free Energy at T=1.1')
        plt.legend(loc='best')
        plt.ylabel('Free Energy')
        plt.xlabel('Number of Atoms')
        plt.tick_params(axis='y', which='both', left='true', right='true')
        plt.tight_layout()
#
# plt.legend(loc='best')
#
# plt.figure('excess internal energy')
# for fname in fnames:
#         plt.plot(current_total_energy[fname]/current_histogram[fname],
#                    color=my_color[fname], label=fname)
#
# plt.legend(loc='best')
#
# plt.figure('excess entropy')
# for fname in fnames:
#         S = (Uexc_N-Fexc_N)/T
#         S = S-S[0]
#         plt.plot(S,
#                    color=my_color[fname], label=fname)
#         plt.xlabel('$N$')
#         plt.ylabel('$S_{exc}$')
#         plt.tight_layout()
#
# plt.figure('excess entropy/N')
# for fname in fnames:
#         S = (Uexc_N-Fexc_N)/T
#         S = S-S[0]
#         SN = np.arange(0, len(S), 1)
#         plt.plot((np.pi/6)*SN/my_volume[fname],S/SN,
#                    color=my_color[fname], label=fname)
#         plt.ylabel('S_Excess')
#         plt.xlabel(r'$\eta$')
# plt.tight_layout()
#
#
# plt.legend(loc='best')
#
# plt.figure('excess internal energy/N')
# for fname in fnames:
#         UN = np.arange(0, len(Uexc_N), 1)
#         plt.plot((np.pi/6)*UN/my_volume[fname],Uexc_N/UN,
#                    color=my_color[fname], label=fname)
# #         plt.ylabel('Excess internal engery')
#         plt.xlabel(r'$\eta$')

for fname in fnames:
        plt.figure('Pressure')
        N = len(Fexc_N)
        p = np.zeros(N-1)
        p_redundant = np.zeros(N-1)
        p_exc = np.zeros(N-1)
        F = Fideal + Fexc_N
        for i in range(0,N-1):
                u = Fexc_N[i+1]-Fexc_N[i] # dN = 1
                p_exc[i] = (-0.5*(Fexc_N[i]+Fexc_N[i+1])+u*(i+.5))/V
                p[i] = p_exc[i] + (i+.5)*T/V # excess + ideal = total pressure
                u = F[i+1]-F[i] # dN = 1
                p_redundant[i] = (-0.5*(F[i]+F[i+1])+u*(i+.5))/V
                # print 'checking: ', i, p_redundant[i], p[i]
        UN = np.arange(0.5, N-1, 1)
        plt.ylabel('Pressure')
        plt.xlabel(r'$\eta$')

        plt.plot((np.pi/6)*UN/my_volume[fname],p,
                   color=my_color[fname], label=('Pressure at', T))
        # # plt.plot((np.pi/6)*UN/my_volume[fname],p_exc,'--',
        # #            color=my_color[fname], label=fname + ' pexc')
        # # plt.plot((np.pi/6)*UN/my_volume[fname],p_redundant,'r--',
        #            label=fname + ' p redundant')
        plt.legend(loc='best')
        # plt.hlines(.0545, 0, .4)
        plt.tick_params(axis='y', which='both', left='true', right='true')
        plt.tight_layout()


        plt.figure('Gibbs')
        Gexc_N = np.zeros(N-2)
        G = np.zeros(N-2)
        mu = np.zeros(N-2)
        p_integer = np.zeros(N-2)
        for j in range(1,N-2):
                p_integer[j] = (p[j]+p[j+1])/2
                Gexc_N[j] = Fexc_N[j] + V*p_integer[j]
                G[j] = Fideal[j] + Fexc_N[j] + V*p_integer[j]
                mu[j] = ((Fideal[j+1]+Fexc_N[j+1]) - (Fideal[j-1]+Fexc_N[j-1]))/2 # mu = dF/dN
        GN = np.arange(1.0, N-1, 1)
        found_one = False
        for i in range(len(G)-1):
            if found_one:
                break
            p1 = p_integer[i]
            g1 = G[i]/GN[i]
            p2 = p_integer[i+1]
            g2 = G[i+1]/GN[i+1]
            N1 = GN[i]
            N2 = GN[i+1]
            def line(p):
                return g1*(p-p2)/(p1-p2) + g2*(p-p1)/(p2-p1)
            for j in range(i+1, len(G)-1):
                p3 = p_integer[j]
                g3 = G[j]/GN[j]
                p4 = p_integer[j+1]
                g4 = G[j+1]/GN[j+1]
                N3 = GN[j]
                N4 = GN[j+1]
                top_pX = (g1*p2/(p1-p2))+(g2*p1/(p2-p1))-(g3*p4/(p3-p4))-(g4*p3/(p4-p3))
                bot_pX = (g1/(p1-p2))+(g2/(p2-p1))-(g3/(p3-p4))-(g4/(p4-p3))
                pX = top_pX/bot_pX
                gX = line(pX)
                if p1 < pX and p2 > pX and p3 < pX and p4 > pX and g3 < gX and g4 > gX:
                    # plt.plot([p1,p2,p3,p4], [g1,g2,g3,g4], 'r+', markersize=25)
                    # plt.plot([pX], [line(pX)], 'x', markersize=25)
                    print('phase transition pressure', pX)
                    print(line(pX), 'chemical potential')
                    Ngas = (N1*(p2-pX) + N2*(pX-p1))/(p2-p1)
                    Nliq = (N3*(p4-pX) + N4*(pX-p3))/(p4-p3)
                    print('Ngas', Ngas)
                    print('Nliq', Nliq)
                    found_one = True
                    break
        plt.ylabel('Chemical Potential')
        plt.xlabel('Pressure')
        # plt.plot(p_integer,Gexc_N/GN,
        #            color=my_color[fname], label=fname)
        plt.plot(p_integer,G/GN, '.--',
                   color=my_color[fname], label='Temperature of 1.1')
        plt.tick_params(axis='y', which='both', left='true', right='true')
        plt.legend(loc='best')

        plt.figure('Ugly way to find phase packing fraction')
        plt.plot((np.pi/6)*UN/my_volume[fname],p,
                       color=my_color[fname], label=fname)
        plt.hlines(pX, 0, .5)

        # #Find Packing Fraction for Pressure of Phase Transistion#
        # p_abs = np.zeros_like(p)
        # for i in range(len(UN-1)):
        #     p_abs[i] = np.abs(p[i]-pX)
        # print(min(p_abs), 'Number')



        plt.figure('Mu vs Pressure')
        mu_excess = np.zeros_like(p)
        for i in range(0,N-1):
            mu_excess[i] = Fexc_N[i+1]-Fexc_N[i] #dN=1
        mu_ideal = T*np.log(UN)
        mu = mu_excess + mu_ideal
        plt.plot(p, mu, '.--', color=my_color[fname], label=fname)




plt.figure('Phase Transistion')
Temp = np.array([.9, .9, 1.0, 1.0, 1.1, 1.1])
Pack = np.array([.003, .35, .02, .33, .04, .31])
plt.ylabel('Temerature')
plt.xlabel('Packing Fraction')
plt.tick_params(axis='y', which='both', left='true', right='true')
plt.plot(Pack, Temp, 'o')



# plt.show()
#
#
#
# all_mu = np.arange(2, 30, 0.01)
# # nQ = (mkT/2pi hbar^2)^1.5
# nQ = 0.001 # HOKEY
#
# beta = 1/T
# # Nmax = len(Fexc_N)
# N_N = np.arange(0, len(Fexc_N), 1)
# Fid_N = N_N*T*np.log(N_N/V/nQ) - N_N*T
# Fid_N[0] = 0
#
# plt.figure('Grand U')
# for fname in fnames:
#         Grand_Uexc = np.zeros_like(all_mu)
#         Grand_N = np.zeros_like(all_mu)
#         for i in range(len(all_mu)):
#             mu = all_mu[i]
#             # Zgrand = \sum_N e^{-\beta(Fid(N) + Fexc_N - mu N)}
#             Zgrand_exponents = -beta*(Fid_N+Fexc_N-mu*N_N)
#             offset = Zgrand_exponents.max()
#             Zgrand_exponents -= offset
#             Zgrand = np.exp(Zgrand_exponents).sum()
#             Grand_Uexc[i] = (Uexc_N*np.exp(Zgrand_exponents)).sum()/Zgrand
#             if Grand_Uexc[i] > 0:
#                 print('craziness', (Uexc_N*np.exp(Zgrand_exponents)).sum(), Zgrand)
#                 assert(False)
#             Grand_N[i] = (N_N*np.exp(Zgrand_exponents)).sum()/Zgrand
#         C_V = 3/2
#         Grand_Uideal = C_V*T*Grand_N
#         Grand_U = Grand_Uideal + Grand_Uexc
#         plt.plot(Grand_N, Grand_U,'-',
#                    color=my_color[fname], label='Total Grand Internal Energy')
#         plt.plot(Grand_N, Grand_Uexc,'--',
#                    color=my_color[fname], label=' Excess Grand Internal Energy')
#         plt.plot(Grand_N, Grand_Uideal,'--',
#                    color='red', label='Ideal Grand Internal Energy')
#         # plt.plot(current_total_energy[fname]/current_histogram[fname], ':',
#         #            color=my_color[fname], label='canonical '+fname)
#         plt.ylabel('Grand Internal Energy')
#         # plt.title('Grand Internal Energy')
#         #plt.title('mu {} {}'.format(all_mu[0], all_mu[-1]))
#         plt.xlabel('Grand Number of Atoms')
#         plt.legend(loc='best')

# plt.figure('Grand N')
# plt.plot(Grand_N, all_mu, label=fname)
#
# plt.plot((V*nQ)*np.exp(all_mu/T), all_mu, label='ideal') # FIXME
# plt.xlim(0, 37)
# plt.legend(loc='best')
# plt.ylabel(r'$\mu$')
# plt.xlabel(r'$N$')
#
# plt.figure('Grand S')
# for fname in fnames:
#         Sexc_N = (Uexc_N-Fexc_N)/T
#         Sexc_N = Sexc_N-Sexc_N[0]
#         Grand_Sexc = np.zeros_like(all_mu)
#         for i in range(len(all_mu)):
#             mu = all_mu[i]
#             # Zgrand = \sum_N e^{-\beta(Fid(N) + Fexc_N - mu N)}
#             Zgrand_exponents = -beta*(Fid_N+Fexc_N-mu*N_N)
#             offset = Zgrand_exponents.max()
#             Zgrand_exponents -= offset
#             Zgrand = np.exp(Zgrand_exponents).sum()
#             Grand_N[i] = (N_N*np.exp(Zgrand_exponents)).sum()/Zgrand
#             Grand_Sexc[i] = (Sexc_N*np.exp(Zgrand_exponents)).sum()/Zgrand
#         #FIXME we need to recompute Grand_N if we want to plot multiple fnames!!!
#         n = Grand_N/V
#         #nQ = 1
#         #Grand_Sideal = Grand_N*(5/2 + np.log(V/Grand_N*(Grand_Uideal/Grand_N)**1.5))
#         Grand_Sideal = Grand_N*(5/2 + np.log(nQ/n))
#         Grand_S = Grand_Sexc + Grand_Sideal
#         plt.plot(Grand_N, Grand_S,'-',
#                     color=my_color[fname], label=fname)
#         plt.title('Grand Entropy')
#         #plt.title('mu {} {}'.format(all_mu[0], all_mu[-1]))
#         plt.plot(Grand_N, Grand_Sideal,':',
#                     color=my_color[fname], label='ideal')
#         plt.ylabel('Grand S')
#         plt.legend(loc='best')
#         plt.tight_layout()
#
# plt.figure('Grand P')
# for fname in fnames:
#     Grand_P = (T*Grand_S + all_mu * Grand_N - Grand_U)/V
#     print('hello world', Grand_S[0], Grand_N[0], Grand_U[0], Grand_P[0])
#     plt.plot(Grand_N, Grand_P,':.',
#              color=my_color[fname], label=fname)
#     p_ideal = T*Grand_N/V
#     plt.title('Grand Pressure')
#     plt.plot(Grand_N, p_ideal,'--',
#                 color=my_color[fname], label='ideal')
#
#     # p_canonical = np.zeros(N-1)
#     # N_canonical = np.zeros(N-1)
#     # for i in range(0,N-1):
#     #     u = F[i+1]-F[i] # dN = 1
#     #     p_canonical[i] = (-F[i]+u*(i+.5))/V+(i+.5)*T/V
#     #     N_canonical[i] = i+0.5
#
#     # plt.plot(N_canonical,p_canonical,
#     #          color=my_color[fname], label='canonical'+fname)
#
#     #plt.title('mu {} {}'.format(all_mu[0], all_mu[-1]))
#     plt.legend(loc='best')
#     plt.title('Grand Pressure')
#     plt.xlabel('Grand N')
#     plt.ylabel('Grand Pressure')
#
# # plt.xlim(0, 5)
# # plt.ylim(0, 1)
#
# plt.figure('Grand G per atom vs Grand P')
# for fnamme in fnames:
#     Grand_G = all_mu*Grand_N
#     # Grand_G = (Grand_U - T*Grand_S + Grand_P*V)
#     plt.plot(Grand_P, Grand_G/Grand_N,'.:',
#                 color=my_color[fname], label=fname)
#
# plt.xlabel('Grand $p$')
# plt.ylabel('Grand $G$')
#
# plt.figure('F Grand vs N')
# for fname in fnames:
#     Grand_F = Grand_U-T*Grand_S
#     plt.plot(Grand_N, Grand_F, # - 3.48*Grand_N,
#                     color=my_color[fname], label=fname)
#     plt.xlabel('N')
#     plt.ylabel('Grand F')
#     plt.title('Grand F')
#     plt.legend(loc='best')
#     plt.tight_layout()
#
plt.show()
