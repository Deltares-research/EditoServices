import torch
import torch.nn.functional as F

# Torch.nn.module is a base class for all the neural network modules

## class for the creation of the Residual Neural Network
class ResNetConv2D(torch.nn.Module):
  def __init__(self,Nblocks,dim,K,
                 kernel_size,
                 padding=0):
      super(ResNetConv2D, self).__init__()
      self.resnet = self._make_ResNet(Nblocks,dim,K,kernel_size,padding)


  # classic structure of a resnet block
  def _make_ResNet(self,Nblocks,dim,K,kernel_size,padding):
      layers = []
      for kk in range(0,Nblocks):
        layers.append(torch.nn.Conv2d(dim,K*dim,kernel_size,padding=padding,bias=False))
        layers.append(torch.nn.ReLU())
        layers.append(torch.nn.Conv2d(K*dim,dim,kernel_size,padding=padding,bias=False))

      return torch.nn.Sequential(*layers)

  def forward(self, x):
      x = self.resnet ( x )

      return x

## class for the LSTM architecture
class ConvLSTM2d(torch.nn.Module):
    def __init__(self, input_size, hidden_size, kernel_size = 3):
        super(ConvLSTM2d, self).__init__()
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.kernel_size = kernel_size
        self.padding = int((kernel_size - 1) / 2)
        self.Gates = torch.nn.Conv2d(input_size + hidden_size, 4 * hidden_size, kernel_size = self.kernel_size, stride = 1, padding = self.padding)

    def forward(self, input_, prev_state, device):

        # get batch and spatial sizes
        batch_size = input_.shape[0]
        spatial_size = input_.shape[2:]

        # generate empty prev_state, if None is provided
        if prev_state is None:
            state_size = [batch_size, self.hidden_size] + list(spatial_size)
            prev_state = (
                torch.autograd.Variable(torch.zeros(state_size)).to(device),
                torch.autograd.Variable(torch.zeros(state_size)).to(device)
            )

        # prev_state has two components
        prev_hidden, prev_cell = prev_state

        stacked_inputs = torch.cat((input_, prev_hidden), 1)
        gates = self.Gates(stacked_inputs)

        # chunk across channel dimension: split it to 4 samples at dimension 1
        in_gate, remember_gate, out_gate, cell_gate = gates.chunk(4, 1)

        # apply sigmoid non linearity
        in_gate = torch.sigmoid(in_gate)
        remember_gate = torch.sigmoid(remember_gate)
        out_gate = torch.sigmoid(out_gate)

        # apply tanh non linearity
        cell_gate = torch.tanh(cell_gate)

        # compute current cell and hidden state
        cell = (remember_gate * prev_cell) + (in_gate * cell_gate)
        hidden = out_gate * torch.tanh(cell)

        return hidden, cell

## class for computing the gradient of the loss function (modified respect to the original code)
class Compute_Grad(torch.nn.Module):
    def __init__(self,ShapeData,):
        super(Compute_Grad, self).__init__()

        with torch.no_grad():
            self.shape     = ShapeData

        self.alphaObs    = torch.nn.Parameter(torch.Tensor([1.]))
        self.alphaAE     = torch.nn.Parameter(torch.Tensor([1.]))

    def forward(self, x,xpred,xobs,mask):

        # compute gradient
        ## true gradient using autograd for prior ||x-g(x)||
        loss1 = F.mse_loss(x, xpred)
        loss2 = F.mse_loss(x*mask, xobs*mask)
        loss  = self.alphaAE**2 * loss1 + self.alphaObs**2 * loss2 ## variational cost

        grad = torch.autograd.grad(loss,x,create_graph=True)[0]

        # Check is this is needed or not
        grad.retain_grad()

        return grad

# Gradient-based minimization using a LSTM using a (sub)gradient as inputs
class model_GradUpdate(torch.nn.Module):
    def __init__(self,ShapeData,DimState, periodicBnd=False):
        super(model_GradUpdate, self).__init__()

        with torch.no_grad():
            self.shape     = ShapeData
            self.DimState = DimState
            # self.DimState  = 5*self.shape[0]
            self.PeriodicBnd = periodicBnd
            if( (self.PeriodicBnd == True) & (len(self.shape) == 2) ):
                print('No periodic boundary available for FxTime (eg, L63) tensors. Forced to False')
                self.PeriodicBnd = False
        self.compute_Grad  = Compute_Grad(ShapeData)
        self.convLayer     = self._make_ConvGrad()

        K = torch.Tensor([0.1]).view(1,1,1,1)
        self.convLayer.weight = torch.nn.Parameter(K)
        self.lstm = ConvLSTM2d(self.shape[1],self.DimState,3)

    def _make_ConvGrad(self):
        layers = []
        layers.append(torch.nn.Conv2d(self.DimState, self.shape[1], (1,1), padding=0,bias=False))

        return torch.nn.Sequential(*layers)

    def forward(self, x,xpred,xobs,mask,hidden,cell,gradnorm=1.0, device = None):

        # compute gradient
        grad = self.compute_Grad(x, xpred,xobs,mask)
        grad  = grad / gradnorm

        if self.PeriodicBnd == True :
            dB     = 7
            #
            grad_  = torch.cat((grad[:,:,x.size(2)-dB:,:],grad,grad[:,:,0:dB,:]),dim=2)
            if hidden is None:
                hidden_,cell_ = self.lstm(grad_,None, device)
            else:
                hidden_  = torch.cat((hidden[:,:,x.size(2)-dB:,:],hidden,hidden[:,:,0:dB,:]),dim=2)
                cell_    = torch.cat((cell[:,:,x.size(2)-dB:,:],cell,cell[:,:,0:dB,:]),dim=2)
                hidden_,cell_ = self.lstm(grad_,[hidden_,cell_], device)

            hidden = hidden_[:,:,dB:x.size(2)+dB,:]
            cell   = cell_[:,:,dB:x.size(2)+dB,:]
        else:
            if hidden is None:
                hidden,cell = self.lstm(grad,None, device)
            else:
                hidden,cell = self.lstm(grad,[hidden,cell], device)

        grad = self.convLayer( hidden )

        return grad,hidden,cell

class Model_4DVarNN_GradFP(torch.nn.Module):
    def __init__(self,mod_AE,ShapeData,DimState,NiterProjection,NiterGrad, lr_grad=0.2, InterpFlag=False,periodicBnd=False):
        super(Model_4DVarNN_GradFP, self).__init__()

        self.model_AE = mod_AE
        self.lr_grad = lr_grad


        with torch.no_grad():
            # print('Opitm type %d'%OptimType)
            self.NProjFP   = int(NiterProjection)
            self.NGrad     = int(NiterGrad)
            self.InterpFlag  = InterpFlag
            self.periodicBnd = periodicBnd

        ## load the updating rule using gradient descent
        self.model_Grad = model_GradUpdate(ShapeData, DimState[0])
        self.model_Grad_input = model_GradUpdate(ShapeData, DimState[1])

    def forward(self, device, x_inp,xobs,mask,g1=None,g2=None,normgrad=0.0,):
        mask_  = torch.add(1.0,torch.mul(mask,-1.0)) #1. - mask

        x      = torch.mul(x_inp,1.0)

        # fixed-point iterations
        if self.NProjFP > 0:
          for kk in range(0,self.NProjFP):
        #if NiterProjection > 0:
        #  x      = torch.mul(x_inp,1.0)
        #  for kk in range(0,NiterProjection):
            x_proj = self.model_AE(x)
            x_proj = torch.mul(x_proj,mask_)
            x      = torch.mul(x, mask)
            x      = torch.add(x , x_proj )

        # gradient iteration
        if self.NGrad > 0:
            # gradient normalisation
            grad       = self.model_Grad.compute_Grad(x, self.model_AE(x),xobs,mask)
            grad_input = self.model_Grad_input.compute_Grad(x, self.model_AE(x),xobs,mask)
            ## true gradient used by Quentin
            true_grad = grad
            true_grad_input = grad_input
            if normgrad == 0. :
                _normgrad = torch.sqrt( torch.mean( grad**2 ) )
                _normgrad_input = torch.sqrt( torch.mean( grad_input**2 ) )
            else:
                _normgrad = normgrad
                _normgrad_input = normgrad
            for kk in range(0,self.NGrad):
                # AE pediction
                xpred = self.model_AE(x)

                # gradient update
                if kk == 0:
                  grad,hidden,cell  = self.model_Grad_input( x, xpred, xobs, mask, g1, g2 , _normgrad_input, device = device )
                  step_update = (1 / (kk + 1))*grad + self.lr_grad*((kk + 1) / self.NGrad)*true_grad_input
                else:
                  grad,hidden,cell  = self.model_Grad( x, xpred, xobs, mask, hidden, cell , _normgrad, device = device )
                  step_update = (1 / (kk + 1))*grad + self.lr_grad*((kk + 1) / self.NGrad)*true_grad

                # optimization update
                
                x = x - step_update

            return x,hidden,cell,_normgrad
        else:
            _normgrad = 1.
            return x,None,None,_normgrad
