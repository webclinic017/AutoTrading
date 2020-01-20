import multiprocessing
import fxcmpy


#Testing fxcm object to see if it can be passed to a shared mameory using multiprocessing manager dict
#Result, As fxcm object has a thread abject in it , it cannot be serialized.


class api:
    def __init__(self, shared_memory_dict):
        self.shared_memory_dict=shared_memory_dict
        self.shared_memory_dict['con']=fxcmpy.fxcmpy(access_token='a46718dbcf04edf1b8135816d96d38a7703f2d65', log_level='error', server='demo')



class con_check:
    def __init__(self, shared_memory_dict):
        self.shared_memory_dict=shared_memory_dict
        print(self.shared_memory_dict['con'].is_connected())



class controller:
    def __init__(self):
        self.manager=multiprocessing.Manager()
        self.shared_memory_dict=self.manager.dict()
        self.shared_memory_dict['con']=None
        self.api=api(self.shared_memory_dict)
        self.con_check=con_check(self.shared_memory_dict)



if __name__ == '__main__':
    multiprocessing.freeze_support() 
    controller=controller()
    