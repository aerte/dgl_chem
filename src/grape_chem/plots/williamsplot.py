# analysis tools

import os
from typing import Optional, Union
from torch import Tensor
from numpy import ndarray
import matplotlib.pyplot as plt

__all__ = [
    "williams_plot"
]

def williams_plot(prediction: Union[Tensor, ndarray], target: Union[Tensor, ndarray], n_features: int,
                  fig_size: tuple = (10,5), save_fig: bool = False, path_to_export: str = None) -> plt.axes:
    """Generates a williams plot based on the given predictions and targets. The plot is based on the formula:
    X/(X X')X', where the X matrix are the targets.
    This plot is used to expose observations
    that are far from the mean of the residuals, thus exerting a lot of influence on the parameter training.

    # TODO: Needs to be completely overhauled.

    Parameters
    -----------
    prediction: Tensor or ndarray
        A prediction array or tensor generated by some sort of model.
    target: Tensor or ndarray
        The target array or tensor corresponding to the prediction.
    n_features: int
        The number of features used in modeling.
    fig_size: tuple
        The output figure size. Default: (10,10)
    save_fig: bool
        Decides if the plot is saved, is overridden if a path is given. Default: False
    path_to_export: str
        File location to save. Default: None

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

    residual = target-prediction
    hat = (target@target@target.T@target.T)
    N = len(residual)

    fig, ax = plt.subplots(1,1,figsize=fig_size)
    ax.scatter(hat, residual, linewidth = 0.7)
    ax.axvline(3*n_features/N)
    ax.set_title('Williams plot')
    ax.set_xlabel('Hat values')
    ax.set_ylabel('Residuals')

    if path_to_export is not None:
        fig.savefig(fname=f'{path_to_export}/williams_plot.svg', format='svg')

    return ax