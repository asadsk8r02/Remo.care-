import minmax as mn
import numpy as np
import json
def cloud(request):
    try:
        data = request.get_json()
        try:
            params = data['params']
        except Exception as e:
            params = {'dec_threshold': 10,'inc_threshold': 10,'outlier_threshold':20,'lower_bpm':40,'higher_bpm':360}
            
        
        
        arr = np.asarray((json.loads(data['arr'])),dtype='object')
        result = mn.detection(arr,**params)
        return ({"result": result,'status':200})
    except Exception as e:
        print(e)
        return json.dumps({"error": 'data not recived','status':400})
    
    #functions-framework --target cloud