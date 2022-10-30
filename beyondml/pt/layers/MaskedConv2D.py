import numpy as np
import torch


class MaskedConv2D(torch.nn.Module):
    """
    Masked 2D Convolutional layer
    """

    def __init__(
        self,
        in_channels,
        out_channels,
        kernel_size=3,
        padding='same',
        strides=1,
        device=None,
        dtype=None
    ):
        """
        Parameters
        ----------
        in_channels : int
            The number of channels for input data
        out_channels : int
            The number of filters to use
        kernel_size : int or tuple (default 3)
            The kernel size to use
        padding : str or int (default 'same')
            Padding to use
        strides : int or tuple (default 1)
            The number of strides to use
        """

        super().__init__()
        self.factory_kwargs = {'device': device, 'dtype': dtype}
        self.in_channels = in_channels
        self.out_channels = out_channels
        self.kernel_size = kernel_size
        self.padding = padding
        self.strides = strides

        filters = torch.Tensor(
            self.out_channels,
            self.in_channels,
            self.kernel_size[0],
            self.kernel_size[1],
        ).to(**self.factory_kwargs)
        filters = torch.nn.init.kaiming_normal_(filters, a=np.sqrt(5))
        self.w = torch.nn.Parameter(filters)
        self.w_mask = torch.ones_like(self.w, **self.factory_kwargs)

        bias = torch.zeros(out_channels, **self.factory_kwargs)
        self.b = torch.nn.Parameter(bias)
        self.b_mask = torch.ones_like(self.b, **self.factory_kwargs)

    @property
    def in_channels(self):
        return self._in_channels

    @in_channels.setter
    def in_channels(self, value):
        if not isinstance(value, int):
            raise TypeError('in_channels must be int')
        self._in_channels = value

    @property
    def out_channels(self):
        return self._out_channels

    @out_channels.setter
    def out_channels(self, value):
        if not isinstance(value, int):
            raise TypeError('out_channels must be int')
        self._out_channels = value

    @property
    def kernel_size(self):
        return self._kernel_size

    @kernel_size.setter
    def kernel_size(self, value):
        if isinstance(value, int):
            value = (value, value)
        elif isinstance(value, tuple):
            if not all([isinstance(val, int) for val in value]) and len(value) == 2:
                raise ValueError('If tuple, kernel_size must be two integers')
        else:
            raise TypeError('kernel_size must be int or tuple')
        self._kernel_size = value

    def forward(self, inputs):
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
        return torch.nn.functional.conv2d(
            inputs,
            self.w * self.w_mask,
            self.b * self.b_mask,
            stride=self.strides,
            padding=self.padding
        )

    def prune(self, percentile):
        """
        Prune the layer by updating the layer's mask

        Parameters
        ----------
        percentile : int
            Integer between 0 and 99 which represents the proportion of weights to be inactive

        Notes
        -----
        Acts on the layer in place
        """
        w_copy = np.abs(self.w.detach().cpu().numpy())
        b_copy = np.abs(self.b.detach().cpu().numpy())
        w_percentile = np.percentile(w_copy, percentile)
        b_percentile = np.percentile(b_copy, percentile)

        new_w_mask = torch.Tensor(
            (w_copy >= w_percentile).astype(int)).to(**self.factory_kwargs)
        new_b_mask = torch.Tensor(
            (b_copy >= b_percentile).astype(int)).to(**self.factory_kwargs)
        self.w_mask = new_w_mask
        self.b_mask = new_b_mask

        self.w = torch.nn.Parameter(
            self.w * self.w_mask
        )
        self.b = torch.nn.Parameter(
            self.b * self.b_mask
        )
