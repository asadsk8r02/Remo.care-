import hrv 
import numpy as np
import json
def hrv_api(request):
    try:
        data = request.get_json()
#         print(type(data))
        try:
            params = data['params']
        except Exception as e:
            params = {'short': (4,16),'long':(17,64)}
            
        
        
        arr = json.loads(data['arr'])

        result = hrv.compute_features_hrv(arr,**params)
        return json.dumps({"result": result,'status':200})
    except Exception as e:
        print(e)
        return json.dumps({"error": str(e),'status':400})
    
    #functions-framework --target hrv_api