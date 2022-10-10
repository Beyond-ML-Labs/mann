import torch


class MultiConv3D(torch.nn.Module):
    """
    Multitask 3D Convolutional layer initialized with weights rather than with hyperparameters
    """

    def __init__(
        self,
        kernel,
        bias,
        padding='same',
        strides=1
    ):
        """
        Parameters
        ----------
        kernel : torch.Tensor or Tensor-like
            The kernel tensor to use
        bias : torch.Tensor or Tensor-like
            The bias tensor to use
        padding : str or int (default 'same')
            The padding to use
        strides : int or tuple (default 1)
            The strides to use
        """

        self.w = torch.nn.Parameter(
            torch.Tensor(kernel)
        )
        self.b = torch.nn.Parameter(
            torch.Tensor(bias)
        )

        self.padding = padding
        self.strides = strides

    def forward(
        self,
        inputs
    ):
        """
        Call the layer on input data

        Parameters
        ----------
        inputs : torch.Tensor
            Inputs to call the layer's logic on

        Returns
        -------
        results : torch.Tensor
            The results of the layer's logic
        """

        outputs = []
        for i in range(len(inputs)):
            outputs.append(
                torch.nn.functional.conv3d(
                    inputs[i],
                    self.w[i],
                    self.b[i],
                    stride=self.strides,
                    padding=self.padding
                )
            )
        return outputs