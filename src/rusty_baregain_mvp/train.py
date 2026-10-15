from .data import load_modeling_data
from .model import evaluate_temporal, save_estimator, train_estimator
def main():
    frame=load_modeling_data(); metrics=evaluate_temporal(frame); save_estimator(train_estimator(frame), len(frame), metrics); print(metrics)
if __name__ == "__main__": main()
