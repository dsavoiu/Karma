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
      'filename': 'demonstration_plot_3.png',

      # list of plots (one dict per plot)
      'subplots': [

        # plot object 'h2d' from 'my_file'
        {
          'expression' : '"my_file:h2d"',
          'plot_method' : 'pcolormesh',
          'cmap' : 'viridis',
        }
      ],

      # adjust layout
      'pad_spec': {
        # set margins
        'top': 0.90,
        'bottom': 0.15,
      },

      # define pads (only one pad)
      'pads': [
        {
          'x_label': 'Variable 1',
          'y_label': 'Variable 2',
          'x_range': (0.5, 6.0),
          'y_range': (0, 10),
          'z_label': 'Entries',  # colorbar label
          # add space between colorbar and its label
          'z_labelpad': 25,
        }
      ]
    }
  ],

  'expansions' : {}
}

p = PlotProcessor(cfg, output_folder='.')
p.run()
