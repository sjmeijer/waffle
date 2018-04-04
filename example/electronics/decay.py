#!/usr/local/bin/python
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm

from siggen import PPC
from scipy import signal
from scipy.ndimage.filters import gaussian_filter1d

from waffle.models.electronics import HiPassFilterModel

em = HiPassFilterModel()

det = PPC( os.path.join(os.environ["DATADIR"],  "siggen", "config_files", "bege.config"), wf_padding=100)
imp_avg = -2
imp_grad = 1.2
det.siggenInst.SetImpurityAvg(imp_avg, imp_grad)





def main():
    plot_wfs(det)


def plot_wfs(det):
    det.lp_order=2

    det.lp_num = [1,2,1]
    det.lp_den = em.zpk_to_ba(0.975, 0.007)

    det.hp_order = 2


    mag = 1.-10.**-5.145
    phi = np.pi**-13.3
    det.hp_num = [1,-2,1]
    det.hp_den = em.zpk_to_ba(mag, phi)

    wf_proc = np.copy(det.MakeSimWaveform(25, 0, 25, 1, 125, 0.95, 1000, smoothing=20))
    wf_compare = np.copy(wf_proc)

    f, ax = plt.subplots(2,2,figsize=(15,8))
    ax[0,0].plot (wf_compare,  color="r")


    cmap = cm.get_cmap('viridis')

    phis = np.logspace(-15, -8, 100, base=np.pi)
    # phis = np.pi - phis

    w,h = get_freq_resp(mag, phi)
    ax[0,1].loglog( w, h, color="r")

    for phi2 in phis:
        color = cmap( (phi2 - phis[0])/(phis[-1] - phis[0]) )

        det.hp_den = em.zpk_to_ba(mag, phi2)
        wf_proc = np.copy(det.MakeSimWaveform(25, 0, 25, 1, 125, 0.95, 1000, smoothing=20))

        try:
            ax[0,0].plot (wf_proc, label="{}, {}".format(phi,mag), color=color)
            ax[1,0].plot (wf_proc-wf_compare, label="{}, {}".format(phi,mag), color=color)
        except TypeError:
            continue

        w,h2 = get_freq_resp(mag, phi2)
        ax[0,1].loglog( w, h2, color=color)


    # plt.legend()
    plt.show()


def get_freq_resp(p_mag, p_phi):
    freq_samp = 1E9
    nyq_freq = 0.5*freq_samp

    num = np.array([1,-2,1])
    den1 = em.zpk_to_ba(p_mag, p_phi)

    w =np.logspace(-15, -7, 500, base=np.pi)

    w, h = signal.freqz(num, den1, worN=w)
    w/= (np.pi /nyq_freq)

    return w, np.abs(h)


if __name__ == "__main__":
    main()