from bokeh.models import CustomJS, ColumnDataSource, BoxSelectTool, Range1d, Rect
from bokeh.plotting import figure, output_file, show
from bokeh.charts import Area, show, output_file, defaults

output_file("boxselecttool_callback.html")

source = ColumnDataSource(data=dict(x=[], y=[], width=[], height=[]))
data = dict(
    python=[2, 3, 7, 5, 26, 221, 44, 233, 254, 265, 266, 267, 120, 111],
    pypy=[12, 33, 47, 15, 126, 121, 144, 233, 254, 225, 226, 267, 110, 130],
    jython=[22, 43, 10, 25, 26, 101, 114, 203, 194, 215, 201, 227, 139, 160],
)
source = ColumnDataSource(data=data)

callback = CustomJS(args=dict(source=source), code="""
        // get data source from Callback args
        var data = source.data;

        /// get BoxSelectTool dimensions from cb_data parameter of Callback
        var geometry = cb_data['geometry'];

        /// calculate Rect attributes
        var width = geometry['x1'] - geometry['x0'];
        var height = geometry['y1'] - geometry['y0'];
        var x = geometry['x0'] + width/2;
        var y = geometry['y0'] + height/2;

        /// update data source with new Rect attributes
        data['x'].push(x);
        data['y'].push(y);
        data['width'].push(width);
        data['height'].push(height);

        // emit update of data source
        source.change.emit();
    """)

box_select = BoxSelectTool(callback=callback)



area1 = Area(data, title="Area Chart", legend="top_left",
             xlabel='time', ylabel='memory')

p = figure(plot_width=400,
           plot_height=400,
           tools=[box_select],
           title="Select Below",
           x_range=Range1d(start=0.0, end=1.0),
           y_range=Range1d(start=0.0, end=1.0))

rect = Rect(x='x',
            y='y',
            width='width',
            height='height',
            fill_alpha=0.3,
            fill_color='#009933')

p.add_glyph(source, area1, selection_glyph=area1, nonselection_glyph=area1)
show(p)