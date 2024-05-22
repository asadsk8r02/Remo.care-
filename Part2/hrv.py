import scipy as sp
import numpy as np
import spectrum
import nolds
import neurokit2 as nk
import json 
def compute_features_hrv(rr,**kwargs):
    '''
    input :
        RR - rri intervals in ms with data type int
        kwargs : 
            short:the short rr interval range for dfa, default (4,16)
            long :the long rr interval range for dfa,default (17,64)
            
    return:
     dictionary with all features and data
    '''
    result_time = time_domain(rr)
    weltch_psd,ar_psd = frequency_domain_weltch(rr)
    pc_plot = plot_poincare(rr)
    dfa_ana = dfa(rr,**kwargs)
    return {'time_domain': result_time,'weltch_psd':weltch_psd,'ar_psd':ar_psd,'pinocare':pc_plot,'dfa':dfa_ana}

def time_domain(rr):
    return_dic ={}
  
    
    hr =[60000/i for i in rr if i !=0]
    return_dic['hist_data_hr']=  hr
    return_dic['hist_data_rr_ms'] = rr
    
    bins = np.arange( ((np.min(rr))// 7.8125)* 7.8125, np.max(rr) + 7.8125, 7.8125)
    counts,bins = np.histogram(rr, bins, density=False)
    return_dic['params'] = {'mean_rr ms':float(np.mean(rr)),'mean_hr 1/(min)':float(np.mean(hr)),'std_rr ms':float(np.std(rr)),'std_hr 1/(min)':float(np.std(hr)),'Rmssd (ms)':float(np.sqrt(np.sum(np.square(np.diff(rr)))/(len(rr)-1))),'NN50 (count)':float(np.sum(np.abs(np.diff(rr)) > 50)),'PNN50 %':float(np.sum(np.abs(np.diff(rr)) > 50)*1/(len(rr)-1)),'triangle_index':float(len(rr)/np.max(counts))}
    

    #print((return_dic['params']))
    return return_dic
def frequency_domain_weltch(rri, fs=4):

    t = np.cumsum(rri)/1000
    f_2 = sp.interpolate.interp1d(t, rri, 'cubic')
    t_interpol = np.arange(1, t[-1], 1/fs)
    rr_interpolated = f_2(t_interpol)
    #rr_interpolated = rr_interpolated - np.mean(rr_interpolated)

    # Estimate the spectral density using Welch's method

    fxx, pxx = sp.signal.welch(x=rr_interpolated,fs=fs,window='hanning')
#     name1= "FFT Spectrum (Welch's periodogram with 256s window and 50% overlap)"
#     name2 = 'AR spectrum (Order 16 with 256s overlap)'
    results = compute_vals(fxx,pxx)
    
    ar = spectrum.pyule(data=rr_interpolated, order=16, sampling=4, scale_by_freq=False)
    ar()
    
    frequencies = np.asarray(ar.frequencies())
    psd = np.asarray(ar.psd)
    powers = np.asarray(10 * np.log10(psd)*10**3)
    results1 = compute_vals(frequencies,powers)

    return results,results1
def compute_vals(fxx,pxx):
       
    '''
    Segement found frequencies in the bands 
     - Very Low Frequency (VLF): 0-0.04Hz 
     - Low Frequency (LF): 0.04-0.15Hz 
     - High Frequency (HF): 0.15-0.4Hz
    '''
    cond_vlf = (fxx >= 0) & (fxx < 0.04)
    cond_lf = (fxx >= 0.04) & (fxx < 0.15)
    cond_hf = (fxx >= 0.15) & (fxx < 0.4)
    
    # calculate power in each band by integrating the spectral density 
    vlf = sp.integrate.trapz(pxx[cond_vlf], fxx[cond_vlf])
    lf = sp.integrate.trapz(pxx[cond_lf], fxx[cond_lf])
    hf = sp.integrate.trapz(pxx[cond_hf], fxx[cond_hf])
    
    # sum these up to get total power
    total_power = vlf + lf + hf

    # find which frequency has the most power in each band
    peak_vlf = fxx[cond_vlf][np.argmax(pxx[cond_vlf])]
    peak_lf = fxx[cond_lf][np.argmax(pxx[cond_lf])]
    peak_hf = fxx[cond_hf][np.argmax(pxx[cond_hf])]

    # fraction of lf and hf
    lf_nu = 100 * lf / (lf + hf)
    hf_nu = 100 * hf / (lf + hf)
    
    results = {}
    results['params'] = {'Power_VLF (ms2)': float(vlf),'Power_LF (ms2)':float(lf),'Power_HF (ms2)':float(hf),'Power_Total (ms2)':float(total_power),'Power_VLF %':float((vlf/total_power)*100),'Power_LF %':float((lf/total_power)*100),'Power_HF %':float((hf/total_power)*100),'ratio_LF/HF':float(lf/hf),'Peak_VLF (Hz)':float(peak_vlf),'Peak_LF (Hz)':float(peak_lf),'Peak_HF (Hz)': float(peak_hf),'Fraction_LF (nu)':float(lf_nu),'Fraction_HF (nu)':float(hf_nu)}
  
    results['fxx'] = list(map(float,fxx))
    results['pxx/(s^2hz)'] =list(map(float,pxx/10**6)) 
#     results['plot'] = plot_psd(fxx,pxx,name)
    #print(type(results['fxx'][0]))
    return results
def plot_poincare(rr):
    rr_n = rr[:-1]
    rr_n1 = rr[1:]

    sd1 = np.std(np.subtract(rr_n, rr_n1) / np.sqrt(2))
    sd2 = np.std(np.add(rr_n, rr_n1) / np.sqrt(2))
    m = np.mean(rr)
    min_rr = np.min(rr)
    max_rr = np.max(rr)
    dic ={'sd1(ms)': float(sd1),'sd2(ms)':float(sd2),'rr(n)(ms)':rr_n,'rr(n+1)(ms)':rr_n1,'mean':float(m),'min_rr':float(min_rr),'max_rr':float(max_rr)}
    return dic

def dfa(rr,**kwargs):
    short = kwargs.get('short', (4,16))
    long = kwargs.get('long', (17,64))
    short = range(short[0], short[1] + 1)
    long = range(long[0], long[1] + 1)
    alpha1, dfa_short = nolds.dfa(rr, short, debug_data=True, overlap=True)
    alpha2, dfa_long = nolds.dfa(rr, long, debug_data=True, overlap=True)
    line1 = dfa_short[2][1] + dfa_short[2][0]* dfa_short[0]
    line2 = dfa_long[2][1] + dfa_long[2][0]* dfa_long[0]
    dic = {}
    dic['plot'] = {'long':{'scatter':{'x_beats':list(map(float,dfa_long[0])),'y_logF(n)':list(map(float,dfa_long[1]))},'plot_line':{'x_beats':list(map(float,dfa_long[0])),'y_logF(n)':list(map(float,line2))}},
                   'short':{'scatter':{'x_beats':list(map(float,dfa_short[0])),'y_logF(n)':list(map(float,dfa_short[1]))},'plot_line':{'x_beats':list(map(float,dfa_short[0])),'y_logF(n)':list(map(float,line1))}}}
    dic['Detrended Fluctuations alpha1']= float(alpha1)
    dic['Detrended Fluctuations alpha2']=float(alpha2)
    dic['corelation_dimention(D2)'] = float( nolds.corr_dim(rr,2))
    dic['apx_entopy'] = float(nk.entropy_approximate(rr,delay=1, dimension=2, r='default', corrected=True))
    dic['sample_entropy'] = float(nk.entropy_sample(rr))
    return dic