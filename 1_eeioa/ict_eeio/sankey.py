import plotly.graph_objects as go
from itertools import cycle


def plot_sankey(
    sources: list[int],
    targets: list[int],
    values: list[float],
    labels: list[str],
    title: str,
    colors: list[str] = [],
    agg_flows: bool = True,
    regroup_small_nodes: bool = False,
    regroup_threshold=1,
    column_names: list[str] = [],
    width=10,
    height=5,
):
    # Convert width and height to pixels instead of inches
    width *= 80
    height *= 80
    # Fill colors if empty
    if len(colors) <= 0 or len(colors) != len(sources):
        colors = []
        print("Filling colors")
        for link in range(len(sources)):
            colors.append("lightgrey")
    else:
        print("Not filling colors")

    if regroup_small_nodes:
        labels, sources, targets, values, colors = regroup_nodes(
            threshold=regroup_threshold,
            labels=labels,
            sources=sources,
            targets=targets,
            values=values,
            colors=colors,
        )

    if agg_flows:
        sources, targets, values, colors = aggregate_flows(
            sources=sources, targets=targets, values=values, colors=colors
        )

    sankey = go.Sankey(
        link=dict(
            source=sources,
            target=targets,
            value=values,
            color=colors,
        ),
        node=dict(
            # pad = 15,
            # thickness = 20,
            # line = dict(color = "black", width = 0.5),
            label=labels,
            # color = "blue"
        ),
    )

    fig = go.Figure(sankey)

    # Columns names legend
    for x_coordinate, column_name in enumerate(column_names):
        fig.add_annotation(
            x=x_coordinate,
            y=1.1,
            xref="x",
            yref="paper",
            text=column_name,
            showarrow=False,
            font=dict(
                # family="Courier New, monospace",
                size=16,
                color="tomato",
            ),
            align="center",
        )

    fig.update_layout(
        title_text=title,
        xaxis={
            "showgrid": False,  # thin lines in the background
            "zeroline": False,  # thick line at x=0
            "visible": False,  # numbers below
        },
        yaxis={
            "showgrid": False,  # thin lines in the background
            "zeroline": False,  # thick line at x=0
            "visible": False,  # numbers below
        },
        plot_bgcolor="rgba(0,0,0,0)",
        font_size=10,
        width=width,
        height=height,
        # paper_bgcolor="rgba(0,0,0,0)", # To make the background transparent
    )
    # fig.show()
    return fig


def aggregate_flows(
    sources: list[int], targets: list[int], values: list[float], colors: list[str]
):
    agg_sources = []
    agg_targets = []
    agg_values = []
    agg_colors = []

    for i in range(len(sources)):
        source = sources[i]
        target = targets[i]
        value = values[i]
        color = colors[i]

        if source not in agg_sources:
            agg_sources.append(source)
            agg_targets.append(target)
            agg_values.append(value)
            agg_colors.append(color)
        else:
            link_exists = False
            for index, key in enumerate(agg_sources):
                if (
                    agg_sources[index] == source
                    and agg_targets[index] == target
                    and agg_colors[index] == color
                ):
                    agg_values[index] += value
                    link_exists = True

            if not link_exists:
                agg_sources.append(source)
                agg_targets.append(target)
                agg_values.append(value)
                agg_colors.append(color)

    return agg_sources, agg_targets, agg_values, agg_colors


def regroup_nodes(
    threshold: float,
    labels: list[str],
    sources: list[int],
    targets: list[int],
    values: list[float],
    colors: list[str],
):
    """
    Regroup small nodes into an 'Others' node

    WARGNING; only one 'Others', will break if aggregating on multiple columns
    """
    if not any("Others" in s for s in labels):
        labels.append("Others")
    # First, compute nodes values
    nodes_values = {}
    for i in range(len(sources)):
        if sources[i] not in nodes_values:
            nodes_values[sources[i]] = values[i]
        else:
            nodes_values[sources[i]] += values[i]

        if targets[i] not in nodes_values:
            nodes_values[targets[i]] = values[i]
        else:
            nodes_values[targets[i]] += values[i]

    new_sources = []
    new_targets = []
    new_values = []
    new_values = []

    print(nodes_values)

    # Then, aggregate nodes under threshold
    for i in range(len(sources)):
        if nodes_values[sources[i]] < threshold:
            new_sources.append(labels.index("Others"))
        else:
            new_sources.append(sources[i])

        if nodes_values[targets[i]] < threshold:
            new_targets.append(labels.index("Others"))
        else:
            new_targets.append(targets[i])

        new_values.append(values[i])

    return labels, new_sources, new_targets, new_values, colors


colors = [
    "aliceblue",
    "antiquewhite",
    "aqua",
    "aquamarine",
    "azure",
    "beige",
    "bisque",
    "black",
    "blanchedalmond",
    "blue",
    "blueviolet",
    "brown",
    "burlywood",
    "cadetblue",
    "chartreuse",
    "chocolate",
    "coral",
    "cornflowerblue",
    "cornsilk",
    "crimson",
    "cyan",
    "darkblue",
    "darkcyan",
    "darkgoldenrod",
    "darkgray",
    "darkgrey",
    "darkgreen",
    "darkkhaki",
    "darkmagenta",
    "darkolivegreen",
    "darkorange",
    "darkorchid",
    "darkred",
    "darksalmon",
    "darkseagreen",
    "darkslateblue",
    "darkslategray",
    "darkslategrey",
    "darkturquoise",
    "darkviolet",
    "deeppink",
    "deepskyblue",
    "dimgray",
    "dimgrey",
    "dodgerblue",
    "firebrick",
    "floralwhite",
    "forestgreen",
    "fuchsia",
    "gainsboro",
    "ghostwhite",
    "gold",
    "goldenrod",
    "gray",
    "grey",
    "green",
    "greenyellow",
    "honeydew",
    "hotpink",
    "indianred",
    "indigo",
    "ivory",
    "khaki",
    "lavender",
    "lavenderblush",
    "lawngreen",
    "lemonchiffon",
    "lightblue",
    "lightcoral",
    "lightcyan",
    "lightgoldenrodyellow",
    "lightgray",
    "lightgrey",
    "lightgreen",
    "lightpink",
    "lightsalmon",
    "lightseagreen",
    "lightskyblue",
    "lightslategray",
    "lightslategrey",
    "lightsteelblue",
    "lightyellow",
    "lime",
    "limegreen",
    "linen",
    "magenta",
    "maroon",
    "mediumaquamarine",
    "mediumblue",
    "mediumorchid",
    "mediumpurple",
    "mediumseagreen",
    "mediumslateblue",
    "mediumspringgreen",
    "mediumturquoise",
    "mediumvioletred",
    "midnightblue",
    "mintcream",
    "mistyrose",
    "moccasin",
    "navajowhite",
    "navy",
    "oldlace",
    "olive",
    "olivedrab",
    "orange",
    "orangered",
    "orchid",
    "palegoldenrod",
    "palegreen",
    "paleturquoise",
    "palevioletred",
    "papayawhip",
    "peachpuff",
    "peru",
    "pink",
    "plum",
    "powderblue",
    "purple",
    "red",
    "rosybrown",
    "royalblue",
    "rebeccapurple",
    "saddlebrown",
    "salmon",
    "sandybrown",
    "seagreen",
    "seashell",
    "sienna",
    "silver",
    "skyblue",
    "slateblue",
    "slategray",
    "slategrey",
    "snow",
    "springgreen",
    "steelblue",
    "tan",
    "teal",
    "thistle",
    "tomato",
    "turquoise",
    "violet",
    "wheat",
    "white",
    "whitesmoke",
    "yellow",
    "yellowgreen",
]
cycol = cycle(colors)

colors_pool = {}


def get_impact_category_color(impact_category: str) -> str:
    if impact_category not in colors_pool:
        colors_pool[impact_category] = next(cycol)
    return colors_pool[impact_category]


def get_impact_category_short_name(impact_category: str) -> str:
    if (
        impact_category
        == "GHG emissions (GWP100) | Problem oriented approach: baseline (CML, 2001) | GWP100 (IPCC, 2007)"
    ):
        return "GHG"
    if (
        impact_category
        == "Carbon dioxide (CO2) CO2EQ IPCC categories 1 to 4 and 6 to 7 (excl land use, land use change and forestry)"
    ):
        return "CO2"
    if (
        impact_category
        == "Methane (CH4) CO2EQ IPCC categories 1 to 4 and 6 to 7 (excl land use, land use change and forestry)"
    ):
        return "CH4"
    if (
        impact_category
        == "Nitrous Oxide (N2O) CO2EQ IPCC categories 1 to 4 and 6 to 7 (excl land use, land use change and forestry)"
    ):
        return "N2O"
    return impact_category
