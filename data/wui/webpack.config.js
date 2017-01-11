const path = require('path');
const webpack = require('webpack');

module.exports = {
  entry: {
    bundle: './src/index.js'
  },
  output: {
    path: path.join(__dirname, 'html'),
    filename: 'bundle.js'
  },
  module: {
    loaders: [
      {
        loader: 'babel',
        exclude: /node_modules/,
        test: /\.js[x]?$/,
        query: {
          cacheDirectory: true,
          presets: ['react', 'latest']
        }
      },
      { test: /\.scss$/, loaders: ['style', 'css', 'sass' ]},
      { test: /\.css$/, loader: 'style-loader!css-loader' },
      { test: /\.svg/, loader: 'url-loader?mimetype=image/svg+xml' },
      { test: /\.eot/, loader: 'url-loader?mimetype=application/vnd.ms-fontobject' },
      { test: /\.otf/, loader: 'url-loader?mimetype=application/x-font-otf' },
      { test: /\.ttf/, loader: 'url-loader?mimetype=application/x-font-ttf' },
      { test: /\.woff2?/, loader: 'url-loader?mimetype=application/font-woff' },
      { test: /\.png$/, loader: 'url-loader?mimetype=image/png' },
    ]
  },
  plugins: [
    new webpack.DefinePlugin({
      'process.env.NODE_ENV': JSON.stringify(process.env.NODE_ENV)
    }),
  ],
};
