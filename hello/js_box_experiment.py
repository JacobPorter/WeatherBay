from bokeh.models import CustomJS, ColumnDataSource, BoxSelectTool, Range1d, Rect, HoverTool
from bokeh.plotting import figure, output_file, show

output_file("boxselecttool_callback.html")

#source = ColumnDataSource(data=dict(x=[], y=[], width=[], height=[], tags=["cdf", [0, 0.1, 0.2, 0.3], "prob", 0]))
source = ColumnDataSource(data=dict(x=[], y=[], width=[], height=[], prob=[], x0=[], x1=[]))
cdf = ColumnDataSource(data=dict(cdf=[0, 0.1, 0.2, 0.3]))
bounds = ColumnDataSource(data=dict(upper=[7], lower=[4]))
#prob = ColumnDataSource(data=dict(prob=[0.0]))

callback = CustomJS(args=dict(source=source, cdf=cdf, bounds=bounds), code="""
        // get data source from Callback args
        var data = source.data;
        var cdf = cdf.data;
        //var prob = prob.data;
        /// get BoxSelectTool dimensions from cb_data parameter of Callback
        var geometry = cb_data['geometry'];
        var upper = bounds.data['upper'][0]
        /// calculate Rect attributes
        var width = geometry['x1'] - geometry['x0'];
        var height = geometry['y1'] - geometry['y0'];
        var x = geometry['x0'] + width/2;
        var y = geometry['y0'] + height/2;

        /// update data source with new Rect attributes
        data['x'].pop();
        data['y'].pop();
        data['width'].pop();
        data['height'].pop();
        data['x'].push(x);
        data['y'].push(y);
        data['width'].push(width);
        data['height'].push(height);
        data['prob'].pop();
        data['prob'].push(Math.round(y));
        data['x0'].pop();
        data['x1'].pop();
        data['x0'].push(geometry['x0'])
        data['x1'].push(geometry['x1'])
        // emit update of data source
        source.change.emit();
    """)

box_select = BoxSelectTool(callback=callback, dimensions="width")

hover = HoverTool(tooltips=[
    ("Prob", "@prob"),
    ("(x0,x1)", "(@x0, @x1)"),
])

p = figure(plot_width=400,
           plot_height=400,
           tools=[box_select, hover],
           title="Select Below",
           x_range=Range1d(start=0.0, end=10.0),
           y_range=Range1d(start=0.0, end=10.0))

rect = Rect(x='x',
            y='y',
            width='width',
            height='height',
            #tags=['cdf', cdf],
            fill_alpha=0.3,
            fill_color='#009933')

p.add_glyph(source, rect, selection_glyph=rect, nonselection_glyph=rect)
show(p)