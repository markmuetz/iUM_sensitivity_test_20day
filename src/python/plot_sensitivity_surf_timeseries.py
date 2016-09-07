from collections import OrderedDict as odict

import numpy as np
import pylab as plt
import iris

from omnium.processes import PylabProcess
from omnium.stash import stash

OPTS = odict([('Precip. flux equiv.', {'ylim': (0, 2000), 'convolve': True, 'yaxis': True}),
             ('LHF', {'ylim': (0, 2000)}),
             ('SHF', {'ylim': (0, 2000)})])


class PlotMultiTimeseries(PylabProcess):
    name = 'plot_sensitivity_surf_timeseries'
    out_ext = 'png'

    def load_upstream(self):
        super(PlotMultiTimeseries, self).load_upstream()
        filenames = [n.filename(self.config) for n in self.node.from_nodes]
        all_timeseries = iris.load(filenames)
        self.data = all_timeseries
        return all_timeseries

    def run(self):
        super(PlotMultiTimeseries, self).run()
        all_timeseries = self.data
        fig, axes = plt.subplots(1, len(all_timeseries))
        plt.subplots_adjust(wspace=0.32)
        if len(all_timeseries) == 1:
            axes = [axes]
        fig.suptitle('sensitivity surface timeseries ({})'.format(self.node.name))
        fig.canvas.set_window_title('timeseries')
        for i, timeseries in enumerate(all_timeseries):
            name, opt = OPTS.items()[i]
            ax = axes[i]
            times = timeseries.coords()[0].points.copy()
            times -= times[0]

            if 'convolve' in opt:
                # Average over 12 hours for precip (dt is 10 min).
                data = np.convolve(timeseries.data, np.ones((72, )) / 72., mode='same')
                ax.plot(times / 24, data)
            else:
                ax.plot(times / 24, timeseries.data)
            ax.set_xlabel('time (days)')

            if 'yaxis' in opt:
                ax.set_ylabel(timeseries.units)
            ax.set_title(name)
            ax.set_ylim(opt['ylim'])
        self.processed_data = fig


