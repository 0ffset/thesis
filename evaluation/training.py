'''
Evaluate a training process.
'''
import os
import glob
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from .util import Util

class TrainingEvaluator:
    SPLITS = ["train", "valid"]

    '''
    Class for evaluating a training process.
    '''
    def __init__(self, data_name):
        if data_name is None:
            raise ValueError("data_name must be set.")
        self.data_name = data_name
        self.fig_dir = os.path.join(".", "evaluation", "fig", "training", data_name)
        self.data_dir = os.path.join(self.fig_dir, "data")
        csv_pattern = os.path.join(self.data_dir, "*.csv")
        self.data = dict()
        for csv_path in glob.glob(csv_pattern):
            # Parse model_id and split from csv path
            csv_basename = os.path.basename(csv_path)
            model_id, split = csv_basename.split("_summaries_")
            model_id = model_id[4:]
            split, _ = split.split("-tag-")

            # Read data from csv file
            if not self.data.get(model_id):
                self.data[model_id] = dict()
            self.data[model_id][split] = pd.read_csv(csv_path, delimiter=",")
    
    @staticmethod
    def get_smoothed(y, a=0.95):
        y_smooth = y.copy()
        for i in range(1, y.shape[-1]):
            y_smooth[i] = a * y_smooth[i-1] + (1 - a) * y[i-1]
        return y_smooth
    
    def plot_loss(self, model_id, plot_split="all", smooth=0.0, iter_per_epoch=1, ax=plt, **plot_kwargs):
        for split, df in self.data[model_id].items():
            if plot_split != "all" and split != plot_split:
                continue
            linespec = "-" if split == "train" else ":"
            loss = df["Value"]
            step = df["Step"]
            epoch = step / iter_per_epoch
            if smooth > 0.0:
                ax.plot(epoch, loss, linespec, alpha=0.2, **plot_kwargs)
                ax.plot(epoch, self.get_smoothed(loss), linespec, label=split, **plot_kwargs)
            else:
                ax.plot(epoch, loss, linespec, **plot_kwargs)
            ax.set_xlabel("epoch")

    def plot_losses(self, model_ids=None, smooth=0.0, iter_per_epoch=1, save_path=None, show=True,
                    ylim=None, plot_split="all", **fig_kwargs):
        if model_ids is None:
            model_ids = self.data.keys()
        if not fig_kwargs.get("figsize"):
            fig_kwargs["figsize"] = (4, 3)
        sns.set(palette=Util.PLOT_PALETTE)
        _, ax = plt.subplots(1, 1, **fig_kwargs)
        for model_id, color in zip(self.data, sns.color_palette()):
            if model_id not in model_ids: # do this to make sure each model gets a unique color
                continue
            self.plot_loss(model_id, smooth=smooth, iter_per_epoch=iter_per_epoch,
                                     plot_split=plot_split, ax=ax, color=color)
            plt.legend(loc="lower left")
        if ylim:
            plt.ylim(ylim)
        return Util.plot_postprocess(save_path, show)