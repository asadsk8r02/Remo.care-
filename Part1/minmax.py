import numpy as np
import datetime
datetime = datetime.datetime


def detection(a,**kwargs):
    '''
    The Funtion takes inpu argument as an array with 4 rowns and n columns where the rowsa are HR,RRI,ACC and Time.
    
    
    '''
    #print(a[0])
    dec_threshold = kwargs.get('dec_threshold', 10)
    inc_threshold = kwargs.get('inc_threshold', 10)
    valid = [] 
    dic_return ={}
    idx = []
    outlier_idx = [] 
    non_liniear =[]
    for i in range(0,len(a[0])):

        st = threshold(a[0][i],a[1][i],**kwargs)
        #print(st)
        if st == 'outlier-range':
            outlier_idx.append([a[3,i],a[0,i],'outlier-range'])
        if st == 'valid' or st == 'pause valid':
            idx.append(i)
        if st == 'valid':
            valid.append(i)
    #print(valid)
    for i in range(1,len(valid)):
        #print(a[0][valid[i]]-a[0][valid[i-1]])
        change = a[0][valid[i]] - a[0][valid[i-1]]
        if change >inc_threshold:
            non_liniear.append([valid[i],'non_linear increase',change,a[0,valid[i-1]],a[0,valid[i]],{'from':a[3,valid[i-1]],'to':a[3,valid[i]]}])
        if change <-(dec_threshold):
            non_liniear.append([valid[i],'non_linear decrease',abs(change),a[0,valid[i-1]],a[0,valid[i]],{'from':a[3,valid[i-1]],'to':a[3,valid[i]]}])
    non_liniear = non_linearity(a,non_liniear,idx)
    dic_return['min_max'] = {'min': min(a[0,valid]),'time_min':(a[3,np.where(a[0]==min(a[0,valid]))]).tolist(),'min_with_pause':min(a[0,idx]),'time_pause':(a[3,np.where(a[0]==min(a[0,idx]))]).tolist(),'max':max(a[0,valid]),'time_max':(a[3,np.where(a[0]==max(a[0,valid]))]).tolist()}
    
    dic_return['non_linear_points'] = [{'idx':i[0],'type':i[1],'change':i[2],'from':str(i[3])+' to '+str(i[4]),'time':i[5]}    for i in non_liniear]
    dic_return['outlier_range_points'] = outlier_idx
    dic_return['outlier_removed_min_max']= detect_outlier(a,valid,**kwargs)
    dic_return['time_start_end']= {'start':a[3,0],'end':a[3,-1]}
   
    
    
    return dic_return

def detect_outlier(a,valid,**kwargs):
    '''
    '''
    hr = a[0,valid]
    hr_valid_time = a[3,valid]
   
    idx_positive_peaks = outlier(hr,**kwargs)
    idx_negative_peaks = outlier(-1*hr,**kwargs)
    hr_idx  = [i for i, v in enumerate(hr) if i not in idx_positive_peaks if i not in idx_negative_peaks ]
    min_max= {'min': min(hr[hr_idx]),'time_min':(hr_valid_time[np.where(hr[hr_idx]==min(hr[hr_idx]))]).tolist(),'max': max(hr[hr_idx]),'time_max':(hr_valid_time[np.where(hr[hr_idx]==max(hr[hr_idx]))]).tolist()}
    #print(hr_valid_time[np.where(hr[hr_idx]==max(hr[hr_idx]))])
    return min_max
    
def outlier(hr,**kwargs):
    outlier_threshold = kwargs.get('outlier_threshold', 20)
    st =[]
    if hr[0] > hr[1] and abs(hr[0]-hr[1])> outlier_threshold:
         st.append(0)
    for i in range(1,len(hr)-1):
        #print(i)
        if hr[i-1]<hr[i] and hr[i+1]<hr[i]:
            past = abs(hr[i-1]-hr[i])
            pres  = abs(hr[i+1]-hr[i])
            #print(past,pres)
            if past >outlier_threshold and pres in range(past-5,past+5):
                #print('here')
                st.append(i)  
        
    if hr[-1] > hr[-2] and abs(hr[-1]-hr[-2])> outlier_threshold:
        st.append(len(hr)-1)

    return st
        
    
        
        

    
def non_linearity(a,non_linear_idx,idx):
    delete =[]
    for i in range(0,len(non_linear_idx)):
#         ind = idx.index(non_linear_idx[i][0])
#         print(a[0,idx[ind]-9:idx[ind]+1],ind)
        if non_linear_idx[i][1] == 'non_linear increase':
            ind = idx.index(non_linear_idx[i][0])
            #print(a[0,idx[ind]-10:idx[ind]])
            if idx[ind]>10:
                if (movement(a[2,idx[ind]-9:idx[ind]+1])) ==True or check_zero(a[0,idx[ind]-9:idx[ind]+1]) == True:
                      delete.append(i)
                else:
                    non_linear_idx[i][1] = non_linear_idx[i][1]+' no -movement detected'
            
            else:
                if (movement(a[2,:idx[ind]+1])) ==True  or check_zero(a[0,:idx[ind]+1]) == True:
                      delete.append(i)
                else:
                    non_linear_idx[i][1] = non_linear_idx[i][1]+' no -movement detected'
            
    non_linear_idx = [v for i, v in enumerate(non_linear_idx) if i not in delete]
    return non_linear_idx

def check_zero(array):
    '''
    The funtion helps to validate the case of continuous Zeros.
    
    '''

    hr = list(array)
    if hr.count(0) >=2 and hr.count(0) <9:
        ind = [i for i, element in enumerate(hr) if element!=0]
        if ind[-1]-ind[-2] >= 2 :
            return True
        else:
            return False
    elif hr.count(0) ==9:
        return True
        
    else:
        return False
    



def acc_fn(data):
    '''
    The function calculates the roll(r) pitch(p) yaw(t) in accordance with  x y z   axis of accelerometer data 
    and the value of each angle gets returned.
    
    input:
    data = axis vale corresponding to the accelerometer for each second.(the acc values should be  dictionary embedded to a list)
    pitch:A pitch moment attempts to cause a system to rotate about its Y axis, from front to back.
    roll:Roll occurs when a force attempts to cause a system to rotate about its X axis.
    yaw:Yaw occurs when a force attempts to cause a system to rotate about its Z axis.
  
    RETURNS:
    
    A LIST
    The corresponding angle of xyz axis of acclerometer i.e pitch roll and yaw.
 
    '''
    #print(data)
    angle =[]
    for i in data:
        x,y,z= i.values()
        p = round(np.arctan(x/np.sqrt(z**2+y**2))  *( 180/np.pi),2)
        r = round(np.arctan(y/np.sqrt(z**2+x**2))  *( 180/np.pi),2)
        if z== 0:
            z=z+1
        t = round(np.arctan(np.sqrt(y**2+x**2)/z)  *( 180/np.pi),2)
    angle.append([p,r,t])
    return angle

def movement(array,**kwargs):
    '''
  
 
  Past 15 acceleration values  are taken and evaluated to detect the movement of the patient.
  The funtion calls acc_fn to get the corresponding angle for the respective acceleration.
  
  Input:
  Array:past 15 second  values of acceleration. 
  
  
  kwargs:
  mov_threshold:Set the threshold of the movement detection.
  Default:5(when ever ther is a change in angle of 5 the funtion return true with respect x y and x axis.)
  
  
  Returns:
  True :If movement in past 10 second.
  Falus:If no movement detected
  '''
    mov_threshold = kwargs.get('mov_threshold', 5)
    mov =[]
    for i in range(1,len(array)):
        lis = []
        val=0
        lis.append(acc_fn(array[i-1])[-1])
        lis.extend(acc_fn(array[i]))
        for l in range(1,len(lis)):
            if abs(abs(lis[l][0])-abs(lis[l-1][0])) >=mov_threshold or abs(abs(lis[l][1])-abs(lis[l-1][1]))>=mov_threshold or abs(abs(lis[l][2])-abs(lis[l-1][2])) >=mov_threshold:
                val =1 
            else:
                pass 
        mov.append(val)
    return  True if sum(mov[-8:]) >1 else False 















def threshold(bpm,rri,**kwargs):
    '''
    The funtion check if the HR values fall inside the valid range and for  pause.
    The default threshold rnage  level of the bpm is set from 40 to 360 and 0 are checked seperatly.
    
    input:
    
    bpm:Hr value to be checed
    rri:corresponding rri values for hr 
    
    **kwargs:
    
    lower_bpm:The threshold set for  the minimum level of bpm(default 40)
    higher_bpm:The threshold set for  the maximum level of bpm(default 360)
    
    Return:
    String
    Returns a pause valid if bpm and rri are 0 else gives pause invalid when HR is 0.
    Returns a outleir if the both conditions above dont satisfy else return valid in other cases.

    '''
    lower_bpm = kwargs.get('lower_bpm', 40)
    higher_bpm = kwargs.get('higher_bpm', 360)
    #print(rri,bpm)
    rri_stat = sum(rri)
    if  bpm == 0:
        if rri_stat == 0:
            return 'pause valid'
        else:
            return 'pause invalid'
    elif  (bpm <0) or  (bpm <=lower_bpm) or (bpm>=higher_bpm):
        return 'outlier-range' 
    else:
         return 'valid'  
        
