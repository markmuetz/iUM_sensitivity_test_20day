from collections import OrderedDict as odict
import importlib

from processes import PylabProcess
from stash import stash

OPTS = odict([('PFE', {'ylim': (0, 1000), 'convolve': True, 'yaxis': True}),
             ('LHF', {'ylim': (0, 1000)}),
             ('SHF', {'ylim': (0, 1000)})])


class PlotSensitivitySurfTimeseries(PylabProcess):
    name = 'plot_sensitivity_surf_timeseries'
    out_ext = 'png'

    def load_modules(self):
        self.np = importlib.import_module('numpy')
        self.plt = importlib.import_module('pylab')
        self.iris = importlib.import_module('iris')

    def load_upstream(self):
        super(PlotSensitivitySurfTimeseries, self).load_upstream()
        filenames = [n.filename(self.config) for n in self.node.from_nodes]
        all_timeseries = self.iris.load(filenames)
        self.data = all_timeseries
        return all_timeseries

    def run(self):
        super(PlotSensitivitySurfTimeseries, self).run()
        all_timeseries = self.data
        fig, axes = self.plt.subplots(1, len(all_timeseries))
        fig.set_size_inches(PylabProcess.cm2inch(17, 7))
        # self.plt.tight_layout()
        self.plt.subplots_adjust(wspace=0.15, bottom=0.25)
        if len(all_timeseries) == 1:
            axes = [axes]
        # fig.suptitle('sensitivity surface timeseries ({})'.format(self.node.name))
        fig.canvas.set_window_title('timeseries')
        for i, timeseries in enumerate(all_timeseries):
            name, opt = OPTS.items()[i]
            ax = axes[i]
            times = timeseries.coords()[0].points.copy()
            times -= times[0]

            if 'convolve' in opt:
                # Average over 12 hours for precip (dt is 10 min).
                data = self.np.convolve(timeseries.data, self.np.ones((72, )) / 72., mode='same')
                ax.plot(times / 24, data)
            else:
                ax.plot(times / 24, timeseries.data)
            ax.set_xlabel('time (days)')

            if 'yaxis' in opt:
                # ax.set_ylabel(timeseries.units)
                ax.set_ylabel('W m$^{-2}$')
            else:
                ax.yaxis.set_ticklabels([])
            ax.set_title(name)
            if self.node.name == 'surf_ts_plots_2day_moist_profile_moist_cons':
                ax.set_ylim((0, 300))
            else:
                ax.set_ylim(opt['ylim'])
        self.processed_data = fig

    def save(self):
        super(PylabProcess, self).save()
        filename = self.node.filename(self.config)
        self.plt.savefig(filename)
        self.saved = True


