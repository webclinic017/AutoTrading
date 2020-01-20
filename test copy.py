import multiprocessing
import fxcmpy


#Testing fxcm object to see if it can be passed to a shared mameory using multiprocessing manager dict
#Result, As fxcm object has a thread abject in it , it cannot be serialized.


class api(multiprocessing.Process):
    def __init__(self):
        multiprocessing.Process.__init__(self)

    def init(self):
        print(self.con.is_connected())

    def run(self):
        self.con=fxcmpy.fxcmpy(access_token='a46718dbcf04edf1b8135816d96d38a7703f2d65', log_level='error', server='demo')
        self.init()




if __name__ == '__main__':
    multiprocessing.freeze_support() 
    api_ins=api()
    api_ins.start()
    api_ins.join()

    