import torch


class SparseConv2D(torch.nn.Module):
    """
    Sparse implementation of a 2D Convolutional layer, expected to be converted from a
    trained, pruned layer
    """

    def __init__(
        self,
        kernel,
        bias,
        padding='same',
        strides=1,
        device=None
    ):
        """
        Parameters
        ----------
        kernel : torch.Tensor or Tensor-like
            The kernel to use
        bias : torch.Tensor or Tensor-like
            The bias to use
        padding : str or int (default 'same')
            The padding to use
        strides : int or tuple (default 1)
            The padding to use
        """

        factory_kwargs = {'device': device}
        super().__init__()
        self.w = torch.Tensor(kernel, **factory_kwargs).to_sparse()
        self.b = torch.Tensor(bias, **factory_kwargs).to_sparse()

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
        kernel = self.w.to_dense()
        bias = self.b.to_dense()

        return torch.nn.functional.conv2d(
            inputs,
            kernel,
            bias,
            stride=self.strides,
            padding=self.padding
        )
