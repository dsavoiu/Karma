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
      'filename': 'demonstration_plot_2.png',

      # list of plots (one dict per plot)
      'subplots': [

        # plot histograms from 'my_file'
        {
          'expression' : '"my_file:h1"',
          'plot_method': 'bar',
          'color': 'orange',
          'label': "Histogram 1",
          'stack': 'my_stack',  # give the stack a name
          'pad': 0,
        },
        {
          'expression' : '"my_file:h2"',
          'plot_method': 'bar',
          'color': 'cornflowerblue',
          'label': "Histogram 2",
          'stack': 'my_stack',
          'pad': 0,
        },
        # plot fractions to total
        {
          'expression' : '"my_file:h1" / ("my_file:h1" + "my_file:h2")',
          'plot_method': 'bar',
          #'label': "Histogram 2",  # no legend entry in bottom pad
          'color': 'orange',
          'stack': 'my_stack',  # new stack in bottom pad despite identical name
          'pad': 1,
        },
        {
          'expression' : '"my_file:h2" / ("my_file:h1" + "my_file:h2")',
          'plot_method': 'bar',
          #'label': "Histogram 2",  # no legend entry in bottom pad
          'color': 'cornflowerblue',
          'stack': 'my_stack',
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
        'hspace': 0.08,
      },

      # define pads (a main pad and a pad for the fractions)
      'pads': [
        # pad 0
        {
          'height_share': 1,  # make pad one unit high
          'y_label' : 'Entries',
          'y_scale' : 'linear',
          'x_range' : (1, 9),
          'x_ticklabels': [],  # do not display tick labels for upper pad
        },
        # pad 1
        {
          'height_share': 1,  # make pad one unit high
          'y_label' : 'Fraction of Sum',
          'y_range' : (0, 1),
          'x_label' : 'Value',
          'x_range' : (1, 9),
          # high 'zorder' needed, line otherwise hidden by bars
          'axhlines' : [dict(values=[0.5], color='black', zorder=100)],
        }
      ],

      'texts' : [
          {
            'text': "$50$%",
            'xy': (6, 0.55),
            'xycoords': 'data',
            'fontsize': 20,
            'pad': 1,
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
