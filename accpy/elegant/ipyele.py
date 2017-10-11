# -*- coding: utf-8 -*-
"""accpy.elegant.ipyele
author:     felix.kramer(at)physik.hu-berlin.de
"""
from __future__ import print_function, division
from subprocess import Popen, PIPE, STDOUT
from numpy import (shape, array, max as npmax, argmax, roll, float64, core,
                   min as npmin, linspace, where)
from matplotlib.pylab import (plot, subplot, xlabel, ylabel, twinx, gca, xlim,
                              ylim, annotate, tight_layout)
from matplotlib.patches import Polygon, Rectangle
from matplotlib.offsetbox import AnchoredOffsetbox, TextArea, VPacker
from matplotlib import cm
from pylab import figure
from IPython.display import display, Javascript
from . import sdds
from ..simulate import const
from ..visualize.stringformat import uc
from ..dataio.hdf5 import h5save


def elegant(runfile, verbose=False, macro=None):
    path = Popen('echo $HOME', shell=True, stdout=PIPE).stdout.read().rstrip()
    path += '/defns.rpn'
    processstring = "export RPN_DEFNS='" + path + "' && elegant " + runfile
    if macro:
        processstring += ' -macro=' + macro
    process = Popen(processstring, shell=True, stdout=PIPE, stderr=STDOUT)
    stdout, stderr = process.communicate()
    if verbose:
        print('-- STDOUT --')
        print(stdout)
        print('-- STDERR --')
        print(stderr)
        print('-- THEEND --')
    return


def Pelegant(filename, Ncores=2, verbose=False, macro=None):
    path = Popen('echo $HOME', shell=True, stdout=PIPE).stdout.read().rstrip()
    path += '/defns.rpn'
    processstring = "export RPN_DEFNS='" + path + "' && mpiexec.hydra -n " + str(Ncores) + " Pelegant " + filename
    if macro:
        processstring += ' -macro=' + macro
    process = Popen(processstring, shell=True, stdout=PIPE, stderr=STDOUT)
    stdout, stderr = process.communicate()
    if verbose:
        print('-- STDOUT --')
        print(stdout)
        print('-- STDERR --')
        print(stderr)
        print('-- THEEND --')
    return


def sddsload(filename, verbose=False):
    data = sdds.SDDS(0)
    data.load(filename)

    pars = data.parameterName
    Npars = len(pars)
    parvals = data.parameterData
    pardict = dict(zip(pars, parvals))

    cols = data.columnName
    Ncols = len(cols)
    colvals = data.columnData
    # shape of colvals opposite for tracking of coordinates (points, particles) and other (1, points)  :(
    if shape(colvals[0])[0]==1:
        colvals = [array(val).T for val in colvals]
    else:
        colvals = [array(val) for val in colvals]
    coldict = dict(zip(cols, colvals))


    if verbose:
        # print information on loaded data
        print("SDDS description: ", data.description)
        print()
        print(Npars, "Paramters: {0:>13}".format('shape'))
        [print('{0:<20} {1:<}'.format(key, shape(val))) for key, val in pardict.items()]
        print()
        print(Ncols, "Columns: {0:>15}".format('shape'))
        [print('{0:<20} {1:<}'.format(key, shape(val))) for key, val in coldict.items()]
        print()

    data = pardict
    data.update(coldict)
    return data


def sdds2hdf5(filename, verbose=False):
    data = sdds.SDDS(0)
    data.load(filename)

    pars = data.parameterName
    parvals = data.parameterData
    datadict = dict(zip(pars, parvals))

    cols = data.columnName
    colvals = data.columnData
    # shape of colvals opposite for tracking of coordinates (points, particles) and other (1, points)  :(
    if shape(colvals[0])[0]==1:
        colvals = [array(val).T for val in colvals]
    else:
        colvals = [array(val) for val in colvals]
    datadict.update(dict(zip(cols, colvals)))
    h5save(filename, verbose, **datadict)


def eleplot(datadict, x, y, *args, **kwargs):
    try:
        selected = kwargs['sel']
        del(kwargs['sel'])
    except:
        selected = [0]
    try:
        label = kwargs['label']
        del(kwargs['label'])
    except:
        label = True
    [plot(datadict[x][:, sel], datadict[y][:, sel], *args, **kwargs) for sel in selected]
    if label:
        xlabel(x)
        ylabel(y)


def trackplot3(datadict, abscissa='Pass'):
    subplot(331)
    eleplot(datadict, abscissa, 'Cx', '.')
    subplot(334)
    eleplot(datadict, abscissa, 'Cxp', '.')
    subplot(337)
    eleplot(datadict, 'Cx', 'Cxp', '.')
    subplot(332)
    eleplot(datadict, abscissa, 'Cy', '.')
    subplot(335)
    eleplot(datadict, abscissa, 'Cyp', '.')
    subplot(338)
    eleplot(datadict, 'Cy', 'Cyp', '.')
    subplot(333)
    eleplot(datadict, abscissa, 'dCt', '.')
    subplot(336)
    eleplot(datadict, abscissa, 'Cdelta', '.')
    subplot(339)
    eleplot(datadict, 'dCt', 'Cdelta', '.')


def trackplot2(datadict, particles=8, abscissa='t'):
    subplot(321)
    eleplot(datadict, abscissa, 'x', '.b', sel=range(particles))
    subplot(323)
    eleplot(datadict, abscissa, 'xp', '.b', sel=range(particles))
    subplot(325)
    eleplot(datadict, 'x', 'xp', '.', sel=range(particles))
    subplot(322)
    eleplot(datadict, abscissa, 'y', '.', sel=range(particles))
    subplot(324)
    eleplot(datadict, abscissa, 'yp', '.', sel=range(particles))
    subplot(326)
    eleplot(datadict, 'y', 'yp', '.', sel=range(particles))


def drawlatt(ax, data):
    s = data['s']
    ax.set_xlim(npmin(s), npmax(s))

    yl = ax.get_ylim()[1]
    dy = abs(ax.get_ylim()[1] - ax.get_ylim()[0])*0.1
    yc = yl+dy/2

    i = 0
    while i < len(s):
        et = data['ElementType'][i]
        try:
            li = where(data['ElementType'][i:] != et)[0][0]
        except:
            li = len(data['ElementType'][i:])

        if i == 0:
            si = s[i]
        else:
            si = s[i - 1]
        sf = s[i + li - 1]
        dx = sf - si
        i += li

        if et == 'DRIF':
            ax.add_patch(Polygon(xy=array([[si, yc], [sf, yc]]), closed=False, color='w', clip_on=False, lw=2, zorder=110))
            continue
        elif et == 'CSBEND':
            c = 'yellow'
        elif et == 'KQUAD':
            c = 'red'
        elif et == 'KSEXT':
            c = 'green'
        else:
            c = 'none'
        if c != 'none':
            ax.add_patch(Rectangle(xy=(si, yl), width=dx, height=dy, ec=None, facecolor=c, clip_on=False, zorder=111))


def multicolorylab(ax, lablist, collist):
    boxs = [TextArea(l, textprops=dict(color=c, rotation=90, ha='center', va='bottom')) for l, c in zip(lablist, collist)]
    ybox = VPacker(children=boxs[::-1], pad=0, sep=5)
    anchored_ybox = AnchoredOffsetbox(loc=8, child=ybox, pad=0., frameon=False,
                                      bbox_to_anchor=(-.045, 0.41),
                                      bbox_transform=ax.transAxes, borderpad=0.)
    ax.add_artist(anchored_ybox)


def drawtwiss(data, fs):
    fig = figure(figsize=fs)
    ax1 = fig.add_subplot(111)
    ax2 = twinx()
    ax1.plot(data['s'], data['betax'], '-g')
    ax1.plot(data['s'], data['betay'], '-b')
    ax1.set_xlabel('s')
    ax1 = gca()
    multicolorylab(ax1, ['$\\beta_x$', ', ','$\\beta_y$', ' / (m)'], ['g', None, 'b', None])
    ax2.plot(data['s'], data['etax'], '-r')
    ax2.set_ylabel(r'$\eta_x$ / (m)', color='r')
    drawlatt(ax1, data)
    ax2.grid(None)
    return fig


def twissdata(data):
    print('General:')
    print('    L = {:}'.format(npmax(data['s'])))
    print('    E = {:}'.format(data['pCentral'][0]))
    print('    Eloss = {:}'.format(data['U0'][0]))
    print('\nTunes:')
    print('    Qx = {:.6}'.format(data['nux'][0]))
    print('    Qy = {:.6}'.format(data['nuy'][0]))
    print('\nChromaticities:')
    print('    ' + uc.greek.xi + 'x = {:.6}'.format(data['dnux/dp'][0]))
    print('    ' + uc.greek.xi + 'y = {:.6}'.format(data['dnuy/dp'][0]))
    print('\nMomentum Compaction Factor:')
    print('    ' + uc.greek.alpha + 'p = {:.5e}'.format(data['alphac'][0]))
    print('\nRadiation Damping times:')
    print('    ' + uc.greek.tau + 'x = {:.6} ms'.format(1e3*data['taux'][0]))
    print('    ' + uc.greek.tau + 'y = {:.6} ms'.format(1e3*data['tauy'][0]))
    print('    ' + uc.greek.tau + uc.greek.delta + ' = {:.6} ms'.format(1e3*data['taudelta'][0]))
    print('\nDamping partition factors:')
    print('    Jx = {:.6}'.format(data['Jx'][0]))
    print('    Jy = {:.6}'.format(data['Jy'][0]))
    print('    J' + uc.greek.delta + ' = {:.6}'.format(data['Jdelta'][0]))
    print('\nHorizontal equilibrium geometric and normalized emittances:')
    print('    ' + uc.greek.epsilon + 'x = {:.6}'.format(data['ex0'][0]))
    print('    ' + uc.greek.epsilon + 'x* = {:.6}'.format(data['enx0'][0]))
    print('\nEquilibrium fractional rms energy spread:')
    print('    ' + uc.greek.epsilon + uc.greek.delta + ' = {:.6e}'.format(data['Sdelta0'][0]))
    print('\nHigher Order::')
    print('    ' + uc.greek.xi + 'x2 = {:}'.format(data['dnux/dp2'][0]))
    print('    ' + uc.greek.xi + 'y2 = {:}'.format(data['dnuy/dp2'][0]))
    print('    ' + uc.greek.xi + 'x3 = {:}'.format(data['dnux/dp3'][0]))
    print('    ' + uc.greek.xi + 'y3 = {:}'.format(data['dnuy/dp3'][0]))
    print('    ' + uc.greek.alpha + 'p2 = {:e}'.format(data['alphac2'][0]))
    return


def twissplot(data, zoom=False, fs=[16, 9]):
    if zoom:
        starti, endi = argmax(data['s'] >= zoom[0]), argmax(data['s'] >= zoom[1])
        clipdata = {}
        for clip in ['s', 'betax', 'betay', 'etax', 'ElementType']:
            clipdata[clip] = data[clip][starti:endi]
        fig = drawtwiss(clipdata, fs)
        return fig
    fig = drawtwiss(data, fs)
    return fig


def b2twissplot(coldict, pardict):
    L = npmax(coldict['s'])
    print('L = {:}'.format(L))
    print('Qx = {:}'.format(pardict['nux'][0]))
    print('Qx = {:}'.format(pardict['nux'][0]))
    print('Qy = {:}'.format(pardict['nuy'][0]))
    print(uc.greek.alpha + 'p = {:e}'.format(pardict['alphac'][0]))

    eleplot(coldict, 's', 'betax', '-g')
    eleplot(coldict, 's', 'betay', '-b')
    twinx()
    eleplot(coldict, 's', 'etax', '-r')

    # Latteice graphics vertical position and size (axis coordinates!)
    lypos = gca().get_ylim()[1]
    tp = Twissplot(lypos = lypos, lysize = lypos*0.12)
    tp.axislabels(yscale=0.5)
    tp.paintlattice(coldict, 0, L, ec=False, fscale=2)
    xlim(0, L)



def autoscroll(threshhold):
    if threshhold==0:  # alway scroll !not good
        javastring = '''
        IPython.OutputArea.prototype._should_scroll = function(lines) {
            return true;
        }
        '''
    elif threshhold==-1:  # never scroll !not good
        javastring = '''
        IPython.OutputArea.prototype._should_scroll = function(lines) {
            return false;
        }
        '''
    else:
        javastring = 'IPython.OutputArea.auto_scroll_threshold = ' + str(threshhold)
    display(Javascript(javastring))


class Twissplot():
    Dnames = ['Injection','U125','UE56','U49','UE52','UE56 + U139 (slicing)','UE112','UE49']
    Tnames = ['Landau + BAM WLS7','MPW','U41','UE49','UE46','CPMU17 + UE48 (EMIL)','PSF WLS7','Cavities']
    names = {'D': Dnames, 'T' : Tnames, 'S' :  core.defchararray.add(Dnames,core.defchararray.add(' + ',Tnames))}

    def __init__(self, lypos = 25, lysize = 3):
        self.lypos = lypos
        self.lysize = lysize

#    def getrolled(self,s,y,fmt=None): # access lattice from -120 to 120m
#        x = array(s,dtype=float64)
#        y = array(y,dtype=float64)
#        x[x > 120] = x[x > 120] - 240.0
#        ishift = argmax(x < 0)
#        x = roll(x,-ishift)
#        y = roll(y,-ishift)
#        if fmt:
#            return x,y,fmt
#        else:
#            return x,y

    # Note:
    # It seem elegant twiss-ouput always prints the length, type and name
    # at the END of the element (!)
    #
    # Check element list
    # print np.unique(twi.ElementType)
    # ['CSBEND' 'DRIF' 'KQUAD' 'KSEXT' 'MALIGN' 'MARK' 'RECIRC' 'WATCH']
    #
    def paintlattice(self,d,s0,s1,ycenter=None,ysize=None,ec=True,labels=True,rolled=False, fscale=1.0):
        if ycenter is None:
            ycenter = self.lypos
        if ysize is None:
            ysize = self.lysize
        s = d['s']
        et = d['ElementType']
        en = d['ElementName']
        if rolled:
            s[s> 120] = s[s > 120] - 240.0
            ishift = argmax(s < 0)
            s = roll(s,-ishift)
            et = roll(et,-ishift)
            en = roll(en,-ishift)

        i0 = argmax(s >= s0)
        i1 = argmax(s >= s1)
        #print i0,i1
        start = s0
        for i in range(i0,i1 + 1):
            # save start if previous element was something else
            if i > i0:
                if et[i] != et[i-1]:
                    start = s[i-1]
            # skip if next element of same type
            if i < i1:
                if et[i] == et[i+1]:
                    continue
            end = min((s[i],s1))
            l = end - start
            #print i, s[i], et[i], en[i], '    length of element:', l
            col = 'none'
            ecol='k'
            if et[i] == 'CSBEND':
                col = 'yellow'
                ecol='black'
            if et[i] == 'KQUAD':
                col = 'red'
            if et[i] == 'KSEXT':
                col = 'green'
            if not ec:
                ecol='none'

            if col != 'none':
                gca().add_patch(Rectangle((start, ycenter-0.5*ysize), l,ysize, ec=ecol, facecolor=col,clip_on=False, zorder = 101))
                if labels:
                    fs = 80 / (s1-s0) * fscale
                    if et[i] == 'KSEXT':
                        annotate(en[i], xy=(start,ycenter), xytext=(start+0.5*l, ycenter - .55*ysize),fontsize=fs,va='top',ha='center',clip_on=False, zorder = 102)
                    else:
                        annotate(en[i], xy=(start,ycenter), xytext=(start+0.5*l, ycenter + .5*ysize),fontsize=fs,va='bottom',ha='center',clip_on=False, zorder = 102)


    def axislabels(self,yscale=1,Dfac=10):
        xlabel('s / m')

        ybox3 = TextArea("       $\\eta_x / {0}".format(int(100/Dfac))+"\mathrm{cm}$", textprops=dict(color="r",rotation=90,ha='left',va='center'))
        ybox1 = TextArea("  $\\beta_y / \mathrm{m}$",     textprops=dict(color="b",rotation=90,ha='left',va='center'))
        ybox2 = TextArea("$\\beta_x / \mathrm{m}$", textprops=dict(color="g",rotation=90,ha='left',va='center'))
        ybox = VPacker(children=[ybox3, ybox1, ybox2],align="bottom", pad=0, sep=5)
        anchored_ybox = AnchoredOffsetbox(loc=8, child=ybox, pad=0., frameon=False, bbox_to_anchor=(-0.08*yscale, 0.15),
                                          bbox_transform=gca().transAxes, borderpad=0.)
        gca().add_artist(anchored_ybox)
        ylim(-1)


    def plotsection(self,d,stype,nr):
        s0 = (nr-1)*30.0 - 7.5
        if stype == 'T':
            s0 += 15.0
        if stype == 'S':
            s1 = s0 + 30.0
        else:
            s1 = s0 + 15.0

        if stype == 'D' and nr == 1:
            plot(*self.getrolled(d.s, d.betax,'g-'))
            plot(*self.getrolled(d.s, d.betay,'b-'))
            x, y, = self.getrolled(d.s, d.etax)
            plot(x,10*y,'r-')
            rolled=True
        else:
            plot(d.s, d.betax,'g-')
            plot(d.s, d.betay,'b-')
            plot(d.s, 10* array(d.etax,dtype=float64) ,'r-')
            rolled=False

        annotate(stype+'{0:0n}'.format(nr),xy=((s1+s0)/2.0,25-5), fontsize=20,ha='center',va='top',zorder=105)
        gca().yaxis.grid(alpha=0.3, zorder=0)

        #    print stype, names[stype][nr-1], names[stype]
        annotate(''+self.names[stype][nr-1]+'',xy=((s1+s0)/2.0,25-9), fontsize=8,ha='center',va='top',zorder=105)

        self.paintlattice(d,s0,s1, self.lypos, self.lysize, ec=True,rolled=rolled)
        self.axislabels()
        xlim(s0,s1)


def trackplot(datadict, turns=False):
    try:  # centroid watch point
        x = ['Pass', 'Pass', 'Pass', 'Pass', 'Pass', 'Pass', 'Cx', 'Cy', 'dCt']
        y = ['Cx', 'Cy', 'dCt', 'Cxp', 'Cyp', 'Cdelta', 'Cxp', 'Cyp', 'Cdelta']
        for i, (x, y) in enumerate(zip(x, y)):
            subplot(3, 3, i+1)
            if turns:
                plot(datadict[x][:turns, ], datadict[y][:turns, ], '.')
            else:
                plot(datadict[x][:, ], datadict[y][:, ], '.')
            xlabel(x)
            ylabel(y)
    except:  # coordinate watch point
        x = ['t', 't', 't', 't', 't', 't', 'x', 'y', 'dt']
        y = ['x', 'y', 'dt', 'xp', 'yp', 'p', 'xp', 'yp', 'p']
        colors = cm.rainbow(linspace(0, 1, datadict['Particles'][0]))
        for i, (x, y) in enumerate(zip(x, y)):
            subplot(3, 3, i+1)
            if turns:
                if x == 't':
                    [plot(datadict[y][:turns, part], '.', color=col) for part, col in enumerate(colors)]
                    xlabel('Pass')
                else:
                    [plot(datadict[x][:turns, part], datadict[y][:turns, part], '.', color=col) for part, col in enumerate(colors)]
                    xlabel(x)
            else:
                if x == 't':
                    [plot(datadict[y][:, part], '.', color=col) for part, col in enumerate(colors)]
                    xlabel('Pass')
                else:
                    [plot(datadict[x][:, part], datadict[y][:, part], '.', color=col) for part, col in enumerate(colors)]
                    xlabel(x)
            ylabel(y)
            tight_layout()
    return


def showbun(datadict):
    x = ['', '', '', '', '', '', 'x', 'y', 't']
    y = ['x', 'y', 't', 'xp', 'yp', 'p', 'xp', 'yp', 'p']
    colors = cm.rainbow(linspace(0, 1, datadict['Particles'][0]))
    for i, (x, y) in enumerate(zip(x, y)):
        subplot(3, 3, i+1)
        if x == '':
            [plot(datadict[y][part, ], '.', color=col) for part, col in enumerate(colors)]
            xlabel('Pass')
        else:
            [plot(datadict[x][part, ], datadict[y][part, ], '.', color=col) for part, col in enumerate(colors)]
            xlabel(x)
        ylabel(y)
    tight_layout()
    return


def mybunch(bunchname, ranges, E_mev):

    cl = const.cl
    qe = const.qe
    me = const.me
    E0 = me*cl**2/qe  # eV
    gamma = 1 + E_mev*1e6/E0
    print('gamma = {}'.format(gamma))

    N = len(ranges['x'])
    bunch = sdds.SDDS(0)  # what does the index mean?
    bunch.setDescription('my predefined bunch', 'bunched-beam phase space')
    bunch.mode = 1  # 1 is binary, 2 is ascii

    parnames = ['Particles', 'pCentral', 'IDSlotsPerBunch']
    parsymbs = ['', 'p$bcen$n', '']
    parunits = ['', 'm$be$nc', '']
    pardescr = ['Number of particles before sampling', 'Reference beta*gamma', 'Number of particle ID slots reserved to a bunch']
    parforms = ['', '', '']
    parfixva = ['', '', '']
    partypes = [bunch.SDDS_LONG, bunch.SDDS_DOUBLE, bunch.SDDS_LONG]
    pardatas = [[N], [gamma], [N]]
    parstuff = zip(parnames, parsymbs, parunits, pardescr, parforms, partypes, parfixva, pardatas)

    for name, symbol, units, description, formatString, typ, fixedValue, data in parstuff:
        bunch.defineParameter(name, symbol, units, description, formatString, typ, fixedValue)
        bunch.setParameterValueList(name, data)

    colnames = ['x', 'xp', 'y', 'yp', 't', 'p', 'particleID']
    colsymbs = ['']*7
    colunits = ['m', '', 'm', '', 's', 'm$be$nc', '']
    coldescr = ['']*7
    colforms = ['']*7
    coltypes = [bunch.SDDS_DOUBLE]*6 + [bunch.SDDS_LONG]
    colfleng = [1]*7
    coldatas = [[list(ranges['x'])],
                [list(ranges['xp'])],
                [list(ranges['y'])],
                [list(ranges['yp'])],
                [list(ranges['t'])],
                [list(1 + ranges['p']*1e6/E0)],
                [range(1, 1 + N)]]
    colstuff = zip(colnames, colsymbs, colunits, coldescr, colforms, coltypes, colfleng, coldatas)

    for name, symbol, units, description, formatString, typ, fieldLength, data in colstuff:
        bunch.defineColumn(name, symbol, units, description, formatString, typ, fieldLength)
        bunch.setColumnValueLists(name, data)


    bunch.save(bunchname)
    return