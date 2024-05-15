import io
import pickle
import sched
import time
import torch

from app import get_prometheus_metrics

models = {
    'cpu': 'app/models/h5models/model_transformer_collected_cpu_usage.pkl',
    'memory': 'app/models/h5models/model_autoencoder_collected_ram_usage.h5'
}

class CPU_Unpickler(pickle.Unpickler):
    def find_class(self, module, name):
        if module == 'torch.storage' and name == '_load_from_bytes':
            return lambda b: torch.load(io.BytesIO(b), map_location='cpu')
        else:
            return super().find_class(module, name)

if __name__ == '__main__':
    print(torch.zeros(1).cuda())
    print(torch.cuda.is_available())
    # model = CPU_Unpickler(open(models['cpu'], 'rb')).load()
