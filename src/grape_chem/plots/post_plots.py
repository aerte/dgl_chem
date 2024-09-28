# analysis tools

import os
from typing import Optional, Union
from torch import Tensor
from numpy import ndarray
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from grape_chem.utils.data import DataSet
import mlflow


__all__ = [
    'loss_plot',
    'parity_plot',
    'parity_plot_mlflow',
    'residual_plot',
    'residual_density_plot'
]


def loss_plot(losses, model_names, early_stop_epoch: int = None, fig_size: tuple = (10,5),
                              save_fig: bool = False, path_to_export: str = None) -> sns.lineplot:
    """Creates a line plot of different losses on the same scale.

    Parameters
    ----------
    losses: list
        A list containing the losses.
    model_names: list
        List of the dataset names or loss type.
    fig_size: tuple
        The output figure size. Default: (10,10)
    save_fig: bool
        Decides if the plot is saved, is overridden if a path is given. Default: False
    path_to_export: str
        File location to save. Default: None

    Returns
    -------
    sns.lineplot

    """

    if save_fig and (path_to_export is None):

        path_to_export = os.getcwd() + '/analysis_results'

        if not os.path.exists(path_to_export):
            os.mkdir(path_to_export)

    loss_dic = dict()
    for idx, name in enumerate(model_names):
        loss_dic[name] = losses[idx]

    df = pd.DataFrame(loss_dic)

    fig, ax = plt.subplots(figsize=fig_size)
    sns.lineplot(data=df)
    ax.set_xlabel('Epochs')
    ax.set_ylabel('Loss')
    if early_stop_epoch is not None:
        plt.axvline(x=early_stop_epoch, linestyle='--', color='r', label='Early Stop')
        plt.legend(loc='best')

    if path_to_export is not None:
        fig.savefig(fname=f'{path_to_export}/loss_plot.svg', format='svg')

    return

def parity_plot(prediction: Union[Tensor, ndarray], target:  Union[Tensor, ndarray], mol_weights: ndarray = None,
                fig_size: tuple = (10,5), save_fig: bool = False, path_to_export: str = None,
                rescale_data: DataSet = None) -> plt.axes:
    """Generates a parity plot based on the given predictions and targets.

    Parameters
    -----------
    prediction: Tensor or ndarray
        A prediction array or tensor generated by some sort of model.
    target: Tensor or ndarray
        The target array or tensor corresponding to the prediction.
    mol_weights: ndarray
        Optional, will be used to color code the residuals based on their molecular weights given.
    fig_size: tuple
        The output figure size. Default: (10,10)
    save_fig: bool
        Decides if the plot is saved, is overridden if a path is given. Default: False
    path_to_export: str
        File location to save. Default: None
    rescale_data: DataSet
        Optional, will be used to rescale the predictions and targets if provided.

    Returns
    -------
    plt.axes

    """

    assert len(prediction) == len(target), 'Predictions and targets are not the same size.'

    if save_fig and (path_to_export is None):

        path_to_export = os.getcwd() + '/analysis_results'

        if not os.path.exists(path_to_export):
            os.mkdir(path_to_export)

    if isinstance(prediction, Tensor):
        prediction = prediction.cpu().detach().numpy()
    if isinstance(target, Tensor):
        target = target.cpu().detach().numpy()

    if rescale_data is not None:
        prediction = rescale_data.rescale_data(prediction)
        target = rescale_data.rescale_data(target)

    min_val = min(np.min(prediction), np.min(target))
    max_val = max(np.max(prediction), np.max(target))


    fig, ax = plt.subplots(1,1,figsize=fig_size)
    if mol_weights is not None:
        p = ax.scatter(target, prediction, linewidth = 0.7, c=mol_weights, cmap='plasma')
        fig.colorbar(p, ax=ax, orientation='vertical', label='Molar Weight')
    else:
        ax.scatter(target, prediction, linewidth=0.7)
    ax.axline((0,0), slope=1, color='black')
    ax.set_title('Parity plot')
    ax.set_xlabel('Ground truth')
    ax.set_ylabel('Prediction')
    plt.xlim(min_val,max_val)
    plt.ylim(min_val,max_val)
    ax.set_aspect('equal', adjustable='box')


    if path_to_export is not None:
        fig.savefig(fname=f'{path_to_export}/parity_plot.svg', format='svg')
    
    if mlflow.active_run():
        mlflow.log_artifact(f'{path_to_export}/parity_plot.svg')

    return ax

def parity_plot_mlflow(plot_name, true_vals, predicted_vals, path):
    plt.figure(figsize=(8, 8))
    plt.scatter(true_vals, predicted_vals, alpha=0.5)
    plt.plot([min(true_vals), max(true_vals)], [min(true_vals), max(true_vals)], 'r--') 
    plt.xlabel("True Values")
    plt.ylabel("Predicted Values")
    plt.title("Parity Plot")
    plt.grid(True)
    
    # CHANGE THIS TO SAVE_PATH FROM CONFIG
    plt_path = os.path.join(path, f"{plot_name}.png")
    plt.savefig(plt_path)
    print(f"Parity plot saved as {plt_path}")
    return plt_path


def residual_plot(prediction: Union[Tensor, ndarray], target: Union[Tensor, ndarray], fig_size: tuple = (10,5),
                    save_fig: bool = False, path_to_export: str = None, rescale_data: DataSet = None) -> plt.axes:
    """Generates a parity plot based on the given predictions and targets.

    Parameters
    -----------
    prediction: Tensor or ndarray
        A prediction array or tensor generated by some sort of model.
    target: Tensor or ndarray
        The target array or tensor corresponding to the prediction.
    fig_size: tuple
        The output figure size. Default: (10,10)
    save_fig: bool
        Decides if the plot is saved, is overridden if a path is given. Default: False
    path_to_export: str
        File location to save. Default: None
    rescale_data: DataSet
        Optional, will be used to rescale the predictions and targets if provided.

    Returns
    -------
    plt.axes

    """

    assert len(prediction) == len(target), 'Predictions and targets are not the same size.'

    if save_fig and (path_to_export is None):

        path_to_export = os.getcwd() + '/analysis_results'

        if not os.path.exists(path_to_export):
            os.mkdir(path_to_export)

    if isinstance(prediction, Tensor):
        prediction = prediction.cpu().detach().numpy()
    if isinstance(target, Tensor):
        target = target.cpu().detach().numpy()

    if rescale_data is not None:
        prediction = rescale_data.rescale_data(prediction)
        target = rescale_data.rescale_data(target)

    residual = prediction-target

    fig, ax = plt.subplots(1,1,figsize=fig_size)
    ax.scatter(target, residual, linewidth = 0.7)
    ax.axline((0,0), slope=0, color='black')
    ax.set_title('Residual plot')
    ax.set_xlabel('Ground truth')
    ax.set_ylabel('Residual')

    if path_to_export is not None:
        fig.savefig(fname=f'{path_to_export}/residual_plot.svg', format='svg')

    return ax


# TODO: make this a general function that can take 1-3 inputs
def residual_density_plot(train_pred:Union[Tensor, ndarray], val_pred: Union[Tensor, ndarray],
                  test_pred: Union[Tensor, ndarray], train_target: Union[Tensor, ndarray],
                  val_target: Union[Tensor, ndarray], test_target: Union[Tensor, ndarray], fig_size: tuple = (20,6),
                    save_fig: bool = False, path_to_export: str = None, rescale_data: DataSet = None) -> plt.axes:
    """Generates a parity plot based on the given predictions and targets.

    Parameters
    -----------
    train_pred: Tensor or ndarray
        The training set predictions.
    val_pred: Tensor or ndarray
        The validation set predictions.
    test_pred: Tensor or ndarray
        The test set predictions.
    train_target: Tensor or ndarray
        The training set targets.
    val_target: Tensor or ndarray
        The validation set targets.
    test_target: Tensor or ndarray
        The test set targets.
    fig_size: tuple
        The output figure size. Default: (10,10)
    save_fig: bool
        Decides if the plot is saved, is overridden if a path is given. Default: False
    path_to_export: str
        File location to save. Default: None
    rescale_data: DataSet
        Optional, will be used to rescale the predictions and targets if provided.

    Returns
    -------
    plt.axes

    """

    all_ = [train_pred, val_pred, test_pred, train_target, val_target, test_target]


    assert len(train_target) == len(train_pred), 'Predictions and targets are not the same size.'

    if save_fig and (path_to_export is None):

        path_to_export = os.getcwd() + '/analysis_results'

        if not os.path.exists(path_to_export):
            os.mkdir(path_to_export)

    for i in range(len(all_)):
        if isinstance(all_[i], Tensor):
            all_[i] = all_[i].cpu().detach().numpy()
        if rescale_data is not None:
            all_[i] = rescale_data.rescale_data(all_[i])

    train_pred, val_pred, test_pred, train_target, val_target, test_target = all_
    residual_train = train_pred-train_target
    residual_val = val_pred-val_target
    residual_test = test_pred-test_target

    from matplotlib.pyplot import rcParams
    rcParams['figure.figsize'] = fig_size

    lim = max(np.abs(residual_train).max(), np.abs(residual_val).max(), np.abs(residual_test).max())
    lim += 0.5*lim

    sns.histplot(data=residual_train, bins=70,kde=True, color='blue', edgecolor="black", label='train')
    sns.histplot(data=residual_val,bins=70, kde=True, color='green', edgecolor="black", label='val')
    sns.histplot(data=residual_test, bins=70, kde=True, color='red', edgecolor="black", label='test')
    # green
    plt.xlabel('mpC', fontsize=16, fontweight='bold')
    plt.ylabel('Count', fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.xlim((-lim,lim))
    sns.despine(top=False, right=False)
    plt.xticks(fontsize=16, fontweight='bold')
    plt.yticks(fontsize=16, fontweight='bold')
    plt.legend()
    plt.show()

    if path_to_export is not None:
        plt.savefig(fname=f'{path_to_export}/residual_plot.svg', format='svg')

