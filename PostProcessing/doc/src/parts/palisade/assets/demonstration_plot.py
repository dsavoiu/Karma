from Karma.PostProcessing.Palisade import PlotProcessor, LiteralString

cfg = {
  # declare input files
  'input_files' : {
    'my_file' : "input_file.root"
  },

  # declare figures (only one in this example)
  'figures' : [

    # define the figure
    {
      # output file name (extension determines file type)
      'filename': 'demonstration_plot.png',

      # list of plots (one dict per plot)
      'subplots': [

        # plot histograms from 'my_file'
        {
          'expression' : '"my_file:h1"',
          'plot_method': 'step',
          'color': 'orange',
          'label': "Histogram 1",
          'pad': 0,
        },
        {
          'expression' : '"my_file:h2"',
          'plot_method': 'bar',
          'color': 'cornflowerblue',
          'label': "Histogram 2",
          'pad': 0,
        },
        # plot difference of above histograms in bottom pad
        {
          'expression' : '"my_file:h1" - "my_file:h2"',
          'plot_method': 'errorbar',
          'label': "Histogram 1 $-$ Histogram 2",
          'color': 'black',
          'pad': 1,
        }
      ],

      # adjust layout
      'pad_spec': {
        # set margins
        'left': 0.15,
        'right': 0.95,
        'bottom': 0.12,
        # set vertical pad spacing
        'hspace': 0.04,
      },

      # define pads (a main pad and a pad for the difference)
      'pads': [
        # pad 0
        {
          'height_share': 2,  # make pad two units high
          'y_label' : 'Entries',
          'y_scale' : 'log',  # use logarithmic scaling for 'y' axis

          'x_range' : (-1, 15),
          'x_ticklabels': [],  # do not display tick labels for upper pad
        },
        # pad 1
        {
          'height_share': 1,  # make pad one unit high
          'y_label' : 'Difference',

          'x_label' : 'Value',
          'x_range' : (-1, 15),  # set x range to match the pad above

          'axhlines' : [0.0],  # draw a reference line at zero
        }
      ],

      'texts' : [
        {
          'text': 'Pad coordinates $(1/2, 1/2)$',
          'xy': (.5, .5),
          'xycoords': 'axes fraction',  # default: 'xy' are fraction of pad dimensions
          # matplotlib keywords
          'ha': 'center',  # align text horizontally
          'va': 'center'   # align text vertically
        },
        {
          'text': 'Data coordinates $(6, 10)$',
          'xy': (6, 10),
          'xycoords': 'data',  # 'xy' are data coordinates
          # matplotlib keywords
          'ha': 'center',
          'va': 'center'
        },
        {
          'text': 'Expectation: $0.0$',
          'xy': (6, 500),
          'xycoords': 'data',
          'pad': 1,  # put this text in lower pad
          # matplotlib keywords
          'color': 'gray'
        },
        # upper plot label (need to escape braces with `LiteralString`)
        {
          'text' : LiteralString(r"upper label with math: $\phi={\left(1\pm\sqrt{5}\right)}/{2}$"),
          'xy': (1, 1),
          'xycoords': 'axes fraction',
          'xytext': (0, 5),
          'textcoords': 'offset points',
          'pad': 0
        }
      ],
    }
  ],

  'expansions' : {}  # not needed, but left in for completeness
}

p = PlotProcessor(cfg, output_folder='.')
p.run()
