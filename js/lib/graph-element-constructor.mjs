export function constructLink(linkData, line_holder, line_text_holder, line_click_holder, widgetView, clickThickness, basic) {
    const line = d3.line()

    line_holder
        .data([linkData])
        .enter()
        .append("path")
        .attr("class", "line")
        .attr("id", function (d) {
            return d.id
        })
        .attr("marker-end", function (d) {
            if (d.arrow && d.t_shape === 0) {
                return "url(#endSquare)";
            } else if (d.arrow && d.t_shape !== 0) {
                return "url(#endCircle)";
            } else {
                return null;
            }
        })
        .attr("d", function (d) {
            let points = [[d.sx, d.sy]].concat(d.bends).concat([[d.tx, d.ty]])
            return line(points)
        })
        .attr("stroke", function (d) {
            return GraphElementConstructor.getColorStringFromJson(d.strokeColor)
        })
        .attr("stroke-width", function (d) {
            return d.strokeWidth
        })
        .attr("fill", "none");

    line_text_holder
        .data([linkData])
        .enter()
        .append("text")
        .attr("class", "linkLabel")
        .attr("text-anchor", "middle")
        .attr("dominant-baseline", "central")
        .attr("fill", "black")
        .attr("stroke-width", 1)
        .attr("stroke", "white")
        .attr("paint-order", "stroke")
        .attr("id", function (d) {
            return d.id
        })
        .text(function (d) {
            return d.label;
        })
        .style("font-size", "0.5em")
        .attr("transform", function (d) { //<-- use transform it's not a g
            return "translate(" + d.label_x + "," + d.label_y + ")";
        })

    if (basic) return

    line_click_holder
        .data([linkData])
        .enter()
        .append("path")
        .attr("class", "line")
        .attr("id", function (d) {
            return d.id
        })
        .attr("d", function (d) {
            let points = [[d.sx, d.sy]].concat(d.bends).concat([[d.tx, d.ty]])
            return line(points)
        })
        .attr("stroke", "transparent")
        .attr("stroke-width", function (d) {
            return Math.max(d.strokeWidth, clickThickness)
        })
        .attr("fill", "none")
        .on("click", function (event, d) {
            widgetView.send({"code": "linkClicked", "id": d.id, "altKey": event.altKey, "ctrlKey": event.ctrlKey});
        });
}

class GraphElementConstructor {
    static getColorStringFromJson(color) {
        return "rgba(" + color.r + ", " + color.g + ", " + color.b + ", " + color.a + ")"
    }
}