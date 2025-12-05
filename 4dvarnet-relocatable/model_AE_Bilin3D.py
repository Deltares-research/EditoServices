import torch
import torch.nn.functional as F

class Encoder(torch.nn.Module):
  def __init__(self, dim_in = 1, dim_hidden = 32, dim_out = 1, kernel_size=3, downsamp=None, bilin_quad = False):
    super(Encoder, self).__init__()

    self.bilin_quad = bilin_quad

    self.conv_in = torch.nn.Conv3d(
        dim_in, dim_hidden, kernel_size = kernel_size, padding= 1
    )

    self.conv_hidden = torch.nn.Conv3d(
        dim_hidden, dim_hidden, kernel_size=kernel_size, padding= 1,
    )

    self.bilin_1 = torch.nn.Conv3d(
        dim_hidden, dim_hidden, kernel_size=kernel_size, padding=kernel_size // 2,
    )

    self.bilin_21 = torch.nn.Conv3d(
        dim_hidden, dim_hidden, kernel_size=kernel_size, padding=kernel_size // 2,
    )

    self.bilin_22 = torch.nn.Conv3d(
        dim_hidden, dim_hidden, kernel_size=kernel_size, padding=kernel_size // 2,
    )

    self.conv_out = torch.nn.Conv3d(
        2 * dim_hidden, dim_hidden, kernel_size=kernel_size, padding=kernel_size // 2,
    )

    self.down = torch.nn.AvgPool3d(downsamp, stride  = 2) if downsamp is not None else torch.nn.Identity()

  def forward(self, x):
    x = self.down( x )
    x = self.conv_in( x )
    x = self.conv_hidden(F.relu(x))

    nonlin = self.bilin_21(x)**2 if self.bilin_quad else (self.bilin_21(x)*self.bilin_22(x))
    x = self.conv_out(
        torch.cat([self.bilin_1(x), nonlin], dim=1)
    )

    return(x)


class Decoder(torch.nn.Module):
  def __init__(self, dim_hidden, dim_out, downsamp = None):
    super(Decoder, self).__init__()
    self.upconv1 = torch.nn.ConvTranspose3d(dim_hidden, dim_out, kernel_size=2, stride=2)

    # self.up = (torch.nn.UpsamplingBilinear2d(scale_factor=downsamp) if downsamp is not None else torch.nn.Identity())

  def forward(self, x):
    x = self.upconv1( x )
    return x

class model_AE(torch.nn.Module):
  def __init__(self, dim_in, DimAE, downsamp, bilin_quad):
    super(model_AE, self).__init__()
    self.encoder = Encoder(dim_in = dim_in, dim_hidden=DimAE, downsamp=downsamp, bilin_quad = bilin_quad)
    self.decoder = Decoder(dim_hidden= DimAE, dim_out= dim_in, downsamp = downsamp)

  def forward(self, x):
    x = x.unsqueeze(1)
    x = self.encoder(x)
    x = self.decoder(x)
    x = x.squeeze(1)
    return x
