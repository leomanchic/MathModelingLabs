def calc_f_equil(self) -> np.ndarray:
    """Calculate f equilimbrium
    Returns:
        np.ndarray: f equilimbrium with sahpe (x, y, N)
    """
    norma = self.u_x**2 + self.u_y**2
    for i, vx, vy, a in zip(self._index, self._vx, self._vy, self._a):
        dot  = self.u_x*vx + self.u_y*vy
        self.f_equil[:,:,i] = self.density*a*(1 + 3*dot + 4.5*dot**2 - 1.5*norma)


def calc_inflow(self):
    """
    Calculate inflow boundary condition
    """
    self.u_x[0] = self.v_init
    self.u_y[0,:] = 0
    rho_2 = np.sum(self.f_in[0,:,self._ind_middle], axis=0)
    rho_3 = np.sum(self.f_in[0,:,self._ind_right], axis=0)
    self.density[0, :] = 1/(1 - self.u_x[0]) * (rho_2 + 2*rho_3)

    self.calc_f_equil()

    self.f_in[0, :, self._ind_left] = self.f_equil[0,:, self._ind_left] +\
                                        self.f_in[0,:, self._ind_right] -\
                                        self.f_equil[0,:, self._ind_right]


def calc_f_out(self):
    """
    Calculate pre-collision (f out)
    """
    self.f_out = self.f_in - self.omega*(self.f_in - self.f_equil)


def bounce_back(self):
    """
    Bounce-back boundary condition on 
    solid obstacle
    """
    bndry = self.f_in[self.obstacle,:]
    self.f_out[self.obstacle,:] = bndry[:, self._index[::-1]]


def collision(self):
    """
    Calculate post-collision process
    """
    for i, vx, vy in zip(self._index, self._vx, self._vy):
        self.f_in[:,:,i] = np.roll(
                                np.roll(self.f_out[:,:,i], vy, axis=1), 
                                vx, axis=0
                            )
